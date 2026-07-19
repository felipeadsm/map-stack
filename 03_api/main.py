"""Marco 3: API real servindo os dados espaciais do marco 2 como GeoJSON.

FastAPI e um framework Python para construir APIs; roda sobre ASGI
(Asynchronous Server Gateway Interface -- o padrao que permite ao Python
lidar com muitas requisicoes concorrentes sem bloquear). Uvicorn e o
servidor que efetivamente escuta a porta e chama a aplicacao FastAPI a
cada requisicao.

Rode com: poetry run python 03_api/main.py
Depois abra http://127.0.0.1:8000/docs -- o FastAPI gera essa pagina
interativa (Swagger UI) sozinho, a partir da assinatura das funcoes abaixo.
"""

from typing import Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from database import SessionLocal
from exercicios import telemetria_proximos
from geojson import geometria_para_geojson
from models import Geocerca, Telemetria

app = FastAPI(title="map-stack API", description="Marco 3: FastAPI + GeoAlchemy2")

# CORS (Cross-Origin Resource Sharing): por padrao, o navegador bloqueia
# uma pagina servida em http://localhost:5173 (o front, marco 4) de fazer
# fetch() para http://localhost:8000 (esta API) -- porta diferente conta
# como "origem" diferente. Este middleware manda o cabecalho HTTP que
# autoriza explicitamente essa origem a consumir a API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def feature_collection(linhas: list, propriedades: Callable) -> dict:
    """Monta um GeoJSON FeatureCollection a partir de linhas do ORM.

    GeoJSON e so um JSON com uma forma padronizada: um FeatureCollection
    e uma lista de Features, e cada Feature tem uma "geometry" (a forma) e
    "properties" (os metadados que quiser anexar, ex: id do veiculo).
    Bibliotecas de mapa no front (Leaflet, Mapbox) sabem ler esse formato
    direto, sem voce precisar ensina-las nada sobre o seu banco.
    """
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": geometria_para_geojson(linha.geom),
                "properties": propriedades(linha),
            }
            for linha in linhas
        ],
    }


@app.get("/geocercas")
def listar_geocercas():
    with SessionLocal() as session:
        geocercas = session.scalars(select(Geocerca)).all()
        return feature_collection(geocercas, lambda g: {"id": g.id, "nome": g.nome})


@app.get("/telemetria")
def listar_telemetria(veiculo_id: str | None = None):
    with SessionLocal() as session:
        stmt = select(Telemetria)
        if veiculo_id:
            stmt = stmt.where(Telemetria.veiculo_id == veiculo_id)
        pontos = session.scalars(stmt).all()
        return feature_collection(
            pontos,
            lambda p: {"id": p.id, "veiculo_id": p.veiculo_id, "capturado_em": p.capturado_em.isoformat()},
        )


@app.get("/telemetria/proximos")
def telemetria_proximos_endpoint(lon: float, lat: float, raio_metros: float = 1000):
    """Usa a funcao que voce implementa em exercicios.py."""
    with SessionLocal() as session:
        pontos = telemetria_proximos(session, lon, lat, raio_metros)
        return feature_collection(
            pontos,
            lambda p: {"id": p.id, "veiculo_id": p.veiculo_id, "capturado_em": p.capturado_em.isoformat()},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
