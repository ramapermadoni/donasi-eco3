import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'
import { tangkapPenanda } from './donate'

import { installApiShim } from './apiShim'
import { muatKontenServer } from './contentLoader'

if (import.meta.env.VITE_REAL_API !== '0') installApiShim()
tangkapPenanda()

// konten dari server (bila contoh sudah dibersihkan) harus siap sebelum halaman dibuat
const siap = import.meta.env.VITE_REAL_API !== '0' ? muatKontenServer() : Promise.resolve(false)
siap.finally(() => createApp(App).use(router).mount('#app'))
