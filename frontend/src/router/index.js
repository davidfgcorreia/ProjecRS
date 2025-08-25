/**
 * Frontend router configuration
 *
 * Purpose
 * - Centralizes SPA routes used by the Vue application.
 * - Each route maps a path to a view component. Routes may pass props to components
 *   (see `props: true` for the Result route).
 *
 * Conventions
 * - Keep route names stable because they are used when calling `router.push({ name })`.
 * - Use route `props: true` when the view expects route params as props.
 * - Prefer lazy-loading large views when the app grows (use dynamic import()).
 *
 * How to add a route
 * 1. Import or lazy-load the view component.
 * 2. Add an entry to the `routes` array with `path`, `name`, and `component`.
 * 3. If the component needs route params as props, set `props: true`.
 *
 * Current routes (purpose)
 * - `/` (Login): authentication entrypoint
 * - `/register` (Register): user registration
 * - `/upload` (Upload): upload PDFs and start processing
 * - `/choose-table` (ChooseTable): select which table to work on
 * - `/result/:count?` (Result): view processing results (optional param `count`)
 * - `/preview` (Preview): preview a table or document
 */

import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import UploadView from '../views/UploadView.vue'
import ResultView from '../views/ResultView.vue'
import ChooseTableView from '../views/ChooseTableView.vue'
import PreviewView from '../views/PreviewView.vue'

const routes = [
  { path: '/', name: 'Login', component: LoginView },
  { path: '/register', name: 'Register', component: RegisterView },
  { path: '/upload', name: 'Upload', component: UploadView },
  { path: '/choose-table', name: 'ChooseTable', component: ChooseTableView },
  { path: '/result/:count?', name: 'Result', component: ResultView, props: true },
  { path: '/preview', name: 'Preview', component: PreviewView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
