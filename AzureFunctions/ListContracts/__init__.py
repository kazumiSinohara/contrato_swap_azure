import os
import logging
import azure.functions as func
from azure.cosmos import CosmosClient



def main(req: func.HttpRequest) -> func.HttpResponse:
    page_size = int(req.params.get("pageSize", 10))
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
        "continuation_token": continuation_token
    }

    try:
        iterator = container.query_items(query=query, **options)
        page = next(iterator.by_page(continuation_token))
        items = list(page)
        token = page.continuation_token

        return func.HttpResponse(
            status_code=200,
            body={
                "items": items,
                "continuationToken": token
            },
            mimetype="application/json"
        )
    except Exception as e:
        logging.exception("Error listing contracts")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
