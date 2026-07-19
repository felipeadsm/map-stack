"""Marco 1: geometria espacial pura, sem banco nem API.

Roda com: poetry run python 01_geometria/exemplo.py
"""

from pyproj import Transformer
from shapely import LineString, Point, Polygon

# --- 1. Geometrias basicas ---------------------------------------------
# Um "drone" na Praca da Se, em SP (lon, lat -- Shapely usa (x, y), ou seja
# (longitude, latitude), na ordem inversa do que normalmente falamos).
drone = Point(-46.6333, -23.5505)

rota = LineString([
    (-46.6333, -23.5505),
    (-46.6300, -23.5480),
    (-46.6250, -23.5470),
])

geocerca = Polygon([
    (-46.6400, -23.5550),
    (-46.6200, -23.5550),
    (-46.6200, -23.5400),
    (-46.6400, -23.5400),
])

print("drone dentro da geocerca?", geocerca.contains(drone))
print("comprimento da rota (graus, nao usar para metros):", rota.length)

# --- 2. O problema de medir em graus ------------------------------------
# rota.length acima esta em graus de lat/lon: nao serve para dizer "isso
# tem 3km". Para distancia em metros precisamos projetar para um CRS
# planar em metros (Web Mercator, EPSG:3857) antes de medir.
para_mercator = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

rota_metros = LineString([para_mercator.transform(x, y) for x, y in rota.coords])
print("comprimento da rota (metros, via Web Mercator):", round(rota_metros.length, 1))

# --- 3. Distancia geodesica de verdade ----------------------------------
# Web Mercator distorce distancias conforme se afasta do equador. Para
# distancia precisa entre pontos GPS, o certo e usar geodesia (elipsoide),
# nao um CRS projetado. pyproj.Geod resolve isso -- comparando com o mesmo
# trajeto (soma dos dois trechos) medido acima via Web Mercator.
from pyproj import Geod  # noqa: E402

geod = Geod(ellps="WGS84")
pontos = list(rota.coords)
trajeto_m = sum(
    geod.inv(lon1, lat1, lon2, lat2)[2]
    for (lon1, lat1), (lon2, lat2) in zip(pontos, pontos[1:])
)
print("comprimento da rota (metros, geodesico WGS84):", round(trajeto_m, 1))
