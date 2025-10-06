# Contract Analysis API - Postman Collection

This Postman collection provides comprehensive testing for all contract analysis endpoints in your Telefónica contract processing system.

## 📥 **Import the Collection**

1. Open Postman
2. Click **Import** button
3. Select **File**
4. Choose `Contract_Analysis_API.postman_collection.json`
5. Import

## 🔧 **Setup Environment Variables**

Before testing, configure these variables in Postman:

### **Required Variables:**

| Variable | Value | How to Get |
|----------|--------|------------|
| `AZURE_FUNCTIONS_KEY` | Your function key | `az functionapp keys list --name functions-contratos --resource-group telefonica-resource-group --query 'functionKeys.default' -o tsv` |
| `AZURE_FUNCTIONS_BASE_URL` | `https://functions-contratos.azurewebsites.net/api` | Pre-filled |
| `AZURE_OPENAI_KEY` | `6B6RIViTaaSHzkOZG44UW2ftJmHs0KEtNYnRjDalCL4B5ZDxM83TJQQJ99ALACYeBjFXJ3w3AAABACOGZba9` | Pre-filled |
| `AZURE_SEARCH_KEY` | `Ve9vAL5i6tEZbr8fP6j7s33KXojnvNGmCbICbUqF2bAzSeDS5SGD` | Pre-filled |
| `COSMOS_KEY` | `2iFZJfmVA4FIj3MKgxPwTB6Bf1eWixzQ9yMZUZRErC25asJ8KS1hmZaSHeIvnLDUvRwpKTCyBjLLACDb5Jsz7A==` | Pre-filled |
| `CONTRACT_ID` | `ABC123` | Replace with real contract ID from your data |

## 📋 **Available Test Requests**

### **1. Azure Functions - Contract Data**

#### **Get Contract by ID**
- **Method**: GET
- **URL**: `{{AZURE_FUNCTIONS_BASE_URL}}/contractid/{{CONTRACT_ID}}`
- **Auth**: `x-functions-key` header
- **Response**: Complete contract JSON (70+ fields)

#### **List All Contracts**
- **Method**: GET
- **URL**: `{{AZURE_FUNCTIONS_BASE_URL}}/contracts?pageSize=10`
- **Auth**: `x-functions-key` header
- **Response**: Paginated contract list

#### **Alternative Contract Lookup**
- **Method**: GET
- **URL**: `{{AZURE_FUNCTIONS_BASE_URL}}/contracts?id={{CONTRACT_ID}}`
- **Auth**: `x-functions-key` header

### **2. Azure OpenAI - Contract Analysis**

#### **Analyze Contract Content (GPT-4)**
- **Method**: POST
- **URL**: `https://telefonica-open-ai.openai.azure.com/openai/deployments/gpt-4/chat/completions`
- **Headers**: `api-key`, `Content-Type: application/json`
- **Body**: Chat completion request for contract analysis

#### **Contract Summary (GPT-3.5)**
- **Method**: POST
- **URL**: `https://telefonica-open-ai.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions`
- **Headers**: `api-key`, `Content-Type: application/json`
- **Body**: Faster summary generation

### **3. Azure Cognitive Search - Contract Search**

#### **Search Contract Content**
- **Method**: POST
- **URL**: `https://telefonica-ai-search.search.windows.net/indexes/contracts-v3-large/docs/search`
- **Headers**: `api-key`, `Content-Type: application/json`
- **Body**: Search query for contract content

#### **Advanced Contract Search**
- **Method**: POST
- **URL**: `https://telefonica-ai-search.search.windows.net/indexes/contracts-v3-large/docs/search`
- **Body**: Advanced search with filters and facets

### **4. Cosmos DB - Raw Contract Data**

#### **Query Contracts by ID**
- **Method**: POST
- **URL**: `https://telefonica-ai-lab.documents.azure.com:443/dbs/poc-contratos/colls/contratos-powerbi/docs`
- **Headers**: `Authorization: Bearer`, `x-ms-version`, `x-ms-date`, `Content-Type`
- **Body**: SQL query for specific contract

