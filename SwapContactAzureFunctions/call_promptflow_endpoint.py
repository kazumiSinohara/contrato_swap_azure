# Re-running the refactored function code after environment reset

import os
import json
import ssl
import urllib.request
from tqdm import tqdm
import logging

def get_contract_information(contract_pdf: str) -> dict:
    def allowSelfSignedHttps(allowed):
        if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
            ssl._create_default_https_context = ssl._create_unverified_context

    allowSelfSignedHttps(True)

    def _get_info_field() -> dict:
        data = {
            "pdf_filename": contract_pdf
        }

        body = str.encode(json.dumps(data))

        url = os.getenv("EXTRACT_INFO_CONTRACT_PROMPT_FLOW_ENDPOINT")
        api_key = os.getenv('EXTRACT_INFO_CONTRACT_PROMPT_FLOW_KEY')
        if not api_key:
            raise Exception("A key should be provided to invoke the endpoint")

        headers = {'Content-Type': 'application/json', 'Authorization': ('Bearer ' + api_key)}
        req = urllib.request.Request(url, body, headers)
        logging.info(f"Prompt flow endpoint URL: {url}")
        try:
            response = urllib.request.urlopen(req)
            result = response.read()
            result_json = json.loads(result)
            return result_json["answer"]
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))
            print(error.info())
            print(error.read().decode("utf8", 'ignore'))
            return "Erro na extração"

    output = {}
    #for section, questions in tqdm(questions_grouped.items(), desc=f"Processando do contrato: {contract_pdf}"):
    #    for question in tqdm(questions, desc=f"Processando do contrato: {contract_pdf} - {section}"):
    output["questions"] = _get_info_field()

    return output
