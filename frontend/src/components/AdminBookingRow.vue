<template>
  <tr>
    <td>{{ booking.id }}</td>
    <td>{{ booking.user?.email || booking.user_email || '—' }}</td>
    <td>{{ booking.service?.name || booking.service_name || '—' }}</td>
    <td>{{ formatDateTime(booking.start_datetime) }}</td>
    <td>
      <select v-model="localStatus" class="status-select">
        <option value="pending">Pending</option>
        <option value="confirmed">Confirmed</option>
        <option value="in_progress">In Progress</option>
        <option value="completed">Completed</option>
        <option value="cancelled">Cancelled</option>
      </select>
    </td>
    <td>
      <select v-model="localCleaner" class="cleaner-select">
        <option :value="null">Unassigned</option>
        <option v-for="c in cleaners" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
    </td>
    <td>${{ booking.price_total ? booking.price_total.toFixed(2) : '0.00' }}</td>
    <td>
      <button class="btn btn-sm" @click="applyChanges">Apply</button>
    </td>
  </tr>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../services/api'

export default {
  props: { booking: Object },
  setup(props, { emit }) {
    const cleaners = ref([])
    const localCleaner = ref(props.booking.cleaner_id || null)
    const localStatus = ref(props.booking.status || 'pending')

    async function fetchCleaners() {
      try {
        const res = await api.get('/admin/cleaners')
        cleaners.value = res.data?.data || res.data || []
      } catch (err) { 
        console.error('Failed to fetch cleaners:', err)
      }
    }

    async function applyChanges() {
      try {
        if (localCleaner.value) {
          await api.put(`/admin/bookings/${props.booking.id}/assign`, { cleaner_id: localCleaner.value })
        }
        if (localStatus.value) {
          await api.put(`/admin/bookings/${props.booking.id}/status`, { status: localStatus.value })
        }
        window.dispatchEvent(new CustomEvent('toast', { detail: { message: 'Updated', type: 'success' } }))
        emit('updated')
      } catch (err) {
        const errorMsg = err.response?.data?.msg || err.response?.data?.message || err.message
        window.dispatchEvent(new CustomEvent('toast', { detail: { message: 'Update failed: ' + errorMsg, type: 'error' } }))
      }
    }

    function formatDateTime(dateString) {
      if (!dateString) return '—'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
      })
    }

    onMounted(fetchCleaners)
    return { cleaners, localCleaner, localStatus, applyChanges, formatDateTime }
  }
}
</script>

<style scoped>
td {
  vertical-align: middle;
}

select {
  padding: 0.5rem;
  border: 2px solid var(--border);
  border-radius: var(--radius-sm);
  background-color: #ffffff !important;
  color: #1f2937 !important;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  margin-right: 0.5rem;
  cursor: pointer;
  min-width: 120px;
}

.status-select {
  min-width: 140px;
}

.cleaner-select {
  min-width: 150px;
}

select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.btn {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  background: var(--gradient-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn:active {
  transform: translateY(0);
}
</style>
