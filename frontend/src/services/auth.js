import { ref } from 'vue'
import api from './api'

export const currentUser = ref(null)

export function setToken(token) {
  if (token) localStorage.setItem('access_token', token)
}

export function getToken() {
  return localStorage.getItem('access_token')
}

export function clearToken() {
  localStorage.removeItem('access_token')
  currentUser.value = null
}

export async function register({ email, password, name, phone, address }) {
  const payload = { email, password, name, phone, address }
  const res = await api.post('/auth/register', payload)
  return res.data
}

export async function login({ email, password }) {
  const res = await api.post('/auth/login', { email, password })
  if (res.data?.access_token) {
    setToken(res.data.access_token)
  }
  return res.data
}

export async function getProfile() {
  const res = await api.get('/user/profile')
  currentUser.value = res.data
  return currentUser.value
}

export function logout() {
  clearToken()
  window.location.href = '/login'
}
