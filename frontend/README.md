# frontend

_PHA2-23 · Last updated: 2026-10-20_

Web interface of PharmaStock built with Vue 3, Vite, TypeScript, Vue Router, Pinia and Chart.js: dashboards, item pages with consumption history and forecast, prioritised shortage-risk list, imports, settings and in-app notifications. Owner: Birkhanym Kazhymukhamet. The screens follow the static mockups in [`../prototype/`](../prototype/README.md) and the component list of [docs/architecture/architecture.md](../docs/architecture/architecture.md) (section 4). The interface talks to the backend only through REST API v1, described in [docs/architecture/api-contract.md](../docs/architecture/api-contract.md).

## Status

As of 20 October 2026 the frontend is a runnable scaffold: the application shell with sidebar navigation, one placeholder route per screen (Dashboard with static KPI cards, Items, Forecast, Risks, Imports, Settings), a typed API client with the health call, a Pinia store that shows whether the backend answers, unit tests of the client and the store, and a production build that passes type checking. No screen reads backend data yet; the dashboard and item views are implemented with PHA2-29.

## Structure

```text
frontend/
├── index.html                   # HTML shell; loads src/main.ts
├── package.json                 # scripts and dependencies
├── vite.config.ts               # Vue plugin, dev proxy /api -> http://localhost:8000, Vitest settings
├── tsconfig.json                # project references (app + node)
├── tsconfig.app.json            # type checking of src/ (browser code and tests)
├── tsconfig.node.json           # type checking of vite.config.ts
├── src/
│   ├── main.ts                  # creates the app, installs Pinia and the router, mounts #app
│   ├── App.vue                  # application shell: sidebar navigation, backend status, <RouterView>
│   ├── env.d.ts                 # Vite client types and the VITE_* variables
│   ├── assets/main.css          # design tokens and layout shared with prototype/styles.css
│   ├── api/
│   │   ├── client.ts            # fetch wrapper for REST API v1 (base /api/v1), getHealth()
│   │   └── client.test.ts
│   ├── stores/
│   │   ├── app.ts               # Pinia store: backend health status
│   │   └── app.test.ts
│   ├── router/index.ts          # routes and sidebar entries
│   ├── components/
│   │   └── PageHeader.vue       # page heading with title and description from the route
│   └── views/                   # one component per screen
│       ├── DashboardView.vue
│       ├── ItemsView.vue
│       ├── ForecastView.vue
│       ├── RisksView.vue
│       ├── ImportsView.vue
│       └── SettingsView.vue
├── .gitignore
└── README.md
```

## Prerequisites

- Node.js 20 or a newer LTS release (20.x or 22.x) with npm 10; `package.json` declares `engines.node >= 20`. The scaffold was verified with Node.js 20.20 and npm 10.8.
- For a live backend: the service from [`../backend/`](../backend/README.md) running on port 8000. The frontend starts, builds and tests without it; only the status indicator in the sidebar reports the backend as unavailable.

## Setup

```bash
cd frontend
npm install
```

## Development

```bash
npm run dev
```

Vite serves the application at <http://localhost:5173> with hot module replacement. Start the backend in a second terminal (`uvicorn app.main:app --reload --port 8000` from `backend/`, see its README) to see the status indicator turn green.

### How the frontend talks to the backend

| Situation | Where API requests go | Configured in |
|---|---|---|
| `npm run dev` | The browser calls relative URLs under `/api/v1`; the Vite dev server forwards everything under `/api` to `http://localhost:8000`, so the interface and the API share one origin and no CORS headers are needed | `vite.config.ts` (`server.proxy`) |
| Production build (`dist/`) | Static files; the web server or the reverse proxy in front of it must route `/api/v1` to the backend ([architecture.md](../docs/architecture/architecture.md), section 7). When the build is served from a different origin than the API, set `VITE_API_BASE_URL` to the absolute API URL at build time | `src/api/client.ts`, `src/env.d.ts` |
| `npm run test` | No network: `fetch` is replaced by a stub in each test | `src/**/*.test.ts` |

