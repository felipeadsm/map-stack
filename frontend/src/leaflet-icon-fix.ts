// Pegadinha classica de Leaflet + bundlers (Vite, Webpack): o icone padrao
// do marcador (o "pin" azul) e referenciado pelo Leaflet como um caminho
// de arquivo relativo (ex: "images/marker-icon.png"), assumindo que o
// leaflet.js e servido de uma pasta com essas imagens do lado. Bundlers
// modernos reescrevem/hasheiam nomes de arquivo, entao esse caminho
// relativo quebra silenciosamente -- os marcadores aparecem como um
// quadrado quebrado ou nada. A correcao padrao e importar as imagens
// explicitamente e sobrescrever as opcoes do icone default. So precisa
// rodar uma vez, no bootstrap do app.

import L from "leaflet";
import marcadorIcone from "leaflet/dist/images/marker-icon.png";
import marcadorIcone2x from "leaflet/dist/images/marker-icon-2x.png";
import marcadorSombra from "leaflet/dist/images/marker-shadow.png";

delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: marcadorIcone2x,
  iconUrl: marcadorIcone,
  shadowUrl: marcadorSombra,
});
