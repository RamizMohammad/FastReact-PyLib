import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// FastReact: Tunnels API/page calls from React dev server to FastAPI
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/data': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
      '/ui': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
    }
  },
  build: {
    outDir: '../frontend_build',
    emptyOutDir: true,
  }
})
