"""Testa o exercicio do marco 1 (01_geometria/exercicios.py).

01_geometria/exercicios.py e api/exercicios.py tem o MESMO nome de
arquivo. Um `import exercicios` normal colidiria no sys.modules com
qualquer outro teste que importe o outro "exercicios" -- por isso
carregamos este por caminho explicito, sob um apelido proprio.
"""

import importlib.util
import sys
from pathlib import Path

from shapely import Polygon

RAIZ = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "geometria_exercicios", RAIZ / "01_geometria" / "exercicios.py"
)
geometria = importlib.util.module_from_spec(_spec)
sys.modules["geometria_exercicios"] = geometria
_spec.loader.exec_module(geometria)


def test_distancia_metros_congonhas_paulista():
    # Distancia geodesica real (conferida com pyproj.Geod diretamente,
    # ver historico do marco 1) -- nao um valor chutado.
    d = geometria.distancia_metros(-46.6553, -23.6261, -46.6565, -23.5613)
    assert 6900 < d < 7500


def test_ponto_dentro_da_geocerca():
    geocerca = Polygon([(-46.64, -23.55), (-46.62, -23.55), (-46.62, -23.54), (-46.64, -23.54)])
    assert geometria.ponto_dentro_da_geocerca(-46.63, -23.545, geocerca) is True
    assert geometria.ponto_dentro_da_geocerca(-46.60, -23.545, geocerca) is False


def test_area_km2():
    quadrado_1km = Polygon([(0, 0), (1000, 0), (1000, 1000), (0, 1000)])
    assert abs(geometria.area_km2(quadrado_1km) - 1.0) < 1e-6
