# Contract Analysis API Examples

This document shows real examples of how to call the contract analysis endpoints in the Telefónica contract processing system.

## 🔧 Setup

### ⚠️ **IMPORTANT: Correct Endpoint URLs**

**✅ WORKING ENDPOINT:**
```
https://functions-contratos.azurewebsites.net/api/ListContracts?pageSize=5
```

**❌ BROKEN ENDPOINT (returns 404):**
```
https://functions-contratos.azurewebsites.net/api/contracts?pageSize=10
```

**🔑 Function Key (Pre-filled in Postman collection):**
```
lYzrDH1uEUjIdH34UmMxFL0SQ64FCd7yHsIoQ8AD7Ye7AzFugo8seg==
```

1. **Set Environment Variables**:
```bash
# Azure Functions (Primary deployment in telefonica-resource-group)
export AZURE_FUNCTIONS_KEY="your-function-key-here"
export AZURE_FUNCTIONS_BASE_URL="https://functions-contratos.azurewebsites.net/api"

# AI Endpoints (from Contract-Flow-v4/.env)
export PROMPT_FLOW_ENDPOINT="https://telefonica-open-ai.openai.azure.com"
export AZURE_OPENAI_API_KEY="6B6RIViTaaSHzkOZG44UW2ftJmHs0KEtNYnRjDalCL4B5ZDxM83TJQQJ99ALACYeBjFXJ3w3AAABACOGZba9"
export AZURE_SEARCH_ENDPOINT="https://telefonica-ai-search.search.windows.net"
export AZURE_SEARCH_ADMIN_KEY="Ve9vAL5i6tEZbr8fP6j7s33KXojnvNGmCbICbUqF2bAzSeDS5SGD"

# Cosmos DB (from AzureFunctions/.env)
export COSMOS_URI="https://telefonica-ai-lab.documents.azure.com:443/"
export COSMOS_KEY="2iFZJfmVA4FIj3MKgxPwTB6Bf1eWixzQ9yMZUZRErC25asJ8KS1hmZaSHeIvnLDUvRwpKTCyBjLLACDb5Jsz7A=="
export COSMOS_DB_NAME="poc-contratos"
export COSMOS_CONTAINER_NAME="contratos-powerbi"
```

2. **Test the APIs**:
```bash
# Run curl examples
./curl_examples.sh

# Or run Python examples
python api_examples.py
```

## 📡 Available Endpoints

### 1. Azure Functions - Contract Data Retrieval

#### Get Contract by ID
```bash
curl -H "x-functions-key: $AZURE_FUNCTIONS_KEY" \
  "$AZURE_FUNCTIONS_BASE_URL/ContractById/{contract_id}"
```

**Note**: The ContractById function appears to have routing issues. Use the working contract IDs from the List Contracts endpoint.

**Response**: Complete contract JSON with 70+ structured fields:
```json
{
  "id": "SWP FO TLF x ACESSE 001 2018",
  "CONTRATO": "SWP FO TLF x ACESSE 001 2018",
  "NOME_DA_EMPRESA_PARCEIRO": "ACESSE COMUNICAÇÃO LTDA",
  "CNPJ": "10.462.644/0001-55",
  "VALOR_ORIGINAL_CONTRATO": "112919,40",
  "QTD_FIBRAS_QTD_FO": "2",
  "MUNICIPIO_A": "Manhuaçu",
  "MUNICIPIO_B": "Juiz de Fora",
  // ... 60+ more fields
}
```

#### List All Contracts (Paginated)
```bash
curl -H "x-functions-key: $AZURE_FUNCTIONS_KEY" \
  "$AZURE_FUNCTIONS_BASE_URL/ListContracts?pageSize=5"
```

**Working Example**:
```bash
curl -H "x-functions-key: YOUR_FUNCTION_KEY" \
  "https://functions-contratos.azurewebsites.net/api/ListContracts?pageSize=5"
```

