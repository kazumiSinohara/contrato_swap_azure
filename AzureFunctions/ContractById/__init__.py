import os
import logging
import azure.functions as func
from azure.cosmos import CosmosClient, exceptions



def main(req: func.HttpRequest) -> func.HttpResponse:
    contract_id = req.route_params.get("contract_id")
    partition_key = f"{contract_id}.pdf"

    cosmos_url = os.getenv("ACCOUNT_URI_COSMOS")
    cosmos_key = os.getenv("ACCOUNT_KEY_COSMOS")
    db_name = os.getenv("COSMOS_DB_NAME")
    container_name = os.getenv("COSMOS_CONTAINER_NAME")
    client = CosmosClient(cosmos_url, credential=cosmos_key)
    database = client.get_database_client(db_name)
    container = database.get_container_client(container_name)

    try:
        item = container.read_item(item=contract_id, partition_key=partition_key)
        return func.HttpResponse(
            status_code=200,
            body=item,
            mimetype="application/json"
        )
    except exceptions.CosmosResourceNotFoundError:
        return func.HttpResponse("Contract not found", status_code=404)
    except Exception as e:
        logging.exception("Error fetching contract by ID")
        return func.HttpResponse(f"Internal error: {str(e)}", status_code=500)
