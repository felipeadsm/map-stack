import { useEffect, useRef, useState } from "react";

// Mede quadros por segundo de verdade, contando quantas vezes o navegador
// chama requestAnimationFrame num intervalo de 1s. requestAnimationFrame e
// a API que o navegador usa para agendar o proximo repaint da tela --
// normalmente ate 60x/s num monitor de 60Hz. Se o main thread (a UNICA
// thread onde JS, layout e paint do DOM rodam) estiver ocupado demais
// processando milhares de elementos, o navegador pula quadros e esse
// numero cai -- e a prova concreta, medida, do que "ficar pesado"
// significa de verdade.
export function useFps(): number {
  const [fps, setFps] = useState(0);
  const contagem = useRef(0);
  const ultimaAmostra = useRef(performance.now());

  useEffect(() => {
    let quadro: number;

    function tick() {
      contagem.current += 1;
      const agora = performance.now();
      const decorrido = agora - ultimaAmostra.current;
      if (decorrido >= 1000) {
        setFps(Math.round((contagem.current * 1000) / decorrido));
        contagem.current = 0;
        ultimaAmostra.current = agora;
      }
      quadro = requestAnimationFrame(tick);
    }

    quadro = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(quadro);
  }, []);

  return fps;
}

export default function FpsMeter() {
  const fps = useFps();
  const cor = fps >= 50 ? "#16a34a" : fps >= 25 ? "#d97706" : "#dc2626";

  return (
    <div
      style={{
        position: "absolute",
        top: 10,
        right: 10,
        zIndex: 1000,
        background: "rgba(0,0,0,0.75)",
        color: cor,
        padding: "4px 10px",
        borderRadius: 6,
        fontFamily: "monospace",
        fontSize: 14,
        fontWeight: "bold",
      }}
    >
      {fps} fps
    </div>
  );
}
