from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from cosmos import get_contract_by_id

app = FastAPI()

@app.get("/contract")
def read_contract(id: str = Query(..., description="Contract ID")):
    result = get_contract_by_id(id)
    if "error" in result:
        return JSONResponse(status_code=404, content={"detail": result["error"]})
    return JSONResponse(status_code=200, content=result)

@app.get("/health")
def health_check():
    return {"status": "ok"}
