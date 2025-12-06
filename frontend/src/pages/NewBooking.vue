<template>
  <div>
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

<style scoped></style>
