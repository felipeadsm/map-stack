"""Testa a interface de adapters (marco 6)."""

import asyncio

import pytest
from ingest.base import IngestAdapter
from ingest.mqtt_adapter import MqttAdapter
from ingest.simulador_adapter import SimuladorAdapter


def test_adapters_implementam_a_interface():
    assert issubclass(SimuladorAdapter, IngestAdapter)
    assert issubclass(MqttAdapter, IngestAdapter)


@pytest.mark.asyncio
async def test_simulador_adapter_produz_posicoes_validas():
    adapter = SimuladorAdapter()
    gerador = adapter.posicoes()
    try:
        primeira = await asyncio.wait_for(gerador.__anext__(), timeout=3)
    finally:
        await gerador.aclose()

    assert isinstance(primeira["veiculo_id"], str) and primeira["veiculo_id"]
    assert -90 <= primeira["lat"] <= 90
    assert -180 <= primeira["lon"] <= 180
