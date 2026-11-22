<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { t, lp } from '../i18n'

const router = useRouter()
const data = ref(null)
const open = ref(false)

function toggle() {
  open.value = data.value ? !open.value : open.value
}
function close() {
  open.value = false
}
function onKey(e) {
  if (e.key === 'Escape') close()
}

let dead = false
onMounted(() => {
  fetch('/api/home/popup-menu')
    .then((r) => r.json())
    .then((d) => {
      if (!dead && d && d.enabled && d.items && d.items.length) data.value = d
    })
    .catch(() => {})
  window.addEventListener('dtp:home-popup', toggle)
})
onBeforeUnmount(() => {
  dead = true
  window.removeEventListener('dtp:home-popup', toggle)
  window.removeEventListener('keydown', onKey)
})
watch(open, (v) => {
  if (v) window.addEventListener('keydown', onKey)
  else window.removeEventListener('keydown', onKey)
})

// Normalisasi tautan: internal yang ada di router -> router-link; selain itu ke sedekah.id.
function resolveLink(link) {
  let l = String(link || '')
  if (l.startsWith('https://sedekah.id')) l = l.slice('https://sedekah.id'.length) || '/'
  if (l.startsWith('/') && !l.startsWith('//')) {
    try {
      const path = l.split(/[?#]/)[0]
      if (router.resolve(path).matched.length) return { internal: true, to: lp(l) }
    } catch (e) {}
    return { internal: false, href: 'https://sedekah.id' + l }
  }
  return { internal: false, href: l }
}
const isImg = (i) => typeof i === 'string' && (i.startsWith('http') || i.startsWith('/'))

const cardCls =
  'rounded-2xl border border-gray-100 bg-gray-50 hover:bg-[color-mix(in_srgb,var(--lime)_8%,white)] hover:border-[color:var(--lime)] transition-colors px-3.5 py-3 flex items-center gap-3'
</script>

<template>
  <div
    v-if="data && open"
    class="fixed inset-0 z-[70] flex items-end sm:items-center justify-center"
    style="background: rgba(8, 15, 44, 0.6); backdrop-filter: blur(2px)"
    role="dialog"
    aria-modal="true"
    :aria-label="data.heading ?? ''"
    @click="close"
  >
    <div
      class="w-full sm:w-auto sm:min-w-[380px] sm:max-w-md bg-white rounded-t-3xl sm:rounded-3xl p-5 pb-24 sm:p-6 shadow-2xl animate-[popupIn_.25s_ease-out]"
      @click.stop
    >
      <div class="flex items-start justify-between gap-3">
        <h2 class="text-base font-bold text-gray-900 leading-snug">{{ data.heading ?? '' }}</h2>
        <button
          type="button"
          :aria-label="t('home.close')"
          class="shrink-0 w-8 h-8 rounded-full bg-gray-100 text-gray-500 flex items-center justify-center text-lg leading-none"
          @click="close"
        >×</button>
      </div>
      <div class="mt-4 flex flex-col gap-2.5">
        <template v-for="it in data.items" :key="it.id">
          <router-link v-if="resolveLink(it.link).internal" :to="resolveLink(it.link).to" :class="cardCls" @click="close">
            <span class="shrink-0 w-11 h-11 rounded-xl bg-white border border-gray-100 flex items-center justify-center overflow-hidden">
              <img v-if="isImg(it.icon)" :src="it.icon" alt="" class="w-full h-full object-contain p-1.5" loading="lazy" />
              <span v-else class="text-2xl leading-none" aria-hidden="true">{{ it.icon }}</span>
            </span>
            <span class="text-sm font-semibold text-gray-800 leading-snug flex-1">{{ it.title }}</span>
            <span class="shrink-0 text-gray-300" aria-hidden="true">›</span>
          </router-link>
          <a v-else :href="resolveLink(it.link).href" :class="cardCls" @click="close">
            <span class="shrink-0 w-11 h-11 rounded-xl bg-white border border-gray-100 flex items-center justify-center overflow-hidden">
              <img v-if="isImg(it.icon)" :src="it.icon" alt="" class="w-full h-full object-contain p-1.5" loading="lazy" />
              <span v-else class="text-2xl leading-none" aria-hidden="true">{{ it.icon }}</span>
            </span>
            <span class="text-sm font-semibold text-gray-800 leading-snug flex-1">{{ it.title }}</span>
            <span class="shrink-0 text-gray-300" aria-hidden="true">›</span>
          </a>
        </template>
      </div>
    </div>
  </div>
</template>

<style>
@keyframes popupIn {
  from { transform: translateY(24px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
</style>
