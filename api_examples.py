"""
Real API Call Examples for Contract Analysis System
===================================================

This file contains working examples of how to call the contract analysis endpoints.
Make sure to set your environment variables first:

export AZURE_FUNCTIONS_KEY="your-function-key-here"
export AZURE_FUNCTIONS_BASE_URL="https://your-functions-app.azurewebsites.net/api"
export PROMPT_FLOW_ENDPOINT="https://your-ml-workspace.services.azureml.net/endpoints/your-endpoint"
export PROMPT_FLOW_KEY="your-endpoint-key-here"
"""

import os
import requests
import json
from typing import Dict, List, Optional

# Load environment variables (with real defaults from .env files)
AZURE_FUNCTIONS_KEY = os.getenv("AZURE_FUNCTIONS_KEY")
AZURE_FUNCTIONS_BASE_URL = os.getenv("AZURE_FUNCTIONS_BASE_URL", "https://functions-contratos.azurewebsites.net/api")

# Real Azure OpenAI credentials from Contract-Flow-v4/.env
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://telefonica-open-ai.openai.azure.com")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "6B6RIViTaaSHzkOZG44UW2ftJmHs0KEtNYnRjDalCL4B5ZDxM83TJQQJ99ALACYeBjFXJ3w3AAABACOGZba9")

# Real Azure Search credentials
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "https://telefonica-ai-search.search.windows.net")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY", "Ve9vAL5i6tEZbr8fP6j7s33KXojnvNGmCbICbUqF2bAzSeDS5SGD")

# Real Cosmos DB credentials from AzureFunctions/.env
COSMOS_URI = os.getenv("COSMOS_URI", "https://telefonica-ai-lab.documents.azure.com:443/")
COSMOS_KEY = os.getenv("COSMOS_KEY", "2iFZJfmVA4FIj3MKgxPwTB6Bf1eWixzQ9yMZUZRErC25asJ8KS1hmZaSHeIvnLDUvRwpKTCyBjLLACDb5Jsz7A==")
COSMOS_DB_NAME = os.getenv("COSMOS_DB_NAME", "poc-contratos")
COSMOS_CONTAINER_NAME = os.getenv("COSMOS_CONTAINER_NAME", "contratos-powerbi")

