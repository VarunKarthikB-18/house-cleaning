<template>
  <div class="new-booking-page">
    <h2>New Booking</h2>
    <BookingForm @created="onCreated" />
  </div>
</template>

<script>
import BookingForm from '../components/BookingForm.vue'
import { useRouter } from 'vue-router'

export default {
  components: { BookingForm },
  setup() {
    const router = useRouter()
    function onCreated() { router.push({ name: 'Bookings' }) }
    return { onCreated }
  }
}
</script>

<style scoped>
.new-booking-page {
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
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
</style>
