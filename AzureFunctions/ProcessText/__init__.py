import azure.functions as func
import logging
import os
import tempfile
import json
from azure.storage.blob import BlobServiceClient

from call_promptflow_endpoint import get_contract_information


def main(myblob: func.InputStream):
    logging.info(f"Name: {myblob.name}")
    txt_filename = myblob.name.split("/")[-1]
    if txt_filename.split(".")[-1] != "txt":
        return func.HttpResponse(f"File {txt_filename} is not a txt")
    blob_service_client = BlobServiceClient(os.getenv("ACCOUNT_URL"), credential=os.getenv("STORAGE_KEY"))
    blob_client = blob_service_client.get_blob_client(container="contratos", blob=txt_filename)
   

    contract_metadata = get_contract_information(txt_filename)
    output = json.dumps(contract_metadata)
    logging.info(f"Extracted: {output}")
    blob_client = blob_service_client.get_blob_client(container="contratos", blob=f"{txt_filename}.json")
    blob_client.upload_blob(output, blob_type="BlockBlob")
