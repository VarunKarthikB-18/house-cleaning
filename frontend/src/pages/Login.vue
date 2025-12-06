<template>
  <div class="login-page">
    <div class="card">
      <h2>Sign In</h2>
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
          const msg = err.response?.data?.msg || err.response?.data?.message || err.message || 'Login error'
          error.value = msg
          window.dispatchEvent(new CustomEvent('toast', { detail: { message: msg, type: 'error' } }))
      } finally { loading.value = false }
    }

    return { email, password, error, loading, submit }
  }
}
</script>

<style scoped>
.login-page {
  min-height: calc(100vh - 200px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(236, 72, 153, 0.1) 50%, rgba(59, 130, 246, 0.1) 100%);
  position: relative;
  overflow: hidden;
}

.login-page::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
  animation: pulse 8s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

.card {
  max-width: 450px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
  background: #ffffff !important;
  backdrop-filter: blur(20px);
  border: 1px solid #e5e7eb;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  color: #1f2937 !important;
}

h2 {
  text-align: center;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 2rem;
  font-size: 2rem;
  font-weight: 700;
}

form {
  display: flex;
  flex-direction: column;
}

label {
  margin-top: 1rem;
  font-weight: 600;
  color: #1f2937 !important;
}

label:first-of-type {
  margin-top: 0;
}

input {
  border: 2px solid #e5e7eb;
  transition: all 0.3s ease;
  background: #ffffff !important;
  color: #1f2937 !important;
}

input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
  background: #ffffff !important;
  color: #1f2937 !important;
}

input::placeholder {
  color: #6b7280 !important;
  opacity: 1;
}

.actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  justify-content: center;
}

.actions .btn-primary {
  flex: 1;
  background: var(--gradient-primary);
  padding: 1rem;
  font-size: 1.1rem;
}

p {
  text-align: center;
  font-size: 0.95rem;
  margin-top: 1.5rem;
  color: #6b7280 !important;
}

p a {
  font-weight: 600;
  color: #6366f1 !important;
  transition: all 0.3s ease;
}

p a:hover {
  background: var(--gradient-secondary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.error {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
  color: #dc2626 !important;
  padding: 1rem;
  border-radius: var(--radius);
  border-left: 4px solid #ef4444;
  margin-top: 1rem;
  font-size: 0.9rem;
  box-shadow: var(--shadow-sm);
  font-weight: 500;
}

@media (max-width: 480px) {
  .card {
    margin: 0;
    padding: 1.5rem;
  }

  .actions {
    flex-direction: column;
  }

  .actions .btn-primary {
    flex: unset;
  }
  
  h2 {
    font-size: 1.5rem;
  }
}
</style>
