<template>
  <div class="card booking-card">
    <div class="row">
      <div>
        <strong>{{ booking.service_name || booking.service?.name || 'Service' }}</strong>
        <div class="meta">{{ booking.start_datetime }} - {{ booking.status }}</div>
      </div>
      <div class="actions">
        <button class="btn" @click="cancel" v-if="canCancel">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'
export default {
  props: { booking: Object },
  computed: {
    canCancel() { return this.booking?.status === 'pending' }
  },
  methods: {
    async cancel() {
      if (!confirm('Cancel this booking?')) return
      try {
        await api.delete(`/bookings/${this.booking.id}`)
        window.dispatchEvent(new CustomEvent('toast', { detail: { message: 'Booking cancelled', type: 'success' } }))
        this.$emit('cancelled')
      } catch (err) {
        window.dispatchEvent(new CustomEvent('toast', { detail: { message: 'Failed to cancel: ' + (err.response?.data?.message || err.message), type: 'error' } }))
      }
    }
  }
}
</script>

<style scoped>
.booking-card { margin-bottom:12px }
.row { display:flex; justify-content:space-between; align-items:center }
.meta { color:#666; font-size:13px }
.actions { display:flex; gap:8px }
</style>
