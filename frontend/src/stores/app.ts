// Application-wide state (Pinia, setup-store style): whether the backend
// answers, as reported by GET /api/v1/health. The stores for the session,
// the catalogue, forecast runs and notifications follow with their screens
// (docs/architecture/architecture.md, section 4).
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { getHealth } from '../api/client'
import type { HealthResponse } from '../api/client'

export type HealthStatus = 'unknown' | 'checking' | 'ok' | 'unavailable'

export const useAppStore = defineStore('app', () => {
  const healthStatus = ref<HealthStatus>('unknown')
  const health = ref<HealthResponse | null>(null)
  const healthError = ref<string | null>(null)
  const healthCheckedAt = ref<Date | null>(null)

  const isBackendAvailable = computed(() => healthStatus.value === 'ok')

  /** Short text for the status indicator in the sidebar. */
  const healthLabel = computed<string>(() => {
    switch (healthStatus.value) {
      case 'ok':
        return health.value
          ? `${health.value.app_name} ${health.value.version} (${health.value.environment})`
          : 'available'
      case 'checking':
        return 'checking'
      case 'unavailable':
        return 'unavailable'
      default:
        return 'not checked'
    }
  })

  /** Call the health endpoint and record the outcome; never throws. */
  async function checkHealth(): Promise<void> {
    healthStatus.value = 'checking'
    try {
      health.value = await getHealth()
      healthStatus.value = 'ok'
      healthError.value = null
    } catch (error) {
      health.value = null
      healthStatus.value = 'unavailable'
      healthError.value = error instanceof Error ? error.message : String(error)
    } finally {
      healthCheckedAt.value = new Date()
    }
  }

  return {
    healthStatus,
    health,
    healthError,
    healthCheckedAt,
    isBackendAvailable,
    healthLabel,
    checkHealth,
  }
})
