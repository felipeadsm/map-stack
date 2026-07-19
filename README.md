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

## Marco 2: PostGIS

```
docker compose up -d   # sobe o Postgres+PostGIS na porta 5433 do host
docker compose exec -T postgis psql -U mapstack -d mapstack < 02_postgis/01_setup.sql
docker compose exec -T postgis psql -U mapstack -d mapstack < 02_postgis/02_exemplo.sql     # exemplos comentados
docker compose exec -T postgis psql -U mapstack -d mapstack < 02_postgis/03_exercicios.sql  # exercicios para implementar
```

## Marco 3: FastAPI + GeoAlchemy2

Precisa do marco 2 rodando (`docker compose up -d` + `01_setup.sql` ja aplicado).

```
poetry run python 03_api/main.py         # sobe a API em http://127.0.0.1:8000 (docs em /docs)
poetry run python 03_api/exercicios.py   # exercicio para implementar
```

## Marco 4: React + Leaflet

Precisa do marco 2 (Docker) e do marco 3 (`poetry run python 03_api/main.py`) rodando. Node/React rodam so dentro de container -- nada instalado no host.

```
docker compose up -d frontend   # sobe o Vite dev server em http://localhost:5173
```

Abas do app: **Mapa** (camadas base OpenStreetMap/satelite + overlays de geocercas/telemetria vindos da API) e **Laboratorio de performance** (compara custo de renderizar milhares de pontos como marcador DOM vs circulo SVG vs circulo Canvas, com contador de FPS ao vivo).

Comandos uteis:
```
docker compose logs -f frontend                          # acompanhar o dev server
docker compose exec frontend npm install <pacote>         # instalar nova dependencia
docker compose exec frontend npx tsc --noEmit -p tsconfig.app.json  # checar tipos
```

## Marco 5: telemetria em stream

Continua rodando dentro do processo do marco 3 (`poetry run python 03_api/main.py`) -- so adiciona um endpoint WebSocket (`/ws/telemetria`) e um simulador de movimento que grava no banco e transmite cada posicao nova aos clientes conectados.

```
poetry run python 03_api/exercicios_movimento.py  # exercicio: geodesia direta (Geod.fwd)
```

Depois de implementar, reinicie `03_api/main.py` e abra a aba "Tempo real" em http://localhost:5173 -- dois veiculos simulados (sim-1, sim-2) devem comecar a se mover.
