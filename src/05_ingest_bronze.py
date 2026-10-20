
"""
O QUE:
Realiza a ingestão local do CSV na camada Bronze,
armazenando o arquivo original e seus metadados.

POR QUÊ:
Garantir rastreabilidade, versionamento e idempotência.
O hash SHA-256 permite identificar arquivos já ingeridos
e evitar processamento desnecessário.
"""

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
import argparse


def calcular_sha256(caminho):
    """Calcula o hash do arquivo sem carregá-lo inteiro na memória."""
    hash_arquivo = hashlib.sha256()

    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            hash_arquivo.update(bloco)

    return hash_arquivo.hexdigest()

# Permite escolher arquivos e destinos diferentes para testes.
parser = argparse.ArgumentParser()
parser.add_argument(
    "--origem",
    default="data/raw/precotaxatesourodireto.csv"
)
parser.add_argument(
    "--bronze",
    default="data/bronze/tesouro_direto"
)

args = parser.parse_args()

origem = Path(args.origem)
bronze = Path(args.bronze)

if not origem.is_file():
    raise FileNotFoundError(f"Arquivo não encontrado: {origem}")

# Identifica a versão pelo conteúdo do arquivo.
hash_atual = calcular_sha256(origem)
pasta_versao = bronze / hash_atual

destino = pasta_versao / origem.name
caminho_metadados = pasta_versao / "metadata.json"

if pasta_versao.exists():
    # Não aceita versões incompletas ou arquivos corrompidos.
    if not destino.is_file() or not caminho_metadados.is_file():
        raise RuntimeError("Versão Bronze incompleta")

    if calcular_sha256(destino) != hash_atual:
        raise RuntimeError("Integridade da Bronze comprometida")

    print("Arquivo já ingerido. Nenhum processamento necessário.")

else:
    pasta_versao.mkdir(parents=True)

    # Preserva o CSV sem modificar seu conteúdo.
    shutil.copy2(origem, destino)

    if calcular_sha256(destino) != hash_atual:
        raise RuntimeError("Falha na verificação do arquivo copiado")

    metadados = {
        "dataset": "tesouro_direto",
        "fonte": "Tesouro Transparente - CKAN",
        "arquivo_original": origem.name,
        "tamanho_bytes": destino.stat().st_size,
        "sha256": hash_atual,
        "ingestao_utc": datetime.now(timezone.utc).isoformat(),
    }

    caminho_metadados.write_text(
        json.dumps(metadados, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("Nova versão armazenada na Bronze.")
    print("SHA-256:", hash_atual)
    print("Destino:", destino)
