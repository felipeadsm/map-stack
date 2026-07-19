import { useEffect, useRef } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import { WS_TELEMETRIA_URL } from "./api";
import type { FeatureCollectionGeoJSON, PontoGeoJSON, TelemetriaProps } from "./types";

const TAMANHO_RASTRO = 20;

interface EstadoVeiculo {
  marcador: L.CircleMarker;
  rastro: L.Polyline | null;
  posicoes: L.LatLngExpression[];
}

// Veiculos da "frota viaria" (marco 6, ate 1000 carros) sao desenhados
// menores e sem rastro -- com esse volume, rastro por carro so vira
// ruido visual, e cada polyline extra e mais um objeto para o Leaflet
// gerenciar. Os veiculos "nomeados" (sim-1, sim-2, mqtt-1, ...) continuam
// com o tratamento rico de antes. Todos, porem, ganham popup ao clicar --
// o renderer Canvas NAO tira a interatividade: o Leaflet faz hit-testing
// manual (calcula se o clique caiu perto de algum circulo desenhado) em
// vez de depender do navegador testar um <div> de verdade, entao
// clique/popup continuam funcionando normalmente. So precisamos
// efetivamente registrar um popup em cada marcador -- o que faltava antes.
function ehVeiculoDaFrota(veiculoId: string): boolean {
  return veiculoId.startsWith("frota-");
}

function conteudoDoPopup(veiculoId: string, capturadoEm: string): string {
  return `<strong>${veiculoId}</strong><br>${new Date(capturadoEm).toLocaleTimeString()}`;
}

// Este componente nao renderiza NADA em JSX (retorna null) -- ele so usa
// o ciclo de vida do React (useEffect) para abrir/fechar o WebSocket, e
// por dentro faz tudo de forma IMPERATIVA no Leaflet: cria cada marcador
// uma vez e depois so MUTA ele (setLatLng) a cada mensagem nova.
//
// Isso e a licao do marco 4 aplicada de proposito: se guardassemos as
// posicoes em `useState` e renderizassemos <CircleMarker> via JSX, cada
// mensagem do WebSocket dispararia uma reconciliacao do React na arvore
// inteira -- com ate 1000 carros da frota viaria atualizando por
// segundo, isso travaria a pagina de novo (o mesmo problema do
// Laboratorio de Performance, so que rodando o tempo todo). Manipular o
// Leaflet direto via useRef evita esse custo: o React so entra em cena
// para montar/desmontar o componente, nunca para as atualizacoes de
// posicao em si.
//
// Cada mensagem do servidor agora e um FeatureCollection (um LOTE de
// posicoes, nao uma so -- ver `consumir_adapter` no backend), entao
// iteramos `mensagem.features` a cada `onmessage`.
export default function CamadaTempoReal() {
  const map = useMap();
  const veiculos = useRef(new Map<string, EstadoVeiculo>());

  useEffect(() => {
    const socket = new WebSocket(WS_TELEMETRIA_URL);

    socket.onmessage = (evento) => {
      const lote: FeatureCollectionGeoJSON<PontoGeoJSON, TelemetriaProps> = JSON.parse(evento.data);

      for (const feature of lote.features) {
        const [lon, lat] = feature.geometry.coordinates;
        const posicao: L.LatLngExpression = [lat, lon];
        const veiculoId = feature.properties.veiculo_id;
        const daFrota = ehVeiculoDaFrota(veiculoId);

        let estado = veiculos.current.get(veiculoId);
        if (!estado) {
          // Primeira vez que este veiculo aparece: cria os objetos Leaflet.
          const marcador = L.circleMarker(posicao, {
            radius: daFrota ? 4 : 7,
            color: daFrota ? "#f97316" : "#16a34a",
            fillOpacity: 0.9,
          })
            .addTo(map)
            .bindPopup(conteudoDoPopup(veiculoId, feature.properties.capturado_em));
          if (!daFrota) marcador.bindTooltip(veiculoId);
          const rastro = daFrota
            ? null
            : L.polyline([posicao], { color: "#16a34a", weight: 2, opacity: 0.5 }).addTo(map);
          estado = { marcador, rastro, posicoes: [posicao] };
          veiculos.current.set(veiculoId, estado);
          continue;
        }

        estado.marcador.setLatLng(posicao);
        // setPopupContent so redesenha algo se o popup estiver ABERTO --
        // clicar num carro em movimento mostra a hora mais recente, nao a
        // hora em que voce clicou.
        estado.marcador.setPopupContent(conteudoDoPopup(veiculoId, feature.properties.capturado_em));
        if (estado.rastro) {
          estado.posicoes.push(posicao);
          if (estado.posicoes.length > TAMANHO_RASTRO) estado.posicoes.shift();
          estado.rastro.setLatLngs(estado.posicoes);
        }
      }
    };

    return () => {
      socket.close();
      veiculos.current.forEach(({ marcador, rastro }) => {
        marcador.remove();
        rastro?.remove();
      });
      veiculos.current.clear();
    };
  }, [map]);

  return null;
}
