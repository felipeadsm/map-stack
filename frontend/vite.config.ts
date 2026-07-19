import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Bind mount Windows -> container Linux nem sempre repassa eventos de
  // inotify (o mecanismo que o Linux usa pra avisar "este arquivo mudou").
  // Sem isso, o Vite as vezes fica servindo uma versao antiga em cache
  // mesmo com o arquivo certo em disco. Polling forca o Vite a checar o
  // arquivo periodicamente em vez de depender desse aviso.
  server: {
    watch: {
      usePolling: true,
      interval: 300,
    },
  },
  test: {
    environment: "jsdom",
  },
})
