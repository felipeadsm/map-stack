import { useEffect, useRef } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import { WS_TELEMETRIA_URL } from "./api";
import type { FeatureGeoJSON, PontoGeoJSON, TelemetriaProps } from "./types";

const TAMANHO_RASTRO = 20;

interface EstadoVeiculo {
  marcador: L.CircleMarker;
  rastro: L.Polyline;
  posicoes: L.LatLngExpression[];
}

// Este componente nao renderiza NADA em JSX (retorna null) -- ele so usa
// o ciclo de vida do React (useEffect) para abrir/fechar o WebSocket, e
// por dentro faz tudo de forma IMPERATIVA no Leaflet: cria cada marcador
// uma vez e depois so MUTA ele (setLatLng) a cada mensagem nova.
//
// Isso e a licao do marco 4 aplicada de proposito: se guardassemos as
// posicoes em `useState` e renderizassemos <CircleMarker> via JSX, cada
// mensagem do WebSocket (varias por segundo, por veiculo) dispararia uma
// reconciliacao do React na arvore inteira -- o mesmo custo que vimos
// disparar no Laboratorio de Performance, so que agora rodando o tempo
// todo, nao so durante pan/zoom. Manipular o Leaflet direto via useRef
// evita esse custo: o React so entra em cena para montar/desmontar o
// componente (conectar/desconectar o socket), nunca para as atualizacoes
// de posicao em si.
export default function CamadaTempoReal() {
  const map = useMap();
  const veiculos = useRef(new Map<string, EstadoVeiculo>());

  useEffect(() => {
    const socket = new WebSocket(WS_TELEMETRIA_URL);

    socket.onmessage = (evento) => {
      const feature: FeatureGeoJSON<PontoGeoJSON, TelemetriaProps> = JSON.parse(evento.data);
      const [lon, lat] = feature.geometry.coordinates;
      const posicao: L.LatLngExpression = [lat, lon];
      const veiculoId = feature.properties.veiculo_id;

      let estado = veiculos.current.get(veiculoId);
      if (!estado) {
        // Primeira vez que este veiculo aparece: cria os objetos Leaflet.
        const marcador = L.circleMarker(posicao, { radius: 7, color: "#16a34a", fillOpacity: 0.9 })
          .addTo(map)
          .bindTooltip(veiculoId);
        const rastro = L.polyline([posicao], { color: "#16a34a", weight: 2, opacity: 0.5 }).addTo(map);
        estado = { marcador, rastro, posicoes: [posicao] };
        veiculos.current.set(veiculoId, estado);
        return;
      }

      estado.marcador.setLatLng(posicao);
      estado.posicoes.push(posicao);
      if (estado.posicoes.length > TAMANHO_RASTRO) estado.posicoes.shift();
      estado.rastro.setLatLngs(estado.posicoes);
    };

    return () => {
      socket.close();
      veiculos.current.forEach(({ marcador, rastro }) => {
        marcador.remove();
        rastro.remove();
      });
      veiculos.current.clear();
    };
  }, [map]);

  return null;
}
