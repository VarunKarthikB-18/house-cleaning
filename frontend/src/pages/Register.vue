<template>
  <div class="card" style="max-width: 520px; margin: 0 auto">
    <h2>Register</h2>
    <form @submit.prevent="submit">
      <label>Name <input v-model="name" required /></label>
      <label>Email <input v-model="email" type="email" required /></label>
      <label>Phone <input v-model="phone" /></label>
      <label>Address <input v-model="address" /></label>
      <label>Password <input v-model="password" type="password" required minlength="6" /></label>
      <div class="actions">
        <button class="btn btn-primary" :disabled="loading">Create account</button>
        <router-link to="/login">Have an account?</router-link>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue'
import * as auth from '../services/auth'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const router = useRouter()
    const name = ref('')
    const email = ref('')
    const phone = ref('')
    const address = ref('')
    const password = ref('')
    const error = ref('')
    const loading = ref(false)

    async function submit() {
      error.value = ''
      if (!email.value || password.value.length < 6) {
        error.value = 'Please enter valid email and password (>=6 chars).'
        return
      }
      loading.value = true
        try {
          await auth.register({ email: email.value, password: password.value, name: name.value, phone: phone.value, address: address.value })
          const loginRes = await auth.login({ email: email.value, password: password.value })
          if (loginRes?.access_token) {
            await auth.getProfile()
            window.dispatchEvent(new CustomEvent('toast', { detail: { message: 'Registered and signed in', type: 'success' } }))
            router.push({ name: 'Dashboard' })
          } else {
            router.push({ name: 'Login' })
          }
        } catch (err) {
          const msg = err.response?.data?.message || err.message || 'Registration error'
          error.value = msg
          window.dispatchEvent(new CustomEvent('toast', { detail: { message: msg, type: 'error' } }))
        } finally { loading.value = false }
    }

    return { name, email, phone, address, password, error, loading, submit }
  }
}
</script>

<style scoped>
.actions { display:flex; gap:12px; align-items:center }
.error { color:#c00 }
</style>
