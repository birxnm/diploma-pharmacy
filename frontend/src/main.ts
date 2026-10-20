// Application entry point: creates the Vue application, installs Pinia and the
// router, loads the global stylesheet and mounts on #app (index.html).
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
