<template>
  <div class="toast-wrapper" aria-live="polite">
    <div v-for="(t, i) in toasts" :key="t.id" :class="['toast', t.type]">{{ t.message }}</div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  setup() {
    const toasts = ref([])
    function pushToast(detail) {
      const id = Date.now() + Math.random()
      const item = { id, message: detail.message || detail, type: detail.type || 'info' }
      toasts.value.push(item)
      // auto remove after 3.5s
      setTimeout(() => {
        const idx = toasts.value.findIndex(t => t.id === id)
        if (idx !== -1) toasts.value.splice(idx, 1)
      }, 3500)
    }

    onMounted(() => {
      window.addEventListener('toast', (e) => pushToast(e.detail))
    })

    return { toasts }
  }
}
</script>

<style scoped>
.toast-wrapper { position: fixed; right: 20px; bottom: 20px; display:flex; flex-direction:column; gap:8px; z-index: 9999 }
.toast { background: rgba(0,0,0,0.8); color: #fff; padding: 10px 14px; border-radius: 8px; min-width: 180px; box-shadow: 0 6px 18px rgba(0,0,0,0.12) }
.toast.success { background: #16a34a }
.toast.error { background: #dc2626 }
.toast.info { background: #0ea5e9 }
</style>
