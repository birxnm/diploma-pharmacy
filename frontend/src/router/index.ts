// Client-side routes of the interface: one route per screen agreed in the
// mockups (prototype/) and in the component list of
// docs/architecture/architecture.md (section 4: Dashboard, Items, Forecast,
// Risks, Imports and Settings views). Views are loaded lazily so that every
// screen becomes its own chunk of the build.
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    /** Name shown in the sidebar and in the browser tab. */
    title: string
    /** One sentence shown under the page heading. */
    description: string
  }
}

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: {
      title: 'Dashboard',
      description:
        'Summary of the latest forecast run: items by risk level, recent imports and unread notifications.',
    },
  },
  {
    path: '/items',
    name: 'items',
    component: () => import('../views/ItemsView.vue'),
    meta: {
      title: 'Items',
      description:
        'Medicine catalogue and item pages: current stock, consumption history as table and chart, suppliers and lead times.',
    },
  },
  {
    path: '/forecast',
    name: 'forecast',
    component: () => import('../views/ForecastView.vue'),
    meta: {
      title: 'Forecast',
      description:
        'Start a forecast run for all or selected items, follow its status and open the forecast per item.',
    },
  },
  {
    path: '/risks',
    name: 'risks',
    component: () => import('../views/RisksView.vue'),
    meta: {
      title: 'Risks',
      description:
        'Prioritised list of items at risk with risk level, expected stock-out date and projected stock.',
    },
  },
  {
    path: '/imports',
    name: 'imports',
    component: () => import('../views/ImportsView.vue'),
    meta: {
      title: 'Imports',
      description:
        'Upload consumption, stock and receipt files and review validation errors and the data-quality summary.',
    },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../views/SettingsView.vue'),
    meta: {
      title: 'Settings',
      description:
        'Risk thresholds and safety-stock parameters; users and roles for administrators.',
    },
  },
  // Unknown paths go back to the dashboard until a "not found" screen is designed.
  { path: '/:pathMatch(.*)*', redirect: { name: 'dashboard' } },
]

export interface NavigationEntry {
  name: string
  title: string
}

/** Sidebar entries in display order: every named route that has a title. */
export const navigation: NavigationEntry[] = routes.flatMap((route) =>
  typeof route.name === 'string' && route.meta ? [{ name: route.name, title: route.meta.title }] : [],
)

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  // Same class as the mockups in prototype/styles.css.
  linkActiveClass: 'is-active',
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} - PharmaStock` : 'PharmaStock'
})

export default router
