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
