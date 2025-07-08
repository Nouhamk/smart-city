import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import MapView from '../views/MapView.vue'
import HistorySettingsView from '../views/HistorySettingsView.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/map',
    name: 'map',
    component: MapView
  },
  {
    path: '/history',
    name: 'history',
    component: HistorySettingsView,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guard for protected routes
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  const isLoggedIn = localStorage.getItem('token')
  const isAdmin = localStorage.getItem('isAdmin') === 'true'
  
  if (requiresAuth && !isLoggedIn) {
    next('/login')
  } else if (requiresAdmin && !isAdmin) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
