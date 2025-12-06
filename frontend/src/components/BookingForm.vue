<template>
  <div class="card">
    <h3>{{ title }}</h3>
    <form @submit.prevent="submit">
      <label>Service
        <select v-model="service_id">
          <option v-for="s in services" :key="s.id" :value="s.id">{{ s.name }} ({{ s.duration_mins }}m)</option>
        </select>
      </label>
      <label>Start (ISO datetime)
        <input v-model="start_datetime" placeholder="2025-12-10T09:00:00Z" />
      </label>
      <label>Notes
        <textarea v-model="notes" /></label>
      <div class="actions"><button class="btn btn-primary">Submit</button></div>
    </form>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../services/api'

export default {
  props: { title: { type: String, default: 'Create Booking' } },
  emits: ['created'],
  setup(_, { emit }) {
    const services = ref([])
    const service_id = ref(null)
    const start_datetime = ref('')
    const notes = ref('')

    async function fetchServices() {
      try {
        const res = await api.get('/services')
        services.value = res.data || []
        if (services.value.length) service_id.value = services.value[0].id
      } catch (err) { console.error('failed services', err) }
    }

    async function submit() {
      try {
        const payload = { service_id, start_datetime, notes }
        await api.post('/bookings', payload)
        window.dispatchEvent(new CustomEvent('toast', { detail: { message: 'Booking created', type: 'success' } }))
        emit('created')
      } catch (err) { window.dispatchEvent(new CustomEvent('toast', { detail: { message: 'Create failed: ' + (err.response?.data?.message || err.message), type: 'error' } })) }
    }

    onMounted(fetchServices)
    return { services, service_id, start_datetime, notes, submit }
  }
}
</script>

<style scoped>
label { display:block; margin-bottom:10px }
.actions { margin-top:10px }
</style>
