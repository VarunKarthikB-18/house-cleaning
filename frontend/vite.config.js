import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Vite config for Vue 3 app
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173
  }
})
