import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: true,
    allowedHosts: ['marat.silaeder.codingprojects.ru'],
    proxy: {
      '/api/': {
        target: 'http://web:8000',
        changeOrigin: true,
        secure: false,
      },
      '/socket.io/': {
        target: 'http://web:8000',
        ws: true,
      }
    }
  }
})