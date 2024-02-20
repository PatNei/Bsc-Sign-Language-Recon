import { UserConfig, defineConfig,loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default ({mode}:UserConfig) => { 
  process.env = {...process.env, ...loadEnv(mode, process.cwd())};
  console.log(process.env.VITE_HOST_IP)
  return defineConfig({
    plugins: [react()],
    root: ".",
    mode: "development",
    server:{
      port:3000,
      open:true,
      strictPort:true,
      hmr: {
        host: process.env.VITE_HOST_IP ?? "localhost"
      }
      

    },
    build: {
      ssr: false,
    }
  })
}