def get_contract_by_id(contract_id: str) -> Dict:
    """Get contract data by ID using Azure Functions"""
    url = f"{AZURE_FUNCTIONS_BASE_URL}/contractid/{contract_id}"

    headers = {
        "x-functions-key": AZURE_FUNCTIONS_KEY
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def list_contracts(page_size: int = 10, continuation_token: Optional[str] = None) -> Dict:
    """List contracts with pagination"""
    url = f"{AZURE_FUNCTIONS_BASE_URL}/contracts"
    params = {"pageSize": page_size}
    if continuation_token:
        params["continuationToken"] = continuation_token

    headers = {
        "x-functions-key": AZURE_FUNCTIONS_KEY
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_contract_by_id_alternative(contract_id: str) -> Dict:
    """Alternative way to get contract by ID"""
    url = f"{AZURE_FUNCTIONS_BASE_URL}/contracts"
    params = {"id": contract_id}

    headers = {
        "x-functions-key": AZURE_FUNCTIONS_KEY
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def analyze_contract_with_openai(question: str) -> str:
    """Ask a question about contracts using Azure OpenAI"""
    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/gpt-4/chat/completions?api-version=2023-12-01-preview"

    headers = {
        "api-key": AZURE_OPENAI_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ],
        "max_tokens": 800,
        "temperature": 0.3
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def search_contracts_in_azure_search(query: str, top: int = 5) -> Dict:
    """Search contract content using Azure Cognitive Search"""
    url = f"{AZURE_SEARCH_ENDPOINT}/indexes/contracts-v3-large/docs/search?api-version=2023-11-01"

    headers = {
        "api-key": AZURE_SEARCH_ADMIN_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "search": query,
        "queryType": "simple",
        "searchFields": "content",
        "select": "id,contract_filename,content",
        "top": top
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def parse_contract_data(contract_metadata: Dict) -> Dict:
    """Parse raw contract metadata into structured format"""
    url = os.getenv("PARSE_CONTRACT_PROMPT_FLOW_ENDPOINT")

    headers = {
        "Authorization": f"Bearer {os.getenv('PARSE_CONTRACT_PROMPT_FLOW_KEY')}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=contract_metadata)
    response.raise_for_status()
    return response.json()["result"]

# Example usage and test functions
def test_contract_retrieval():
    """Test contract retrieval endpoints"""
    print("🔍 Testing Contract Retrieval...")

    try:
        # Test listing contracts
        print("\n📋 Listing contracts (first page)...")
        contracts = list_contracts(page_size=5)
        print(f"Found {len(contracts.get('items', []))} contracts")

        if contracts.get('items'):
            first_contract_id = contracts['items'][0]['id']
            print(f"\n📄 Getting contract by ID: {first_contract_id}")

            # Test getting specific contract
            contract_data = get_contract_by_id(first_contract_id)
            print(f"Contract: {contract_data.get('CONTRATO', 'N/A')}")
            print(f"Company: {contract_data.get('NOME_DA_EMPRESA_PARCEIRO', 'N/A')}")

            # Test alternative endpoint
            contract_data_alt = get_contract_by_id_alternative(first_contract_id)
            print("✓ Alternative endpoint works")

    except Exception as e:
        print(f"❌ Error: {e}")

def test_ai_analysis():
    """Test AI-powered contract analysis"""
    print("\n🤖 Testing AI Contract Analysis...")

    try:
        # Test Azure OpenAI
        print("\n🧠 Testing Azure OpenAI...")
        question = "Analise um contrato de telecomunicações e extraia informações sobre valor, empresa parceira e prazo."
        answer = analyze_contract_with_openai(question)
        print(f"💡 OpenAI Answer: {answer[:200]}...")

        # Test Azure Search
        print("\n🔍 Testing Azure Cognitive Search...")
        search_results = search_contracts_in_azure_search("contrato valor", top=3)
        print(f"📄 Found {len(search_results.get('value', []))} search results")

    except Exception as e:
        print(f"❌ Error: {e}")

def curl_examples():
    """Print curl command examples"""
    print("\n📋 cURL Command Examples:")
    print("=" * 50)

    print("""
# 1. Get contract by ID
curl -H "x-functions-key: YOUR_FUNCTION_KEY" \\
  "https://your-functions-app.azurewebsites.net/api/contractid/ABC123"

# 2. List contracts with pagination
curl -H "x-functions-key: YOUR_FUNCTION_KEY" \\
  "https://your-functions-app.azurewebsites.net/api/contracts?pageSize=20"

# 3. Alternative contract lookup
curl -H "x-functions-key: YOUR_FUNCTION_KEY" \\
  "https://your-functions-app.azurewebsites.net/api/contracts?id=ABC123"

# 4. AI Contract Analysis (Question Answering)
curl -X POST \\
  -H "Authorization: Bearer YOUR_PROMPT_FLOW_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "pdf_filename": "contrato.pdf.txt",
    "question": "Qual é o valor do contrato?",
    "k": 5,
    "index": "contracts"
  }' \\
  "https://your-ml-workspace.services.azureml.net/endpoints/your-endpoint"

# 5. Parse Contract Data
curl -X POST \\
  -H "Authorization: Bearer YOUR_PARSE_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "Nome da empresa cedente (parte) do contrato sem cnpj": "Empresa XYZ",
    "Área nas torres para instalação dos equipamentos": "100 m2",
    "Localização da torre contratada": "São Paulo",
    "O prazo/vigência de duração do contrato (data de início e término)": "01/01/2023 a 01/01/2028",
    "Valor do contrato": "R$ 1.000.000,00"
  }' \\
  "https://your-parse-endpoint.services.azureml.net/endpoints/parse-endpoint"
""")

if __name__ == "__main__":
    print("🚀 Contract Analysis API Examples")
    print("=" * 40)

    # Show curl examples first
    curl_examples()

    # Test if environment is configured
    if not AZURE_FUNCTIONS_KEY:
        print("\n⚠️  Please set AZURE_FUNCTIONS_KEY environment variable")
    if not PROMPT_FLOW_ENDPOINT:
        print("⚠️  Please set PROMPT_FLOW_ENDPOINT environment variable")
    else:
        # Run tests
        test_contract_retrieval()
        test_ai_analysis()
