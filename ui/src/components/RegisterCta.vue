<script setup>
import { lsGet, lsSet } from '../utils/storage'
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { auth } from '../auth'
import Icon from './Icon.vue'
import { t, lp } from '../i18n'
// Ajakan daftar untuk pengunjung yang belum login (muncul 1,5 dtk setelah buka beranda; seperti sedekah.id)
const KEY = 'sedekah_register_cta_dismissed_v1'
const mounted = ref(false)
const shown = ref(false)
let timer = null
onMounted(() => {
  if (lsGet(KEY) === '1') return
  mounted.value = true
  timer = setTimeout(() => { shown.value = true }, 1500)
})
onBeforeUnmount(() => clearTimeout(timer))
function close() {
  lsSet(KEY, '1')
  shown.value = false
  setTimeout(() => { mounted.value = false }, 300)
}
</script>

<template>
  <div v-if="mounted && !auth.user" class="fixed left-0 right-0 z-40 px-4 pointer-events-none"
    :style="{ bottom: '96px', transition: 'transform 320ms cubic-bezier(0.16, 1, 0.3, 1), opacity 320ms ease', transform: shown ? 'translateY(0)' : 'translateY(120%)', opacity: shown ? 1 : 0 }">
    <div class="max-w-[448px] mx-auto pointer-events-auto relative">
      <!-- tombol tutup: lencana kecil di sudut kanan atas kartu, tidak menumpuk isi -->
      <button :aria-label="t('home.close')" class="absolute -top-2.5 -right-1 z-10 w-7 h-7 rounded-full bg-white flex items-center justify-center transition-all hover:bg-gray-50 active:scale-90"
        style="box-shadow: 0 2px 8px rgba(0, 0, 0, 0.18); border: 1px solid #f0f6fc" @click="close"><Icon name="x" class="w-3.5 h-3.5 text-gray-500" /></button>
      <div class="rounded-2xl bg-white relative" style="box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.06); border: 1px solid color-mix(in srgb, var(--lime) 35%, transparent); background: linear-gradient(135deg, #f0f6fc 0%, #ffffff 60%)">
        <div class="flex items-center gap-3 pl-3.5 pr-3 py-3">
          <div class="w-11 h-11 rounded-2xl flex items-center justify-center flex-shrink-0" style="background: linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%); box-shadow: 0 4px 12px color-mix(in srgb, var(--lime) 40%, transparent)"><Icon name="userPlus" class="w-5 h-5 text-white" /></div>
          <div class="flex-1 min-w-0">
            <p class="text-[13.5px] font-extrabold text-gray-900 leading-tight">{{ t('home.registerTitle') }}</p>
            <p class="text-[11.5px] text-gray-500 leading-snug mt-0.5">{{ t('home.registerSubtitle') }}</p>
          </div>
          <router-link :to="lp('/auth/register')" class="flex items-center gap-1 pl-3.5 pr-3 py-2 rounded-xl text-[12.5px] font-bold transition-all active:scale-[0.96] flex-shrink-0"
            style="background: linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%); color: #fff; box-shadow: 0 4px 12px color-mix(in srgb, var(--lime) 35%, transparent)">{{ t('home.registerCta') }}<Icon name="arrowRight" class="w-3.5 h-3.5" /></router-link>
        </div>
      </div>
    </div>
  </div>
</template>
