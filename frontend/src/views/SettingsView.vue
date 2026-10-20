<script setup lang="ts">
// Settings: risk thresholds and safety-stock parameters; users and roles for
// administrators. Placeholder.
import PageHeader from '../components/PageHeader.vue'
</script>

<template>
  <div class="page">
    <PageHeader />

    <section class="card section">
      <div class="card-header">
        <div>
          <h2>Thresholds, users and roles</h2>
          <p class="card-sub">What this screen will show once the configuration endpoints are available.</p>
        </div>
      </div>
      <div class="card-body">
        <span class="placeholder-note">planned</span>
        <ul>
          <li>
            Risk thresholds and safety-stock parameters read and changed through
            <code>GET /api/v1/config/thresholds</code> and <code>PUT /api/v1/config/thresholds</code> (FR-11);
            changes are written to the audit log by the backend (FR-15).
          </li>
          <li>Suppliers and lead times per item (FR-04).</li>
          <li>
            User and role management for administrators: <code>administrator</code>, <code>pharmacist</code>,
            <code>viewer</code> (FR-14); the endpoints are proposed in the API contract, section 6.
          </li>
          <li>Audit log of imports, forecast runs and configuration changes (FR-15), proposed endpoint.</li>
        </ul>
        <p class="placeholder-refs">
          Requirements: FR-04, FR-11, FR-14, FR-15. Mockup: <code>prototype/settings.html</code>.
          Implementation: February 2027, with notifications and threshold configuration.
        </p>
      </div>
    </section>
  </div>
</template>
