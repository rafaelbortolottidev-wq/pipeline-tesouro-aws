
"""
O QUE:
Constrói a camada Gold a partir da Silver, selecionando
a última observação disponível de cada título e vencimento.

POR QUÊ:
Disponibilizar uma visão analítica consolidada dos preços
e taxas mais recentes, facilitando consultas no Athena
sem percorrer todo o histórico.
"""

from pathlib import Path

import pandas as pd

# Define os caminhos das camadas.
origem = Path("data/silver/tesouro_direto/tesouro_direto.parquet")
destino = Path("data/gold/tesouro_direto/ultimas_taxas.parquet")

if not origem.is_file():
    raise FileNotFoundError(f"Silver não encontrada: {origem}")

# Carrega os dados tratados da Silver.
df = pd.read_parquet(origem)

# Seleciona a observação mais recente por título e vencimento.
gold = (
    df.sort_values("data_base")
    .drop_duplicates(
        subset=["tipo_titulo", "data_vencimento"],
        keep="last"
    )
    .sort_values(["tipo_titulo", "data_vencimento"])
    .reset_index(drop=True)
)

# Publica o resultado local em formato Parquet.
destino.parent.mkdir(parents=True, exist_ok=True)
gold.to_parquet(destino, engine="pyarrow", index=False)

print("\n--- GOLD GERADA ---")
print("Registros na Silver:", len(df))
print("Registros na Gold:", len(gold))
print("Arquivo:", destino)
print("Última data-base:", gold["data_base"].max())
print("\nRegistros por tipo de título:")
print(gold["tipo_titulo"].value_counts())
