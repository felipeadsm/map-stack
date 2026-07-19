"""Malha viaria real (ruas de verdade) para os carros da frota andarem em
cima -- em vez de se mover em linha reta por cima de quarteiroes e predios.

Fonte: OpenStreetMap, via Overpass API (um servico publico que responde
consultas sobre o banco de dados do OSM). Baixamos uma vez os segmentos de
via ("ways" com tag highway=...) dentro de uma caixa delimitadora (bbox)
cobrindo o centro de Sao Paulo, e guardamos em cache local -- Overpass e
um servico compartilhado e gratuito, entao evitamos bater nele de novo a
cada reinicio do servidor.

O grafo que construimos aqui e deliberadamente simples: cada NO do OSM
(inclusive os que so descrevem a curva de uma rua, sem ser cruzamento de
verdade) vira um vertice, e cada par consecutivo de nos dentro de uma via
vira uma aresta. Isso da "de graca" o formato curvo das ruas reais -- nao
precisamos de nenhuma biblioteca de geometria alem do que ja usamos nos
marcos anteriores.
"""

import json
from pathlib import Path

import httpx

# South, West, North, East -- cobre aprox. Se/Anhangabau/Bela Vista/Liberdade,
# a mesma regiao da geocerca "centro-expandido-sp" do marco 2, um pouco maior.
BBOX = (-23.575, -46.665, -23.535, -46.610)

CACHE = Path(__file__).resolve().parent / "cache_rede_viaria.json"

TIPOS_DE_VIA = (
    "primary",
    "secondary",
    "tertiary",
    "residential",
    "unclassified",
    "living_street",
    "primary_link",
    "secondary_link",
    "tertiary_link",
)


def _baixar_dados_overpass() -> dict:
    sul, oeste, norte, leste = BBOX
    tipos = "|".join(TIPOS_DE_VIA)
    consulta = (
        f'[out:json][timeout:60];'
        f'way["highway"~"^({tipos})$"]({sul},{oeste},{norte},{leste});'
        f"(._;>;);"
        f"out body;"
    )
    resposta = httpx.post(
        "https://overpass-api.de/api/interpreter", data={"data": consulta}, timeout=90
    )
    resposta.raise_for_status()
    return resposta.json()


def _construir_grafo(dados_overpass: dict) -> tuple[dict[int, tuple[float, float]], dict[int, list[int]]]:
    """Retorna (nos, adjacencia).

    `nos`: id do no do OSM -> (lon, lat).
    `adjacencia`: id do no -> lista de ids de nos vizinhos (grafo NAO
    direcionado -- simplificacao deliberada, ignora sentido de mao unica).
    """
    nos: dict[int, tuple[float, float]] = {}
    for elemento in dados_overpass["elements"]:
        if elemento["type"] == "node":
            nos[elemento["id"]] = (elemento["lon"], elemento["lat"])

    adjacencia: dict[int, list[int]] = {}
    for elemento in dados_overpass["elements"]:
        if elemento["type"] != "way":
            continue
        ids_da_via = elemento["nodes"]
        for no_a, no_b in zip(ids_da_via, ids_da_via[1:]):
            adjacencia.setdefault(no_a, []).append(no_b)
            adjacencia.setdefault(no_b, []).append(no_a)

    return nos, adjacencia


def carregar_rede() -> tuple[dict[int, tuple[float, float]], dict[int, list[int]]]:
    """Carrega a malha viaria, do cache local se existir, ou baixando do
    Overpass (e salvando em cache) na primeira vez."""
    if CACHE.exists():
        dados = json.loads(CACHE.read_text(encoding="utf-8"))
    else:
        dados = _baixar_dados_overpass()
        CACHE.write_text(json.dumps(dados), encoding="utf-8")

    return _construir_grafo(dados)
