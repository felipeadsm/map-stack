import { describe, expect, it } from "vitest";
import { CENTRO_SP } from "./geo";
import { gerarPontos } from "./geraPontos";

describe("gerarPontos", () => {
  it("gera exatamente a quantidade pedida", () => {
    expect(gerarPontos(0)).toHaveLength(0);
    expect(gerarPontos(250)).toHaveLength(250);
  });

  it("mantem os pontos dentro do raio esperado ao redor do centro", () => {
    const pontos = gerarPontos(500);
    for (const [lat, lon] of pontos) {
      expect(Math.abs(lat - CENTRO_SP[0])).toBeLessThanOrEqual(0.3);
      expect(Math.abs(lon - CENTRO_SP[1])).toBeLessThanOrEqual(0.3);
    }
  });
});
