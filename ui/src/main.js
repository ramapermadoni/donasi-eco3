import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'
import { tangkapPenanda } from './donate'

import { installApiShim } from './apiShim'

if (import.meta.env.VITE_REAL_API !== '0') installApiShim()
tangkapPenanda()

createApp(App).use(router).mount('#app')
