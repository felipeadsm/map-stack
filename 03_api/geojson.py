"""Conversao de geometria do banco para GeoJSON.

Quando o GeoAlchemy2 le uma coluna geometry, o valor Python que volta e
WKB (Well-Known Binary -- o mesmo WKT do marco 2, so que em binario, mais
compacto para trafegar). `to_shape` converte esse WKB num objeto Shapely
(o mesmo Point/Polygon do marco 1). `shapely.geometry.mapping` converte um
objeto Shapely no dict Python equivalente a um objeto "geometry" de
GeoJSON (o campo que vai dentro de cada "Feature").
"""

from geoalchemy2.shape import to_shape
from shapely.geometry import mapping


def geometria_para_geojson(geom_wkb) -> dict:
    return mapping(to_shape(geom_wkb))
