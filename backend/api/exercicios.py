"""Exercicio do marco 3. Complete a funcao marcada com TODO.

Precisa do container do marco 2 rodando com os dados de teste inseridos
(docker compose up -d + 02_postgis/01_setup.sql).

Rode com: poetry run python 03_api/exercicios.py
"""

from geoalchemy2 import Geography
from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID
from sqlalchemy import cast, select
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Telemetria


def telemetria_proximos(session: Session, lon: float, lat: float, raio_metros: float) -> list[Telemetria]:
    """Amostras de telemetria a ate raio_metros do ponto (lon, lat).

    Mesma logica do exercicio 1 do marco 2 (ST_DWithin), agora em
    SQLAlchemy em vez de SQL puro. O GeoAlchemy2 expoe as funcoes
    espaciais do PostGIS como funcoes Python importaveis (ST_DWithin,
    ST_MakePoint, ST_SetSRID, etc.) que geram SQL quando usadas dentro de
    um `select(...)`.

    Dica:
      ponto = ST_SetSRID(ST_MakePoint(lon, lat), 4326)
      select(Telemetria).where(
          ST_DWithin(cast(ponto, Geography), cast(Telemetria.geom, Geography), raio_metros)
      )

    O `cast(..., Geography)` e o equivalente SQLAlchemy do `::geography` do
    marco 2: sem ele, ST_DWithin usa a variante para o tipo `geometry`, que
    mede a distancia em graus (o SRID e 4326), nao em metros -- por isso
    500 "passava" praticamente qualquer ponto do planeta.
    """
    ponto = ST_SetSRID(ST_MakePoint(lon, lat), 4326)
    query = select(Telemetria).where(
        ST_DWithin(cast(ponto, Geography), cast(Telemetria.geom, Geography), raio_metros)
    )
    proximos = session.execute(query).scalars().all()

    return proximos


if __name__ == "__main__":
    with SessionLocal() as session:
        proximos = telemetria_proximos(session, -46.6333, -23.5505, 500)
        veiculos = sorted({p.veiculo_id for p in proximos})
        assert veiculos == ["drone-1"], f"esperado ['drone-1'], veio {veiculos}"
        print("exercicio passou:", [(p.veiculo_id, p.id) for p in proximos])
