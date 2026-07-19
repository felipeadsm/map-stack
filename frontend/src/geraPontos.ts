import { CENTRO_SP } from "./geo";

// Gera pontos aleatorios num raio (bruto, em graus) ao redor do centro --
// so para termos MUITOS pontos sem depender do banco. O objetivo do
// Laboratorio de Performance e testar o CUSTO DE RENDERIZACAO no
// navegador; a origem dos dados (banco vs gerado na hora) nao muda o
// argumento.
export function gerarPontos(quantidade: number): [number, number][] {
  const pontos: [number, number][] = [];
  for (let i = 0; i < quantidade; i++) {
    const lat = CENTRO_SP[0] + (Math.random() - 0.5) * 0.6;
    const lon = CENTRO_SP[1] + (Math.random() - 0.5) * 0.6;
    pontos.push([lat, lon]);
  }
  return pontos;
}
