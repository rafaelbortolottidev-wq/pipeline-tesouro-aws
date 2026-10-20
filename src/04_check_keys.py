
"""
O QUE:
Verifica se a combinação de título, vencimento e data-base
identifica unicamente os registros do Tesouro Direto.

POR QUÊ:
Detectar duplicidades e chaves incompletas antes da
transformação, garantindo integridade e confiabilidade
dos dados nas camadas Silver e Gold.
"""

import csv
from pathlib import Path

caminho = Path("data/raw/precotaxatesourodireto.csv")

campos_chave = (
    "Tipo Titulo",
    "Data Vencimento",
    "Data Base"
)

chaves_encontradas = set()
duplicados = 0
chaves_incompletas = 0
exemplos = []

# Verifica a unicidade da chave candidata.
with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
    leitor = csv.DictReader(arquivo, delimiter=";")

    for linha in leitor:
        chave = tuple(
            (linha.get(campo) or "").strip()
            for campo in campos_chave
        )

        if any(not valor for valor in chave):
            chaves_incompletas += 1
            continue

        if chave in chaves_encontradas:
            duplicados += 1

            if len(exemplos) < 5:
                exemplos.append(chave)
        else:
            chaves_encontradas.add(chave)

print("\n--- VALIDAÇÃO DA CHAVE ---")
print("Chaves únicas:", len(chaves_encontradas))
print("Registros duplicados:", duplicados)
print("Chaves incompletas:", chaves_incompletas)

if exemplos:
    print("\nExemplos de duplicidades:")
    for exemplo in exemplos:
        print(exemplo)
