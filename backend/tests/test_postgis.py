"""Roda os exercicios SQL do marco 2 dentro do container e confere que
passam -- fecha o loop de teste automatizado ate no que nao e Python.
"""

import subprocess
from pathlib import Path

RAIZ_DO_REPO = Path(__file__).resolve().parent.parent.parent


def test_marco2_exercicios_sql_passam():
    caminho_sql = RAIZ_DO_REPO / "backend" / "02_postgis" / "03_exercicios.sql"
    with open(caminho_sql, "rb") as arquivo_sql:
        resultado = subprocess.run(
            ["docker", "compose", "exec", "-T", "postgis", "psql", "-U", "mapstack", "-d", "mapstack"],
            stdin=arquivo_sql,
            cwd=RAIZ_DO_REPO,
            capture_output=True,
            text=True,
        )

    saida = resultado.stdout + resultado.stderr
    assert resultado.returncode == 0, saida
    assert "todos os exercicios passaram" in saida, saida
