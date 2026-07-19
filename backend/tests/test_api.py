"""Testes de integracao da API (marco 3/5/6) via FastAPI TestClient.

Precisam do Postgres do marco 2 rodando com os dados de teste inseridos
(`docker compose up -d postgis` + `01_setup.sql` ja aplicado -- ver README).
`TestClient(main.app)` como context manager dispara o `lifespan` de
verdade (os adapters de ingestao sobem/descem junto), exatamente como no
servidor real -- so que sem precisar do uvicorn escutando uma porta.
"""

from fastapi.testclient import TestClient

import main


def test_geocercas_retorna_feature_collection():
    with TestClient(main.app) as client:
        resposta = client.get("/geocercas")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["type"] == "FeatureCollection"
    assert any(f["properties"]["nome"] == "centro-expandido-sp" for f in corpo["features"])


def test_telemetria_filtra_por_veiculo():
    with TestClient(main.app) as client:
        resposta = client.get("/telemetria", params={"veiculo_id": "drone-2"})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo["features"]) >= 1
    assert all(f["properties"]["veiculo_id"] == "drone-2" for f in corpo["features"])


def test_telemetria_proximos_via_http():
    with TestClient(main.app) as client:
        resposta = client.get(
            "/telemetria/proximos", params={"lon": -46.6333, "lat": -23.5505, "raio_metros": 500}
        )
    assert resposta.status_code == 200
    corpo = resposta.json()
    veiculos = {f["properties"]["veiculo_id"] for f in corpo["features"]}
    assert "drone-1" in veiculos
