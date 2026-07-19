-- Marco 2: PostGIS. Roda com (a partir da raiz do repo):
--   docker compose exec -T postgis psql -U mapstack -d mapstack < 02_postgis/01_setup.sql
-- "-T" desliga alocacao de pseudo-TTY (nao estamos numa sessao interativa,
-- so mandando um arquivo pela entrada padrao). "-U" e o usuario do Postgres,
-- "-d" e o nome do banco -- ambos definidos no docker-compose.yml.

-- "CREATE EXTENSION" liga um modulo opcional dentro do Postgres. A imagem
-- postgis/postgis ja vem com o modulo instalado no disco, mas cada banco
-- (database) precisa "ativa-lo" explicitamente -- e o que faz esse comando.
CREATE EXTENSION IF NOT EXISTS postgis;

-- Confirma a versao da extensao instalada.
SELECT PostGIS_Version();

-- Tabela de geocercas (fences), mesma ideia do Polygon do marco 1.
-- "geometry(Polygon, 4326)" declara: esta coluna guarda geometrias do tipo
-- Polygon, no SRID 4326 (WGS84, graus). O Postgres passa a rejeitar
-- qualquer INSERT que tente misturar tipos ou SRIDs diferentes ali.
DROP TABLE IF EXISTS geocercas;
CREATE TABLE geocercas (
    id   serial PRIMARY KEY,
    nome text NOT NULL,
    geom geometry(Polygon, 4326) NOT NULL
);

-- Tabela de telemetria: cada linha e uma amostra de posicao de um veiculo
-- num instante. "geometry(Point, 4326)" e o mesmo Point(lon, lat) do
-- Shapely, so que guardado no banco em vez de em memoria Python.
DROP TABLE IF EXISTS telemetria;
CREATE TABLE telemetria (
    id           serial PRIMARY KEY,
    veiculo_id   text NOT NULL,
    geom         geometry(Point, 4326) NOT NULL,
    capturado_em timestamptz NOT NULL DEFAULT now()
);

-- Indice espacial GiST (Generalized Search Tree): sem ele, "quais pontos
-- estao dentro deste poligono" faria um table scan (testa linha por linha).
-- Com o indice, o Postgres usa uma estrutura em arvore que descarta regioes
-- inteiras do espaco de uma vez -- essencial quando telemetria vira
-- milhoes de linhas.
CREATE INDEX telemetria_geom_idx ON telemetria USING GIST (geom);
CREATE INDEX geocercas_geom_idx ON geocercas USING GIST (geom);

-- Uma geocerca cobrindo aprox. o centro expandido de Sao Paulo (mesma
-- area do exercicio de geometria do marco 1).
-- ST_GeomFromText le uma string WKT (Well-Known Text -- o formato de texto
-- puro para geometrias, ex: 'POINT(lon lat)') e ST_SetSRID carimba o SRID
-- nela (o WKT sozinho nao carrega SRID).
INSERT INTO geocercas (nome, geom) VALUES (
    'centro-expandido-sp',
    ST_SetSRID(
        ST_GeomFromText('POLYGON((-46.64 -23.55, -46.62 -23.55, -46.62 -23.54, -46.64 -23.54, -46.64 -23.55))'),
        4326
    )
);

-- Algumas amostras de telemetria de um "drone" (mesmo cenario do marco 1).
-- ST_MakePoint(lon, lat) e um jeito mais direto de construir um Point do
-- que escrever WKT na mao.
INSERT INTO telemetria (veiculo_id, geom) VALUES
    ('drone-1', ST_SetSRID(ST_MakePoint(-46.6333, -23.5505), 4326)),
    ('drone-1', ST_SetSRID(ST_MakePoint(-46.6300, -23.5480), 4326)),
    ('drone-1', ST_SetSRID(ST_MakePoint(-46.6250, -23.5470), 4326)),
    ('drone-2', ST_SetSRID(ST_MakePoint(-46.6000, -23.5450), 4326));
