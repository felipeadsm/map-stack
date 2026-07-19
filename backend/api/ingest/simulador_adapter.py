"""Adapter que move veiculos ficticios em loop continuo -- o mesmo
simulador do marco 5, so que agora reescrito no formato de IngestAdapter:
so produz `Posicao`s (yield), sem saber nada sobre banco ou WebSocket.
"""

import asyncio
import random
from datetime import datetime, timezone
from typing import AsyncIterator

from exercicios_movimento import proxima_posicao

from .base import IngestAdapter, Posicao

VEICULOS_INICIAIS = {
    "sim-1": {"lon": -46.6333, "lat": -23.5505, "azimute": 45.0},
    "sim-2": {"lon": -46.62, "lat": -23.555, "azimute": 200.0},
}

INTERVALO_S = 1.0
VELOCIDADE_M_S = 8.0  # ~29 km/h, ritmo de carro em via urbana


class SimuladorAdapter(IngestAdapter):
    """A cada INTERVALO_S segundos, escolhe um novo rumo (com variacao
    aleatoria em cima do rumo anterior, pra parecer uma curva) e calcula a
    proxima posicao via geodesia de verdade (`proxima_posicao`, exercicio
    do marco 5)."""

    async def posicoes(self) -> AsyncIterator[Posicao]:
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
                yield Posicao(
                    veiculo_id=veiculo_id,
                    lon=lon,
                    lat=lat,
                    capturado_em=datetime.now(timezone.utc),
                )
