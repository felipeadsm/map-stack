"""Marco 5: simulador de movimento. Move alguns veiculos ficticios em
loop continuo, grava cada posicao no banco (mesma tabela do marco 2) e
manda cada atualizacao para quem estiver conectado no WebSocket.

Nota sobre a chamada ao banco aqui dentro: `session.execute`/`commit` do
SQLAlchemy "sincrono" BLOQUEIAM a thread enquanto esperam o Postgres
responder. Como este loop roda dentro do event loop assincrono do
asyncio (a engrenagem que permite o FastAPI atender varias requisicoes
"ao mesmo tempo" sem multiplas threads), esse bloqueio tecnicamente
atrasa outras tarefas assincronas por alguns milissegundos a cada volta.
Para 2-3 veiculos gravando 1x/segundo isso e irrelevante; num sistema de
producao com centenas de veiculos, o certo seria um driver assincrono de
verdade (ex: SQLAlchemy com asyncpg) ou rodar a escrita numa thread separada.
"""

import asyncio
import random
from datetime import datetime, timezone
from typing import Awaitable, Callable

from geoalchemy2.functions import ST_MakePoint, ST_SetSRID
from sqlalchemy import insert

from database import SessionLocal
from exercicios_movimento import proxima_posicao
from models import Telemetria

VEICULOS_INICIAIS = {
    "sim-1": {"lon": -46.6333, "lat": -23.5505, "azimute": 45.0},
    "sim-2": {"lon": -46.62, "lat": -23.555, "azimute": 200.0},
}

INTERVALO_S = 1.0
VELOCIDADE_M_S = 8.0  # ~29 km/h, ritmo de carro em via urbana


async def simular_movimento(broadcast: Callable[[dict], Awaitable[None]]) -> None:
    """Loop infinito. A cada INTERVALO_S segundos: escolhe um novo rumo
    (com uma variacao aleatoria em cima do rumo anterior, pra parecer uma
    curva e nao uma reta perfeita), calcula a proxima posicao via
    `proxima_posicao` (o exercicio que voce implementa), grava no banco e
    chama `broadcast(...)` para propagar a atualizacao aos clientes WebSocket.
    """
    estado = {veiculo_id: dict(info) for veiculo_id, info in VEICULOS_INICIAIS.items()}

    while True:
        await asyncio.sleep(INTERVALO_S)

        for veiculo_id, info in estado.items():
            info["azimute"] = (info["azimute"] + random.uniform(-20, 20)) % 360

            try:
                lon, lat = proxima_posicao(
                    info["lon"], info["lat"], info["azimute"], VELOCIDADE_M_S * INTERVALO_S
                )
            except NotImplementedError:
                continue  # exercicio ainda nao implementado -- veiculo fica parado

            info["lon"], info["lat"] = lon, lat
            agora = datetime.now(timezone.utc)

            with SessionLocal() as session:
                session.execute(
                    insert(Telemetria).values(
                        veiculo_id=veiculo_id,
                        geom=ST_SetSRID(ST_MakePoint(lon, lat), 4326),
                        capturado_em=agora,
                    )
                )
                session.commit()

            await broadcast(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lon, lat]},
                    "properties": {"veiculo_id": veiculo_id, "capturado_em": agora.isoformat()},
                }
            )
