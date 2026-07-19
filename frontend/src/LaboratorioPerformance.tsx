import { useEffect, useMemo, useState } from "react";
import { CircleMarker, MapContainer, Marker, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./leaflet-icon-fix";
import FpsMeter from "./FpsMeter";
import { CENTRO_SP } from "./geo";
import { gerarPontos } from "./geraPontos";

type Modo = "marcador-dom" | "circulo-svg" | "circulo-canvas";

function useContagemDom(seletor: string, ativo: boolean): number {
  const [contagem, setContagem] = useState(0);

  useEffect(() => {
    if (!ativo) {
      setContagem(0);
      return;
    }
    const intervalo = setInterval(() => {
      setContagem(document.querySelectorAll(seletor).length);
    }, 500);
    return () => clearInterval(intervalo);
  }, [seletor, ativo]);

  return contagem;
}

export default function LaboratorioPerformance() {
  const [quantidade, setQuantidade] = useState(1000);
  const [modo, setModo] = useState<Modo>("marcador-dom");
  const [semente, setSemente] = useState(0);

  // useMemo evita regerar os pontos a cada re-render (ex: quando o FPS
  // muda de estado) -- so regera quando quantidade/modo/semente mudam de
  // verdade. Sem isso, cada tick do FpsMeter (1x/s) recriaria a lista
  // inteira de pontos por acidente.
  const pontos = useMemo(() => gerarPontos(quantidade), [quantidade, modo, semente]);

  const seletorDom =
    modo === "marcador-dom" ? ".leaflet-marker-icon" : modo === "circulo-svg" ? "svg path" : "";
  const contagemDom = useContagemDom(seletorDom, seletorDom !== "");

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{ padding: 12, background: "#f1f5f9", display: "flex", gap: 16, flexWrap: "wrap" }}>
        <label>
          Pontos:{" "}
          <select value={quantidade} onChange={(e) => setQuantidade(Number(e.target.value))}>
            {[100, 1000, 5000, 20000, 50000].map((n) => (
              <option key={n} value={n}>
                {n.toLocaleString("pt-BR")}
              </option>
            ))}
          </select>
        </label>

        <label>
          Renderizacao:{" "}
          <select value={modo} onChange={(e) => setModo(e.target.value as Modo)}>
            <option value="marcador-dom">Marcador com icone (1 &lt;div&gt;+&lt;img&gt; por ponto)</option>
            <option value="circulo-svg">Circulo vetorial, renderer SVG (1 &lt;path&gt; por ponto)</option>
            <option value="circulo-canvas">Circulo vetorial, renderer Canvas (0 DOM por ponto)</option>
          </select>
        </label>

        <button onClick={() => setSemente((s) => s + 1)}>Regerar pontos</button>

        {seletorDom && <span>Nos DOM medidos agora: <strong>{contagemDom.toLocaleString("pt-BR")}</strong></span>}
      </div>

      <p style={{ padding: "0 12px", color: "#475569", fontSize: 14 }}>
        Arraste e de zoom no mapa observando o contador de FPS no canto superior
        direito. Com "Marcador com icone" e dezenas de milhares de pontos, cada
        pan/zoom forca o navegador a recalcular posicao (layout) e repintar
        (paint) de um <code>&lt;div&gt;</code> por ponto -- e um custo que cresce
        linearmente com a quantidade de elementos, e o layout/paint do DOM nao
        usa a GPU. Com o renderer Canvas, os circulos sao pixels desenhados
        direto numa unica superficie -- zero elementos DOM extras, entao pan/zoom
        nao mexe no layout do navegador (so redesenha a textura do canvas).
      </p>

      {/* key={modo} forca o React a desmontar e recriar o MapContainer
          inteiro ao trocar de modo -- necessario porque `preferCanvas` e
          uma opcao lida so na CRIACAO do mapa Leaflet; mudar a prop num
          mapa ja existente nao teria efeito nenhum. */}
      <div style={{ position: "relative", flex: 1 }}>
        <FpsMeter />
        <MapContainer
          key={modo}
          center={CENTRO_SP}
          zoom={11}
          preferCanvas={modo === "circulo-canvas"}
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" />

          {modo === "marcador-dom" &&
            pontos.map((posicao, i) => <Marker key={i} position={posicao} />)}

          {modo !== "marcador-dom" &&
            pontos.map((posicao, i) => (
              <CircleMarker key={i} center={posicao} radius={4} pathOptions={{ color: "#dc2626" }} />
            ))}
        </MapContainer>
      </div>
    </div>
  );
}
