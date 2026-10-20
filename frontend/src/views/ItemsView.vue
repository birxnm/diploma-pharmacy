<script setup lang="ts">
// Items: medicine catalogue and the item page (current stock, consumption
// history as table and chart, suppliers and lead times). Placeholder until PHA2-29.
import PageHeader from '../components/PageHeader.vue'
</script>

<template>
  <div class="page">
    <PageHeader />

    <section class="card section">
      <div class="card-header">
        <div>
          <h2>Catalogue and item pages</h2>
          <p class="card-sub">What this screen will show once the catalogue endpoints are available.</p>
        </div>
      </div>
      <div class="card-body">
        <span class="placeholder-note">planned</span>
        <ul>
          <li>
            Catalogue table from <code>GET /api/v1/items</code> with search and filters: code, name, unit,
            group, primary supplier, lead time, current stock, risk level and active flag (FR-03, FR-04).
          </li>
          <li>
            Item page with the weekly consumption and stock history from
            <code>GET /api/v1/items/{id}/history</code> as a table and a Chart.js line chart (FR-05).
          </li>
          <li>Stock-out weeks highlighted in the chart and the table, as they are censored demand (FR-17).</li>
          <li>Link to the forecast of the item (FR-07) and to its planned receipts (FR-10).</li>
        </ul>
        <p class="placeholder-refs">
          Requirements: FR-03, FR-04, FR-05, FR-17. Mockups: <code>prototype/items.html</code>,
          <code>prototype/item.html</code>. Implementation: PHA2-29.
        </p>
      </div>
    </section>
  </div>
</template>
