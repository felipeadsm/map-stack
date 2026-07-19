"""Testa o exercicio do marco 5 (api/exercicios_movimento.py)."""

import exercicios_movimento as movimento  # api/ ja esta no sys.path via conftest.py


def test_proxima_posicao_norte():
    # Andar 1000m para o norte (azimute 0) nao muda a longitude
    # (meridianos sao linhas de longitude constante) -- valor conferido
    # com pyproj.Geod diretamente antes de escrever o exercicio.
    lon2, lat2 = movimento.proxima_posicao(-46.6333, -23.5505, 0, 1000)
    assert abs(lon2 - (-46.6333)) < 1e-6
    assert abs(lat2 - (-23.54147079402815)) < 1e-6


def test_proxima_posicao_ida_e_volta():
    lon2, lat2 = movimento.proxima_posicao(-46.6333, -23.5505, 0, 1000)
    lon3, lat3 = movimento.proxima_posicao(lon2, lat2, 180, 1000)
    assert abs(lon3 - (-46.6333)) < 1e-6
    assert abs(lat3 - (-23.5505)) < 1e-6
