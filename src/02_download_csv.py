"""
O QUE:
Consulta a API CKAN, identifica o recurso CSV e realiza
o download dos dados históricos do Tesouro Direto.

POR QUÊ:
Obter os dados diretamente da fonte oficial e preservar
o arquivo original, sem transformações, para garantir
rastreabilidade, auditoria e possibilidade de reprocessamento.
"""

import json
import shutil
from pathlib import Path
from urllib.request import Request, urlopen

import truststore

# Utiliza os certificados confiáveis do Windows para conexões HTTPS.
truststore.inject_into_ssl()

API_URL = (
    "https://www.tesourotransparente.gov.br/ckan/api/3/action/"
    "package_show?id=taxas-dos-titulos-ofertados-pelo-tesouro-direto"
)

headers = {"User-Agent": "Mozilla/5.0"}

# Consulta o catálogo CKAN para localizar o recurso CSV.
with urlopen(Request(API_URL, headers=headers), timeout=30) as response:
    dados = json.load(response)

if not dados.get("success"):
    raise RuntimeError("Falha na consulta à API CKAN")

# Descobre a URL do CSV sem depender de um endereço fixo.
recurso = next(
    (
        r for r in dados["result"]["resources"]
        if (r.get("format") or "").upper() == "CSV"
    ),
    None
)

if recurso is None:
    raise RuntimeError("Nenhum recurso CSV encontrado")

# Preserva o arquivo original para análise e reprocessamento.
destino = Path("data/raw/precotaxatesourodireto.csv")
destino.parent.mkdir(parents=True, exist_ok=True)

# Realiza o download sem carregar todo o CSV na memória.
with urlopen(Request(recurso["url"], headers=headers), timeout=120) as origem:
    with destino.open("wb") as arquivo:
        shutil.copyfileobj(origem, arquivo)

print(f"Arquivo salvo: {destino}")
print(f"Tamanho: {destino.stat().st_size:,} bytes")


