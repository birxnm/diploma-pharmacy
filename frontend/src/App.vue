<script setup lang="ts">
// Application shell: sidebar with brand, navigation and the backend status,
// and the content area where the router renders the current screen. Layout
// and class names mirror prototype/styles.css so that the Vue screens look
// like the agreed mockups.
import { onMounted } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

import { navigation } from './router'
import { useAppStore } from './stores/app'

const app = useAppStore()

onMounted(() => {
  void app.checkHealth()
})
</script>

<template>
  <div class="app">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-mark" aria-hidden="true">P</span>
        <span class="brand-name">PharmaStock</span>
        <span v-if="app.health" class="brand-tag">{{ app.health.environment }}</span>
      </div>

      <nav class="nav" aria-label="Main navigation">
        <RouterLink v-for="entry in navigation" :key="entry.name" :to="{ name: entry.name }" class="nav-link">
          {{ entry.title }}
        </RouterLink>
      </nav>

      <div class="sidebar-footer">
        <div class="health" :data-status="app.healthStatus" role="status" aria-live="polite">
          <span class="health-dot" aria-hidden="true"></span>
          <span class="health-text">
            <span class="health-title">Backend</span>
            <span class="health-detail">{{ app.healthLabel }}</span>
          </span>
        </div>
        <p v-if="app.healthError" class="health-error">{{ app.healthError }}</p>
        <button
          type="button"
          class="btn btn-sm health-action"
          :disabled="app.healthStatus === 'checking'"
          @click="app.checkHealth()"
        >
          Check again
        </button>
      </div>
    </aside>

    <main class="content">
      <RouterView />
    </main>
  </div>
</template>
