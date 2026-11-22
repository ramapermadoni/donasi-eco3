<script setup>
import { shareLink } from '../utils/share'
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { t, lp } from '../i18n'
import Icon from '../components/Icon.vue'
import BottomNav from '../components/BottomNav.vue'
import videos from '../data/videos.json'

// Replace with Frappe: list of videos {src, poster, caption, likes, comments, campaign}
const router = useRouter()
const route = useRoute()
const items = ref(videos.map((v) => ({ ...v, likes: +v.likes || 0, liked: false, saved: false, open: false })))
const muted = ref(true)
const progress = ref(0)
function onTime(i, e) { const el = e.currentTarget; if (!el.paused && el.duration) progress.value = el.currentTime / el.duration }
const root = ref(null)
const els = ref([])
let io = null

function playOnly(i) { els.value.forEach((v, n) => { if (!v) return; if (n === i) { v.muted = muted.value; v.play().catch(() => {}) } else v.pause() }) }
function toggleMute() { muted.value = !muted.value; els.value.forEach((v) => v && (v.muted = muted.value)) }
function like(v) { v.liked = !v.liked; v.likes += v.liked ? 1 : -1 }
async function share(v) {
  const url = location.origin + '/video#' + v.id
  await shareLink('donasi', url)
}
function tap(i) { const el = els.value[i]; el && (el.paused ? el.play().catch(() => {}) : el.pause()) }

onMounted(async () => {
  await nextTick()
  io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting && e.intersectionRatio > 0.6) playOnly(+e.target.dataset.i) }), { root: root.value, threshold: [0.6] })
  root.value.querySelectorAll('section').forEach((s) => io.observe(s))
  const q = String(route.query.v || '')
  const target = q && root.value.querySelector('#video-' + CSS.escape(q))
  if (target) root.value.scrollTop = target.offsetTop
})
onBeforeUnmount(() => { io && io.disconnect(); els.value.forEach((v) => v && v.pause()) })
</script>

<template>
  <div class="desktop-bg" aria-hidden="true"></div>
  <div class="vd">
    <div class="bg-black">
      <div ref="root" class="h-[100dvh] overflow-y-scroll snap-y snap-mandatory" style="scrollbar-width:none">
        <section v-for="(v, i) in items" :id="'video-' + v.id" :key="v.id" :data-i="i" class="relative h-[100dvh] snap-start flex items-center justify-center max-w-[480px] mx-auto">
          <div class="h-full w-full flex overflow-x-auto snap-x snap-mandatory" style="scrollbar-width:none;overscroll-behavior-x:contain">
            <div class="min-w-full h-full snap-center flex justify-center">
              <video :ref="(el) => (els[i] = el)" :src="v.src" :poster="v.poster || undefined" class="h-full w-full object-contain" style="object-position:center top" muted loop playsinline preload="metadata" @click="tap(i)" @timeupdate="onTime(i, $event)"></video>
            </div>
          </div>

          <div class="absolute right-3 bottom-32 flex flex-col items-center gap-5 z-10">
            <button class="flex flex-col items-center gap-1 text-white active:scale-90 transition-transform" @click="like(v)">
              <Icon name="heart" class="w-8 h-8 drop-shadow" :style="{ fill: v.liked ? '#ef4444' : 'rgba(0,0,0,0.3)', stroke: v.liked ? '#ef4444' : 'white' }" /><span class="text-xs font-semibold drop-shadow">{{ v.likes }}</span>
            </button>
            <button class="flex flex-col items-center gap-1 text-white active:scale-90 transition-transform">
              <Icon name="message" class="w-8 h-8 drop-shadow" style="fill:rgba(0,0,0,0.3);stroke:white" /><span class="text-xs font-semibold drop-shadow">{{ v.comments }}</span>
            </button>
            <button class="flex flex-col items-center gap-1 text-white active:scale-90 transition-transform" @click="v.saved = !v.saved">
              <Icon name="bookmark" class="w-8 h-8 drop-shadow" :style="{ fill: v.saved ? 'var(--lime)' : 'rgba(0,0,0,0.3)', stroke: v.saved ? 'var(--lime)' : 'white' }" /><span class="text-xs font-semibold drop-shadow">{{ t('video.save') }}</span>
            </button>
            <button class="flex flex-col items-center gap-1 text-white active:scale-90 transition-transform" @click="share(v)">
              <Icon name="share" class="w-8 h-8 drop-shadow" style="fill:rgba(0,0,0,0.3);stroke:white" /><span class="text-xs font-semibold drop-shadow">{{ t('video.share') }}</span>
            </button>
          </div>

          <button :aria-label="t('video.tapToUnmute')" class="absolute top-4 right-4 z-20 inline-flex items-center gap-1 px-2 py-1 bg-white active:scale-95 transition-transform" :class="{ 'animate-pulse': muted }" style="box-shadow:0 2px 10px rgba(0,0,0,0.3)" @click="toggleMute">
            <Icon :name="muted ? 'micOff' : 'mic'" style="width:13px;height:13px;stroke-width:2.5" :style="{ color: muted ? '#dc2626' : '#16a34a' }" />
            <span class="font-bold" :style="{ fontSize: '11px', color: muted ? '#dc2626' : '#16a34a' }">Audio: {{ muted ? 'OFF' : 'ON' }}</span>
          </button>

          <div class="absolute inset-x-0 bottom-24 z-10 text-white">
            <div class="pl-4 pr-20">
              <router-link v-if="v.campaignSlug" class="mb-3 inline-flex items-center gap-1.5 px-3 py-2 font-bold bg-white text-[#1a1a1a] active:scale-95 transition-transform" style="font-size:12px;box-shadow:0 2px 10px rgba(0,0,0,0.25);border-left:4px solid var(--lime)" :to="lp('/campaigns/' + v.campaignSlug)">
                <Icon name="shoppingBasket" class="w-4 h-4" style="color:#005399;stroke-width:2.5" /><span class="truncate max-w-[200px]">{{ v.campaignTitle || t('video.donate') }}</span>
              </router-link>
              <div class="flex items-center gap-2">
                <img src="https://sedekah.id/icons/video-avatar.png" alt="" class="w-9 h-9 rounded-full flex-shrink-0" style="border:2px solid white;background:#fff;box-shadow:0 2px 8px rgba(0,0,0,0.3)" />
                <p class="font-bold drop-shadow" style="font-size:15px">sedekah.id</p>
                <Icon name="badgeCheck" class="flex-shrink-0" style="width:18px;height:18px;fill:#3897f0;stroke:white" />
              </div>
              <p v-if="v.caption" class="drop-shadow mt-2 text-white/85" :class="{ 'line-clamp-2': !v.open }" style="font-size:12px;line-height:1.5;white-space:pre-line" @click="v.open = !v.open">{{ v.caption }}</p>
            </div>
          </div>
          <div class="absolute inset-x-0 bottom-0 h-56 pointer-events-none" style="background:linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.65) 100%)"></div>
        </section>
      </div>
      <div class="fixed left-1/2 -translate-x-1/2 w-full max-w-[480px] z-40 px-4 pointer-events-none" style="bottom:calc(5.5rem + env(safe-area-inset-bottom))">
        <div class="h-[3px] rounded-full overflow-hidden" style="background:rgba(255,255,255,0.25)"><div class="h-full" :style="{ width: Math.min(progress * 100, 100) + '%', background: 'var(--lime)' }"></div></div>
      </div>
    </div>
  </div>
  <BottomNav hide-fab />
</template>
