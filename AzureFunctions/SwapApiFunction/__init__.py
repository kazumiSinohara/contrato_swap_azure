import azure.functions as func
import json
import logging
from cosmos import get_contract_by_id

def main(req: func.HttpRequest) -> func.HttpResponse:
    contract_id = req.params.get('id')
    if not contract_id:
        return func.HttpResponse("Missing 'id' parameter", status_code=400)

    logging.info(f"Looking up contract ID: {contract_id}")
    result = get_contract_by_id(contract_id)

    if "error" in result:
        return func.HttpResponse(
            json.dumps({"detail": result["error"]}),
            status_code=404,
            mimetype="application/json"
        )

    return func.HttpResponse(
        json.dumps(result, ensure_ascii=False),
        mimetype="application/json"
    )
