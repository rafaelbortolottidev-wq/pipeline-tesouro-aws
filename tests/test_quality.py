
"""
O QUE:
Testa automaticamente se o validador de qualidade
identifica registros com chaves duplicadas.

POR QUÊ:
Garantir que dados inconsistentes sejam rejeitados
antes de sua publicação nas camadas analíticas.
"""

import runpy
import unittest
from pathlib import Path

import pandas as pd

# Carrega a função de validação existente.
raiz = Path(__file__).resolve().parents[1]
modulo = runpy.run_path(
    str(raiz / "src/08_validate_quality.py"),
    run_name="quality_test"
)

validar_camadas = modulo["validar_camadas"]


class TestDataQuality(unittest.TestCase):

    def test_rejeitar_duplicidade(self):
        # Cria um registro fictício com o esquema da Silver.
        dados = {
            "tipo_titulo": pd.Series(["Tesouro Selic"], dtype="string"),
            "data_vencimento": pd.to_datetime(["2029-03-01"]),
            "data_base": pd.to_datetime(["2026-10-09"]),
        }

        for coluna in [
            "taxa_compra_manha",
            "taxa_venda_manha",
            "pu_compra_manha",
            "pu_venda_manha",
            "pu_base_manha",
        ]:
            dados[coluna] = pd.Series([1.0], dtype="Float64")

        registro = pd.DataFrame(dados)

        # Duplica propositalmente a mesma chave.
        duplicados = pd.concat(
            [registro, registro],
            ignore_index=True
        )

        # O teste passa somente se a validação rejeitar os dados.
        with self.assertRaisesRegex(ValueError, "chaves duplicadas"):
            validar_camadas(duplicados, "Silver teste")


if __name__ == "__main__":
    unittest.main()
