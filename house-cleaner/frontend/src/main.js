import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import * as auth from './services/auth'
import './styles/variables.css'
import './styles/base.css'
import './styles/layout.css'
import './styles/components.css'

const app = createApp(App)
app.use(router)

const token = auth.getToken()
if (token) {
  auth.getProfile().catch(() => {
    auth.clearToken()
  }).finally(() => {
    app.mount('#app')
  })
} else {
  app.mount('#app')
}
