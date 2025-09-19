import os
import json
import ssl
import urllib.request
from tqdm import tqdm

def parse_contract_information(contract_metadata: dict) -> dict:
    def allowSelfSignedHttps(allowed):
        # bypass the server certificate verification on client side
        if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
            ssl._create_default_https_context = ssl._create_unverified_context

    allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

    def _parse_data() -> dict:
        data = {
            "nome_cedente": contract_metadata["CEDENTE (Empresa que cede a fibra)"],
            "area_estimada": contract_metadata["ÁREA ESTIMADA (m2)"] if "ÁREA ESTIMADA (m2)" in contract_metadata else contract_metadata["Área Estimada (m2)"],
            "localizacao_torre": contract_metadata["LOCALIZAÇÃO"],
            "prazo_vigencia": contract_metadata["PERÍODO Contratual (ANOS) / PRAZO CONTRATO (Duração contratual)"],
            "valor_contrato": contract_metadata["VALOR ORIGINAL (CONTRATO) (Valor total contratado)"]
        }

        body = str.encode(json.dumps(data))

        url = os.getenv("PARSE_CONTRACT_PROMPT_FLOW_ENDPOINT")
        # Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
        api_key = os.getenv('PARSE_CONTRACT_PROMPT_FLOW_KEY')
        if not api_key:
            raise Exception("A key should be provided to invoke the endpoint")


        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

        req = urllib.request.Request(url, body, headers)

        try:
            response = urllib.request.urlopen(req)

            result = response.read()
            result_json = json.loads(result)
            return result_json["result"]
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))

            # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
            print(error.info())
            print(error.read().decode("utf8", 'ignore'))

    output = {}
    output = _parse_data()

    return output