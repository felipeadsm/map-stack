"""Simula um dispositivo de campo publicando telemetria via MQTT -- para
testar o MqttAdapter sem precisar de hardware de verdade.

Precisa do EMQX rodando (`docker compose up -d emqx`) e da API rodando
(`poetry run python api/main.py`, que ja consome o topico via
MqttAdapter). Rode com: poetry run python api/ingest/mqtt_publicador_teste.py
"""

import json
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

TOPICO = "mapstack/telemetria"

# Uma rota simples, a pe, perto do centro de SP -- so para ver o ponto se
# mover no mapa via caminho MQTT (aba "Tempo real" do front).
ROTA = [
    (-46.6500, -23.5600),
    (-46.6490, -23.5590),
    (-46.6480, -23.5580),
    (-46.6470, -23.5570),
    (-46.6460, -23.5560),
]

cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
cliente.connect("localhost", 1883)
cliente.loop_start()

for lon, lat in ROTA:
    mensagem = {
        "veiculo_id": "mqtt-1",
        "lon": lon,
        "lat": lat,
        "capturado_em": datetime.now(timezone.utc).isoformat(),
    }
    cliente.publish(TOPICO, json.dumps(mensagem))
    print("publicado:", mensagem)
    time.sleep(1)

cliente.loop_stop()
cliente.disconnect()
