<template>
  <section>
    <h1 class="page-title">House Cleaning App</h1>
    <p class="lead">Book trusted cleaners quickly and easily.</p>
    <div class="cta">
      <router-link class="btn btn-primary" to="/register">Get Started</router-link>
      <router-link class="btn" to="/login">Sign In</router-link>
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
