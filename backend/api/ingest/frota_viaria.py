"""Adapter que simula uma frota grande (por padrao 1000 carros) andando
sobre a malha viaria REAL do centro de Sao Paulo (ver rede_viaria.py).

Cada carro esta sempre "em cima" de uma aresta do grafo (entre dois nos do
OSM), avancando por ela; ao chegar no no de destino, escolhe uma aresta
de saida ao acaso -- de preferencia qualquer uma que NAO seja voltar por
onde veio (so volta se for a unica opcao, ou seja, um beco sem saida no
recorte da malha). Como cada segmento entre nos consecutivos de uma via
segue o desenho real da rua (inclusive curvas), o carro nunca "corta
caminho" por cima de quarteirao ou predio -- ele so anda sobre os
segmentos que existem de verdade no OpenStreetMap.
"""

import asyncio
import random
from datetime import datetime, timezone
from typing import AsyncIterator

from pyproj import Geod

from .base import IngestAdapter, Posicao
from .rede_viaria import carregar_rede

GEOD = Geod(ellps="WGS84")
INTERVALO_S = 1.0


def _comprimento_m(nos: dict[int, tuple[float, float]], no_a: int, no_b: int) -> float:
    lon1, lat1 = nos[no_a]
    lon2, lat2 = nos[no_b]
    _, _, distancia = GEOD.inv(lon1, lat1, lon2, lat2)
    return distancia


def _escolher_proxima_aresta(adjacencia: dict[int, list[int]], no_atual: int, no_anterior: int | None) -> int:
    vizinhos = adjacencia.get(no_atual, [])
    # Evita voltar imediatamente por onde veio, A NAO SER que seja a unica
    # opcao (beco sem saida) -- sem essa regra, num no de grau 2 (o caso
    # mais comum: um ponto no meio da curva de uma rua, nao um cruzamento
    # de verdade) o carro teria 50% de chance de "dar meia-volta" a cada
    # passo, parecendo tremer no lugar em vez de seguir a rua para frente.
    opcoes = [v for v in vizinhos if v != no_anterior]
    return random.choice(opcoes or vizinhos)


class _Carro:
    __slots__ = ("veiculo_id", "no_anterior", "no_atual", "no_destino", "progresso_m", "comprimento_m")

    def __init__(self, veiculo_id: str, no_partida: int, nos, adjacencia):
        self.veiculo_id = veiculo_id
        self.no_anterior: int | None = None
        self.no_atual = no_partida
        self.no_destino = _escolher_proxima_aresta(adjacencia, no_partida, None)
        self.progresso_m = 0.0
        self.comprimento_m = _comprimento_m(nos, self.no_atual, self.no_destino)

    def avancar(self, distancia_m: float, nos, adjacencia) -> None:
        self.progresso_m += distancia_m
        # "while" (nao "if"): num tick com distancia grande ou aresta bem
        # curta, o carro pode atravessar mais de um segmento no mesmo tick.
        while self.comprimento_m > 0 and self.progresso_m >= self.comprimento_m:
            self.progresso_m -= self.comprimento_m
            self.no_anterior, self.no_atual = self.no_atual, self.no_destino
            self.no_destino = _escolher_proxima_aresta(adjacencia, self.no_atual, self.no_anterior)
            self.comprimento_m = _comprimento_m(nos, self.no_atual, self.no_destino)

    def posicao_atual(self, nos) -> tuple[float, float]:
        lon1, lat1 = nos[self.no_atual]
        lon2, lat2 = nos[self.no_destino]
        fracao = (self.progresso_m / self.comprimento_m) if self.comprimento_m > 0 else 0.0
        # Interpolacao linear simples (nao geodesica) entre os dois nos.
        # Diferente do exercicio do marco 1, aqui e uma aproximacao segura
        # de proposito: cada segmento tem poucos metros/dezenas de metros
        # de comprimento, entao a distorcao de tratar lon/lat como plano
        # cartesiano nessa escala e desprezivel (o problema so aparece em
        # distancias grandes, como vimos comparando Web Mercator com
        # geodesia no marco 1).
        return (lon1 + (lon2 - lon1) * fracao, lat1 + (lat2 - lat1) * fracao)


class FrotaViariaAdapter(IngestAdapter):
    def __init__(self, quantidade: int = 1000, velocidade_m_s: float = 11.0, prefixo: str = "frota"):
        self.quantidade = quantidade
        self.velocidade_m_s = velocidade_m_s
        self.prefixo = prefixo

    async def posicoes(self) -> AsyncIterator[Posicao]:
        nos, adjacencia = carregar_rede()
        nos_de_partida = [no for no, vizinhos in adjacencia.items() if vizinhos]

        carros = [
            _Carro(f"{self.prefixo}-{i}", random.choice(nos_de_partida), nos, adjacencia)
            for i in range(self.quantidade)
        ]

        while True:
            await asyncio.sleep(INTERVALO_S)
            agora = datetime.now(timezone.utc)

            for carro in carros:
                carro.avancar(self.velocidade_m_s * INTERVALO_S, nos, adjacencia)
                lon, lat = carro.posicao_atual(nos)
                yield Posicao(veiculo_id=carro.veiculo_id, lon=lon, lat=lat, capturado_em=agora)
