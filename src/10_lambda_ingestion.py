"""
O QUE:
Baixa o CSV do Tesouro Direto, publica novas versões na Bronze do S3
 e solicita processamento no AWS Glue.

POR QUÊ:
Automatizar a ingestão e evitar gravações e transformações repetidas
por meio do SHA-256, com recuperação se o acionamento do Glue falhar.
"""

import hashlib
import json
import os
import tempfile
import time
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import boto3
from botocore.exceptions import ClientError


API_URL = (
    "https://www.tesourotransparente.gov.br/ckan/api/3/action/"
    "package_show?id=taxas-dos-titulos-ofertados-pelo-tesouro-direto"
)
HEADERS = {"User-Agent": "Mozilla/5.0"}
ARQUIVO = "precotaxatesourodireto.csv"
JOB_GLUE = "tesouro-bronze-silver-gold"


def objeto_existe(s3, bucket, chave):
    """Verifica a existência de um objeto no S3."""
    try:
        s3.head_object(Bucket=bucket, Key=chave)
        return True
    except ClientError as erro:
        codigo = erro.response["Error"]["Code"]
        if codigo in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


def gravar_status(s3, bucket, chave, status, job_run_id=None):
    """Registra o estado do acionamento do Glue, separado dos metadados."""
    registro = {
        "status": status,
        "atualizado_utc": datetime.now(timezone.utc).isoformat(),
    }
    if job_run_id:
        registro["glue_job_run_id"] = job_run_id

    s3.put_object(
        Bucket=bucket,
        Key=chave,
        Body=json.dumps(registro, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
    )


def iniciar_glue(s3, bucket, chave_status):
    """Solicita a execução do Glue e registra que ela foi iniciada."""
    execucao = boto3.client("glue").start_job_run(JobName=JOB_GLUE)
    job_run_id = execucao["JobRunId"]
    gravar_status(s3, bucket, chave_status, "iniciado", job_run_id)
    print(f"Glue iniciado: {job_run_id}")
    return job_run_id


def lambda_handler(event, context):
    bucket = os.environ["TESOURO_BUCKET"]
    s3 = boto3.client("s3")

    # Descobre a URL do CSV no catálogo oficial CKAN.
    with urlopen(Request(API_URL, headers=HEADERS), timeout=30) as resposta:
        dados = json.load(resposta)

    if not dados.get("success"):
        raise RuntimeError("Falha na consulta à API CKAN")

    recurso = next(
        (
            item
            for item in dados["result"]["resources"]
            if (item.get("format") or "").upper() == "CSV"
        ),
        None,
    )
    if not recurso or not recurso.get("url"):
        raise RuntimeError("Recurso CSV não encontrado")

    sha256 = hashlib.sha256()
    tamanho = 0

    with tempfile.TemporaryFile() as arquivo:
        # Uma tentativa adicional para limitação HTTP 429.
        for tentativa in range(2):
            try:
                resposta = urlopen(
                    Request(recurso["url"], headers=HEADERS),
                    timeout=120,
                )
                break
            except HTTPError as erro:
                if erro.code != 429 or tentativa == 1:
                    raise
                retry_after = erro.headers.get("Retry-After")
                espera = (
                    int(retry_after)
                    if retry_after and retry_after.isdigit()
                    else 30
                )
                if espera > 60:
                    raise RuntimeError(
                        f"Servidor solicitou aguardar {espera} segundos."
                    ) from erro
                print(f"HTTP 429. Aguardando {espera} segundos.")
                time.sleep(espera)

        with resposta:
            while True:
                bloco = resposta.read(1024 * 1024)
                if not bloco:
                    break
                arquivo.write(bloco)
                sha256.update(bloco)
                tamanho += len(bloco)

        if tamanho == 0:
            raise RuntimeError("CSV recebido está vazio")

        hash_atual = sha256.hexdigest()
        prefixo = f"bronze/tesouro_direto/{hash_atual}/"
        chave_csv = prefixo + ARQUIVO
        chave_metadata = prefixo + "metadata.json"
        chave_status = prefixo + "glue-status.json"

        csv_existe = objeto_existe(s3, bucket, chave_csv)
        metadata_existe = objeto_existe(s3, bucket, chave_metadata)

        if csv_existe and metadata_existe:
            # Versões antigas sem marcador já foram processadas manualmente.
            if objeto_existe(s3, bucket, chave_status):
                resposta_status = s3.get_object(Bucket=bucket, Key=chave_status)
                status = json.loads(resposta_status["Body"].read())
                if status.get("status") == "pendente":
                    job_run_id = iniciar_glue(s3, bucket, chave_status)
                    return {
                        "status": "glue_retomado",
                        "sha256": hash_atual,
                        "glue_job_run_id": job_run_id,
                    }

            print("Arquivo já ingerido. Nenhuma gravação necessária.")
            return {"status": "sem_alteracoes", "sha256": hash_atual}

        if csv_existe or metadata_existe:
            raise RuntimeError("Versão Bronze incompleta no S3")

        # Publica o CSV original em prefixo versionado pelo hash.
        arquivo.seek(0)
        s3.upload_fileobj(
            arquivo,
            bucket,
            chave_csv,
            ExtraArgs={"ContentType": "text/csv"},
        )

    metadados = {
        "dataset": "tesouro_direto",
        "fonte": "Tesouro Transparente - CKAN",
        "arquivo_original": ARQUIVO,
        "tamanho_bytes": tamanho,
        "sha256": hash_atual,
        "ingestao_utc": datetime.now(timezone.utc).isoformat(),
    }

    s3.put_object(
        Bucket=bucket,
        Key=chave_metadata,
        Body=json.dumps(metadados, indent=4, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
    )
    print(f"Nova versão Bronze: s3://{bucket}/{prefixo}")

    # Se start_job_run falhar, o marcador pendente permite retomar depois.
    gravar_status(s3, bucket, chave_status, "pendente")
    job_run_id = iniciar_glue(s3, bucket, chave_status)

    return {
        "status": "nova_versao",
        "sha256": hash_atual,
        "chave_s3": chave_csv,
        "glue_job_run_id": job_run_id,
    }
