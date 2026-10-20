
"""
O QUE:
Consulta a API CKAN do Tesouro Nacional para descobrir
a URL do arquivo CSV de preços e taxas dos títulos públicos.

POR QUÊ:
Evitar URLs fixas no código, permitindo localizar o arquivo
automaticamente mesmo que seu endereço seja alterado.
Isso melhora a manutenção e a confiabilidade da ingestão.
"""

import truststore
truststore.inject_into_ssl()
import json
from urllib.request import Request, urlopen

API_URL = (
    "https://www.tesourotransparente.gov.br/ckan/api/3/action/"
    "package_show?id=taxas-dos-titulos-ofertados-pelo-tesouro-direto"
)

request = Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})

with urlopen(request, timeout=30) as response:
    dados = json.load(response)

if not dados["success"]:
    raise RuntimeError("Falha na consulta à API CKAN")

recursos = dados["result"]["resources"]

for recurso in recursos:
    if recurso["format"].upper() == "CSV":
        print("Arquivo:", recurso["name"])
        print("URL:", recurso["url"])
        print("Tamanho (bytes):", recurso["size"])
        print("Última atualização:", recurso["last_modified"])
