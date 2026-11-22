<script setup>
// Popup "Aamiin-kan doa mereka" + "Video Kebaikan Hari Ini" — tiruan DoaAminPopup sedekah.id (dua mode, satu kerangka).
// Data disediakan pengendali (HomePopups); komponen ini hanya mengirim POST /api/doa/:id/amin (fire-and-forget).
import { lsGet, lsSet } from '../utils/storage'
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import Icon from './Icon.vue'
import { t, lp } from '../i18n'
import { timeAgo } from '../utils/time'
import { maskName, initial } from '../utils/text'

const props = defineProps({ doas: { type: Array, default: () => [] }, video: { type: Object, default: null } })
const emit = defineEmits(['close'])
const router = useRouter()

const AMIN_KEY = 'dtp_doa_amins'
const COLORS = ['#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6', '#ef4444']
const GRAD = 'linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%)'
const GLOW = '0 4px 12px color-mix(in srgb, var(--lime) 30%, transparent)'

const list = ref(props.doas.slice(0, 3).map((d) => ({ ...d })))
const idx = ref(0)
const busy = ref(false)
const kind = ref('amin')
const mobile = ref(false)
const sheet = ref(null)
const overlay = ref(null)
const dragY = ref(0)
const dragging = ref(false)
let timer = null
let closing = false
let pendingKind = 'amin'
let mq = null
const onMq = () => { mobile.value = mq.matches }

const cur = computed(() => list.value[idx.value])
const mask = (n) => maskName(n) || t('doa.anonymousDonor')
const donor = (d) => (d.is_anonymous ? t('doa.anonymousDonor') : mask(d.donor_name))
const color = (id) => { let t = 0; const s = String(id); for (let i = 0; i < s.length; i++) t = (31 * t + s.charCodeAt(i)) >>> 0; return COLORS[t % COLORS.length] }
const dotBg = (a) => (a < idx.value ? 'var(--lime-dark)' : a === idx.value ? 'var(--lime)' : '#e5e7eb')

function close() {
  if (closing) return
  closing = true
  const el = sheet.value
  overlay.value?.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 200, fill: 'forwards' })
  const kf = mobile.value ? [{ transform: `translateY(${dragY.value}px)` }, { transform: 'translateY(100%)' }]
    : [{ transform: 'translateY(0) scale(1)', opacity: 1 }, { transform: 'translateY(28px) scale(.96)', opacity: 0 }]
  if (el) { const a = el.animate(kf, { duration: 220, easing: 'ease-in', fill: 'forwards' }); a.onfinish = () => emit('close') } else emit('close')
}

function onKey(e) { if (e.key === 'Escape') close() }

onMounted(() => {
  mq = window.matchMedia('(max-width: 639px)')
  onMq()
  mq.addEventListener('change', onMq)
  window.addEventListener('keydown', onKey)
  overlay.value?.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 200, fill: 'backwards' })
  const kf = mobile.value ? [{ transform: 'translateY(100%)' }, { transform: 'translateY(0)' }]
    : [{ transform: 'translateY(28px) scale(.94)', opacity: 0 }, { transform: 'translateY(0) scale(1)', opacity: 1 }]
  sheet.value?.animate(kf, { duration: mobile.value ? 380 : 320, easing: 'cubic-bezier(0.22,1,0.36,1)', fill: 'backwards' })
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  mq?.removeEventListener('change', onMq)
  clearTimeout(timer)
})
watch(idx, () => { busy.value = false })

