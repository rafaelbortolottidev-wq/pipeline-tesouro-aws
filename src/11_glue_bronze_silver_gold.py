"""
O QUE:
Transforma a última versão Bronze do Tesouro Direto no S3
em arquivos Parquet nas camadas Silver e Gold.

POR QUÊ:
Automatizar as transformações já validadas localmente,
preservando as regras de negócio e a qualidade dos dados.
"""

import json
import tempfile
from pathlib import Path

import boto3
import pandas as pd


BUCKET = "rafael-portfolio-tesouro-aws"

BRONZE_PREFIX = "bronze/tesouro_direto/"
SILVER_KEY = "silver/tesouro_direto/tesouro_direto.parquet"
GOLD_KEY = "gold/tesouro_direto/ultimas_taxas.parquet"

RENOMEAR = {
    "Tipo Titulo": "tipo_titulo",
    "Data Vencimento": "data_vencimento",
    "Data Base": "data_base",
    "Taxa Compra Manha": "taxa_compra_manha",
    "Taxa Venda Manha": "taxa_venda_manha",
    "PU Compra Manha": "pu_compra_manha",
    "PU Venda Manha": "pu_venda_manha",
    "PU Base Manha": "pu_base_manha",
}

NUMERICAS = [
    "taxa_compra_manha",
    "taxa_venda_manha",
    "pu_compra_manha",
    "pu_venda_manha",
    "pu_base_manha",
]

CHAVE = ["tipo_titulo", "data_vencimento", "data_base"]


def localizar_bronze(s3):
    """Localiza a versão Bronze mais recente pelos metadados."""
    versoes = []

    paginas = s3.get_paginator("list_objects_v2").paginate(
        Bucket=BUCKET,
        Prefix=BRONZE_PREFIX,
    )

    for pagina in paginas:
        for objeto in pagina.get("Contents", []):
            chave = objeto["Key"]

            if not chave.endswith("/metadata.json"):
                continue

            resposta = s3.get_object(
                Bucket=BUCKET,
                Key=chave,
            )

            metadata = json.loads(resposta["Body"].read())
            versoes.append((
                metadata["ingestao_utc"],
                chave,
                metadata,
            ))

    if not versoes:
        raise FileNotFoundError(
            "Nenhuma versão Bronze encontrada no S3"
        )

    _, chave_metadata, metadata = max(
        versoes,
        key=lambda item: item[0],
    )

    chave_csv = (
        chave_metadata.rsplit("/", 1)[0]
        + "/"
        + metadata["arquivo_original"]
    )

    return chave_csv


def validar(df, camada):
    """Valida esquema, campos obrigatórios e chave única."""
    if list(df.columns) != list(RENOMEAR.values()):
        raise ValueError(f"{camada}: esquema de colunas inválido")

    if df.empty or df[CHAVE].isna().any().any():
        raise ValueError(f"{camada}: dados vazios ou chave nula")

    if df["tipo_titulo"].str.strip().eq("").any():
        raise ValueError(f"{camada}: título vazio")

    if df.duplicated(subset=CHAVE).any():
        raise ValueError(f"{camada}: chave duplicada")

    print(f"[OK] {camada}: {len(df)} registros")


def main():
    s3 = boto3.client("s3")
    chave_csv = localizar_bronze(s3)

    print(f"Bronze: s3://{BUCKET}/{chave_csv}")

    with tempfile.TemporaryDirectory() as diretorio:
        pasta = Path(diretorio)

        csv = pasta / "bronze.csv"
        silver_path = pasta / "silver.parquet"
        gold_path = pasta / "gold.parquet"

        s3.download_file(BUCKET, chave_csv, str(csv))

        # Bronze -> Silver
        silver = pd.read_csv(
            csv,
            sep=";",
            encoding="utf-8-sig",
            dtype="string",
            keep_default_na=False,
        ).rename(columns=RENOMEAR)

        for coluna in ["data_vencimento", "data_base"]:
            silver[coluna] = pd.to_datetime(
                silver[coluna].str.strip(),
                format="%d/%m/%Y",
                errors="raise",
            )

        for coluna in NUMERICAS:
            valores = (
                silver[coluna]
                .str.strip()
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
                .replace("", pd.NA)
            )
            silver[coluna] = pd.to_numeric(valores, errors="raise")

        validar(silver, "Silver")

        # Silver -> Gold
        gold = (
            silver.sort_values("data_base")
            .drop_duplicates(
                subset=["tipo_titulo", "data_vencimento"],
                keep="last",
            )
            .sort_values(["tipo_titulo", "data_vencimento"])
            .reset_index(drop=True)
        )

        validar(gold, "Gold")

        if gold.duplicated(
            subset=["tipo_titulo", "data_vencimento"]
        ).any():
            raise ValueError("Gold: título e vencimento duplicados")

        # Publica somente depois de validar as duas camadas.
        silver.to_parquet(silver_path, engine="pyarrow", index=False)
        gold.to_parquet(gold_path, engine="pyarrow", index=False)

        s3.upload_file(str(silver_path), BUCKET, SILVER_KEY)
        s3.upload_file(str(gold_path), BUCKET, GOLD_KEY)

        print(f"Concluído: Silver={len(silver)}, Gold={len(gold)}")
        print(f"Última data-base: {gold['data_base'].max()}")


if __name__ == "__main__":
    main()