- Every request goes through `src/api/client.ts`. It prefixes paths with `API_BASE_URL` (default `/api/v1`), sends and parses JSON, and turns a failed response into an `ApiError` with the `status`, the `code` and the `message` of the error envelope `{"error": {"code", "message", "details"}}` of the API contract (section 1.5). A request that never reaches the server (backend down, proxy misconfigured) raises `ApiError` with status `0` and code `NETWORK_ERROR`.
- `getHealth()` calls `GET /api/v1/health`; the `app` store (`src/stores/app.ts`) runs it when the shell is mounted and on "Check again", and the sidebar shows the result (`PharmaStock 0.1.0 (development)` when the backend answers).
- The backend also lists `http://localhost:5173` in `CORS_ORIGINS`, so the dev proxy is a convenience, not a requirement: with `VITE_API_BASE_URL=http://localhost:8000/api/v1` the browser calls the backend directly.
- Authentication is not implemented yet. Once `POST /api/v1/auth/login` exists (FR-14), a session store will keep the bearer token and the client will attach it as `Authorization: Bearer <token>`.

To check the proxy without the browser, with both servers running:

```bash
curl http://localhost:5173/api/v1/health
```

## Build

```bash
npm run build      # type check (vue-tsc) and production build into dist/
npm run preview    # serve dist/ locally at http://localhost:4173 to inspect the build
```

The build fails on any TypeScript error. `npm run preview` has no API proxy; it is meant for checking the static output, not for working against the backend.

## Tests

```bash
npm run test         # run once (Vitest)
npm run test:watch   # watch mode
```

Unit tests live next to the module they test (`*.test.ts`) and run in a Node environment without a browser. They cover the API client (URL building, JSON bodies, error envelope, network failure) and the `app` store. A frontend job (`npm install`, `npm run build`, `npm run test`) is planned to be added to `.github/workflows/ci.yml` (PHA2-22).

## Scripts

| Script | Command | Purpose |
|---|---|---|
| `npm run dev` | `vite` | Development server with the API proxy |
| `npm run build` | `vue-tsc --build && vite build` | Type check and production build into `dist/` |
| `npm run preview` | `vite preview` | Serve the production build locally |
| `npm run test` | `vitest run` | Unit tests, single run |
| `npm run test:watch` | `vitest` | Unit tests in watch mode |
| `npm run type-check` | `vue-tsc --build` | Type check only |

## Routes

| Path | View | Purpose | Requirements |
|---|---|---|---|
| `/` | `DashboardView` | KPI cards (static sample values for now); later top items at risk, notifications, projected-stock chart, latest import summary | FR-08, FR-09, FR-12, FR-18 |
| `/items` | `ItemsView` | Medicine catalogue and item page with history table and chart | FR-03, FR-04, FR-05, FR-17 |
| `/forecast` | `ForecastView` | Start and follow forecast runs; forecast per item with interval and model information | FR-06, FR-07, FR-16 |
| `/risks` | `RisksView` | Prioritised risk list with filters, planned deliveries and CSV export | FR-08, FR-09, FR-10, FR-13 |
| `/imports` | `ImportsView` | Upload of import files, validation report, data-quality summary | FR-01, FR-02, FR-10, FR-17, FR-18 |
| `/settings` | `SettingsView` | Thresholds and safety stock, suppliers and lead times, users and roles | FR-04, FR-11, FR-14, FR-15 |

Unknown paths redirect to the dashboard. Every view except the dashboard is a placeholder that lists what the screen will show, which endpoints it will call and which mockup it follows.

## Conventions

- `src/views/`: one component per screen, named `<Screen>View.vue`, loaded lazily by the router. Shared pieces go to `src/components/`.
- `src/stores/`: Pinia setup stores, one per concern (`app` now; session, catalogue, runs and notifications later).
- `src/api/`: the only place that calls `fetch`. Response types mirror the API contract field for field (`snake_case`, same names as the database entities).
- `src/assets/main.css`: the CSS custom properties and class names of `prototype/styles.css`, so that styles can be moved over block by block as each screen is implemented. No CSS framework, no external fonts.
- Interface strings are in English (NFR-10); the layout targets desktop browsers and stays usable at 1280 px (NFR-09). Risk levels are always labelled with text next to the colour.
- Branches are named `PHA2-<n>-<slug>`; the pull request must pass `npm run build` and `npm run test`.

## Planned next steps

- PHA2-29: dashboard and items views reading `GET /api/v1/items` and `GET /api/v1/items/{id}/history`, with the first Chart.js chart.
- Session store and login screen when `POST /api/v1/auth/login` is available (FR-14); role-dependent navigation (`viewer` sees no actions).
- Forecast, risk, import and settings screens in the order of the plan ([plan-and-milestones.md](../docs/project-management/plan-and-milestones.md)); an API client generated from the backend's OpenAPI schema once the endpoints are stable.
- `frontend` service in Docker Compose (static build served next to the backend, NFR-07) and the frontend jobs in CI.

Related tasks: this folder is produced under Linear issue PHA2-23 ([Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b), link will be added when the instance is confirmed).
