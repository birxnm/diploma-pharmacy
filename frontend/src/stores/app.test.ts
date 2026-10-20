import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { useAppStore } from './app'

const healthBody = { status: 'ok', app_name: 'PharmaStock', version: '0.1.0', environment: 'test' }

describe('app store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('starts without a health check', () => {
    const store = useAppStore()

    expect(store.healthStatus).toBe('unknown')
    expect(store.health).toBeNull()
    expect(store.healthCheckedAt).toBeNull()
    expect(store.isBackendAvailable).toBe(false)
    expect(store.healthLabel).toBe('not checked')
  })

  it('records the backend name, version and environment when the health endpoint answers', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn<typeof fetch>().mockResolvedValue(
        new Response(JSON.stringify(healthBody), { status: 200, headers: { 'Content-Type': 'application/json' } }),
      ),
    )
    const store = useAppStore()

    await store.checkHealth()

    expect(store.healthStatus).toBe('ok')
    expect(store.health).toEqual(healthBody)
    expect(store.healthError).toBeNull()
    expect(store.isBackendAvailable).toBe(true)
    expect(store.healthLabel).toBe('PharmaStock 0.1.0 (test)')
    expect(store.healthCheckedAt).toBeInstanceOf(Date)
  })

  it('marks the backend unavailable and keeps the error message when the request fails', async () => {
    vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockRejectedValue(new TypeError('Failed to fetch')))
    const store = useAppStore()

    await store.checkHealth()

    expect(store.healthStatus).toBe('unavailable')
    expect(store.health).toBeNull()
    expect(store.isBackendAvailable).toBe(false)
    expect(store.healthLabel).toBe('unavailable')
    expect(store.healthError).toContain('/api/v1/health')
    expect(store.healthCheckedAt).toBeInstanceOf(Date)
  })
})
