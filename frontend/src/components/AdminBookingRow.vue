<template>
  <tr>
    <td>{{ booking.id }}</td>
    <td>{{ booking.user?.email || booking.user_email || '—' }}</td>
    <td>{{ booking.service?.name || booking.service_name }}</td>
    <td>{{ booking.start_datetime }}</td>
    <td>
      <select v-model="localStatus">
        <option value="pending">pending</option>
        <option value="confirmed">confirmed</option>
        <option value="in_progress">in_progress</option>
        <option value="completed">completed</option>
        <option value="cancelled">cancelled</option>
      </select>
    </td>
    <td>
      <select v-model="localCleaner">
        <option :value="null">Unassigned</option>
        <option v-for="c in cleaners" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <button class="btn" @click="applyChanges">Apply</button>
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
        cleaners.value = res.data || []
      } catch (err) { /* ignore */ }
    }

    async function applyChanges() {
      try {
        if (localCleaner.value) await api.put(`/admin/bookings/${props.booking.id}/assign`, { cleaner_id: localCleaner.value })
        if (localStatus.value) await api.put(`/admin/bookings/${props.booking.id}/status`, { status: localStatus.value })
        window.dispatchEvent(new CustomEvent('toast', { detail: { message: 'Updated', type: 'success' } }))
        emit('updated')
      } catch (err) { window.dispatchEvent(new CustomEvent('toast', { detail: { message: 'Update failed: ' + (err.response?.data?.message || err.message), type: 'error' } })) }
    }

    onMounted(fetchCleaners)
    return { cleaners, localCleaner, localStatus, applyChanges }
  }
}
</script>

<style scoped>
select { margin-right:8px }
</style>
