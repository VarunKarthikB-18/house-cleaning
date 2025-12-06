<template>
  <div>
    <h2>Admin Dashboard</h2>
    <div class="stats">
      <div class="stat" v-for="(v,k) in stats" :key="k">
        <strong>{{ v }}</strong>
        <div>{{ k }}</div>
      </div>
    </div>

    <div v-if="loading">Loading bookings...</div>
    <div v-else>
      <div v-if="bookings.length === 0" class="empty">No bookings</div>
      <table v-if="bookings.length > 0" class="admin-table">
        <thead><tr><th>ID</th><th>User</th><th>Service</th><th>Start</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
          <AdminBookingRow v-for="b in bookings" :key="b.id" :booking="b" @updated="fetchAll" />
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import AdminBookingRow from '../components/AdminBookingRow.vue'

export default {
  components: { AdminBookingRow },
  setup() {
    const bookings = ref([])
    const stats = ref({ pending: 0, confirmed: 0, in_progress: 0, completed: 0 })
    const loading = ref(true)

    async function fetchAll() {
      loading.value = true
      try {
        const [bRes, sRes] = await Promise.all([api.get('/admin/bookings'), api.get('/admin/stats')])
        bookings.value = bRes.data || []
        stats.value = sRes.data || stats.value
      } catch (err) {
        alert('Failed to load admin data: ' + (err.response?.data?.message || err.message))
      } finally { loading.value = false }
    }

    onMounted(fetchAll)
    return { bookings, stats, loading, fetchAll }
  }
}
</script>

<style scoped>
.stats { display:flex; gap:12px; margin-bottom: 12px }
.stat { background:#fff; padding:12px; border-radius:8px; box-shadow:0 6px 18px rgba(0,0,0,0.06) }
.admin-table { width:100%; border-collapse:collapse }
.admin-table th, .admin-table td { padding:8px; border-bottom:1px solid #eee }
.empty { color:#666 }
</style>
