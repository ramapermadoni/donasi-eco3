<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { t, lp, isEn } from '../i18n'
import AppHeader from '../components/AppHeader.vue'
import Icon from '../components/Icon.vue'
import BottomNav from '../components/BottomNav.vue'
import doas from '../data/doa.json'
import data from '../data/sedekah'

// Replace with Frappe: GET /api/doa?take=9&skip=N  and  POST /api/doa/<id>/amin (max 10 per donor/doa)
const router = useRouter()
const PAGE = 9
const MAX_AMIN = 10
const list = reactive(doas.map((d) => ({ ...d, mine: 0 })))
const shown = ref(PAGE)
const visible = computed(() => list.slice(0, shown.value))
const popup = ref(false)
let aminCount = 0

function sparkle(el) {
  const r = el.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2
  const ems = ['✨', '✨', '⭐', '🤲', '✨', '⭐']
  ems.forEach((em, i) => {
    const a = (2 * Math.PI * i) / ems.length + (Math.random() - 0.5) * 0.4, m = 28 + 22 * Math.random()
    const s = document.createElement('span')
    s.className = 'doa-sparkle'; s.textContent = em; s.style.left = x + 'px'; s.style.top = y + 'px'
    s.style.setProperty('--dx', Math.cos(a) * m + 'px'); s.style.setProperty('--dy', Math.sin(a) * m + 'px')
    document.body.appendChild(s); setTimeout(() => s.remove(), 800)
  })
}
function amin(d, n, ev) {
  if (d.mine >= MAX_AMIN) return
  d.mine++; d.amin++
  if (ev && ev.currentTarget) sparkle(ev.currentTarget)
  if (++aminCount === 1) setTimeout(() => (popup.value = true), 600) // invitation after first amin
}
function back() { window.history.length > 1 ? router.back() : router.push(lp('/')) }
// /en menampilkan format angka & waktu gaya Inggris (Rp2,000 · 3m ago)
const money = (v) => (isEn.value ? String(v).replace(/\./g, ',') : v)
const ago = (w) => (isEn.value ? String(w).replace(/^(\d+) mnt lalu$/, '$1m ago').replace(/^(\d+) jam lalu$/, '$1h ago').replace(/^(\d+) hari lalu$/, '$1d ago') : w)
const programs = data.campaigns.slice(0, 9)
</script>

