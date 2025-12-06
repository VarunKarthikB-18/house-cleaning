import { createRouter, createWebHistory } from 'vue-router'
import Home from './pages/Home.vue'
import Login from './pages/Login.vue'
import Register from './pages/Register.vue'
import Dashboard from './pages/Dashboard.vue'
import AdminDashboard from './pages/AdminDashboard.vue'
import UserDashboard from './pages/UserDashboard.vue'
import NotFound from './pages/NotFound.vue'
import Bookings from './pages/Bookings.vue'
import NewBooking from './pages/NewBooking.vue'
import * as auth from './services/auth'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/admin', name: 'Admin', component: AdminDashboard, meta: { requiresAuth: true, adminOnly: true } },
  { path: '/user', name: 'User', component: UserDashboard, meta: { requiresAuth: true } },
  { path: '/bookings', name: 'Bookings', component: Bookings, meta: { requiresAuth: true } },
  { path: '/bookings/new', name: 'NewBooking', component: NewBooking, meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const token = auth.getToken()
  if (to.meta.requiresAuth) {
    if (!token) return next({ name: 'Login', query: { next: to.fullPath } })
    if (!auth.currentUser.value) {
      try {
        await auth.getProfile()
      } catch (err) {
        auth.clearToken()
        return next({ name: 'Login' })
      }
    }
    if (to.meta.adminOnly && auth.currentUser.value?.role !== 'admin') {
      return next({ name: 'Dashboard' })
    }
    return next()
  }

  if ((to.name === 'Login' || to.name === 'Register') && token) {
    if (!auth.currentUser.value) {
      try { await auth.getProfile() } catch (_) { auth.clearToken(); return next() }
    }
    return next({ name: 'Dashboard' })
  }

  return next()
})

export default router
