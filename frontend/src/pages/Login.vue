<template>
  <div class="card" style="max-width: 420px; margin: 0 auto">
    <h2>Login</h2>
    <form @submit.prevent="submit">
      <label>Email <input v-model="email" type="email" required /></label>
      <label>Password <input v-model="password" type="password" required minlength="6" /></label>
      <div class="actions">
        <button class="btn btn-primary" :disabled="loading">Sign In</button>
        <router-link to="/register">Register</router-link>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import * as auth from '../services/auth'
import { useRouter } from 'vue-router'
import { ref } from 'vue'

export default {
  setup() {
    const router = useRouter()
    const email = ref('')
    const password = ref('')
    const error = ref('')
    const loading = ref(false)

    async function submit() {
      error.value = ''
      if (!email.value || !password.value) {
        error.value = 'Please provide email and password.'
        return
      }
      loading.value = true
      try {
        const res = await auth.login({ email: email.value, password: password.value })
          if (res?.access_token) {
            await auth.getProfile()
            window.dispatchEvent(new CustomEvent('toast', { detail: { message: 'Signed in', type: 'success' } }))
            router.push({ name: 'Dashboard' })
        } else {
          error.value = 'Login failed. Please check your credentials.'
        }
      } catch (err) {
          const msg = err.response?.data?.message || err.message || 'Login error'
          error.value = msg
          window.dispatchEvent(new CustomEvent('toast', { detail: { message: msg, type: 'error' } }))
      } finally { loading.value = false }
    }

    return { email, password, error, loading, submit }
  }
}
</script>

<style scoped>
label { display:block; margin-bottom: 12px }
.actions { display:flex; gap: 12px; align-items:center }
.error { color: #c00; margin-top: 8px }
</style>
