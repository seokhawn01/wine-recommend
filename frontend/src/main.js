import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import './assets/index.css'
import { useAuthStore } from '@/stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Supabase 세션 복원 후 앱 마운트
const authStore = useAuthStore()
authStore.init().then(() => {
  app.mount('#app')
})