// seret ke bawah (bottom-sheet)
let startY = 0, lastY = 0, lastT = 0, vel = 0
function dStart(e) {
  if (!mobile.value || (e.pointerType === 'mouse' && e.button !== 0)) return
  if (e.target.closest('button,a,video')) return
  dragging.value = true; startY = lastY = e.clientY; lastT = performance.now(); vel = 0
  try { e.currentTarget.setPointerCapture(e.pointerId) } catch { /* abaikan */ }
}
function dMove(e) {
  if (!dragging.value) return
  const dy = e.clientY - startY
  const now = performance.now()
  vel = ((e.clientY - lastY) / Math.max(1, now - lastT)) * 1000
  lastY = e.clientY; lastT = now
  dragY.value = dy < 0 ? 0 : dy * 0.7 // elastis ke bawah, tertahan ke atas
}
function dEnd() {
  if (!dragging.value) return
  dragging.value = false
  const off = (lastY - startY)
  if (off > 120 || vel > 600) close()
  else { const from = dragY.value; dragY.value = 0; sheet.value?.animate([{ transform: `translateY(${from}px)` }, { transform: 'translateY(0)' }], { duration: 250, easing: 'cubic-bezier(0.22,1,0.36,1)' }) }
}

function sparkle(btn) {
  const r = btn.getBoundingClientRect()
  const x = r.left + r.width / 2, y = r.top + r.height / 2
  const em = ['✨', '✨', '⭐', '🤲', '✨', '⭐']
  em.forEach((t, i) => {
    const a = (2 * Math.PI * i) / em.length + (Math.random() - 0.5) * 0.4
    const d = 30 + 24 * Math.random()
    const s = document.createElement('span')
    s.className = 'doa-sparkle'
    s.textContent = t
    s.style.left = x + 'px'; s.style.top = y + 'px'
    s.style.setProperty('--dx', Math.cos(a) * d + 'px')
    s.style.setProperty('--dy', Math.sin(a) * d + 'px')
    document.body.appendChild(s)
    setTimeout(() => s.remove(), 800)
  })
}
function next(k) { pendingKind = k; idx.value++ }
function skip(d) { if (busy.value || d !== cur.value) return; busy.value = true; next('skip') }
function aamiin(d, e) {
  if (busy.value || !d || d !== cur.value) return
  busy.value = true
  let m = {}
  try { m = JSON.parse(lsGet(AMIN_KEY, '{}')) } catch { m = {} }
  m[d.id] = (m[d.id] ?? 0) + 1
  lsSet(AMIN_KEY, JSON.stringify(m))
  d.amin_count = (d.amin_count || 0) + 1
  fetch(`/api/doa/${d.id}/amin`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ delta: 1 }) }).catch(() => {})
  sparkle(e.currentTarget)
  timer = setTimeout(() => next('amin'), 320)
}
function afterLeave() { if (idx.value >= list.value.length) close() }

function cardEnter(el, done) {
  const a = el.animate([{ opacity: 0, transform: 'translateY(24px) scale(.97)' }, { opacity: 1, transform: 'none' }], { duration: 280, easing: 'ease-out' })
  a.onfinish = done
}
function cardLeave(el, done) {
  // seperti asli: jenis keluar dibaca dari aksi sebelumnya (awalnya 'amin')
  const amin = kind.value === 'amin'
  kind.value = pendingKind
  const a = el.animate(
    amin ? [{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'translateY(-360px) scale(.82)' }]
      : [{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'translateY(22px) scale(.97)' }],
    { duration: amin ? 420 : 200, easing: amin ? 'ease-in' : 'ease', fill: 'forwards' })
  a.onfinish = done
}

function watchVideo(e) {
  if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return
  e.preventDefault()
  emit('close'); router.push(lp(`/video?v=${props.video.id}`))
}
</script>

