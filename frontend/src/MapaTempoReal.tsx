import { MapContainer, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./leaflet-icon-fix";
import CamadaTempoReal from "./CamadaTempoReal";
import { CENTRO_SP } from "./geo";

export default function MapaTempoReal() {
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <p style={{ padding: "8px 12px", margin: 0, background: "#f1f5f9", color: "#475569", fontSize: 14 }}>
        Sim-1/sim-2 (verde) e ate 1000 carros da frota viaria (laranja, marco 6
        -- andando sobre ruas reais do centro de SP, baixadas do OpenStreetMap).
        Um veiculo mqtt-1 aparece quando voce roda{" "}
        <code>backend/api/ingest/mqtt_publicador_teste.py</code>. Renderer
        Canvas ligado (<code>preferCanvas</code>) -- e o mesmo volume que
        travaria a pagina com marcadores DOM, ver Laboratorio de Performance.
      </p>
      <MapContainer center={CENTRO_SP} zoom={13} preferCanvas style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <CamadaTempoReal />
      </MapContainer>
    </div>
  );
}
