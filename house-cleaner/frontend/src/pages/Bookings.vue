<template>
  <div class="bookings-page">
    <h2>Your Bookings</h2>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else>
      <div v-if="bookings.length===0" class="empty">No bookings yet.</div>
      <div v-if="bookings.length > 0" class="bookings-list">
        <BookingCard v-for="b in bookings" :key="b.id" :booking="b" @cancelled="fetchBookings" />
      </div>
      <div class="actions">
        <router-link class="btn btn-primary" to="/bookings/new">New Booking</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import BookingCard from '../components/BookingCard.vue'

export default {
  components: { BookingCard },
  setup() {
    const bookings = ref([])
    const loading = ref(true)

    async function fetchBookings() {
      loading.value = true
      try {
        const res = await api.get('/bookings')
        bookings.value = res.data?.data || res.data?.bookings || []
      } catch (err) {
        const errorMsg = err.response?.data?.msg || err.response?.data?.message || err.message
        window.dispatchEvent(new CustomEvent('toast', { 
          detail: { message: 'Failed to load bookings: ' + errorMsg, type: 'error' } 
        }))
      } finally { loading.value = false }
    }

    onMounted(fetchBookings)
    return { bookings, loading, fetchBookings }
  }
}
</script>

<style scoped>
.bookings-page {
  width: 100%;
  max-width: 100%;
}

h2 {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 2rem;
  text-align: center;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.empty {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(236, 72, 153, 0.05) 100%);
  color: #6b7280 !important;
  padding: 3rem 2rem;
  margin: 2rem 0;
  text-align: center;
  border-radius: var(--radius-lg);
  border: 2px dashed var(--border);
  font-size: 1.1rem;
}

.bookings-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

.actions {
  text-align: center;
  margin-top: 2rem;
}

.btn-primary {
  margin-top: 1rem;
  width: auto;
  min-width: 150px;
}
</style>
