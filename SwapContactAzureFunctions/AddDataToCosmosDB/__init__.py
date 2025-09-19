import azure.functions as func
import logging
import os
import tempfile
import json
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient, PartitionKey, exceptions


def main(myblob: func.InputStream):
    logging.info(f"Processing blob: {myblob.name}")
    json_filename = myblob.name.split("/")[-1]

    if not json_filename.endswith(".json"):
        return func.HttpResponse(f"File {json_filename} is not a JSON", status_code=400)

    blob_service_client = BlobServiceClient(
        os.getenv("ACCOUNT_URL"),
        credential=os.getenv("STORAGE_KEY")
    )
    blob_client = blob_service_client.get_blob_client(container="contratos", blob=json_filename)

    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'wb') as tmp:
            download_stream = blob_client.download_blob()
            tmp.write(download_stream.readall())

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logging.info(f"Loaded JSON with keys: {list(data.keys())}")

        questions = data.get("questions")
        if not questions:
            logging.warning("No 'questions' field found.")
        elif isinstance(questions, str):
            try:
                flat_questions = json.loads(questions)
                if isinstance(flat_questions, dict):
                    data.update(flat_questions)
                    data.pop("questions", None)
                    logging.info(f"Flattened {len(flat_questions)} question fields into top-level keys.")
                else:
                    logging.warning("Decoded 'questions' is not a dict.")
            except json.JSONDecodeError:
                logging.error("Failed to decode 'questions' string as JSON.")
        else:
            logging.warning(f"'questions' is not a string: {type(questions)}")

        # Add required metadata fields
        contract_base = myblob.name.split("contratos/")[-1].split(".pdf")[0]
        data["contractPDF"] = f"{contract_base}.pdf"
        data["id"] = contract_base

        logging.info(f"Prepared final data with {len(data)} total keys for Cosmos DB.")

        # Cosmos DB connection
        cosmos_client = CosmosClient(
            os.getenv('ACCOUNT_URI_COSMOS'),
            credential=os.getenv('ACCOUNT_KEY_COSMOS')
        )
        database = cosmos_client.get_database_client('poc-contratos')
        container_name = 'contratos-powerbi'

        try:
            container = database.create_container(
                id=container_name,
                partition_key=PartitionKey(path="/contractPDF")
            )
        except exceptions.CosmosResourceExistsError:
            container = database.get_container_client(container_name)
        except exceptions.CosmosHttpResponseError as e:
            logging.error(f"Cosmos DB error: {e}")
            raise

        container.upsert_item(data)
        logging.info(f"✅ Successfully upserted item with id '{data['id']}' and {len(data)} fields.")

    finally:
        os.remove(path)
