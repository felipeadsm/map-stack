import { useState } from "react";
import LaboratorioPerformance from "./LaboratorioPerformance";
import MapaBase from "./MapaBase";
import MapaTempoReal from "./MapaTempoReal";

type Aba = "mapa" | "performance" | "tempo-real";

export default function App() {
  const [aba, setAba] = useState<Aba>("mapa");

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <nav style={{ display: "flex", gap: 8, padding: 8, background: "#0f172a" }}>
        <button onClick={() => setAba("mapa")} disabled={aba === "mapa"}>
          Mapa (marco 4)
        </button>
        <button onClick={() => setAba("performance")} disabled={aba === "performance"}>
          Laboratorio de performance
        </button>
        <button onClick={() => setAba("tempo-real")} disabled={aba === "tempo-real"}>
          Tempo real (marco 5)
        </button>
      </nav>
      <div style={{ flex: 1, minHeight: 0 }}>
        {aba === "mapa" && <MapaBase />}
        {aba === "performance" && <LaboratorioPerformance />}
        {aba === "tempo-real" && <MapaTempoReal />}
      </div>
    </div>
  );
}
