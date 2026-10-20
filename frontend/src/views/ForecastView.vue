<script setup lang="ts">
// Forecast: start a forecast run, follow its status and open the forecast per
// item with history, point forecast, interval and model information. Placeholder.
import PageHeader from '../components/PageHeader.vue'
</script>

<template>
  <div class="page">
    <PageHeader />

    <section class="card section">
      <div class="card-header">
        <div>
          <h2>Forecast runs and item forecasts</h2>
          <p class="card-sub">What this screen will show once the forecast-run endpoints are available.</p>
        </div>
      </div>
      <div class="card-body">
        <span class="placeholder-note">planned</span>
        <ul>
          <li>
            Form to start a run for all or selected items with a configurable horizon (initial value 12 weeks)
            through <code>POST /api/v1/forecast-runs</code>; the run is queued and answered with
            <code>202 Accepted</code> (FR-06).
          </li>
          <li>
            List of runs with status, model and horizon; the current run is polled with
            <code>GET /api/v1/forecast-runs/{id}</code> until it is completed or failed.
          </li>
          <li>
            Forecast per item from <code>GET /api/v1/items/{id}/forecast</code>: history, point forecast and
            interval in one Chart.js chart, plus the model information (FR-07).
          </li>
          <li>Hold-out MAE and WAPE of the selected model against the baselines (FR-16).</li>
        </ul>
        <p class="placeholder-refs">
          Requirements: FR-06, FR-07, FR-16. Mockup: <code>prototype/forecast.html</code>. Implementation:
          forecast and risk screens, January–February 2027 (<code>docs/project-management/plan-and-milestones.md</code>).
        </p>
      </div>
    </section>
  </div>
</template>
