<template>
  <section style="text-align: center">
    <h1 class="page-title">House Cleaning Made Easy</h1>
    <p class="lead">Book trusted cleaners quickly and easily. Reliable, professional service at your fingertips.</p>
    <div class="cta" style="display: flex; gap: 12px; justify-content: center">
      <router-link class="btn btn-primary" to="/register" style="display: inline-block; text-decoration: none">Get Started</router-link>
      <router-link class="btn" to="/login" style="display: inline-block; text-decoration: none">Sign In</router-link>
    </div>
  </section>
</template>

<script>
export default { }
</script>

<style scoped>
.page-title { font-size: 28px; margin-bottom: 8px }
.lead { color: #555 }
.cta { margin: 18px 0 }
</style>
