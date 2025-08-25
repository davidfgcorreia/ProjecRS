/*
main.js - Frontend bootstrap

Purpose:
- Create the Vue application, configure plugins (Pinia, Vue Router, Vuetify),
  and mount the app to the DOM.

How to extend:
- Add global providers (i18n, Sentry, analytics) before `app.mount()`.
- Register global components with `app.component()` or modify Pinia stores here.

Notes:
- Keep side-effects limited; prefer small plugin files for complex initialization.
*/

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import './style.css'
import { createVuetify } from 'vuetify'
import 'vuetify/styles'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const vuetify = createVuetify({
  components,
  directives,
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(vuetify)

// Mount the app onto the HTML element with id `#app`.
app.mount('#app')
