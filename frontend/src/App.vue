<template>
  <div class="app-root">
    <HeaderBar />
    <main class="container">
      <router-view />
    </main>
    <Toast />
  </div>
</template>

<script>
import HeaderBar from './components/HeaderBar.vue'
import Toast from './components/Toast.vue'
export default {
  components: { HeaderBar, Toast }
}
</script>

<style>
.app-root { background: #ffffff; min-height: 100vh; }
.container { max-width: 1100px; margin: 32px auto; padding: 20px; }
</style>
