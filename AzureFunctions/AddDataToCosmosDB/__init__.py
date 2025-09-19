import azure.functions as func
import logging
import os
import tempfile
import json
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from call_parse_contract_endpoint import parse_contract_information

def main(myblob: func.InputStream):
    logging.info(f"Name: {myblob.name}")
    json_filename = myblob.name.split("/")[-1]
    if json_filename.split(".")[-1] != "json":
        return func.HttpResponse(f"File {json_filename} is not a json")
    blob_service_client = BlobServiceClient(os.getenv("ACCOUNT_URL"), credential=os.getenv("STORAGE_KEY"))
    blob_client = blob_service_client.get_blob_client(container="contratos", blob=json_filename)
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'wb') as tmp:
            download_stream = blob_client.download_blob()
            tmp.write(download_stream.readall())

        with open(path) as f:
            data = json.load(f)

        parsed_data = parse_contract_information(data)
        logging.info(f"Parsed data: {parsed_data}")

        new_data = {**data}
        new_data.pop('Nome da empresa cedente (parte) do contrato sem cnpj', None)
        try:
            new_data["Área Estimada (m2)"] = float(parsed_data["area_estimada"])
        except:
            new_data["Área Estimada (m2)"] = 0.0
        new_data["Nome da empresa cedente"] = parsed_data["nome_cedente"]
        try:
            localizacao_parsed = parsed_data["localizacao_torre"]
            if "não" in localizacao_parsed.lower():
                new_data["Localização"] = "NaN"
            else:
                new_data["Localização"] = localizacao_parsed
        except:
            new_data["Localização"] = "NaN"
        new_data["O prazo/vigência de duração do contrato (data de início e término)"] = parsed_data["prazo_vigencia"]
        try:
            valor_contrato_parsed = parsed_data["valor_contrato"]
            if "R$" in valor_contrato_parsed:
                new_data["Valor do contrato"] = valor_contrato_parsed
            else:
                new_data["Valor do contrato"] = float(valor_contrato_parsed)
        except:
            new_data["Valor do contrato"] = 0
        new_data["contractPDF"] = myblob.name.split("contratos/")[-1].split(".pdf")[0]+".pdf"
        new_data["id"] = myblob.name.split("contratos/")[-1].split(".pdf")[0]
        logging.info(f"Final data: {new_data}")
        URL = os.getenv('ACCOUNT_URI_COSMOS')
        KEY = os.getenv('ACCOUNT_KEY_COSMOS')
        client = CosmosClient(URL, credential=KEY)
        DATABASE_NAME = 'poc-contratos'
        database = client.get_database_client(DATABASE_NAME)
        CONTAINER_NAME = 'contratos-powerbi'
        try:
            container = database.create_container(id=CONTAINER_NAME, partition_key=PartitionKey(path="/contractPDF"))
        except exceptions.CosmosResourceExistsError:
            container = database.get_container_client(CONTAINER_NAME)
        except exceptions.CosmosHttpResponseError:
            raise
        container.upsert_item(new_data)
    finally:
        os.remove(path) 