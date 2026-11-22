<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Icon from './Icon.vue'
import { t, lp, stripLocale } from '../i18n'
const props = defineProps({ hideTabs: Boolean, hideFab: Boolean })
// sedekah.id hanya menampilkan video mini di beranda dan detail campaign
const route = useRoute()
const path = computed(() => stripLocale(route.path))
// Di beranda, tombol Sedekah membuka menu program (HomePopupMenu) alih-alih navigasi; di halaman lain tetap ke "/".
const onHome = (e) => { if (path.value === '/') { e.preventDefault(); window.dispatchEvent(new CustomEvent('dtp:home-popup')) } }
const showFab = computed(() => !props.hideFab && (path.value === '/' || path.value.startsWith('/campaigns/')))
// video mini yang diputar otomatis (sama seperti sedekah.id; di Frappe ambil dari video terbaru)
const FAB_VIDEO = 'https://sedekah.id/api/media/videos/2026/10/56f478f1-132a-4662-a736-95d2ff3ed323.mp4'
const internal = ['/', '/akun', '/penyaluran', '/laporan', '/teman']
const props_ = (h) => (internal.includes(h) ? { to: lp(h) } : { href: lp(h) })
const on = (h) => (h === '/' ? path.value === '/' : path.value.startsWith(h))
const left = [{ k: 'penyaluran', i: 'mapPin', h: '/penyaluran' }, { k: 'laporan', i: 'history', h: '/laporan' }]
const right = [{ k: 'teman', i: 'users', h: '/teman' }, { k: 'akun', i: 'circleUser', h: '/akun' }]
</script>

<template>
  <div>
    <div v-if="showFab" class="fixed left-1/2 -translate-x-1/2 w-full max-w-[448px] z-40 px-3 pointer-events-none bottom-[calc(11rem+env(safe-area-inset-bottom))]">
      <div class="flex justify-end">
        <router-link :to="lp('/video')" aria-label="Video donasi" class="pointer-events-auto block relative overflow-hidden rounded-xl transition-transform active:scale-95 hover:scale-105"
          style="width: 92px; height: 156px; box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3); border: 2px solid white; background: #000">
          <video :src="FAB_VIDEO" class="w-full h-full object-cover" autoplay muted loop playsinline preload="metadata"></video>
        </router-link>
      </div>
    </div>
    <nav v-if="!hideTabs" class="fixed bottom-0 left-0 right-0 z-50 px-2 pb-3 pt-2">
      <div class="max-w-[448px] mx-auto relative">
        <div class="relative backdrop-blur-xl bg-white/80 rounded-3xl shadow-2xl overflow-visible"
          style="box-shadow: 0 8px 32px color-mix(in srgb, var(--lime) 15%, transparent), 0 2px 8px rgba(0, 0, 0, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.8)">
          <div class="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-white/60 to-transparent"></div>
          <div class="absolute inset-0 bg-gradient-to-b from-white/40 via-transparent to-black/5 pointer-events-none"></div>
          <div class="grid grid-cols-5 h-16 relative z-10">
            <component :is="internal.includes(it.h) ? 'router-link' : 'a'" v-for="it in left" :key="it.k" v-bind="props_(it.h)"
              class="flex flex-col items-center justify-center gap-1 transition-all relative" :class="on(it.h) ? 'text-[color:var(--lime-text)]' : 'text-gray-500 hover:text-[color:var(--lime-text)]'">
              <Icon :name="it.i" class="w-6 h-6 transition-all relative z-10" :class="{ 'scale-110': on(it.h) }" :stroke-width="on(it.h) ? 2.5 : 2" />
              <span class="text-xs transition-all relative z-10" :style="{ fontWeight: on(it.h) ? 600 : 400 }">{{ t(`nav.${it.k}`) }}</span>
            </component>
            <router-link class="relative flex flex-col items-center justify-end gap-1 pb-1" :to="lp('/')" @click.capture="onHome">
              <div class="absolute -top-6 left-1/2 -translate-x-1/2 z-30">
                <div class="w-14 h-14 rounded-full flex items-center justify-center shadow-xl border-4 border-white relative z-30 transition-all bg-gradient-to-br"
                  :class="on('/') ? 'from-[color:var(--lime)] to-[color:var(--lime-dark)]' : 'from-[color:color-mix(in_srgb,var(--lime)_80%,transparent)] to-[color:color-mix(in_srgb,var(--lime-dark)_80%,transparent)]'"
                  style="box-shadow: 0 8px 24px color-mix(in srgb, var(--lime) 40%, transparent), 0 4px 8px rgba(0, 0, 0, 0.2)"><Icon name="house" class="w-7 h-7 text-white" /></div>
                <div class="absolute inset-0 w-14 h-14 rounded-full bg-[color:var(--lime-dark)] opacity-20 blur-lg z-20" style="animation: bnavPulse 2s ease-in-out infinite"></div>
              </div>
              <span class="text-xs text-[color:var(--lime-text)] relative z-10" style="font-weight: 600">{{ t('nav.sedekah') }}</span>
            </router-link>
            <component :is="internal.includes(it.h) ? 'router-link' : 'a'" v-for="it in right" :key="it.k" v-bind="props_(it.h)"
              class="flex flex-col items-center justify-center gap-1 transition-all relative" :class="on(it.h) ? 'text-[color:var(--lime-text)]' : 'text-gray-500 hover:text-[color:var(--lime-text)]'">
              <Icon :name="it.i" class="w-6 h-6 transition-all relative z-10" :class="{ 'scale-110': on(it.h) }" :stroke-width="on(it.h) ? 2.5 : 2" />
              <span class="text-xs transition-all relative z-10" :style="{ fontWeight: on(it.h) ? 600 : 400 }">{{ t(`nav.${it.k}`) }}</span>
            </component>
          </div>
        </div>
      </div>
    </nav>
  </div>
</template>

<style>
@keyframes bnavPulse { 0%, 100% { transform: scale(1); opacity: 0.2; } 50% { transform: scale(1.1); opacity: 0.3; } }
</style>
