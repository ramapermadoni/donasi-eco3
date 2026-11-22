<script setup>
import { useRoute, useRouter } from 'vue-router'
import { locale, lp, switchLocale } from '../i18n'
import NotifBell from './NotifBell.vue'
const props = defineProps({ logo: { type: String, default: '/logo-donasi.svg' } })
const route = useRoute(), router = useRouter()
const pick = (code) => { const to = switchLocale(code, route.path, location.search); if (to) router.push(to) }
</script>

<template>
  <header class="sticky top-0 z-40 bg-white" style="border-bottom: 1px solid #f0f0f0">
    <div class="max-w-[480px] mx-auto flex items-center justify-between px-4 h-14">
      <router-link class="flex items-center" :to="lp('/')"><img alt="donasi" width="171" height="36" class="h-7 w-auto" style="color: transparent" :src="props.logo" /></router-link>
      <div class="flex items-center gap-2">
        <div class="flex items-center rounded-xl overflow-hidden" style="border: 1.5px solid #e5e7eb" role="group" aria-label="Pilih bahasa">
          <button v-for="l in ['ID', 'EN']" :key="l" type="button" class="px-3 py-1.5 text-[13px] font-bold leading-none transition-colors"
            :style="locale === l.toLowerCase() ? 'background:var(--lime);color:#fff' : 'background:transparent;color:#9ca3af'" :aria-pressed="locale === l.toLowerCase()" @click="pick(l.toLowerCase())">{{ l }}</button>
        </div>
        <NotifBell />
      </div>
    </div>
  </header>
</template>
