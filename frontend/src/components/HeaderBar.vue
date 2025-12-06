<template>
  <header class="header">
    <div class="left">
      <router-link to="/" style="text-decoration: none; color: inherit;">
        <span style="font-weight: 600; font-size: 18px;">🏠 House Cleaner</span>
      </router-link>
    </div>
    <nav class="nav">
      <template v-if="!isAuthed">
        <router-link to="/login">Login</router-link>
      </template>
      <template v-if="isAuthed">
        <router-link to="/bookings">My Bookings</router-link>
        <router-link to="/reviews">Reviews</router-link>
        <button class="btn-link logout-btn" @click="doLogout">Logout</button>
      </template>
    </nav>
  </header>
</template>

<script>
import { computed } from 'vue'
import * as auth from '../services/auth'

export default {
  setup() {
    const isAuthed = computed(() => !!auth.getToken() && !!auth.currentUser.value)
    function doLogout() { auth.logout() }
    return { isAuthed, doLogout }
  }
}
</script>

<style scoped>
.logout-btn {
  background: rgba(239, 68, 68, 0.2) !important;
  color: #ffffff !important;
  border: 1px solid rgba(239, 68, 68, 0.5) !important;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.4) !important;
  border-color: rgba(239, 68, 68, 0.8) !important;
  transform: translateY(-2px);
}
</style>
