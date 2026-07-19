"""Adapter que escuta um broker MQTT (EMQX, subindo via docker-compose) e
repassa cada mensagem recebida como uma Posicao.

MQTT (Message Queuing Telemetry Transport) e um protocolo de pub/sub leve
feito para dispositivos com pouca banda/energia -- o padrao de fato pra
telemetria de campo (rastreadores GPS, sensores IoT, gateways). Em vez de
o dispositivo chamar sua API HTTP diretamente (o que exigiria ele saber
seu endereco, autenticacao, etc.), ele so PUBLICA mensagens num TOPICO no
broker; qualquer um inscrito (SUBSCRIBE) nesse topico recebe, sem o
publicador saber quem esta ouvindo. Este adapter representa esse papel de
"assinante": ele e quem consome, dentro do nosso backend.

Rode `api/ingest/mqtt_publicador_teste.py` para simular um dispositivo
publicando, e ver este adapter (ja ligado em main.py) receber ao vivo.
"""

import asyncio
import json
from datetime import datetime
from typing import AsyncIterator

import paho.mqtt.client as mqtt

from .base import IngestAdapter, Posicao


class MqttAdapter(IngestAdapter):
    def __init__(self, host: str = "localhost", port: int = 1883, topico: str = "mapstack/telemetria"):
        self.host = host
        self.port = port
        self.topico = topico

    async def posicoes(self) -> AsyncIterator[Posicao]:
        loop = asyncio.get_running_loop()
        fila: asyncio.Queue[Posicao] = asyncio.Queue()

        def ao_conectar(client, userdata, flags, reason_code, properties=None):
            client.subscribe(self.topico)

        def ao_receber(client, userdata, mensagem):
            # Este callback roda numa THREAD interna do paho-mqtt (a
            # biblioteca gerencia a conexao de rede em background, fora do
            # asyncio) -- nao no nosso event loop. Por isso usamos
            # call_soon_threadsafe: e a forma segura de colocar algo na
            # fila asyncio a partir de uma thread diferente da que criou
            # esse event loop.
            try:
                dados = json.loads(mensagem.payload.decode("utf-8"))
                posicao = Posicao(
                    veiculo_id=dados["veiculo_id"],
                    lon=float(dados["lon"]),
                    lat=float(dados["lat"]),
                    capturado_em=datetime.fromisoformat(dados["capturado_em"]),
                )
                loop.call_soon_threadsafe(fila.put_nowait, posicao)
            except (KeyError, ValueError, json.JSONDecodeError):
                pass  # mensagem mal formada -- ignora, nao derruba o adapter

        cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        cliente.on_connect = ao_conectar
        cliente.on_message = ao_receber
        cliente.connect(self.host, self.port)
        cliente.loop_start()  # thread separada cuidando da rede MQTT

        try:
            while True:
                yield await fila.get()
        finally:
            cliente.loop_stop()
            cliente.disconnect()
