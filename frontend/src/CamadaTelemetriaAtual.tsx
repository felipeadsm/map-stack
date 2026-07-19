import { useEffect, useRef } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import { paraLatLng } from "./geo";
import type { PontoGeoJSON, TelemetriaProps } from "./types";

interface Props {
  pontos: { geometry: PontoGeoJSON; properties: TelemetriaProps }[];
}

// Mesma licao de CamadaTempoReal.tsx, agora aplicada aqui: com ate ~1000
// veiculos (a frota viaria do marco 6), renderizar cada um como um
// <CircleMarker> JSX dentro de <LayersControl.Overlay> sobrecarrega o
// react-leaflet -- ele espera controlar POUCAS camadas (a ideia de
// "overlay" e "liga/desliga isto"), nao centenas de elementos filhos
// individuais recriados a cada fetch. Aqui desenhamos tudo de forma
// imperativa (um L.CircleMarker por ponto, criado uma vez por render
// deste componente) em vez de deixar o React reconciliar 1000 elementos.
export default function CamadaTelemetriaAtual({ pontos }: Props) {
  const map = useMap();
  const marcadores = useRef<L.CircleMarker[]>([]);

  useEffect(() => {
    marcadores.current = pontos.map((t) =>
      L.circleMarker(paraLatLng(t.geometry.coordinates), {
        radius: 6,
        color: "#16a34a",
        fillOpacity: 0.9,
      })
        .addTo(map)
        .bindPopup(`${t.properties.veiculo_id}<br>${new Date(t.properties.capturado_em).toLocaleString()}`)
    );

    return () => {
      marcadores.current.forEach((m) => m.remove());
      marcadores.current = [];
    };
  }, [map, pontos]);

  return null;
}
