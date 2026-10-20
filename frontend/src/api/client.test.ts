import { afterEach, describe, expect, it, vi } from 'vitest'

import { API_BASE_URL, ApiError, getHealth, request } from './client'

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

const healthBody = { status: 'ok', app_name: 'PharmaStock', version: '0.1.0', environment: 'test' }

describe('api client', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('uses the relative path /api/v1 as the default base URL', () => {
    expect(API_BASE_URL).toBe('/api/v1')
  })

  it('getHealth() calls GET /api/v1/health and returns the parsed body', async () => {
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(healthBody))
    vi.stubGlobal('fetch', fetchMock)

    const health = await getHealth()

    expect(fetchMock).toHaveBeenCalledOnce()
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/v1/health')
    expect(init?.method).toBe('GET')
    expect(health).toEqual(healthBody)
  })

  it('serialises query parameters and JSON bodies', async () => {
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(jsonResponse({ items: [], total: 0 }))
    vi.stubGlobal('fetch', fetchMock)

    await request('/risks', { method: 'POST', query: { level: 'high', limit: 50, offset: undefined }, body: { a: 1 } })

    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/v1/risks?level=high&limit=50')
    expect(init?.method).toBe('POST')
    expect(init?.body).toBe('{"a":1}')
    expect(init?.headers).toMatchObject({ 'Content-Type': 'application/json' })
  })

  it('maps the error envelope of the API contract to ApiError', async () => {
    const envelope = {
      error: { code: 'NOT_FOUND', message: 'Item 17 not found', details: [{ field: 'id', message: 'unknown' }] },
    }
    vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(envelope, 404)))

    const error = await getHealth().catch((e: unknown) => e)

    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({ status: 404, code: 'NOT_FOUND', message: 'Item 17 not found' })
    expect((error as ApiError).details).toEqual(envelope.error.details)
  })

  it('falls back to the status text when the error body is not the envelope', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn<typeof fetch>().mockResolvedValue(new Response('Bad Gateway', { status: 502, statusText: 'Bad Gateway' })),
    )

    const error = await getHealth().catch((e: unknown) => e)

    expect(error).toMatchObject({ status: 502, code: 'HTTP_ERROR', message: '502 Bad Gateway' })
  })

  it('reports a network failure as ApiError with status 0 and code NETWORK_ERROR', async () => {
    vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockRejectedValue(new TypeError('Failed to fetch')))

    const error = await getHealth().catch((e: unknown) => e)

    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({ status: 0, code: 'NETWORK_ERROR' })
    expect((error as ApiError).message).toContain('/api/v1/health')
  })
})
