import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  root: ".",
  mode: "development",
  server:{
    port:3000,
    host:"0.0.0.0",
    open:true,
    strictPort:true,
    https:false
    

  },
  build: {
    ssr: false,
  }
})
