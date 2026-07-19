import { useState } from "react";
import LaboratorioPerformance from "./LaboratorioPerformance";
import MapaBase from "./MapaBase";

type Aba = "mapa" | "performance";

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
      </nav>
      <div style={{ flex: 1, minHeight: 0 }}>
        {aba === "mapa" ? <MapaBase /> : <LaboratorioPerformance />}
      </div>
    </div>
  );
}
