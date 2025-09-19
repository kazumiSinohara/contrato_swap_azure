import azure.functions as func
import logging
import os
import tempfile
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

def main(myblob: func.InputStream):
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