// Vite configuration of the PharmaStock frontend.
//
// The development server forwards every request under /api to the FastAPI
// backend (uvicorn on port 8000), so that the interface and the API share one
// origin during development and the relative API base URL (/api/v1) works
// without CORS. The production build has no proxy: the static web server or
// the reverse proxy in front of it routes /api/v1 to the backend
// (docs/architecture/architecture.md, section 7), or VITE_API_BASE_URL is set
// to an absolute URL at build time (see src/api/client.ts).
//
// `defineConfig` is imported from vitest/config so that the Vitest settings
// are type-checked together with the Vite ones.
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [vue()],
  server: {
    // The backend allows this origin in CORS_ORIGINS (backend/README.md).
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
})
