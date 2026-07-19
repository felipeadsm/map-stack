"""Exercicio do marco 5: geodesia direta, usada pelo simulador de
movimento (simulador.py) para mover cada veiculo a cada tick.

Rode com: poetry run python 03_api/exercicios_movimento.py
"""

from pyproj import Geod


def proxima_posicao(
    lon: float, lat: float, azimute_graus: float, distancia_metros: float
) -> tuple[float, float]:
    """Anda `distancia_metros` a partir de (lon, lat), na direcao
    `azimute_graus` (0 = norte, 90 = leste, 180 = sul, 270 = oeste),
    seguindo a curvatura do elipsoide WGS84. Retorna o ponto de chegada
    (lon, lat).

    Complementa o exercicio 1 do marco 1: la voce usou `geod.inv(...)` --
    dados DOIS PONTOS, ache distancia e azimute entre eles (o "problema
    geodesico inverso"). Aqui e o caminho contrario: dado UM PONTO +
    azimute + distancia, ache o ponto de chegada (o "problema geodesico
    direto"/forward). Mesmo objeto Geod, outro metodo:

      geod.fwd(lon, lat, azimute_graus, distancia_metros) -> (lon2, lat2, azimute_de_volta)

    Descarte o terceiro valor (o azimute pra fazer o caminho de volta --
    nao precisamos dele aqui).
    """
    geod = Geod(ellps="WGS84")
    lon2, lat2, _ = geod.fwd(lon, lat, azimute_graus, distancia_metros)
    
    return lon2, lat2


if __name__ == "__main__":
    geod = Geod(ellps="WGS84")

    # Andar 1000m para o norte (azimute 0) parte de -23.5505 e chega em
    # -23.54147 -- a longitude nao muda (meridianos sao linhas de
    # longitude constante).
    lon2, lat2 = proxima_posicao(-46.6333, -23.5505, 0, 1000)
    assert abs(lon2 - (-46.6333)) < 1e-6, f"longitude nao deveria mudar, veio {lon2}"
    assert abs(lat2 - (-23.54147079402815)) < 1e-6, f"esperado ~-23.54147, veio {lat2}"

    # Ida e volta: andar 1000m num azimute e depois 1000m no azimute
    # oposto deve retornar (quase) exatamente ao ponto de partida.
    lon3, lat3 = proxima_posicao(lon2, lat2, 180, 1000)
    assert abs(lon3 - (-46.6333)) < 1e-6
    assert abs(lat3 - (-23.5505)) < 1e-6

    print("exercicio passou:", (round(lon2, 6), round(lat2, 6)))
