<template>
  <div class="card" style="max-width: 420px; margin: 0 auto">
    <h2 style="margin-top: 0; color: var(--text)">Sign In</h2>
    <form @submit.prevent="submit">
      <label>Email <input v-model="email" type="email" required placeholder="you@example.com" /></label>
      <label>Password <input v-model="password" type="password" required minlength="6" placeholder="Your password" /></label>
      <div class="actions">
        <button class="btn btn-primary" :disabled="loading">{{ loading ? 'Signing in...' : 'Sign In' }}</button>
      </div>
      <p style="text-align: center; margin-top: 12px; color: var(--muted)">
        Don't have an account? <router-link to="/register">Create one</router-link>
      </p>
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
.card {
  max-width: 420px;
  margin: 4rem auto;
}

h2 {
  text-align: center;
  color: var(--text);
  margin-bottom: 2rem;
}

form {
  display: flex;
  flex-direction: column;
}

label {
  margin-top: 1rem;
}

label:first-of-type {
  margin-top: 0;
}

.actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  justify-content: center;
}

.actions .btn-primary {
  flex: 1;
}

p {
  text-align: center;
  font-size: 0.95rem;
  margin-top: 1.5rem;
  color: var(--text-light);
}

p a {
  font-weight: 600;
  color: var(--primary);
}

.error {
  background-color: rgba(255, 107, 107, 0.1);
  color: #c00;
  padding: 0.75rem;
  border-radius: 4px;
  border-left: 3px solid #c00;
  margin-top: 1rem;
  font-size: 0.9rem;
}

@media (max-width: 480px) {
  .card {
    margin: 2rem 1rem;
    padding: 1.5rem;
  }

  .actions {
    flex-direction: column;
  }

  .actions .btn-primary {
    flex: unset;
  }
}
</style>
