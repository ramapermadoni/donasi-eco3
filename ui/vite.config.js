import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Dev: teruskan /api/* ke backend Frappe lokal (donasi-eco3, port 8082). TIDAK ke sedekah.id.
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '127.0.0.1',
    port: 5174,
    proxy: { '/api': { target: 'http://127.0.0.1:8082', changeOrigin: false, headers: { Host: 'donasi.localhost' } } },
  },
})
