import type {
  FeatureCollectionGeoJSON,
  GeocercaProps,
  PoligonoGeoJSON,
  PontoGeoJSON,
  TelemetriaProps,
} from "./types";

// A API do marco 3 roda fora do container do front (voce ainda esta com
// ela em `poetry run python 03_api/main.py` no host). O navegador -- nao
// o container do Vite -- e quem faz essas chamadas fetch(), entao
// "localhost:8000" aqui se refere a maquina do usuario, nao ao container.
const API_URL = "http://localhost:8000";

// "ws://" e o equivalente de "http://" para WebSocket: mesmo host/porta,
// protocolo diferente porque a conexao fica aberta (nao e um
// request/response que termina). Se a API estivesse atras de HTTPS, seria
// "wss://" (o "s" de seguro), do mesmo jeito que HTTP vira HTTPS.
export const WS_TELEMETRIA_URL = "ws://localhost:8000/ws/telemetria";

export async function buscarGeocercas(): Promise<
  FeatureCollectionGeoJSON<PoligonoGeoJSON, GeocercaProps>
> {
  const resposta = await fetch(`${API_URL}/geocercas`);
  return resposta.json();
}

export async function buscarTelemetria(): Promise<
  FeatureCollectionGeoJSON<PontoGeoJSON, TelemetriaProps>
> {
  const resposta = await fetch(`${API_URL}/telemetria`);
  return resposta.json();
}
