<template>
  <div class="card">
    <h3>{{ title }}</h3>
    <p>{{ desc }}</p>
    <div class="price">{{ price }}</div>
    <slot />
  </div>
</template>

<script>
export default {
  props: { title: String, desc: String, price: String }
}
</script>

<style scoped>
.card { background:#fff; padding:18px; border-radius:8px; box-shadow:0 6px 18px rgba(0,0,0,0.06) }
.price { margin-top:8px; font-weight:600 }
</style>
