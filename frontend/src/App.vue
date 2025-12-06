<template>
  <div class="app-root">
    <HeaderBar />
    <main class="container">
      <router-view />
    </main>
    <FooterBar />
    <Toast />
  </div>
</template>

<script>
import HeaderBar from './components/HeaderBar.vue'
import FooterBar from './components/FooterBar.vue'
import Toast from './components/Toast.vue'
export default {
  components: { HeaderBar, FooterBar, Toast }
}
</script>

<style>
.app-root {
  background: var(--bg-solid);
  background-image: 
    radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.05) 0px, transparent 50%),
    radial-gradient(at 100% 0%, rgba(236, 72, 153, 0.05) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(59, 130, 246, 0.05) 0px, transparent 50%),
    radial-gradient(at 0% 100%, rgba(16, 185, 129, 0.05) 0px, transparent 50%);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  flex: 1;
  overflow-y: auto;
}

/* Ensure proper alignment for all pages */
main.container > * {
  width: 100%;
}

@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }
}
</style>
