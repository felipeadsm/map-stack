"""Testa a interface de adapters (marco 6)."""

import asyncio

import pytest
from ingest.base import IngestAdapter
from ingest.frota_viaria import FrotaViariaAdapter
from ingest.mqtt_adapter import MqttAdapter
from ingest.simulador_adapter import SimuladorAdapter


def test_adapters_implementam_a_interface():
    assert issubclass(SimuladorAdapter, IngestAdapter)
    assert issubclass(MqttAdapter, IngestAdapter)
    assert issubclass(FrotaViariaAdapter, IngestAdapter)


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
    # Poucos veiculos, historico tem valor -- essa flag e o que impede a
    # tabela telemetria de crescer sem fim (ver FrotaViariaAdapter abaixo).
    assert primeira["persistir_historico"] is True


@pytest.mark.asyncio
async def test_frota_viaria_nao_persiste_historico():
    # Regressao: a tabela telemetria chegou a passar de 1 milhao de linhas
    # (99.5% delas da frota) porque essa flag nao existia. Sem ela, cada um
    # dos ~1000 carros grava uma linha nova por segundo, para sempre.
    adapter = FrotaViariaAdapter(quantidade=5)
    gerador = adapter.posicoes()
    try:
        primeira = await asyncio.wait_for(gerador.__anext__(), timeout=5)
    finally:
        await gerador.aclose()

    assert primeira["persistir_historico"] is False
