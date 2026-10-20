
"""
O QUE:
Analisa a estrutura e o conteúdo do CSV histórico do Tesouro
Direto, identificando colunas, registros, títulos e datas.

POR QUÊ:
Conhecer a qualidade e as características dos dados antes
das transformações, apoiando a definição de regras de
validação e modelagem das camadas Silver e Gold.
"""

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

# Localiza o CSV original baixado do Tesouro Nacional.
caminho = Path("data/raw/precotaxatesourodireto.csv")

if not caminho.exists():
    raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

total_registros = 0
tipos_titulos = Counter()
datas_invalidas = 0
data_inicial = None
data_final = None

# Lê o CSV respeitando o separador utilizado pela fonte.
with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
    leitor = csv.DictReader(arquivo, delimiter=";")

    print("Colunas identificadas:", leitor.fieldnames)

    for linha in leitor:
        total_registros += 1
        tipos_titulos[linha["Tipo Titulo"]] += 1

        # Verifica a validade e o período histórico das datas.
        try:
            data = datetime.strptime(
                linha["Data Base"], "%d/%m/%Y"
            ).date()

            if data_inicial is None or data < data_inicial:
                data_inicial = data

            if data_final is None or data > data_final:
                data_final = data

        except (ValueError, TypeError):
            datas_invalidas += 1

print("\n--- RESULTADO DO PROFILING ---")
print("Total de registros:", total_registros)
print("Tipos de títulos:", len(tipos_titulos))
print("Data inicial:", data_inicial)
print("Data final:", data_final)
print("Datas inválidas:", datas_invalidas)

print("\nRegistros por tipo de título:")

for titulo, quantidade in tipos_titulos.most_common():
    print(f"{titulo}: {quantidade}")
