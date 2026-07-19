-- Roda com:
--   docker compose exec -T postgis psql -U mapstack -d mapstack < 02_postgis/02_exemplo.sql

-- --- 1. ST_Contains: quais amostras de telemetria caem dentro da geocerca?
-- Convencao do PostGIS: quase toda funcao espacial comeca com "ST_"
-- (Spatial Type), um prefixo herdado do padrao SQL/MM da OGC (Open
-- Geospatial Consortium, a entidade que padroniza esses formatos).
SELECT t.veiculo_id, t.geom
FROM telemetria t
JOIN geocercas g ON g.nome = 'centro-expandido-sp'
WHERE ST_Contains(g.geom, t.geom);

-- --- 2. geometry vs geography: o mesmo erro do marco 1, agora no banco ---
-- A coluna "geom" e do tipo "geometry": o Postgres trata (lon, lat) como
-- um plano cartesiano puro. ST_Distance nesse tipo retorna graus, nao
-- metros -- inutil para "quantos metros ha entre estes dois pontos".
SELECT ST_Distance(a.geom, b.geom) AS distancia_em_graus_nao_usar
FROM telemetria a, telemetria b
WHERE a.veiculo_id = 'drone-1' AND b.veiculo_id = 'drone-2'
LIMIT 1;

-- "::geography" faz um cast (conversao de tipo) para "geography": um tipo
-- do PostGIS que assume o elipsoide WGS84 e calcula tudo com geodesia real
-- -- o mesmo pyproj.Geod que usamos no exercicio de distancia do marco 1,
-- so que rodando dentro do banco.
SELECT ST_Distance(a.geom::geography, b.geom::geography) AS distancia_em_metros
FROM telemetria a, telemetria b
WHERE a.veiculo_id = 'drone-1' AND b.veiculo_id = 'drone-2'
LIMIT 1;

-- --- 3. ST_Intersects: a rota do drone-1 cruza a geocerca? ---
-- ST_MakeLine agrupa varios Points (em ordem) numa LineString -- o mesmo
-- que fizemos com shapely.LineString, mas construido a partir de linhas
-- ja existentes na tabela via agregacao SQL.
WITH rota_drone1 AS (
    SELECT ST_MakeLine(geom ORDER BY id) AS geom
    FROM telemetria
    WHERE veiculo_id = 'drone-1'
)
SELECT ST_Intersects(g.geom, r.geom) AS rota_cruza_geocerca
FROM geocercas g, rota_drone1 r
WHERE g.nome = 'centro-expandido-sp';

-- --- 4. EXPLAIN: confirmando que o indice GiST esta sendo usado ---
-- EXPLAIN mostra o "plano de execucao": os passos internos que o Postgres
-- escolheu para responder a query. Se aparecer "Index Scan using
-- telemetria_geom_idx", o indice espacial criado no setup esta em uso; se
-- aparecer "Seq Scan" (varredura sequencial, linha por linha), o indice
-- nao ajudou nessa consulta (comum em tabelas pequenas como a nossa, onde
-- o Postgres decide que nao vale a pena).
EXPLAIN
SELECT t.veiculo_id
FROM telemetria t
JOIN geocercas g ON g.nome = 'centro-expandido-sp'
WHERE ST_Contains(g.geom, t.geom);
