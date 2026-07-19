# map-stack

Repo de estudo pratico de engenharia geoespacial: geometria, PostGIS, telemetria em tempo real e visualizacao em mapa. Stack: Python (backend/processamento) + React (frontend).

## Roadmap

1. **Geometria pura** (`01_geometria/`) — Shapely + Pyproj, sem banco nem API. Points/LineStrings/Polygons, CRS (WGS84 vs Web Mercator) e distancia geodesica.
2. **PostGIS** — Docker com `postgis/postgis`, queries espaciais em SQL puro (`ST_Contains`, `ST_Distance`, `ST_Intersects`).
3. **FastAPI + GeoAlchemy2** — API expondo os dados espaciais como GeoJSON.
4. **React + Leaflet** — consumindo a API e desenhando no mapa.
5. **Telemetria em stream** — simulador de posicoes publicando via WebSocket, front atualizando em tempo real.
6. (Avancado) Deck.gl para grandes volumes de pontos, ou vector tiles.

## Marco 1: geometria

```
poetry install
poetry run python 01_geometria/exemplo.py     # exemplos comentados
poetry run python 01_geometria/exercicios.py  # exercicios para implementar
```
