"""Exercicios do marco 1. Preencha as funcoes marcadas com TODO.

Rode com: poetry run python 01_geometria/exercicios.py
Cada exercicio se autoverifica com assert -- sem output, sem erro, esta certo.
"""

from pyproj import Geod
from shapely import Point, Polygon


def distancia_metros(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Distancia geodesica em metros entre dois pontos GPS (WGS84).

    Dica: use pyproj.Geod(ellps="WGS84").inv(...)
    """
    geod = Geod(ellps="WGS84")
    _, _, distancia = geod.inv(lon1, lat1, lon2, lat2)
    return distancia


def ponto_dentro_da_geocerca(lon: float, lat: float, geocerca: Polygon) -> bool:
    """Verdadeiro se o ponto (lon, lat) esta dentro do poligono da geocerca."""
    ponto = Point(lon, lat)
    return geocerca.contains(ponto)


def area_km2(geocerca_metros: Polygon) -> float:
    """Area em km2 de um poligono que ja esta num CRS em metros (ex: EPSG:3857)."""
    area_m2 = geocerca_metros.area
    area_km2 = area_m2 / 1_000_000  # Converte de m² para km²
    return area_km2


if __name__ == "__main__":
    # Aeroporto de Congonhas -> Avenida Paulista, aprox 7.2km em linha reta
    d = distancia_metros(-46.6553, -23.6261, -46.6565, -23.5613)
    assert 6900 < d < 7500, f"esperado ~7.2km, veio {d}"

    geocerca = Polygon([(-46.64, -23.55), (-46.62, -23.55), (-46.62, -23.54), (-46.64, -23.54)])
    assert ponto_dentro_da_geocerca(-46.63, -23.545, geocerca) is True
    assert ponto_dentro_da_geocerca(-46.60, -23.545, geocerca) is False

    quadrado_1km = Polygon([(0, 0), (1000, 0), (1000, 1000), (0, 1000)])
    a = area_km2(quadrado_1km)
    assert abs(a - 1.0) < 1e-6, f"esperado 1.0 km2, veio {a}"

    print("todos os exercicios passaram")
