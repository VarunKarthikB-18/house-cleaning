<template>
  <div>
    <h2>Your Bookings</h2>
    <div v-if="loading">Loading...</div>
    <div v-else>
      <div v-if="bookings.length === 0" class="empty">No bookings yet. <router-link to="/bookings/new">Book now</router-link></div>
      <div v-if="bookings.length > 0">
        <BookingCard v-for="b in bookings" :key="b.id" :booking="b" @cancelled="fetchBookings" />
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
        bookings.value = res.data || []
      } catch (err) {
        alert('Failed to load bookings: ' + (err.response?.data?.message || err.message))
      } finally { loading.value = false }
    }

    onMounted(fetchBookings)
    return { bookings, loading, fetchBookings }
  }
}
</script>

<style scoped>
.empty { color: #666; margin: 12px 0 }
</style>
