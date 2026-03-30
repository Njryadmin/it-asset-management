import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import App from './App.vue'
import router from './router'
import './styles/global.css'

const app = createApp(App)

// Global error handler - prevents blank pages on unhandled errors
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err, info)
  ElMessage.error('页面加载出错，请刷新重试')
}

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  // Ignore browser extension / aborted request errors
  if (event.reason?.message?.includes('message channel') ||
      event.reason?.name === 'AbortError') {
    event.preventDefault()
    return
  }
  console.error('Unhandled rejection:', event.reason)
})

// Register Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')