<template>
  <div ref="overlay" class="fixed inset-0 z-[70] flex justify-center" :class="mobile ? 'items-end' : 'items-center p-4'"
    style="background: rgba(8,15,44,0.6); backdrop-filter: blur(2px)" role="dialog" aria-modal="true" :aria-label="t('doa.popupAria')" @click="close">
    <div ref="sheet" class="relative bg-white" :class="mobile ? 'w-full rounded-t-[26px] px-5' : 'w-full max-w-[380px] rounded-[26px] px-5 pb-5'"
      :style="{
        paddingTop: mobile ? '22px' : '46px',
        boxShadow: mobile ? '0 -12px 40px rgba(8,15,44,0.28)' : '0 20px 60px rgba(8,15,44,0.4)',
        ...(mobile ? { paddingBottom: 'calc(env(safe-area-inset-bottom, 0px) + 18px)', touchAction: 'pan-x', transform: dragY ? `translateY(${dragY}px)` : undefined } : {}),
      }"
      @click.stop @pointerdown="dStart" @pointermove="dMove" @pointerup="dEnd" @pointercancel="dEnd">
      <span v-if="mobile" aria-hidden="true" class="absolute left-1/2 -translate-x-1/2" style="top:8px;width:40px;height:4px;border-radius:999px;background:#e5e7eb" />
      <div v-else class="absolute left-1/2 -translate-x-1/2 flex items-center justify-center rounded-full" aria-hidden="true"
        :style="{ top: '-28px', width: '56px', height: '56px', background: GRAD, border: '4px solid white', boxShadow: '0 6px 18px color-mix(in srgb, var(--lime) 45%, transparent)', fontSize: '26px' }">{{ video ? '🎬' : '🤲' }}</div>

      <button type="button" :aria-label="t('doa.close')" class="absolute right-3 top-3 w-8 h-8 rounded-full flex items-center justify-center hover:bg-gray-100 transition-colors" style="color:#9ca3af" @click="close"><Icon name="x" class="w-4 h-4" /></button>

      <template v-if="video">
        <p class="text-center" style="font-size:10px;font-weight:800;letter-spacing:.16em;color:var(--lime-dark);text-transform:uppercase">{{ t('doa.eyebrow') }}</p>
        <h2 class="text-center mt-1.5" style="font-size:17px;font-weight:900;color:#1a1a1a;letter-spacing:-.01em">{{ t('doa.videoHeadline') }}</h2>
        <div class="mt-4 rounded-2xl overflow-hidden bg-black" style="aspect-ratio:3 / 4">
          <video :src="video.videoUrl" :poster="video.thumbnailUrl || undefined" class="w-full h-full object-cover" autoplay muted loop playsinline preload="metadata" />
        </div>
        <a :href="lp(`/video?v=${video.id}`)" class="mt-4 flex items-center justify-center gap-2 rounded-xl py-3 active:scale-[0.98] transition-transform"
          :style="{ background: GRAD, boxShadow: GLOW, fontSize: '14px', fontWeight: 800, color: '#fff' }" @click="watchVideo">
          <Icon name="play" class="w-4 h-4" style="fill:#1a1a1a" /> {{ t('doa.videoCta') }}
        </a>
      </template>

      <template v-else>
        <p class="text-center" style="font-size:10px;font-weight:800;letter-spacing:.16em;color:var(--lime-dark);text-transform:uppercase">{{ t('doa.eyebrow') }}</p>
        <div class="relative mt-2 mb-1">
          <span aria-hidden="true" style="position:absolute;top:-14px;left:-2px;font-size:46px;line-height:1;color:#f0f6fc;font-weight:900;font-family:Georgia,serif">“</span>
          <p class="relative text-center px-2" style="font-size:14.5px;line-height:1.7;color:#1f2937;font-style:italic;font-weight:500">{{ t('doa.hadith') }}</p>
        </div>
        <p class="text-center" style="font-size:11px;font-weight:700;color:#b6bcc6;margin-top:6px">{{ t('doa.hadithSource') }}</p>
        <div class="flex items-center gap-2.5 my-4">
          <span class="flex-1 h-px" style="background:linear-gradient(90deg, transparent, #e5e7eb)" />
          <span style="font-size:15px">✨</span>
          <span class="flex-1 h-px" style="background:linear-gradient(90deg, #e5e7eb, transparent)" />
        </div>
        <h2 class="text-center" style="font-size:17px;font-weight:900;color:#1a1a1a;letter-spacing:-.01em">{{ t('doa.popupHeadline') }}</h2>
        <p class="text-center" style="font-size:12px;color:#6b7280;margin-top:3px;margin-bottom:14px;line-height:1.5">{{ t('doa.popupSubline') }}</p>

        <div class="relative" style="min-height:196px">
          <Transition :css="false" mode="out-in" @enter="cardEnter" @leave="cardLeave" @after-leave="afterLeave">
            <div v-if="cur" :key="cur.id" class="relative rounded-2xl p-4"
              :style="{ background: 'linear-gradient(160deg, #ffffff 0%, #f0f6fc 100%)', border: '1px solid #c7dcf0', boxShadow: '0 6px 22px color-mix(in srgb, var(--lime) 16%, transparent)' }">
              <button type="button" :aria-label="t('doa.skipAria')" class="absolute right-2.5 top-2.5 w-7 h-7 rounded-full flex items-center justify-center hover:bg-gray-50 transition-colors" style="border:1px solid #f0f6fc;color:#b6bcc6" @click="skip(cur)"><Icon name="x" class="w-3.5 h-3.5" /></button>
              <div class="flex items-center gap-2.5 pr-7">
                <div class="flex-shrink-0 rounded-full flex items-center justify-center text-white font-extrabold" aria-hidden="true"
                  :style="{ width: '38px', height: '38px', background: color(cur.id), fontSize: '16px' }">{{ initial(cur.donor_name || 'T') }}</div>
                <div class="min-w-0">
                  <p class="truncate" style="font-size:13px;font-weight:800;color:#1a1a1a">{{ donor(cur) }}</p>
                  <p style="font-size:10.5px;font-weight:500;color:#9ca3af">{{ timeAgo(cur.paid_at) }}</p>
                </div>
              </div>
              <p class="mt-3" style="font-size:14px;line-height:1.6;color:#374151;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;min-height:45px">{{ cur.message }}</p>
              <div class="flex items-center gap-2.5 mt-3.5">
                <span class="flex items-center gap-1 rounded-full px-2.5 py-1 flex-shrink-0" style="background:#f0f6fc;border:1px solid #c7dcf0">
                  <span style="font-size:11px">🤲</span>
                  <span style="font-size:11.5px;font-weight:800;color:var(--lime-text)">{{ cur.amin_count }}</span>
                </span>
                <button type="button" :disabled="busy" :aria-label="t('doa.aminAria')" class="amin-pop-btn flex-1 flex items-center justify-center gap-2 rounded-xl py-2.5 transition-all relative overflow-visible"
                  :style="{ background: GRAD, border: '1px solid var(--lime-dark)', cursor: busy ? 'default' : 'pointer', opacity: busy ? .85 : 1, boxShadow: GLOW }" @click="aamiin(cur, $event)">
                  <span style="font-size:16px;line-height:1">🤲</span>
                  <span style="font-size:14px;font-weight:800;color:#1a1a1a;letter-spacing:.01em">{{ t('doa.aminDone') }}</span>
                </button>
              </div>
            </div>
          </Transition>
        </div>

        <div class="flex items-center justify-center gap-1.5 mt-4">
          <span v-for="(_, a) in list" :key="a" class="rounded-full transition-all duration-300" :style="{ width: a === idx ? '20px' : '6px', height: '6px', background: dotBg(a) }" />
        </div>
      </template>
    </div>
  </div>
</template>

<style>
.doa-sparkle {
  position: fixed;
  pointer-events: none;
  z-index: 9999;
  font-size: 16px;
  will-change: transform, opacity;
  animation: doa-sparkle-fly 700ms ease-out forwards;
}
@keyframes doa-sparkle-fly {
  0%   { opacity: 1; transform: translate(-50%, -50%) scale(0.4) rotate(0deg); }
  30%  { opacity: 1; transform: translate(calc(-50% + var(--dx) * 0.5), calc(-50% + var(--dy) * 0.5)) scale(1.1) rotate(90deg); }
  100% { opacity: 0; transform: translate(calc(-50% + var(--dx)), calc(-50% + var(--dy) - 12px)) scale(0.6) rotate(180deg); }
}
.amin-pop-btn:not(:disabled):active { transform: scale(0.97); }
.amin-pop-btn:not(:disabled):hover { box-shadow: 0 6px 18px color-mix(in srgb, var(--lime) 45%, transparent); }
</style>
