<script setup lang="ts">
// Heading block of a screen. Title and description default to the meta of the
// current route (src/router/index.ts), so most views render it without props.
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps<{
  title?: string
  description?: string
}>()

const route = useRoute()

const title = computed(() => props.title ?? route.meta.title)
const description = computed(() => props.description ?? route.meta.description)
</script>

<template>
  <header class="topbar">
    <div>
      <h1>{{ title }}</h1>
      <p v-if="description" class="subtitle">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="topbar-actions">
      <slot name="actions" />
    </div>
  </header>
</template>
