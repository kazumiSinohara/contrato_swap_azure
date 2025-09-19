from azure.storage.blob import BlobServiceClient
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def retriever(pdf_filename: str) -> str:
    container_name = "contratos"
    logging.info(f"Retrieving blob for {pdf_filename}")
    #blob_file = f"{pdf_filename}.txt"

    # Get connection string from environment variable
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING environment variable is not set")

    blob_service_client = BlobServiceClient.from_connection_string(conn_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=pdf_filename)
    blob_data = blob_client.download_blob().readall().decode("utf-8")

    return blob_data

# ✅ Test it
if __name__ == "__main__":
    filename = "SWP FO TLF x ITAKE 001 2012 4.pdf.txt"
    try:
        result = retriever(filename)
        print(result)
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set the AZURE_STORAGE_CONNECTION_STRING environment variable")

