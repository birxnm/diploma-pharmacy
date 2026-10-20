/**
 * HTTP client for REST API v1 of the PharmaStock backend.
 *
 * The conventions follow docs/architecture/api-contract.md: JSON bodies,
 * snake_case field names reused from the database entities, the error envelope
 * `{ "error": { "code", "message", "details" } }` (section 1.5) and a bearer
 * token for every endpoint except /health and /auth/login (section 1.4). The
 * token is not attached yet; it will come from the session store once
 * authentication (FR-14) exists in the backend.
 *
 * Only the endpoints the interface already uses are typed here. A client
 * generated from the OpenAPI schema of the backend is planned once more than
 * the health endpoint exists (docs/architecture/architecture.md, section 4).
 */

/**
 * Base URL of the API without a trailing slash. Relative by default, so that
 * the Vite dev proxy (vite.config.ts) or the reverse proxy of the deployment
 * routes the requests to the backend; VITE_API_BASE_URL overrides it at build
 * time (src/env.d.ts).
 */
export const API_BASE_URL: string = (import.meta.env.VITE_API_BASE_URL ?? '/api/v1').replace(/\/+$/, '')

/** Response of GET /api/v1/health (api-contract.md, section 3.1). */
export interface HealthResponse {
  status: 'ok'
  app_name: string
  version: string
  environment: string
}

/** Body of every error response (api-contract.md, section 1.5). */
export interface ApiErrorBody {
  error: {
    code: string
    message: string
    details?: unknown[]
  }
}

/** Error raised for every failed request, whatever the cause. */
export class ApiError extends Error {
  /** HTTP status of the response; 0 when the request never reached the server. */
  readonly status: number
  /**
   * Stable code from the error envelope (for example NOT_FOUND, VALIDATION_ERROR).
   * NETWORK_ERROR and HTTP_ERROR are set by this client when no envelope is available.
   */
  readonly code: string
  /** Structured details of the envelope, when the backend sent any. */
  readonly details: unknown[] | undefined

  constructor(status: number, code: string, message: string, details?: unknown[], options?: ErrorOptions) {
    super(message, options)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  /** Serialised as JSON and sent with Content-Type: application/json. */
  body?: unknown
  /** Query parameters; entries with an undefined value are omitted. */
  query?: Record<string, string | number | boolean | undefined>
  signal?: AbortSignal
}

/** Perform a request against the API and return the parsed JSON body. */
export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const url = buildUrl(path, options.query)
  const headers: Record<string, string> = { Accept: 'application/json' }
  let body: string | undefined
  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(options.body)
  }

  let response: Response
  try {
    response = await fetch(url, {
      method: options.method ?? 'GET',
      headers,
      body,
      signal: options.signal,
    })
  } catch (cause) {
    throw new ApiError(0, 'NETWORK_ERROR', `Could not reach the API at ${url}`, undefined, { cause })
  }

  if (!response.ok) {
    throw await parseError(response)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}

function buildUrl(path: string, query?: RequestOptions['query']): string {
  const normalisedPath = path.startsWith('/') ? path : `/${path}`
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value !== undefined) {
      params.set(key, String(value))
    }
  }
  const queryString = params.toString()
  return queryString ? `${API_BASE_URL}${normalisedPath}?${queryString}` : `${API_BASE_URL}${normalisedPath}`
}

async function parseError(response: Response): Promise<ApiError> {
  let code = 'HTTP_ERROR'
  let message = `${response.status} ${response.statusText}`.trim()
  let details: unknown[] | undefined
  try {
    const payload: unknown = await response.json()
    if (isApiErrorBody(payload)) {
      code = payload.error.code
      message = payload.error.message
      details = payload.error.details
    } else if (isRecord(payload) && typeof payload.detail === 'string') {
      // Default FastAPI body, used until the envelope handlers are installed in the backend.
      message = payload.detail
    }
  } catch {
    // The body is not JSON (for example an HTML page from a proxy); keep the status text.
  }
  return new ApiError(response.status, code, message, details)
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function isApiErrorBody(value: unknown): value is ApiErrorBody {
  if (!isRecord(value) || !isRecord(value.error)) {
    return false
  }
  return typeof value.error.code === 'string' && typeof value.error.message === 'string'
}

/** GET /api/v1/health: liveness of the backend (api-contract.md, section 3.1). Public, no token. */
export function getHealth(options: Pick<RequestOptions, 'signal'> = {}): Promise<HealthResponse> {
  return request<HealthResponse>('/health', options)
}
