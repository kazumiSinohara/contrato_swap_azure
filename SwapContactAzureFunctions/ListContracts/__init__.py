import os
import logging
import azure.functions as func
from azure.cosmos import CosmosClient
import json

cosmos_url = os.getenv("ACCOUNT_URI_COSMOS")
cosmos_key = os.getenv("ACCOUNT_KEY_COSMOS")


def main(req: func.HttpRequest) -> func.HttpResponse:
    page_size = int(req.params.get("pageSize", 10))
    continuation_token = req.params.get("continuationToken")
    logging.info(f"page_size: {page_size}")
    logging.info(f"continuation_token: {continuation_token}")

    db_name = "poc-contratos"
    container_name = "contratos-powerbi"

    if not cosmos_key:
        raise ValueError("ACCOUNT_KEY_COSMOS is not set or is empty")

    client = CosmosClient(cosmos_url, credential=cosmos_key)
    database = client.get_database_client(db_name)
    container = database.get_container_client(container_name)

    query = "SELECT * FROM c ORDER BY c._ts DESC"

    try:
        iterator = container.query_items(
            query=query,
            enable_cross_partition_query=True,
            max_item_count=page_size  # ✅ Set page size here
        )

        # ✅ Only pass continuation_token here
        pages = iterator.by_page(continuation_token=continuation_token)
        page = next(pages)

        items = list(page)
        token = pages.continuation_token

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
