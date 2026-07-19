import { describe, expect, it } from "vitest";
import { paraLatLng } from "./geo";

describe("paraLatLng", () => {
  it("inverte [lon, lat] do GeoJSON para [lat, lon] do Leaflet", () => {
    // Praca da Se: GeoJSON manda [-46.6333, -23.5505] (lon, lat).
    // Leaflet espera [-23.5505, -46.6333] (lat, lon) -- se essa conversao
    // quebrar, o mapa desenha longe de SP sem lancar erro nenhum.
    expect(paraLatLng([-46.6333, -23.5505])).toEqual([-23.5505, -46.6333]);
  });
});
