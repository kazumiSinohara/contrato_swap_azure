import azure.functions as func
import datetime
import json
import logging
import os
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch
from azure.storage.blob import BlobServiceClient
from azure.search.documents.indexes.models import (
                SearchableField,
                SearchField,
                SearchFieldDataType,
                SimpleField,
            )
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from call_parse_contract_endpoint import parse_contract_information
import tempfile

from call_promptflow_endpoint import get_contract_information

app = func.FunctionApp()


@app.blob_trigger(arg_name="myblob", path="contratos/{name}.pdf",
                               connection="AzureBlobStorageLab") 
def ExtractTextFromPDF(myblob: func.InputStream):
    doc_intelligence_endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    doc_intelligence_key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    logging.info(f"Name: {myblob.name}")
    pdf_filename = myblob.name.split("/")[-1]
    if pdf_filename.split(".")[-1] != "pdf":
        return func.HttpResponse(f"File {pdf_filename} is not an pdf")
    blob_service_client = BlobServiceClient(os.getenv("ACCOUNT_URL"), credential=os.getenv("STORAGE_KEY"))
    blob_client = blob_service_client.get_blob_client(container="contratos", blob=pdf_filename)
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'wb') as tmp:
            download_stream = blob_client.download_blob()
            tmp.write(download_stream.readall())

        loader = AzureAIDocumentIntelligenceLoader(file_path=path, api_key = doc_intelligence_key, api_endpoint = doc_intelligence_endpoint, api_model="prebuilt-layout", mode="markdown")
        docs_single = loader.load()

        extracted_text = docs_single[0].page_content

        blob_client = blob_service_client.get_blob_client(container="contratos", blob=f"{pdf_filename}.txt")
        blob_client.upload_blob(extracted_text, blob_type="BlockBlob")

    finally:
        os.remove(path)

@app.function_name(name="ListContracts")
@app.route(route="ListContracts", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def ListContractsHttp(req: func.HttpRequest) -> func.HttpResponse:
    page_size = int(req.params.get("pageSize", 10))

    # Support both GET (query params) and POST (request body) for continuation tokens
    if req.method == "POST":
        try:
            req_body = req.get_json()
            continuation_token = req_body.get("continuationToken") if req_body else None
        except:
            continuation_token = None
    else:
        continuation_token = req.params.get("continuationToken", None)

    cosmos_url = os.getenv("ACCOUNT_URI_COSMOS")
    cosmos_key = os.getenv("ACCOUNT_KEY_COSMOS")
    db_name = os.getenv("COSMOS_DB_NAME")
    container_name = os.getenv("COSMOS_CONTAINER_NAME")
    
    client = CosmosClient(cosmos_url, credential=cosmos_key)
    database = client.get_database_client(db_name)
    container = database.get_container_client(container_name)

    query = "SELECT * FROM c ORDER BY c._ts DESC"
    options = {
        "enable_cross_partition_query": True,
        "max_item_count": page_size,
    }

    try:
        iterator = container.query_items(
            query=query, 
            parameters=None, 
            **options
        ).by_page(continuation_token)
        page = next(iterator)
        items = list(page)
        token = page.continuation_token

        return func.HttpResponse(
            status_code=200,
            body=json.dumps({
                "items": items,
                "continuationToken": token
            }),
            mimetype="application/json"
        )
    except Exception as e:
        logging.exception("Error listing contracts")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.function_name(name="ContractById")
@app.route(route="contractid/{contract_id}", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def ContractByIdHttp(req: func.HttpRequest) -> func.HttpResponse:
    # Delegate to existing v1-style implementation
    from ContractById import __init__ as contract_by_id
    return contract_by_id.main(req)

@app.function_name(name="SwapApiFunction")
@app.route(route="contracts", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def SwapApiFunctionHttp(req: func.HttpRequest) -> func.HttpResponse:
    # Delegate to existing v1-style implementation
    from SwapApiFunction import __init__ as swap_api
    return swap_api.main(req)

@app.blob_trigger(arg_name="myblob", path="contratos/{name}.txt",
                               connection="AzureBlobStorageLab") 
def ProcessText(myblob: func.InputStream):
    logging.info(f"Name: {myblob.name}")
    txt_filename = myblob.name.split("/")[-1]
    if txt_filename.split(".")[-1] != "txt":
        return func.HttpResponse(f"File {txt_filename} is not a txt")
    blob_service_client = BlobServiceClient(os.getenv("ACCOUNT_URL"), credential=os.getenv("STORAGE_KEY"))
    blob_client = blob_service_client.get_blob_client(container="contratos", blob=txt_filename)

    # extract metadata and save JSON
    contract_metadata = get_contract_information(txt_filename)
    output = json.dumps(contract_metadata)
    logging.info(f"Extracted: {output}")
    blob_client = blob_service_client.get_blob_client(container="contratos", blob=f"{txt_filename}.json")
    blob_client.upload_blob(output, blob_type="BlockBlob")


@app.blob_trigger(arg_name="myblob", path="contratos/{name}.json",
                               connection="AzureBlobStorageLab") 
def AddDataToCosmosDB(myblob: func.InputStream):
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
            new_data["Área Estimada (m2)"] =  float(parsed_data["area_estimada"])
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