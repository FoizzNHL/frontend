import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(),tailwindcss()],
  define: {
    global: 'window',
  },
  optimizeDeps: {
    include: ['mqtt'],
  },
  build: {
    commonjsOptions: {
      transformMixedEsModules: true,
    },
  },
  server: {
    proxy: {
      // 👇 proxy only this path
      '/nhle': {
        target: 'https://api-web.nhle.com',
        changeOrigin: true,
        rewrite: p => p.replace(/^\/nhle/, ''),
      },
    },
  },
})
