import os
import logging
import azure.functions as func
from azure.cosmos import CosmosClient, exceptions
import json

cosmos_url = os.getenv("ACCOUNT_URI_COSMOS")
cosmos_key = os.getenv("ACCOUNT_KEY_COSMOS")

def main(req: func.HttpRequest) -> func.HttpResponse:
    contract_id = req.route_params.get("contract_id")
    partition_key = req.route_params.get("partition_key")

    logging.info(f"contract_id: {contract_id}")
    logging.info(f"partition_key: {partition_key}")

    
    db_name = "poc-contratos"
    container_name = "contratos-powerbi"
    logging.info(f"cosmos_url: {cosmos_url}")
    logging.info(f"cosmos_key: {cosmos_key}")
    logging.info(f"db_name: {db_name}")
    logging.info(f"container_name: {container_name}")
    if not cosmos_key:
        raise ValueError("ACCOUNT_KEY_COSMOS is not set or is empty")
    
    client = CosmosClient(cosmos_url, credential=cosmos_key)
    database = client.get_database_client(db_name)
    container = database.get_container_client(container_name)

    try:
        item = container.read_item(item=contract_id, partition_key=partition_key)
        logging.info(f"item: {item}")
        return func.HttpResponse(
            status_code=200,
            body=json.dumps(item),
            mimetype="application/json"
        )
    except exceptions.CosmosResourceNotFoundError:
        return func.HttpResponse("Contract not found", status_code=404)
    except Exception as e:
        logging.exception("Error fetching contract by ID")
        return func.HttpResponse(f"Internal error: {str(e)}", status_code=500)
