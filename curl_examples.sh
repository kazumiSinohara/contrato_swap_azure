#!/bin/bash

# Contract Analysis API - cURL Examples
# ====================================
#
# This script uses real endpoints from your .env files:
# - Azure Functions: functions-contratos.azurewebsites.net
# - Azure OpenAI: telefonica-open-ai.openai.azure.com
# - Azure Search: telefonica-ai-search.search.windows.net
# - Cosmos DB: telefonica-ai-lab.documents.azure.com
#
# Before running, set your function key:
# export AZURE_FUNCTIONS_KEY="lYzrDH1uEUjIdH34UmMxFL0SQ64FCd7yHsIoQ8AD7Ye7AzFugo8seg=="

echo "🚀 Contract Analysis API Examples (Real Endpoints)"
echo "=================================================="
echo ""
echo "✅ WORKING ENDPOINT: /api/ListContracts"
echo "❌ BROKEN ENDPOINT:  /api/contracts"
echo ""

# Set real URLs and keys from .env files
AZURE_FUNCTIONS_BASE_URL="https://functions-contratos.azurewebsites.net/api"
AZURE_FUNCTIONS_KEY="${AZURE_FUNCTIONS_KEY:-lYzrDH1uEUjIdH34UmMxFL0SQ64FCd7yHsIoQ8AD7Ye7AzFugo8seg==}"
AZURE_OPENAI_KEY="6B6RIViTaaSHzkOZG44UW2ftJmHs0KEtNYnRjDalCL4B5ZDxM83TJQQJ99ALACYeBjFXJ3w3AAABACOGZba9"
AZURE_SEARCH_KEY="Ve9vAL5i6tEZbr8fP6j7s33KXojnvNGmCbICbUqF2bAzSeDS5SGD"

# Check if required environment variables are set
if [ -z "$AZURE_FUNCTIONS_KEY" ]; then
    echo "❌ Please set AZURE_FUNCTIONS_KEY environment variable"
    echo "💡 Get it with: az functionapp keys list --name functions-contratos --resource-group telefonica-resource-group --query 'functionKeys.default' -o tsv"
    exit 1
fi

echo "✅ Environment configured"
echo "🔗 Using real endpoints from your .env files"

# Example 1: List contracts (✅ WORKING)
echo -e "\n📋 1. Listing contracts (✅ WORKING)..."
curl -s -H "x-functions-key: $AZURE_FUNCTIONS_KEY" \
  "$AZURE_FUNCTIONS_BASE_URL/ListContracts?pageSize=3" | jq '.items[0:2]'

# Example 2: Get contract by ID (⚠️ may have routing issues)
echo -e "\n📄 2. Getting contract by ID (⚠️ may have routing issues)..."
echo "Using contract ID from the list above..."
curl -s -H "x-functions-key: $AZURE_FUNCTIONS_KEY" \
  "$AZURE_FUNCTIONS_BASE_URL/ContractById/SWP%20FO%20TLF%20x%20ACESSE%20001%202018" | jq '.'

# Example 3: Alternative contract lookup (⚠️ may have routing issues)
echo -e "\n🔍 3. Alternative contract lookup (⚠️ may have routing issues)..."
curl -s -H "x-functions-key: $AZURE_FUNCTIONS_KEY" \
  "$AZURE_FUNCTIONS_BASE_URL/ContractById?id=SWP%20FO%20TLF%20x%20ACESSE%20001%202018" | jq '.'

# Example 4: Azure OpenAI Contract Analysis
echo -e "\n🤖 4. Azure OpenAI Contract Analysis..."
curl -s -X POST \
  -H "api-key: $AZURE_OPENAI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Analise o seguinte contrato de telecomunicações e extraia: valor do contrato, nome da empresa parceira, e prazo de vigência."
      }
    ],
    "max_tokens": 800,
    "temperature": 0.3
  }' \
  "https://telefonica-open-ai.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2023-12-01-preview" | jq '.'

# Example 5: Azure Cognitive Search
echo -e "\n🔍 5. Azure Cognitive Search - Contract Content..."
curl -s -X POST \
  -H "api-key: $AZURE_SEARCH_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "search": "contrato valor",
    "queryType": "simple",
    "searchFields": "content",
    "select": "id,contract_filename,content",
    "top": 3
  }' \
  "https://telefonica-ai-search.search.windows.net/indexes/contracts-v3-large/docs/search?api-version=2023-11-01" | jq '.'

# Example 6: Cosmos DB Query (if you have contract IDs)
echo -e "\n💾 6. Cosmos DB Contract Lookup..."
echo "Note: Replace CONTRACT_ID with an actual contract ID from your database"
curl -s -X POST \
  -H "Authorization: Bearer 2iFZJfmVA4FIj3MKgxPwTB6Bf1eWixzQ9yMZUZRErC25asJ8KS1hmZaSHeIvnLDUvRwpKTCyBjLLACDb5Jsz7A==" \
  -H "Content-Type: application/json" \
  -H "x-ms-version: 2018-12-31" \
  -H "x-ms-date: $(date -u +%a,\ %d\ %b\ %Y\ %H:%M:%S\ GMT)" \
  -d '{
    "query": "SELECT * FROM c WHERE c.id = @contractId",
    "parameters": [
      {
        "name": "@contractId",
        "value": "CONTRACT_ID_HERE"
      }
    ]
  }' \
  "https://telefonica-ai-lab.documents.azure.com:443/dbs/poc-contratos/colls/contratos-powerbi/docs" | jq '.'

echo -e "\n✨ Examples completed!"
