<template>
  <div class="register-page">
    <div class="card">
      <h2>Create Account</h2>
    <form @submit.prevent="submit">
      <label>Full Name <input v-model="name" type="text" required placeholder="John Doe" /></label>
      <label>Email <input v-model="email" type="email" required placeholder="you@example.com" /></label>
      <label>Phone <input v-model="phone" type="text" placeholder="(555) 123-4567" /></label>
      <label>Address <input v-model="address" type="text" placeholder="123 Main St, City, State" /></label>
      <label>Password <input v-model="password" type="password" required minlength="6" placeholder="At least 6 characters" /></label>
      <div class="actions">
        <button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? 'Creating...' : 'Sign Up' }}</button>
      </div>
      <p style="text-align: center; margin-top: 12px; color: var(--muted)">
        Already have an account? <router-link to="/login">Sign in</router-link>
      </p>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
    </div>
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
          const msg = err.response?.data?.msg || err.response?.data?.message || err.message || 'Registration error'
          error.value = msg
          window.dispatchEvent(new CustomEvent('toast', { detail: { message: msg, type: 'error' } }))
        } finally { loading.value = false }
    }

    return { name, email, phone, address, password, error, loading, submit }
  }
}
</script>

<style scoped>
.register-page {
  min-height: calc(100vh - 200px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, rgba(236, 72, 153, 0.1) 0%, rgba(99, 102, 241, 0.1) 50%, rgba(16, 185, 129, 0.1) 100%);
  position: relative;
  overflow: hidden;
}

.register-page::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(236, 72, 153, 0.1) 0%, transparent 70%);
  animation: pulse 8s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

.card {
  max-width: 500px;
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
  background: var(--gradient-secondary);
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
  border-color: var(--secondary);
  box-shadow: 0 0 0 4px rgba(236, 72, 153, 0.1);
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
  background: var(--gradient-secondary);
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
  color: #ec4899 !important;
  transition: all 0.3s ease;
}

p a:hover {
  color: #6366f1 !important;
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
