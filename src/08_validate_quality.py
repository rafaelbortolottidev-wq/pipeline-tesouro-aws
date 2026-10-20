
"""
O QUE:
Valida a estrutura, a integridade e a consistência dos
dados das camadas SILVER e GOLD do Tesouro Direto.

POR QUÊ:
Detectar problemas de qualidade antes da publicação
analítica, evitando disponibilizar dados inconsistentes.
"""

from pathlib import Path

import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
)

SILVER = Path("data/silver/tesouro_direto/tesouro_direto.parquet")
GOLD = Path("data/gold/tesouro_direto/ultimas_taxas.parquet")

CHAVE = ["tipo_titulo", "data_vencimento", "data_base"]
COLUNAS_DATAS = ["data_vencimento", "data_base"]
COLUNAS_NUMERICAS = [
    "taxa_compra_manha",
    "taxa_venda_manha",
    "pu_compra_manha",
    "pu_venda_manha",
    "pu_base_manha",
]

COLUNAS_ESPERADAS = CHAVE + COLUNAS_NUMERICAS


def validar_camadas(df, nome):
    """Verifica esquema, campos obrigatórios e unicidade."""

    # Confirma a estrutura esperada.
    if set(df.columns) != set(COLUNAS_ESPERADAS):
        raise ValueError(f"{nome}: esquema de colunas inválido")

    if not pd.api.types.is_string_dtype(df["tipo_titulo"]):
        raise ValueError(f"{nome}: tipo_titulo não é texto")

    for coluna in COLUNAS_DATAS:
        if not is_datetime64_any_dtype(df[coluna]):
            raise ValueError(f"{nome}: {coluna} não é data")

    for coluna in COLUNAS_NUMERICAS:
        if not is_numeric_dtype(df[coluna]):
            raise ValueError(f"{nome}: {coluna} não é numérico")

    # A chave de negócio precisa estar completa.
    if df[CHAVE].isna().any().any():
        raise ValueError(f"{nome}: chave com valores nulos")

    if df["tipo_titulo"].str.strip().eq("").any():
        raise ValueError(f"{nome}: título vazio")

    # Cada combinação da chave deve ser única.
    if df.duplicated(subset=CHAVE).any():
        raise ValueError(f"{nome}: chaves duplicadas")

    print(f"[OK] {nome}: esquema e integridade")


def validar_gold(silver, gold):
    """Compara a Gold com as últimas observações da Silver."""

    if silver.empty or gold.empty:
        raise ValueError("Silver ou Gold está vazia")

    esperado = (
        silver.sort_values("data_base")
        .drop_duplicates(
            subset=["tipo_titulo", "data_vencimento"],
            keep="last"
        )
        .sort_values(["tipo_titulo", "data_vencimento"])
        .reset_index(drop=True)
    )

    atual = (
        gold.sort_values(["tipo_titulo", "data_vencimento"])
        .reset_index(drop=True)
    )

    try:
        pd.testing.assert_frame_equal(
            atual[COLUNAS_ESPERADAS],
            esperado[COLUNAS_ESPERADAS]
        )
    except AssertionError as erro:
        raise ValueError(
            "Gold não corresponde às últimas observações da Silver"
        ) from erro

    print("[OK] Gold consistente com a Silver")


def main():
    for caminho in [SILVER, GOLD]:
        if not caminho.is_file():
            raise FileNotFoundError(f"Arquivo ausente: {caminho}")

    silver = pd.read_parquet(SILVER)
    gold = pd.read_parquet(GOLD)

    print("\n--- DATA QUALITY ---")

    validar_camadas(silver, "Silver")
    validar_camadas(gold, "Gold")
    validar_gold(silver, gold)

    print("\nRESULTADO: APROVADO")
    print(f"Silver: {len(silver)} registros")
    print(f"Gold: {len(gold)} registros")


if __name__ == "__main__":
    main()
