<template>
  <header class="header">
    <div class="left">
      <span style="font-weight: 600; font-size: 18px;">🏠 House Cleaner</span>
    </div>
    <nav class="nav">
      <router-link v-if="!isAuthed" to="/login">Login</router-link>
      <router-link v-if="!isAuthed" to="/register">Register</router-link>
      <router-link v-if="isAuthed" to="/dashboard">Dashboard</router-link>
      <button v-if="isAuthed" class="btn-link" @click="doLogout">Logout</button>
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
.header { display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-bottom:1px solid #eee }
.left { display:flex; align-items:center; gap:12px }
.nav { display:flex; gap:12px; align-items:center }
.btn-link { background:none; border:0; color:#007bff; cursor:pointer }
</style>
