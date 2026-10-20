<script setup lang="ts">
// Imports: upload of consumption, stock and receipt files, validation errors
// and the data-quality summary per import. Placeholder.
import PageHeader from '../components/PageHeader.vue'
</script>

<template>
  <div class="page">
    <PageHeader />

    <section class="card section">
      <div class="card-header">
        <div>
          <h2>Data import</h2>
          <p class="card-sub">What this screen will show once the import endpoints are available.</p>
        </div>
      </div>
      <div class="card-body">
        <span class="placeholder-note">planned</span>
        <ul>
          <li>
            Upload form for the four file types <code>consumption.csv</code>, <code>stock.csv</code>,
            <code>receipts.csv</code> and <code>planned_receipts.csv</code> (CSV or XLSX) through
            <code>POST /api/v1/imports</code> (FR-01, FR-10).
          </li>
          <li>
            Validation report from <code>GET /api/v1/imports/{id}</code>: missing columns, negative quantities,
            unknown items, duplicate periods, with row references (FR-02).
          </li>
          <li>Data-quality summary per import: coverage, gaps, outliers and flagged stock-out weeks (FR-17, FR-18).</li>
          <li>Import history with status and the user who uploaded the file.</li>
        </ul>
        <p class="placeholder-refs">
          Requirements: FR-01, FR-02, FR-10, FR-17, FR-18. Mockup: <code>prototype/imports.html</code>.
          Backend endpoint: PHA2-28; file formats in <code>docs/data/data-specification.md</code>.
        </p>
      </div>
    </section>
  </div>
</template>
