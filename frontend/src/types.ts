// Tipos minimos do formato GeoJSON que a API do marco 3 devolve.
// GeoJSON de verdade tem mais variantes (MultiPoint, MultiPolygon etc.),
// mas so declaramos o que realmente usamos -- suficiente pro TypeScript
// nos avisar se acessarmos um campo que nao existe.

export interface PontoGeoJSON {
  type: "Point";
  coordinates: [number, number]; // [longitude, latitude] -- nessa ordem, igual ao Shapely do marco 1
}

export interface PoligonoGeoJSON {
  type: "Polygon";
  coordinates: [number, number][][];
}

export interface FeatureGeoJSON<G, P> {
  type: "Feature";
  geometry: G;
  properties: P;
}

export interface FeatureCollectionGeoJSON<G, P> {
  type: "FeatureCollection";
  features: FeatureGeoJSON<G, P>[];
}

export interface TelemetriaProps {
  // /telemetria e /telemetria/proximos devolvem o id numerico da linha de
  // historico; /telemetria/atual nao tem "linha" (1 por veiculo, sempre
  // sobrescrita) e reusa o veiculo_id como id.
  id: number | string;
  veiculo_id: string;
  capturado_em: string;
}

export interface GeocercaProps {
  id: number;
  nome: string;
}
