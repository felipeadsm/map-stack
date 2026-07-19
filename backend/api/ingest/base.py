"""Interface comum para qualquer fonte de telemetria.

Ate aqui (marco 5), so existia uma fonte de posicoes: o simulador,
chamando `broadcast(...)` direto de dentro do proprio loop de movimento.
Isso significa que "gerar posicoes" e "o que fazer com elas" (gravar no
banco, mandar pro WebSocket) estavam misturados no mesmo codigo.

Um "adapter" aqui resolve isso: qualquer fonte (simulador, um broker MQTT,
um arquivo de replay, um GPS de verdade mandando HTTP) so precisa saber
produzir `Posicao`s por este unico metodo. O resto do app (main.py) nao
sabe e nao precisa saber DE ONDE veio a posicao -- so consome o mesmo
formato, sempre do mesmo jeito. Trocar/adicionar uma fonte de dados vira
"escrever mais um adapter", sem tocar no banco nem no WebSocket.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncIterator, TypedDict


class Posicao(TypedDict):
    veiculo_id: str
    lon: float
    lat: float
    capturado_em: datetime


class IngestAdapter(ABC):
    @abstractmethod
    def posicoes(self) -> AsyncIterator[Posicao]:
        """Gerador assincrono infinito (`async def ... yield`, chamado com
        `async for`): produz uma `Posicao` cada vez que uma amostra nova
        de telemetria chega, de qualquer fonte que este adapter represente.
        """
        raise NotImplementedError
