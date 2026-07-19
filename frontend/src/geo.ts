// Ponto de partida geografico compartilhado entre as telas (Praca da Se,
// centro de Sao Paulo).
export const CENTRO_SP: [number, number] = [-23.5505, -46.6333];

// Leaflet usa [latitude, longitude]; GeoJSON usa [longitude, latitude] --
// a mesma pegadinha de ordem de coordenadas do marco 1 (Shapely tambem usa
// (x, y) = (lon, lat)). Trocar a ordem nao da erro nenhum -- so desenha no
// lugar errado do planeta, silenciosamente.
export function paraLatLng([lon, lat]: [number, number]): [number, number] {
  return [lat, lon];
}
