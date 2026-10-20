<script setup lang="ts">
// Risks: prioritised list of items at risk with risk level, expected stock-out
// date and projected stock; filters by level; CSV export. Placeholder.
import PageHeader from '../components/PageHeader.vue'
</script>

<template>
  <div class="page">
    <PageHeader />

    <section class="card section">
      <div class="card-header">
        <div>
          <h2>Prioritised risk list</h2>
          <p class="card-sub">What this screen will show once the risk endpoints are available.</p>
        </div>
      </div>
      <div class="card-body">
        <span class="placeholder-note">planned</span>
        <ul>
          <li>
            Items at risk from <code>GET /api/v1/risks?level=high|medium|low</code>, ordered by risk level and
            expected stock-out date, with current stock, weekly forecast, lead time and planned receipts (FR-08,
            FR-09).
          </li>
          <li>
            Risk level shown as a badge with a text label (High, Medium, Low) next to the colour, so that it is
            readable without colour vision.
          </li>
          <li>Filters by level, medicine group and expected stock-out date; text search by code or name.</li>
          <li>Recording of a planned delivery for an item at risk (FR-10).</li>
          <li>Export of the list as CSV through <code>GET /api/v1/reports/risks.csv</code> (FR-13).</li>
        </ul>
        <p class="placeholder-refs">
          Requirements: FR-08, FR-09, FR-10, FR-13. Mockup: <code>prototype/risks.html</code>. Implementation:
          forecast and risk screens, January–February 2027 (<code>docs/project-management/plan-and-milestones.md</code>).
        </p>
      </div>
    </section>
  </div>
</template>
