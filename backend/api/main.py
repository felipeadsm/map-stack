"""API do map-stack: marcos 3 (FastAPI + GeoAlchemy2), 5 (WebSocket) e 6
(adapters de ingestao plugaveis) reunidos no mesmo processo.

FastAPI e um framework Python para construir APIs; roda sobre ASGI
(Asynchronous Server Gateway Interface -- o padrao que permite ao Python
lidar com muitas requisicoes concorrentes sem bloquear). Uvicorn e o
servidor que efetivamente escuta a porta e chama a aplicacao FastAPI a
cada requisicao.

Rode com: poetry run python api/main.py
Depois abra http://127.0.0.1:8000/docs -- o FastAPI gera essa pagina
interativa (Swagger UI) sozinho, a partir da assinatura das funcoes abaixo.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID
from sqlalchemy import insert, select

from database import SessionLocal
from exercicios import telemetria_proximos
from geojson import geometria_para_geojson
from ingest.base import IngestAdapter, Posicao
from ingest.frota_viaria import FrotaViariaAdapter
from ingest.mqtt_adapter import MqttAdapter
from ingest.simulador_adapter import SimuladorAdapter
from models import Geocerca, Telemetria

# Marco 5: quem esta conectado no WebSocket agora. Um `set` simples --
# cada conexao aberta em /ws/telemetria entra aqui, e sai quando desconecta.
conexoes_ativas: set[WebSocket] = set()


async def broadcast(mensagem: dict) -> None:
    """Manda `mensagem` (um Feature GeoJSON) para todo mundo conectado.

    Diferente de um GET, que responde a UM pedido, o WebSocket e uma
    conexao aberta e persistente nos dois sentidos -- o servidor pode
    mandar mensagem a qualquer momento, sem o cliente pedir de novo. Por
    isso "broadcast" (mandar a mesma coisa pra todo mundo conectado) e o
    padrao natural aqui, e nao existiria com HTTP comum.
    """
    conexoes_mortas = []
    for conexao in conexoes_ativas:
        try:
            await conexao.send_json(mensagem)
        except Exception:
            conexoes_mortas.append(conexao)
    for conexao in conexoes_mortas:
        conexoes_ativas.discard(conexao)


def _gravar_lote(lote: list[Posicao]) -> None:
    with SessionLocal() as session:
        session.execute(
            insert(Telemetria).values(
                [
                    {
                        "veiculo_id": p["veiculo_id"],
                        "geom": ST_SetSRID(ST_MakePoint(p["lon"], p["lat"]), 4326),
                        "capturado_em": p["capturado_em"],
                    }
                    for p in lote
                ]
            )
        )
        session.commit()


def _lote_para_feature_collection(lote: list[Posicao]) -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [p["lon"], p["lat"]]},
                "properties": {"veiculo_id": p["veiculo_id"], "capturado_em": p["capturado_em"].isoformat()},
            }
            for p in lote
        ],
    }


async def consumir_adapter(adapter: IngestAdapter) -> None:
    """Laco generico: para QUALQUER adapter (simulador, MQTT, a frota
    viaria, o que vier depois), faz sempre a mesma coisa com as Posicoes
    que ele produzir -- grava no banco e propaga via WebSocket. Antes do
    marco 6, essa logica de "gravar + mandar" estava duplicada dentro do
    proprio simulador; com o adapter, ela existe uma vez so, e vale para
    qualquer fonte.

    Agrupa em LOTE em vez de gravar/transmitir uma Posicao por vez: a
    FrotaViariaAdapter produz ~1000 posicoes de uma vez, a cada tick. Sem
    lote, seriam 1000 INSERTs (1000 idas e voltas ao Postgres) e 1000
    mensagens WebSocket separadas por segundo -- caro por natureza, e o
    mesmo tipo de problema (fazer por item em vez de em conjunto) que
    discutimos no Laboratorio de Performance, agora no backend. Em vez
    disso: espera a primeira posicao chegar, depois drena tudo que ja
    estiver disponivel SEM esperar mais nada, e grava/transmite isso como
    um unico lote. Fontes lentas (o simulador, 1 veiculo por vez) acabam
    virando "lotes de tamanho 1" -- o mesmo codigo serve para os dois casos.
    """
    fila: asyncio.Queue[Posicao] = asyncio.Queue()

    async def alimentar_fila() -> None:
        async for posicao in adapter.posicoes():
            await fila.put(posicao)

    asyncio.create_task(alimentar_fila())

    while True:
        lote = [await fila.get()]
        while True:
            try:
                lote.append(fila.get_nowait())
            except asyncio.QueueEmpty:
                break

        _gravar_lote(lote)
        await broadcast(_lote_para_feature_collection(lote))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # "lifespan" e o lugar certo (na versao atual do FastAPI) para
    # codigo que deve rodar uma vez quando o servidor sobe e uma vez
    # quando ele desliga -- aqui, disparamos UMA task por adapter
    # configurado. Adicionar uma fonte nova de telemetria (outro topico
    # MQTT, um arquivo de replay, etc.) e so acrescentar mais uma linha
    # aqui, sem tocar no resto do arquivo.
    tarefas = [
        asyncio.create_task(consumir_adapter(SimuladorAdapter())),
        asyncio.create_task(consumir_adapter(MqttAdapter())),
        asyncio.create_task(consumir_adapter(FrotaViariaAdapter(quantidade=1000))),
    ]
    yield
    for tarefa in tarefas:
        tarefa.cancel()


app = FastAPI(
    title="map-stack API",
    description="Marcos 3, 5 e 6: FastAPI + GeoAlchemy2 + WebSocket + adapters de ingestao",
    lifespan=lifespan,
)

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
def listar_telemetria(veiculo_id: str | None = None, limite: int = 500):
    """Historico de telemetria (todas as amostras, mais recentes primeiro).

    `limite` existe para nao repetir o problema que travou a aba Mapa: os
    adapters do marco 5/6 gravam continuamente, entao "todo o historico"
    cresce pra sempre. Sem um teto, qualquer cliente que chame este
    endpoint sem filtro acaba baixando (e tentando desenhar) dezenas de
    milhares de linhas eventualmente -- o mesmo cenario do Laboratorio de
    Performance, so que sem querer.
    """
    with SessionLocal() as session:
        stmt = select(Telemetria).order_by(Telemetria.capturado_em.desc()).limit(limite)
        if veiculo_id:
            stmt = stmt.where(Telemetria.veiculo_id == veiculo_id)
        pontos = session.scalars(stmt).all()
        return feature_collection(
            pontos,
            lambda p: {"id": p.id, "veiculo_id": p.veiculo_id, "capturado_em": p.capturado_em.isoformat()},
        )


@app.get("/telemetria/atual")
def telemetria_atual():
    """So a posicao MAIS RECENTE de cada veiculo -- o que uma tela de
    "onde esta a frota agora" deveria mostrar, em vez do historico
    completo. Usa `DISTINCT ON` (extensao do Postgres): para cada valor
    distinto de `veiculo_id`, mantem so a primeira linha depois de
    ordenar por `capturado_em` decrescente -- ou seja, a mais nova.
    """
    with SessionLocal() as session:
        stmt = (
            select(Telemetria)
            .distinct(Telemetria.veiculo_id)
            .order_by(Telemetria.veiculo_id, Telemetria.capturado_em.desc())
        )
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


@app.websocket("/ws/telemetria")
async def websocket_telemetria(websocket: WebSocket):
    """Endpoint WebSocket: o navegador conecta uma vez (`new WebSocket(...)`
    no front) e fica recebendo, de forma continua, cada posicao nova que o
    simulador gerar -- sem precisar dar poll (ficar perguntando "tem
    novidade?" de tempos em tempos, como faria com fetch()).
    """
    await websocket.accept()
    conexoes_ativas.add(websocket)
    try:
        while True:
            # Nao esperamos nenhuma mensagem do cliente -- so usamos
            # receive_text() para o FastAPI notar quando o navegador
            # fecha a conexao (ai isso levanta WebSocketDisconnect).
            await websocket.receive_text()
    except WebSocketDisconnect:
        conexoes_ativas.discard(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
