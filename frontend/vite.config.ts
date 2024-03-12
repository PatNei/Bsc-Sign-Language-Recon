import { UserConfig, defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default ({ mode }: UserConfig) => {
  if (mode === "Production") {
    return defineConfig({
      plugins: [react()],
      root: ".",
      server: {
        port: 5002,
        open: false,
        strictPort: true,
        hmr: false, //{ host: process.env.VITE_HOST_IP ?? "localhost" }
        host: "127.0.0.1"

      },
    })
  }
  else {
    return defineConfig({
      plugins: [react()],
      root: ".",
      mode: "Development",
      server: {
        port: 3000,
        open: true,
        strictPort: true,
        hmr: {
          host: process.env.VITE_HOST_IP ?? "localhost"
        }
      },
      build: {
        ssr: false,
      }
    })
  }
}
