import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./leaflet-icon-fix";
import CamadaTempoReal from "./CamadaTempoReal";
import { CENTRO_SP } from "./geo";

export default function MapaTempoReal() {
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <p style={{ padding: "8px 12px", margin: 0, background: "#f1f5f9", color: "#475569", fontSize: 14 }}>
        Dois veiculos simulados (sim-1, sim-2) atualizando via WebSocket. Um
        terceiro (mqtt-1) aparece quando voce roda{" "}
        <code>backend/api/ingest/mqtt_publicador_teste.py</code> -- mesmo
        WebSocket, fonte de dados diferente (adapter MQTT em vez do
        simulador). Se sim-1/sim-2 nao se moverem, e porque o exercicio de{" "}
        <code>backend/api/exercicios_movimento.py</code> ainda nao foi
        implementado -- o simulador nota isso e mantem os veiculos parados,
        sem quebrar o resto da API.
      </p>
      <MapContainer center={CENTRO_SP} zoom={13} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <CamadaTempoReal />
      </MapContainer>
    </div>
  );
}
