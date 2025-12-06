<template>
  <div>
    <h1>Dashboard</h1>
    <div v-if="loading">Loading...</div>
    <div v-else>
      <AdminDashboard v-if="role === 'admin'" />
      <UserDashboard v-else />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import * as auth from '../services/auth'
import AdminDashboard from './AdminDashboard.vue'
import UserDashboard from './UserDashboard.vue'

export default {
  components: { AdminDashboard, UserDashboard },
  setup() {
    const loading = ref(true)
    const role = ref(null)
    onMounted(async () => {
      try {
        const profile = await auth.getProfile()
        role.value = profile?.role || 'user'
      } catch (err) {
        auth.clearToken()
      } finally { loading.value = false }
    })
    return { loading, role }
  }
}
</script>

<style scoped>
h1 {
  margin-bottom: 2rem;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 2.5rem;
  font-weight: 700;
}
</style>
