import os
from azure.cosmos import CosmosClient, exceptions

cosmos_url = os.getenv("COSMOS_URI")
cosmos_key = os.getenv("COSMOS_KEY")
db_name = os.getenv("COSMOS_DB_NAME")
container_name = os.getenv("COSMOS_CONTAINER_NAME")

client = CosmosClient(cosmos_url, credential=cosmos_key)
database = client.get_database_client(db_name)
container = database.get_container_client(container_name)

def get_contract_by_id(contract_id: str):
    try:
        partition_key = f"{contract_id}.pdf"
        item = container.read_item(item=contract_id, partition_key=partition_key)
        return item
    except exceptions.CosmosResourceNotFoundError:
        return {"error": "Item not found"}
    except Exception as e:
        return {"error": f"Internal error: {str(e)}"}