#### **List Recent Contracts**
- **Method**: POST
- **URL**: `https://telefonica-ai-lab.documents.azure.com:443/dbs/poc-contratos/colls/contratos-powerbi/docs`
- **Body**: SQL query for recent contracts

#### **Search High-Value Contracts**
- **Method**: POST
- **URL**: `https://telefonica-ai-lab.documents.azure.com:443/dbs/poc-contratos/colls/contratos-powerbi/docs`
- **Body**: SQL query for high-value contracts

## 🚀 **How to Use**

### **Step 1: Set Your Function Key**
```bash
# Get your Azure Functions key
az functionapp keys list --name functions-contratos \
  --resource-group telefonica-resource-group \
  --query 'functionKeys.default' -o tsv
```

### **Step 2: Update CONTRACT_ID Variable**
- Replace `ABC123` with a real contract ID from your database
- You can get contract IDs by running the "List All Contracts" request first

### **Step 3: Test the Endpoints**
1. Start with **Azure Functions** endpoints (they don't require complex setup)
2. Test **Azure OpenAI** endpoints for AI analysis
3. Try **Azure Search** for contract content search
4. Use **Cosmos DB** endpoints for direct database queries

## 📊 **Expected Responses**

### **Contract Data Response Example:**
```json
{
  "id": "CONTRACT123",
  "CONTRATO": "SWP FO TLF x ITAKE 001 2012",
  "NOME_DA_EMPRESA_PARCEIRO": "Empresa Parceira Ltda",
  "CNPJ": "12.345.678/0001-90",
  "VALOR_ORIGINAL_CONTRATO": "R$ 1.500.000,00",
  "QTD_FIBRAS_QTD_FO": "24",
  "MUNICIPIO_A": "São Paulo",
  "MUNICIPIO_B": "Rio de Janeiro",
  // ... 60+ more fields
}
```

### **Search Response Example:**
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

### **OpenAI Response Example:**
```json
{
  "choices": [
    {
      "message": {
        "content": "O contrato analisado é um acordo de swap de fibras ópticas..."
      }
    }
  ]
}
```

## 🔍 **Troubleshooting**

### **Authentication Issues**
- **Azure Functions**: Make sure `AZURE_FUNCTIONS_KEY` is set correctly
- **OpenAI/Search**: Keys are pre-filled in the collection
- **Cosmos DB**: Check that `x-ms-date` header is auto-generated

### **Contract ID Issues**
- Use "List All Contracts" to get valid contract IDs
- Replace `{{CONTRACT_ID}}` with actual IDs from your database

### **Rate Limiting**
- Azure OpenAI has rate limits - space out requests
- Azure Functions may have concurrent execution limits

## 📁 **Collection Structure**

```
Contract Analysis API - Telefónica/
├── Azure Functions - Contract Data/
│   ├── Get Contract by ID
│   ├── List All Contracts (Paginated)
│   └── Alternative Contract Lookup
├── Azure OpenAI - Contract Analysis/
│   ├── Analyze Contract Content (GPT-4)
│   └── Contract Summary (GPT-3.5)
├── Azure Cognitive Search - Contract Search/
│   ├── Search Contract Content
│   ├── Advanced Contract Search
│   └── Search with Scoring Profile
├── Cosmos DB - Raw Contract Data/
│   ├── Query Contracts by ID
│   ├── List Recent Contracts
│   └── Search High-Value Contracts
└── Health Checks & Monitoring/
    ├── Azure Functions Health Check
    └── Cosmos DB Health Check
```

## 🔐 **Security Notes**

- This collection contains real API keys for your Azure services
- Never commit this collection to version control
- Keep your `AZURE_FUNCTIONS_KEY` secure
- Rotate keys regularly in production

## 🎯 **Quick Start**

1. Import the collection
2. Set `AZURE_FUNCTIONS_KEY` variable
3. Run "List All Contracts" to get contract IDs
4. Update `CONTRACT_ID` variable
5. Test all endpoints!

Happy testing! 🚀
