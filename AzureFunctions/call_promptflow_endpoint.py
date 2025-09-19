import os
import json
import ssl
import urllib.request
from tqdm import tqdm
import os

def get_contract_information(contract_pdf: str) -> dict:
    def allowSelfSignedHttps(allowed):
        # bypass the server certificate verification on client side
        if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
            ssl._create_default_https_context = ssl._create_unverified_context

    allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

    def _get_info_field(query: str) -> dict:
        data = {"pdf_filename": contract_pdf,
        "question": query,
        "k":5,
        "index": "contracts"}

        body = str.encode(json.dumps(data))

        url = os.getenv("EXTRACT_INFO_CONTRACT_PROMPT_FLOW_ENDPOINT")
        # Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
        api_key = os.getenv("EXTRACT_INFO_CONTRACT_PROMPT_FLOW_KEY")
        if not api_key:
            raise Exception("A key should be provided to invoke the endpoint")


        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

        req = urllib.request.Request(url, body, headers)

        try:
            response = urllib.request.urlopen(req)

            result = response.read()
            result_json = json.loads(result)
            return result_json["answer"]
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))

            # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
            print(error.info())
            print(error.read().decode("utf8", 'ignore'))

    fields = ["Nome da empresa cedente (parte) do contrato sem cnpj", "O objeto do contrato", "Obrigações do cliente do contrato", "Localização da torre contratada", "O prazo/vigência de duração do contrato (data de início e término)",
"Informações sobre o pagamento", "Valor do contrato", "Área nas torres para instalação dos equipamentos", "Penalidades por ocupação indevida nas torres", "Procedimentos para solicitação e liberação dos itens de infraestrutura"]

    output = {}
    for field in tqdm(fields):
        output[field] = _get_info_field(field)

    return output