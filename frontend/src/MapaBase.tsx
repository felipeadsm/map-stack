import { useEffect, useState } from "react";
import { LayersControl, MapContainer, Polygon, Popup, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./leaflet-icon-fix";
import { buscarGeocercas, buscarTelemetriaAtual } from "./api";
import CamadaTelemetriaAtual from "./CamadaTelemetriaAtual";
import { CENTRO_SP, paraLatLng } from "./geo";
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
//
// Essa aba busca /telemetria/atual (so a posicao mais recente de cada
// veiculo), nao o historico completo -- que cresce pra sempre com o
// simulador/MQTT/frota viaria rodando em loop.
//
// A telemetria (ate ~1000 veiculos com a frota viaria do marco 6) NAO e
// desenhada como filhos JSX de <LayersControl.Overlay> -- foi exatamente
// isso que travou a pagina (ver CamadaTelemetriaAtual.tsx): o
// LayersControl espera controlar poucas camadas, nao reconciliar
// centenas/milhares de elementos React de uma vez. A tela ficava presa
// no meio dessa reconciliacao, e por isso nem os tiles do mapa
// terminavam de pintar -- a thread principal estava ocupada demais para
// processar o carregamento das imagens.

export default function MapaBase() {
  const [geocercas, setGeocercas] = useState<
    { geometry: PoligonoGeoJSON; properties: GeocercaProps }[]
  >([]);
  const [telemetria, setTelemetria] = useState<
    { geometry: PontoGeoJSON; properties: TelemetriaProps }[]
  >([]);

  useEffect(() => {
    buscarGeocercas().then((fc) => setGeocercas(fc.features));
    buscarTelemetriaAtual().then((fc) => setTelemetria(fc.features));
  }, []);

  return (
    <MapContainer center={CENTRO_SP} zoom={13} preferCanvas style={{ height: "100%", width: "100%" }}>
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

        {/* Overlay = camadas empilhaveis por cima da base -- so a
            geocerca (poucos poligonos) fica aqui dentro; e barato. */}
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
      </LayersControl>

      {/* Telemetria: fora do LayersControl, desenhada de forma
          imperativa (ver CamadaTelemetriaAtual.tsx) -- escala pra
          centenas/milhares de veiculos sem travar a reconciliacao do React. */}
      <CamadaTelemetriaAtual pontos={telemetria} />
    </MapContainer>
  );
}
