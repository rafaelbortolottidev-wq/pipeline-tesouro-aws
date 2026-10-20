
"""
O QUE:
Transforma os dados da camada Bronze em um arquivo Parquet
na camada Silver, padronizando colunas e tipos de dados.

POR QUÊ:
Preparar os dados para consultas analíticas, melhorar
a eficiência do armazenamento e garantir consistência
dos formatos utilizados no pipeline.
"""

import json
from pathlib import Path

import pandas as pd


# Identifica a versão Bronze mais recente pelos metadados.
bronze = Path("data/bronze/tesouro_direto")
arquivos_metadata = list(bronze.glob("*/metadata.json"))

if not arquivos_metadata:
    raise FileNotFoundError("Nenhuma versão Bronze encontrada")

metadata_path = max(
    arquivos_metadata,
    key=lambda p: json.loads(
        p.read_text(encoding="utf-8")
    )["ingestao_utc"]
)

metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
origem = metadata_path.parent / metadata["arquivo_original"]

# Lê o CSV preservando os valores originais como texto.
df = pd.read_csv(
    origem,
    sep=";",
    encoding="utf-8-sig",
    dtype="string",
    keep_default_na=False
)

# Padroniza os nomes das colunas.
colunas = {
    "Tipo Titulo": "tipo_titulo",
    "Data Vencimento": "data_vencimento",
    "Data Base": "data_base",
    "Taxa Compra Manha": "taxa_compra_manha",
    "Taxa Venda Manha": "taxa_venda_manha",
    "PU Compra Manha": "pu_compra_manha",
    "PU Venda Manha": "pu_venda_manha",
    "PU Base Manha": "pu_base_manha"
}

df = df.rename(columns=colunas)

# Converte datas brasileiras para o tipo datetime.
for coluna in ["data_vencimento", "data_base"]:
    df[coluna] = pd.to_datetime(
        df[coluna].str.strip(),
        format="%d/%m/%Y",
        errors="raise"
    )

# Converte números brasileiros para valores numéricos.
colunas_numericas = [
    "taxa_compra_manha",
    "taxa_venda_manha",
    "pu_compra_manha",
    "pu_venda_manha",
    "pu_base_manha"
]

for coluna in colunas_numericas:
    valores = df[coluna].str.strip()

    valores = (
        valores
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .replace("", pd.NA)
    )

    df[coluna] = pd.to_numeric(valores, errors="raise")

# Grava o resultado em Parquet na camada Silver local.
destino = Path("data/silver/tesouro_direto/tesouro_direto.parquet")
destino.parent.mkdir(parents=True, exist_ok=True)

df.to_parquet(destino, engine="pyarrow", index=False)

print("\n--- SILVER GERADA ---")
print("Arquivo:", destino)
print("Registros:", len(df))
print("Colunas:", len(df.columns))
print("\nTipos de dados:")
print(df.dtypes)
