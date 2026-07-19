-- Exercicios do marco 2. Complete o corpo de cada FUNCTION marcada com TODO.
--
-- Roda com:
--   docker compose exec -T postgis psql -U mapstack -d mapstack < 02_postgis/03_exercicios.sql
--
-- Cada exercicio e uma "function" SQL (um bloco de codigo reutilizavel
-- dentro do banco, equivalente a def em Python). No fim, blocos DO ($$ ... $$)
-- chamam sua funcao e usam RAISE EXCEPTION para falhar se o resultado
-- estiver errado -- e o "assert" do SQL. Sem erro no final = passou tudo.

-- --- Exercicio 1 ---------------------------------------------------------
-- Retorne os veiculo_id (sem repetir) cuja telemetria esteja a ate
-- raio_metros de distancia do ponto dado.
-- Dica: ST_DWithin(a::geography, b::geography, raio) -- equivalente a
-- "ST_Distance(a::geography, b::geography) <= raio", mas mais eficiente
-- porque consegue usar o indice GiST em vez de calcular a distancia exata
-- de toda linha da tabela.
CREATE OR REPLACE FUNCTION veiculos_proximos(ponto geometry, raio_metros double precision)
RETURNS SETOF text AS $$
    SELECT DISTINCT veiculo_id
    FROM telemetria
    WHERE ST_DWithin(ponto::geography, geom::geography, raio_metros);
$$ LANGUAGE sql;

-- --- Exercicio 2 ---------------------------------------------------------
-- Area em km2 da geocerca com o nome dado, calculada geodesicamente (nao
-- em graus^2). Dica: ST_Area(geom::geography) retorna metros quadrados
-- direto, sem precisar reprojetar para Web Mercator como fizemos em
-- Python no marco 1 -- o tipo "geography" ja resolve isso.
CREATE OR REPLACE FUNCTION area_geocerca_km2(nome_geocerca text)
RETURNS double precision AS $$
    SELECT ST_Area(geom::geography) / 1000000.0
    FROM geocercas
    WHERE nome = nome_geocerca;
$$ LANGUAGE sql;

-- --- Exercicio 3 ---------------------------------------------------------
-- Nome da geocerca que contem o ponto dado, ou NULL se nenhuma contiver.
-- Dica: ST_Contains(geocerca, ponto); LIMIT 1 caso geocercas se sobreponham.
CREATE OR REPLACE FUNCTION geocerca_do_ponto(ponto geometry)
RETURNS text AS $$
    SELECT nome
    FROM geocercas
    WHERE ST_Contains(geom, ponto)
    LIMIT 1;
$$ LANGUAGE sql;

-- --- Verificacao -----------------------------------------------------------
DO $$
DECLARE
    resultado text[];
    resultado_num double precision;
    resultado_txt text;
BEGIN
    -- Exercicio 1: a 500m do primeiro ponto de drone-1 tem que aparecer o
    -- proprio drone-1 (drone-2 esta a 3.4km, bem mais longe -- nao devia
    -- aparecer). Checamos "contem drone-1", nao igualdade exata: a partir
    -- do marco 5/6 o simulador e o adapter MQTT escrevem nessa mesma
    -- tabela continuamente, entao outros veiculos podem legitimamente
    -- passar perto desse ponto tambem.
    SELECT array_agg(DISTINCT v ORDER BY v) INTO resultado
    FROM veiculos_proximos(ST_SetSRID(ST_MakePoint(-46.6333, -23.5505), 4326), 500) AS v;
    IF NOT ('drone-1' = ANY(resultado)) THEN
        RAISE EXCEPTION 'exercicio 1: esperado conter drone-1, veio %', resultado;
    END IF;
    IF 'drone-2' = ANY(resultado) THEN
        RAISE EXCEPTION 'exercicio 1: drone-2 nao deveria estar a 500m, veio %', resultado;
    END IF;
    RAISE NOTICE 'exercicio 1 ok';

    -- Exercicio 2: a geocerca de teste tem ~2.26 km2 de area real.
    SELECT area_geocerca_km2('centro-expandido-sp') INTO resultado_num;
    IF resultado_num IS NULL OR abs(resultado_num - 2.262) > 0.01 THEN
        RAISE EXCEPTION 'exercicio 2: esperado ~2.262 km2, veio %', resultado_num;
    END IF;
    RAISE NOTICE 'exercicio 2 ok';

    -- Exercicio 3: ponto dentro da geocerca de teste, e ponto bem longe (fora).
    SELECT geocerca_do_ponto(ST_SetSRID(ST_MakePoint(-46.63, -23.545), 4326)) INTO resultado_txt;
    IF resultado_txt IS DISTINCT FROM 'centro-expandido-sp' THEN
        RAISE EXCEPTION 'exercicio 3a: esperado centro-expandido-sp, veio %', resultado_txt;
    END IF;

    SELECT geocerca_do_ponto(ST_SetSRID(ST_MakePoint(-46.10, -23.10), 4326)) INTO resultado_txt;
    IF resultado_txt IS NOT NULL THEN
        RAISE EXCEPTION 'exercicio 3b: esperado NULL, veio %', resultado_txt;
    END IF;
    RAISE NOTICE 'exercicio 3 ok';

    RAISE NOTICE 'todos os exercicios passaram';
END $$;