<template>
  <div class="frame">
    <AppHeader />
    <main class="pb-28 max-w-[480px] mx-auto">
      <div class="flex items-center gap-3 px-4 py-3 sticky top-0 bg-white z-10 border-b border-gray-100">
        <a class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100" :aria-label="t('doa.back')" :href="lp('/')" @click.prevent="back"><Icon name="chevronLeft" class="w-5 h-5 text-gray-700" /></a>
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 rounded-lg flex items-center justify-center" style="background:var(--lime)"><Icon name="heart" class="w-3.5 h-3.5" style="fill:#fff;stroke:#fff" /></div>
          <span style="font-size:15px;font-weight:800;color:#1a1a1a">{{ t('doa.title') }}</span>
        </div>
      </div>

      <section class="px-4 pt-4">
        <div class="grid grid-cols-2 gap-3">
          <div v-for="(d, n) in visible" :key="n" class="rounded-2xl p-3.5 flex flex-col" style="background:linear-gradient(160deg, #ffffff 0%, #f0f6fc 100%);border:1px solid #c7dcf0;box-shadow:0 2px 12px color-mix(in srgb, var(--lime) 8%, transparent)">
            <Icon name="quote" class="w-4 h-4 mb-2" style="color:var(--lime);fill:var(--lime)" />
            <p class="flex-1" style="font-size:12px;line-height:1.5;color:#374151;display:-webkit-box;-webkit-line-clamp:5;-webkit-box-orient:vertical;overflow:hidden">{{ d.text }}</p>
            <div class="mt-2.5 pt-2.5 border-t border-gray-100">
              <p style="font-size:11px;font-weight:700;color:#1a1a1a" class="truncate">{{ d.name === 'Teman Sedekah' ? t('doa.anonymousDonor') : d.name }}</p>
              <div class="flex items-center justify-between mt-0.5">
                <span style="font-size:10px;font-weight:700;color:var(--lime-text)">{{ money(d.amount) }}</span>
                <span style="font-size:9px;color:#9ca3af">{{ ago(d.when) }}</span>
              </div>
              <button type="button" :disabled="d.mine >= MAX_AMIN" :aria-label="d.mine >= MAX_AMIN ? t('doa.aminCappedAria') : t('doa.aminAria')" class="amin-btn mt-2 w-full flex items-center justify-center gap-1.5 rounded-lg py-1.5 px-2 transition-all relative overflow-visible"
                :style="{ background: d.mine >= MAX_AMIN ? '#f3f4f6' : 'linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%)', border: d.mine >= MAX_AMIN ? '1px solid #e5e7eb' : '1px solid var(--lime-dark)', cursor: d.mine >= MAX_AMIN ? 'not-allowed' : 'pointer', opacity: d.mine >= MAX_AMIN ? 0.7 : 1 }" @click="amin(d, n, $event)">
                <span style="font-size:13px;line-height:1">🤲</span>
                <span :style="{ fontSize: '10px', fontWeight: 700, color: d.mine >= MAX_AMIN ? '#9ca3af' : '#1a1a1a' }">{{ d.mine >= MAX_AMIN ? t('doa.aminDone') : t('doa.amin') }} · {{ d.amin }}</span>
              </button>
            </div>
          </div>
        </div>

        <button v-if="shown < list.length" class="mt-5 w-full py-3 rounded-xl border-2 border-dashed transition-all flex items-center justify-center gap-2 disabled:opacity-50" style="border-color:var(--lime);background:color-mix(in srgb, var(--lime) 5%, transparent);font-size:13px;font-weight:700;color:var(--lime-text)" @click="shown += PAGE">{{ t('doa.more') }}</button>
        <p v-else-if="list.length > PAGE" class="mt-4 text-center" style="font-size:11px;color:#9ca3af">{{ t('doa.allShown') }}</p>
      </section>

      <section class="px-4 pt-8">
        <div class="flex items-center gap-2 mb-3">
          <div class="w-7 h-7 rounded-lg flex items-center justify-center" style="background:linear-gradient(135deg, var(--lime), var(--lime-dark))"><Icon name="target" class="w-3.5 h-3.5" style="color:#fff;stroke-width:2.5" /></div>
          <span style="font-size:15px;font-weight:800;color:#1a1a1a">{{ t('doa.waysToGive') }}</span>
        </div>
        <p class="mb-3" style="font-size:11px;color:#9ca3af">{{ t('doa.waysToGiveSub') }}</p>
        <div class="grid grid-cols-2 gap-3">
          <router-link v-for="c in programs" :key="c.slug" :to="lp('/campaigns/' + c.slug)" class="block rounded-2xl overflow-hidden active:scale-[0.98] transition-transform" style="background:white;border:1px solid #f3f4f6;box-shadow:0 2px 12px rgba(0, 0, 0, 0.04)">
            <div class="relative w-full" style="aspect-ratio:4/3;background:#f3f4f6">
              <img v-if="c.image" :src="c.image" :alt="c.title" class="absolute inset-0 w-full h-full object-cover" />
              <div v-else class="absolute inset-0" style="background:linear-gradient(135deg, var(--lime), var(--lime-dark))"></div>
              <div v-if="c.category" class="absolute top-2 left-2 px-2 py-0.5 rounded-full" style="background:rgba(255,255,255,0.92);font-size:9px;font-weight:700;color:var(--lime-text)">{{ c.category }}</div>
            </div>
            <div class="p-2.5">
              <h3 style="font-size:12px;font-weight:700;color:#1a1a1a;line-height:1.35;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:32px">{{ c.title }}</h3>
              <div class="mt-2">
                <div class="w-full rounded-full overflow-hidden" style="height:4px;background:#f3f4f6"><div class="h-full rounded-full" :style="{ width: Math.min(100, c.percent || 0) + '%', background: 'linear-gradient(90deg, var(--lime), var(--lime-dark))' }"></div></div>
                <div class="flex items-center justify-between mt-1.5">
                  <span style="font-size:10px;font-weight:700;color:var(--lime-text)">{{ (c.raised || '').replace('Rp ', 'Rp') }}</span>
                  <span style="font-size:9px;color:#9ca3af">{{ c.percent || 0 }}%</span>
                </div>
              </div>
            </div>
          </router-link>
        </div>
        <div class="mt-4 text-center"><router-link :to="lp('/public/campaigns')" class="inline-flex items-center gap-1 hover:opacity-70" style="font-size:12px;font-weight:700;color:var(--lime-text)">{{ t('doa.viewAllPrograms') }}</router-link></div>
      </section>
    </main>

    <!-- invitation popup after the first "Aminkan" -->
    <transition name="fade">
      <div v-if="popup" class="pop-back" role="dialog" :aria-label="t('doa.popupAria')" @click.self="popup = false">
        <div class="pop">
          <button class="x" :aria-label="t('doa.close')" @click="popup = false"><Icon name="x" /></button>
          <p class="eb">{{ t('doa.eyebrow') }}</p>
          <h3>{{ t('doa.popupHeadline') }}</h3>
          <p class="sub">{{ t('doa.popupSubline') }}</p>
          <p class="hd">“{{ t('doa.hadith') }}”</p>
          <p class="hs">{{ t('doa.hadithSource') }}</p>
          <router-link :to="lp('/video')" class="vid">
            <span class="pl"><Icon name="play" /></span>
            <span><b>{{ t('doa.videoHeadline') }}</b><small>{{ t('doa.videoCta') }}</small></span>
          </router-link>
          <button class="skip" @click="popup = false" :aria-label="t('doa.skipAria')">{{ t('doa.skipAria') }}</button>
        </div>
      </div>
    </transition>
  </div>
  <BottomNav />
</template>

<style>
.amin-btn:not(:disabled):active { transform: scale(0.94); }
.amin-btn:not(:disabled):hover { box-shadow: 0 4px 12px color-mix(in srgb, var(--lime) 40%, transparent); }
.doa-sparkle { position: fixed; pointer-events: none; z-index: 9999; font-size: 16px; will-change: transform, opacity; animation: doa-sparkle-fly 700ms ease-out forwards; }
@keyframes doa-sparkle-fly {
  0% { opacity: 1; transform: translate(-50%, -50%) scale(0.4) rotate(0deg); }
  30% { opacity: 1; transform: translate(calc(-50% + var(--dx) * 0.5), calc(-50% + var(--dy) * 0.5)) scale(1.1) rotate(90deg); }
  100% { opacity: 0; transform: translate(calc(-50% + var(--dx)), calc(-50% + var(--dy) - 12px)) scale(0.6) rotate(180deg); }
}
</style>