**Response**:
```json
{
  "items": [
    {
      "id": "SWP FO TLF x ACESSE 001 2018",
      "CONTRATO": "SWP FO TLF x ACESSE 001 2018",
      "NOME_DA_EMPRESA_PARCEIRO": "ACESSE COMUNICAÇÃO LTDA",
      "CNPJ": "10.462.644/0001-55",
      "VALOR_ORIGINAL_CONTRATO": "112919,40"
    }
  ],
  "continuationToken": "+RID:~FDNPAJr3Mhw...#ISV:2#IEO:65567..."
}
```

### 2. AI-Powered Contract Analysis

#### Ask Questions About Contracts (Azure OpenAI)
```bash
curl -X POST \
  -H "api-key: 6B6RIViTaaSHzkOZG44UW2ftJmHs0KEtNYnRjDalCL4B5ZDxM83TJQQJ99ALACYeBjFXJ3w3AAABACOGZba9" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Analise o contrato e me diga qual é o valor total do contrato?"
      }
    ],
    "max_tokens": 800,
    "temperature": 0.3
  }' \
  "https://telefonica-open-ai.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2023-12-01-preview"
```

**Response**:
```json
{
  "choices": [
    {
      "message": {
        "content": "O valor do contrato é R$ 1.500.000,00 (um milhão e quinhentos mil reais)."
      }
    }
  ]
}
```

#### Search Contract Content (Azure Cognitive Search)
```bash
curl -X POST \
  -H "api-key: Ve9vAL5i6tEZbr8fP6j7s33KXojnvNGmCbICbUqF2bAzSeDS5SGD" \
  -H "Content-Type: application/json" \
  -d '{
    "search": "contrato valor",
    "queryType": "simple",
    "searchFields": "content",
    "select": "id,contract_filename,content",
    "top": 5
  }' \
  "https://telefonica-ai-search.search.windows.net/indexes/contracts-v3-large/docs/search?api-version=2023-11-01"
```

**Response**:
```json
{
  "value": [
    {
      "@search.score": 0.85,
      "id": "doc1",
      "contract_filename": "contrato.pdf",
      "content": "O valor do contrato é de R$ 1.500.000,00..."
    }
  ]
}
```

#### Parse Raw Contract Data (Legacy)
```bash
curl -X POST \
  -H "Authorization: Bearer $PARSE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "Nome da empresa cedente (parte) do contrato sem cnpj": "Telefónica Brasil S.A.",
    "Área nas torres para instalação dos equipamentos": "200 m²",
    "Localização da torre contratada": "São Paulo - SP",
    "O prazo/vigência de duração do contrato (data de início e término)": "01/01/2023 a 01/01/2028",
    "Valor do contrato": "R$ 2.000.000,00"
  }' \
  "$PARSE_ENDPOINT"
```

**Response**: Structured JSON with normalized data:
```json
{
  "nome_cedente": "Telefónica Brasil S.A.",
  "area_estimada": "200",
  "localizacao_torre": "São Paulo - SP",
  "prazo_vigencia": "01/01/2023 a 01/01/2028",
  "valor_contrato": "R$ 2.000.000,00"
}
```

## 🐍 Python Examples

See `api_examples.py` for complete Python code examples using the `requests` library.

Key functions:
- `get_contract_by_id(contract_id)` - Retrieve contract data
- `list_contracts(page_size, continuation_token)` - List contracts with pagination
- `analyze_contract_question(pdf_filename, question, k)` - AI question answering
- `parse_contract_data(metadata_dict)` - Parse raw contract metadata

## 📊 Contract Data Structure

Contracts contain 70+ fields organized in categories:

- **Identification**: Contract ID, number, modality, company info
- **Parties**: Company names, CNPJ, responsible units
- **Geography**: Cities, states, routes, distances
- **Technical**: Fiber count, capacity, wavelengths, SLA metrics
- **Financial**: Contract value, CAPEX/OPEX savings
- **Dates**: Signature date, validity periods, renewals
- **SLA & Status**: MTTR, contract status, responsible person

## 🔑 Authentication

- **Azure Functions**: Use `x-functions-key` header with function key
- **AI Endpoints**: Use `Authorization: Bearer {key}` header with endpoint key

## 🚀 Quick Test

```bash
# Test if your setup works
./curl_examples.sh
```

This will test all endpoints and show real responses from your deployed system.
