import json

# Grupos temáticos organizados como listas de perguntas em português
questions_grouped = {
  "Identificação do Contrato": [
    "Qual é o identificador único interno atribuído ao acordo de cessão ou swap?",
    "Qual é o número oficial ou referência formal do contrato registrado?",
    "Qual é a modalidade contratual que rege este acordo (ex: cessão recíproca, aluguel, cooperação técnica)?",
    "Qual é o nome ou designação do contrato principal ao qual este acordo está vinculado?",
    "Existe um documento de aceite formal emitido entre as partes para validar a entrega?",
    "Há observações contratuais que impactam execução, vigência ou interpretação do acordo?"
  ],
  "Partes Envolvidas": [
    "Qual é a razão social da empresa contratada como parceira neste acordo?",
    "Qual é o número do CNPJ da parte contratada mencionado no contrato?",
    "Qual unidade organizacional ou diretoria da sua empresa assinou o contrato em nome da companhia?",
    "Qual das partes está na posição de ceder o direito de uso da infraestrutura?",
    "Qual entidade detém a posse ou titularidade formal da infraestrutura cedida?",
    "Qual é o grupo empresarial ou conglomerado econômico atualmente responsável pela gestão da empresa parceira?",
    "A qual grupo econômico pertencia a empresa contratada na época da celebração do contrato?"
  ],
  "Geografia e Rota": [
    "Qual é o município de origem da infraestrutura descrita no contrato?",
    "Qual é o município de destino da rota firmada entre as partes?",
    "Qual é a unidade federativa correspondente ao ponto inicial da infraestrutura?",
    "Qual é a unidade federativa do ponto final da rota descrita?",
    "Qual é a UF regional administrativa que abrange a infraestrutura contratada?",
    "Qual é a identificação técnica (ou apelido operacional) atribuída ao ponto A?",
    "Qual é a identificação técnica (ou apelido operacional) atribuída ao ponto B?",
    "Qual é o nome técnico, código ou designação da rota estabelecida entre as partes?",
    "Qual é a distância física, em quilômetros, do trajeto contratado?",
    "Qual é o total de quilômetros-fibra lineares especificados no acordo?",
    "Qual é a atenuação média medida por enlace no trecho contratado?"
  ],
  "Capacidade Técnica e Infraestrutura": [
    "Quantas fibras ópticas estão envolvidas no escopo do contrato?",
    "Existe previsão contratual de paridade ou proteção na rota estabelecida?",
    "Quantos comprimentos de onda (lambdas) estão habilitados para uso técnico?",
    "Qual é a capacidade nominal, em Gbps, por canal de transmissão?",
    "Qual é a capacidade de banda atualmente ativada sob este contrato?",
    "Qual é a capacidade máxima prevista ou projetada conforme o contrato?",
    "Quantos circuitos lógicos estão formalmente estabelecidos na infraestrutura contratada?",
    "Qual é o tipo de equipamento instalado no ponto terminal B da rota?",
    "Há circuitos EILD contratados como parte integrante da infraestrutura?"
  ],
  "Financeiro": [
    "Qual é o valor bruto original estipulado no contrato?",
    "Qual é o valor unitário acordado por quilômetro de fibra óptica?",
    "Qual é o investimento evitado (CAPEX) estimado em função da celebração do contrato?",
    "Qual é o custo operacional evitado (OPEX) em razão da vigência do acordo?"
  ],
  "Datas e Vigência": [
    "Em que data foi formalmente assinado o contrato entre as partes?",
    "Qual é o ano civil de assinatura do contrato?",
    "Qual é o ano de referência atual usado para fins de análise contratual?",
    "Qual é o último ano validado de conformidade contratual?",
    "Qual é o tempo total de vigência inicial do contrato, em anos?",
    "Qual é o prazo contratual total, incluindo períodos de renovação?",
    "Em que data ocorre o vencimento da primeira vigência do contrato?",
    "Por quantos anos o contrato se renova automaticamente, caso não haja denúncia?",
    "Considerando renovações automáticas, até que ano o contrato permanecerá em vigor?",
    "Com que antecedência mínima uma das partes deve se manifestar para evitar a renovação automática?",
    "Qual é o prazo contratual para rescisão motivada por inadimplemento?",
    "Qual é o prazo para denúncia unilateral sem necessidade de justificativa?",
    "Qual é a multa percentual sobre os valores vincendos em caso de rescisão antecipada?"
  ],
  "SLA e Status": [
    "Qual é o tempo máximo de restabelecimento (SLA MTTR) acordado em horas?",
    "Qual é o status atual de execução ou vigência deste contrato?",
    "Qual é o nome ou unidade da sua organização responsável pelo acompanhamento do contrato?"
  ]
}


# Export to a file for Prompt Flow
import tempfile
from pathlib import Path
file_path = Path(tempfile.gettempdir()) / "questions_grouped.json"
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(questions_grouped, f, ensure_ascii=False, indent=2)

file_path.name
