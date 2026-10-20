
"""
O QUE:
Executa as transformações Silver e Gold e realiza
a validação de qualidade em sequência.

POR QUÊ:
Interromper o pipeline quando ocorrerem erros,
impedindo que dados inválidos sejam liberados
para publicação na AWS.
"""

import subprocess
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parents[1]

etapas = [
    "06_build_silver.py",
    "07_build_gold.py",
    "08_validate_quality.py",
]

for etapa in etapas:
    print(f"\nExecutando: {etapa}", flush=True)

    subprocess.run(
        [sys.executable, str(raiz / "src" / etapa)],
        cwd=raiz,
        check=True
    )

print("\nPIPELINE APROVADO PARA PUBLICAÇÃO")
