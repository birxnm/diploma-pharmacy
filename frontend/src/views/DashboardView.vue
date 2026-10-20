<script setup lang="ts">
// Dashboard: KPI cards and, later, the top items at risk, notifications, the
// projected-stock chart of one item and the summary of the latest import.
// The values below are the sample scenario of the mockups (prototype/index.html);
// they are static until the API endpoints exist (PHA2-29).
import PageHeader from '../components/PageHeader.vue'

interface Kpi {
  label: string
  value: string
  note: string
  highlight?: boolean
}

const kpis: Kpi[] = [
  { label: 'Items tracked', value: '30', note: 'active items in the catalogue (31 incl. inactive)' },
  { label: 'Items at high risk', value: '4', note: 'Medium 7 · Low 19', highlight: true },
  { label: 'Last forecast run', value: '19 Oct 2026', note: 'run #12 · model sba · horizon 12 weeks' },
  { label: 'Data coverage', value: '97%', note: '156 weeks of history · 11 stock-out weeks flagged' },
]
</script>

<template>
  <div class="page">
    <PageHeader />

    <section class="grid grid-kpi section" aria-label="Key figures">
      <div v-for="kpi in kpis" :key="kpi.label" class="card kpi">
        <div class="kpi-label">{{ kpi.label }}</div>
        <div class="kpi-value" :class="{ 'is-high': kpi.highlight }">{{ kpi.value }}</div>
        <div class="kpi-note">{{ kpi.note }}</div>
      </div>
    </section>

    <section class="card section">
      <div class="card-header">
        <div>
          <h2>Placeholder values</h2>
          <p class="card-sub">The figures above are static sample values, not results of the forecasting module.</p>
        </div>
      </div>
      <div class="card-body">
        <span class="placeholder-note">planned</span>
        <p>
          The dashboard will read the counts per risk level and the latest run from
          <code>GET /api/v1/risks</code>, unread notifications from <code>GET /api/v1/notifications</code>
          and the latest import summary from <code>GET /api/v1/imports/{id}</code>. Planned blocks:
        </p>
        <ul>
          <li>Top items at risk, ordered by risk level and expected stock-out date (FR-09).</li>
          <li>Notifications for high-risk items (FR-12).</li>
          <li>Projected stock of one high-risk item over the forecast horizon as a Chart.js line chart (FR-08).</li>
          <li>Summary of the latest import: coverage, gaps, outliers (FR-18).</li>
        </ul>
        <p class="placeholder-refs">
          Requirements: FR-08, FR-09, FR-12, FR-18. Mockup: <code>prototype/index.html</code>. Implementation: PHA2-29.
        </p>
      </div>
    </section>
  </div>
</template>
