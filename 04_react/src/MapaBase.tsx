import { useEffect, useState } from "react";
import { LayersControl, MapContainer, Marker, Polygon, Popup, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./leaflet-icon-fix";
import { buscarGeocercas, buscarTelemetria } from "./api";
import type { GeocercaProps, PoligonoGeoJSON, PontoGeoJSON, TelemetriaProps } from "./types";

// react-leaflet e uma camada FINA sobre o Leaflet, nao um mapa reescrito
// em React. O <MapContainer> cria uma instancia real de L.Map (a classe
// do Leaflet puro) e a guarda numa ref; cada componente filho (<TileLayer>,
// <Marker>, ...) e so um componente React cujo useEffect chama os metodos
// imperativos do Leaflet (map.addLayer(...), etc.) quando monta, e os
// desfaz quando desmonta. O React NAO controla como o mapa e desenhado
// pixel a pixel -- ele so decide QUANDO criar/destruir objetos Leaflet,
// via seu ciclo de vida normal de componente.
//
// Isso importa para performance: reconciliar (fazer o "diff") de uma
// arvore React com milhares de <Marker> é caro por si so, ANTES mesmo do
// Leaflet entrar em cena -- ver LaboratorioPerformance.tsx.

// Coordenadas em [latitude, longitude] aqui (Leaflet usa essa ordem,
// AO CONTRARIO do GeoJSON, que usa [longitude, latitude] -- outra
// pegadinha de CRS/convencao para prestar atencao).
const CENTRO_SP: [number, number] = [-23.5505, -46.6333];

function paraLatLng(coords: [number, number]): [number, number] {
  return [coords[1], coords[0]];
}

export default function MapaBase() {
  const [geocercas, setGeocercas] = useState<
    { geometry: PoligonoGeoJSON; properties: GeocercaProps }[]
  >([]);
  const [telemetria, setTelemetria] = useState<
    { geometry: PontoGeoJSON; properties: TelemetriaProps }[]
  >([]);

  useEffect(() => {
    buscarGeocercas().then((fc) => setGeocercas(fc.features));
    buscarTelemetria().then((fc) => setTelemetria(fc.features));
  }, []);

  return (
    <MapContainer center={CENTRO_SP} zoom={13} style={{ height: "100%", width: "100%" }}>
      {/* BaseLayer = camadas de fundo, mutuamente exclusivas (so uma
          ativa por vez) -- e aqui que "satelite" entra: e SO OUTRO
          provedor de tiles raster, mesma mecanica do OpenStreetMap, so
          que as imagens sao fotos de satelite em vez de um mapa
          desenhado. Nao ha nada de especial no "modo satelite" alem de
          trocar a URL de onde os quadradinhos de imagem vem. */}
      <LayersControl position="topright">
        <LayersControl.BaseLayer checked name="Mapa (OpenStreetMap)">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
        </LayersControl.BaseLayer>
        <LayersControl.BaseLayer name="Satelite (Esri World Imagery)">
          <TileLayer
            attribution="Tiles &copy; Esri"
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          />
        </LayersControl.BaseLayer>

        {/* Overlay = camadas empilhaveis por cima da base, cada uma pode
            ser ligada/desligada independente -- os dados que vieram da
            SUA api (marco 3), nao de um provedor de mapa terceiro. */}
        <LayersControl.Overlay checked name="Geocercas">
          <>
            {geocercas.map((g) => (
              <Polygon
                key={g.properties.id}
                positions={g.geometry.coordinates[0].map(paraLatLng)}
                pathOptions={{ color: "#2563eb" }}
              >
                <Popup>{g.properties.nome}</Popup>
              </Polygon>
            ))}
          </>
        </LayersControl.Overlay>

        <LayersControl.Overlay checked name="Telemetria">
          <>
            {telemetria.map((t) => (
              <Marker key={t.properties.id} position={paraLatLng(t.geometry.coordinates)}>
                <Popup>
                  {t.properties.veiculo_id} <br />
                  {new Date(t.properties.capturado_em).toLocaleString()}
                </Popup>
              </Marker>
            ))}
          </>
        </LayersControl.Overlay>
      </LayersControl>
    </MapContainer>
  );
}
