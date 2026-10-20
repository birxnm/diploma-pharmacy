/// <reference types="vite/client" />

// Variables read from import.meta.env. Vite exposes only variables prefixed
// with VITE_; they are baked into the build, so they must never hold secrets.
interface ImportMetaEnv {
  /**
   * Base URL of REST API v1 without a trailing slash. Defaults to the relative
   * path `/api/v1`, which the dev proxy (vite.config.ts) or the production
   * reverse proxy routes to the backend. Set an absolute URL only when the
   * static build is served from a different origin than the API.
   */
  readonly VITE_API_BASE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
