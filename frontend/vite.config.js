import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// In Docker Compose the API service is named "web"
const api = process.env.VITE_API_PROXY || 'http://127.0.0.1:8000'
const ws = process.env.VITE_WS_PROXY || 'ws://127.0.0.1:8000'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
    proxy: {
      '/api': { target: api, changeOrigin: true },
      '/captcha': { target: api, changeOrigin: true },
      '/media': { target: api, changeOrigin: true },
      '/ws': {
        target: ws,
        ws: true,
        changeOrigin: true,
      },
    },
  },
})
