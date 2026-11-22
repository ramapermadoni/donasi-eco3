<script setup>
import { postJson } from '../utils/net'
import { lp } from '../i18n'
import { ref, computed, onMounted, watch } from 'vue'
import Icon from '../components/Icon.vue'
import BottomNav from '../components/BottomNav.vue'
import { auth } from '../auth'
import snapshot from '../data/gamification.json'

// Port 1:1 dari halaman asli /jejak-kebaikan (chunk Next.js, komponen hero kanvas "x" + dialog klaim "m").
// Live: GET /api/donor/gamification (401 = tamu). Mode mock (VITE_REAL_API=0): snapshot gamification.json.
// Frappe hook: klaim = POST /api/donor/gamification/claim {rewardId,recipientName,phone,address} -> {ok}
const REAL = import.meta.env.VITE_REAL_API !== '0'
const g = ref(null)
const state = ref('loading') // loading | guest | ready
const sel = ref(null)

async function loadG() {
  if (!REAL) { g.value = snapshot; state.value = auth.user ? 'ready' : 'guest'; return }
  try {
    const r = await fetch('/api/donor/gamification')
    if (r.status === 401) { state.value = 'guest'; return }
    g.value = await r.json(); state.value = 'ready'
  } catch { state.value = 'guest' }
}
onMounted(loadG)

const idn = (n) => (n ?? 0).toLocaleString('id-ID')
const lv = computed(() => g.value?.level || {})
const levels = computed(() => g.value?.levels || [])
const rewards = computed(() => g.value?.rewards || [])
const points = computed(() => g.value?.points ?? 0)
const left = computed(() => (lv.value.nextThreshold != null ? Math.max(0, lv.value.nextThreshold - points.value) : 0))
function btn(r) {
  const diff = r.pointCost - points.value
  const label = r.outOfStock ? 'Habis' : diff > 0 ? `${idn(diff)} Jejak Kebaikan Lagi` : g.value.claimEnabled ? 'Tukar' : 'Segera'
  return { label, ok: diff <= 0 && !r.outOfStock && !!g.value.claimEnabled }
}

// ---- dialog klaim (komponen "m" asli) ----
const rcpName = ref('')
const rcpPhone = ref('')
const address = ref('')
const claimBusy = ref(false)
const claimErr = ref('')
const claimed = ref(false)
function pick(r) { rcpName.value = g.value.donorName ?? ''; rcpPhone.value = g.value.phone ?? ''; address.value = ''; claimErr.value = ''; claimed.value = false; sel.value = r }
async function claim() {
  claimErr.value = ''; claimBusy.value = true
  try {
    if (REAL) {
      const { r, j } = await postJson('/api/donor/gamification/claim', { rewardId: sel.value.id, recipientName: rcpName.value.trim(), phone: rcpPhone.value.trim(), address: address.value.trim() })
      if (!r.ok || !j.ok) { claimErr.value = j.error ?? 'Gagal menukar.'; return }
    } else await new Promise((r) => setTimeout(r, 600))
    claimed.value = true
  } catch { claimErr.value = 'Terjadi kesalahan. Coba lagi.' } finally { claimBusy.value = false }
}
function close() { sel.value = null }
function done() { sel.value = null; loadG() }

// ---- hero kanvas "jalan" (komponen "x" asli, disalin apa adanya) ----
const heroEl = ref(null)
const cvEl = ref(null)
watch([heroEl, cvEl, levels, () => lv.value.currentIndex], ([t, a, e, r], _o, onCleanup) => {
  if (!t || !a || !e.length) return
  const l = a.getContext('2d')
  if (!l) return
  const n = e.map((_, i) => 420 + 900 * i)
  const o = n.length ? n[n.length - 1] + 300 : 0
  const c = e.map((x) => { if (!x.badgeUrl) return null; const im = new Image(); im.crossOrigin = 'anonymous'; im.src = x.badgeUrl.replace(/^https?:\/\/sedekah\.id(?=\/)/, ''); // asli: same-origin; di tiruan lewat proxy /api/media agar kanvas tidak kena CORS
    im.onload = () => j(); return im })
  let u = 0, d = 0, f = 1, h = 0, p = 0, x = 0, m = []
  const gg = (e2, t2) => { const a2 = 330 / (330 + t2); return { x: h + e2 * a2, y: p + (x - p) * a2, s: a2 } }
  const y = (e2, t2, a2, r2) => { l.beginPath(); l.ellipse(e2, t2, a2, Math.max(1, r2), 0, 0, 6.283); l.fill() }
  let b = (n[r] ?? n[0] ?? 0) - 430
  let v = b
  function j() {
    if (!u || !d || !l) return
    l.clearRect(0, 0, u, d)
    for (const e2 of m) { l.globalAlpha = Math.max(.12, .85 * e2.a); l.fillStyle = '#fff6ea'; l.beginPath(); l.arc(e2.x, e2.y, e2.r, 0, 6.283); l.fill() }
    l.globalAlpha = 1
    const t2 = gg(-150, 2), a2 = gg(150, 2), i2 = gg(-150, 2600), s2 = gg(150, 2600)
    l.fillStyle = '#221a30'; l.beginPath(); l.moveTo(t2.x, t2.y); l.lineTo(a2.x, a2.y); l.lineTo(s2.x, s2.y); l.lineTo(i2.x, i2.y); l.closePath(); l.fill()
    l.strokeStyle = 'rgba(255,194,75,.25)'; l.lineWidth = 1.3; l.beginPath(); l.moveTo(t2.x, t2.y); l.lineTo(i2.x, i2.y); l.moveTo(a2.x, a2.y); l.lineTo(s2.x, s2.y); l.stroke()
    l.fillStyle = '#FFC24B'
    for (let e2 = 0; e2 < 46; e2++) {
      const t3 = 90 * e2 - b % 90
      if (t3 > 2 && t3 < 2600) {
        const e3 = gg(0, t3), a3 = gg(0, t3 + 44), r3 = 6 * e3.s, n3 = 6 * a3.s
        l.globalAlpha = Math.max(.1, Math.min(.85, 1 - t3 / 2600))
        l.beginPath(); l.moveTo(e3.x - r3, e3.y); l.lineTo(e3.x + r3, e3.y); l.lineTo(a3.x + n3, a3.y); l.lineTo(a3.x - n3, a3.y); l.closePath(); l.fill()
      }
    }
    l.globalAlpha = 1
    const oo = []
    for (let e2 = 0; e2 < n.length; e2++) { const t3 = n[e2] - b; if (t3 > 4 && t3 < 2600) oo.push([e2, t3]) }
    oo.sort((e2, t3) => t3[1] - e2[1])
    for (const [t3, a3] of oo) {
      const nn = gg((t3 % 2 ? 1 : -1) * 208, a3), i3 = nn.s, s3 = nn.y, o3 = t3 <= r
      l.fillStyle = 'rgba(0,0,0,.4)'; y(nn.x, s3, 40 * i3, 8 * i3)
      const u3 = 34 * i3, d3 = 19 * i3, f3 = s3 - d3
      l.fillStyle = '#241634'; l.fillRect(nn.x - u3, f3, 2 * u3, d3); l.fillStyle = '#3a2455'; y(nn.x, f3, u3, .32 * u3)
      l.strokeStyle = 'rgba(255,194,75,.3)'; l.lineWidth = 1.1; l.beginPath(); l.ellipse(nn.x, f3, u3, Math.max(1, .32 * u3), 0, 0, 6.283); l.stroke()
      const h3 = 23 * i3, p3 = 16 * i3, x3 = f3 - p3
      l.fillStyle = '#2e1c47'; l.fillRect(nn.x - h3, x3, 2 * h3, p3); l.fillStyle = '#4a2f6b'; y(nn.x, x3, h3, .32 * h3)
      const m3 = c[t3], b3 = Math.max(6, 58 * i3), v3 = nn.x - b3 / 2, j3 = x3 - .92 * b3
      if (m3 && m3.complete && m3.naturalWidth) {
        l.save()
        if (o3) { l.shadowColor = '#FFC24B'; l.shadowBlur = 22 * i3 } else l.globalAlpha = .42
        l.drawImage(m3, v3, j3, b3, b3)
      } else {
        l.save()
        if (o3) { l.shadowColor = '#FFC24B'; l.shadowBlur = 20 * i3 }
        l.fillStyle = o3 ? '#FFC24B' : '#6d5a86'; l.beginPath(); l.arc(nn.x, j3 + b3 / 2, .36 * b3, 0, 6.283); l.fill()
      }
      l.restore()
      if (i3 > .26) {
        const a4 = Math.max(9, Math.min(15, 17 * i3))
        l.textAlign = 'center'; l.shadowColor = 'rgba(20,8,30,.85)'; l.shadowBlur = 6
        if (t3 === r) { l.font = `700 ${Math.max(8, 9.5 * i3)}px system-ui,sans-serif`; l.fillStyle = '#FFC24B'; l.fillText('POSISI SAAT INI', nn.x, j3 - Math.max(11, 13 * i3)) }
        l.font = `700 ${a4}px system-ui,sans-serif`; l.fillStyle = o3 ? '#fff3e0' : '#d9c7e2'; l.fillText(e[t3]?.name ?? '', nn.x, j3 - 2); l.shadowBlur = 0
      }
    }
  }
  function k() {
    f = Math.min(window.devicePixelRatio || 1, 2)
    const e2 = t.getBoundingClientRect()
    u = t.clientWidth || Math.round(e2.width) || t.offsetWidth || (t.parentElement?.clientWidth ?? 0) || document.documentElement.clientWidth || 430
    d = t.clientHeight || Math.round(e2.height) || t.offsetHeight || 290
    if (!u || !d) return
    a.width = u * f; a.height = d * f; a.style.width = u + 'px'; a.style.height = d + 'px'
    l.setTransform(f, 0, 0, f, 0, 0); h = u / 2; p = .46 * d; x = 1.2 * d
    const r2 = Math.round(u * p / 5200)
    m = []
    for (let i = 0; i < r2; i++) m.push({ x: Math.random() * u, y: Math.random() * p * .8, r: 1.1 * Math.random() + .3, a: Math.random() })
    j()
  }
  let N = 0
  const w = () => { b += (v - b) * .14; j(); N = requestAnimationFrame(w) }
  k()
  const L = [30, 120, 400, 1200, 3e3].map((e2) => window.setTimeout(k, e2))
  N = requestAnimationFrame(w)
  const P = () => k()
  window.addEventListener('resize', P)
  const C = () => { if (!document.hidden) k() }
  document.addEventListener('visibilitychange', C)
  const M = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(() => k()) : null
  M?.observe(t)
  let S = false, E = 0, A = 0
  const T = (e2) => { S = true; E = e2.clientY; A = v; try { t.setPointerCapture(e2.pointerId) } catch { /* ignore */ } }
  const R = (e2) => { if (S) v = Math.max(0, Math.min(o, A - (e2.clientY - E) * 4.2)) }
  const z = () => { S = false }
  t.addEventListener('pointerdown', T); t.addEventListener('pointermove', R); t.addEventListener('pointerup', z); t.addEventListener('pointercancel', z); t.addEventListener('pointerleave', z)
  onCleanup(() => {
    cancelAnimationFrame(N); L.forEach((e2) => clearTimeout(e2)); window.removeEventListener('resize', P); document.removeEventListener('visibilitychange', C); M?.disconnect()
    t.removeEventListener('pointerdown', T); t.removeEventListener('pointermove', R); t.removeEventListener('pointerup', z); t.removeEventListener('pointercancel', z); t.removeEventListener('pointerleave', z)
    c.forEach((e2) => { if (e2) e2.onload = null })
  })
}, { flush: 'post' })
</script>

<template>
  <div class="frame" style="background: #f5f6f8">
    <!-- memuat -->
    <div v-if="state === 'loading'" class="min-h-screen flex items-center justify-center bg-[#f5f6f8]"><div class="w-8 h-8 rounded-full border-4 border-gray-200 animate-spin" style="border-top-color: #005399"></div></div>

    <!-- tamu -->
    <div v-else-if="state === 'guest'" class="min-h-screen flex flex-col items-center justify-center text-center px-6 pb-24 bg-[#f5f6f8]">
      <Icon name="trophy" class="w-12 h-12 text-[color:var(--lime)] mb-3" />
      <p class="font-bold text-lg text-gray-800">Jejak Kebaikan</p>
      <p class="text-sm text-gray-500 mt-1 mb-5">Masuk untuk melihat Jejak Kebaikan, level, dan bingkisanmu.</p>
      <router-link :to="lp('/akun?next=/jejak-kebaikan')" class="px-5 py-3 rounded-xl bg-[color:var(--lime)] text-[#1a1a1a] font-bold text-sm">Masuk</router-link>
    </div>

    <!-- program belum aktif -->
    <div v-else-if="!g?.enabled" class="min-h-screen flex flex-col items-center justify-center text-center px-6 pb-24 bg-[#f5f6f8]">
      <Icon name="sparkles" class="w-12 h-12 text-[color:var(--lime)] mb-3" />
      <p class="font-bold text-lg text-gray-800">Segera hadir</p>
      <p class="text-sm text-gray-500 mt-1">Program Jejak Kebaikan sedang disiapkan. Nantikan ya!</p>
    </div>

    <div v-else class="min-h-screen bg-[#f5f6f8] pb-28">
      <div class="max-w-[480px] mx-auto">
        <div v-if="levels.length" ref="heroEl" class="relative overflow-hidden select-none" style="height: 290px; touch-action: none; cursor: grab; background: linear-gradient(180deg, #141038 0%, #2a1a5e 24%, #5f2585 45%, #a8317c 63%, #e85a54 81%, #ffb454 100%)">
          <svg viewBox="0 0 100 100" fill="none" aria-hidden="true" class="absolute" style="top: 8%; left: 14%; width: 46px; height: 46px; filter: drop-shadow(0 0 16px rgba(255, 225, 180, 0.6))"><circle cx="50" cy="50" r="30" fill="#fff1d6" /><circle cx="63" cy="42" r="27" fill="#3a1f5e" /></svg>
          <svg viewBox="0 0 400 80" preserveAspectRatio="none" aria-hidden="true" class="absolute left-0 right-0 w-full" style="top: 40%; height: 17%"><path d="M0,80 L46,32 L86,64 L128,22 L182,68 L226,38 L280,70 L330,28 L400,72 L400,80 Z" fill="#2a1550" /><path d="M96,80 L150,18 L176,46 L206,12 L260,80 Z" fill="#1e0f3e" /></svg>
          <canvas ref="cvEl" class="absolute inset-0 w-full h-full"></canvas>
          <div class="absolute top-0 left-0 right-0 flex items-start justify-between px-4 pt-3.5 pointer-events-none">
            <div>
              <p class="text-[25px] font-black leading-none" style="color: #ffc24b; text-shadow: 0 0 15px rgba(255, 194, 75, 0.5)">{{ idn(points) }}</p>
              <p class="text-[9px] tracking-[0.18em] uppercase mt-1" style="color: #e6c7e6">jejak kebaikan</p>
            </div>
            <div v-if="lv.currentName" class="text-right">
              <p class="text-[9px] tracking-[0.14em] uppercase" style="color: #e6c7e6">Level kamu</p>
              <p class="text-sm font-extrabold" style="color: #ffe6b8">{{ lv.currentName }}</p>
            </div>
          </div>
          <p class="absolute bottom-2 left-0 right-0 text-center text-[9.5px] tracking-[0.15em] uppercase pointer-events-none" style="color: rgba(255, 243, 224, 0.55)">tarik jalan untuk lihat perjalanan levelmu</p>
        </div>
        <div v-else class="px-5 pt-8 pb-14 relative" style="background: linear-gradient(180deg, #005399 0%, #003f75 100%)">
          <div class="flex items-center gap-2 text-[#1a1a1a]"><Icon name="trophy" style="width: 18px; height: 18px" /><span class="font-bold text-sm">Jejak Kebaikan</span></div>
          <div class="mt-4 text-center">
            <p class="text-4xl font-black text-[#1a1a1a]">{{ idn(points) }}</p>
            <p class="text-xs font-semibold text-[#1a1a1a]/70 mt-1 tracking-wide uppercase">jejak kebaikan terkumpul</p>
          </div>
        </div>

        <div class="px-4 -mt-7 relative z-10">
          <div class="bg-white rounded-2xl p-4" style="box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08)">
            <template v-if="lv.nextName">
              <div class="flex items-center justify-between text-xs mb-1.5">
                <span class="flex items-center gap-1.5 font-semibold text-gray-700"><img v-if="lv.currentBadge" :src="lv.currentBadge" alt="" class="w-5 h-5 object-contain" />{{ lv.currentName ?? 'Mulai' }}</span>
                <span class="flex items-center gap-1.5 text-gray-400"><img v-if="lv.nextBadge" :src="lv.nextBadge" alt="" class="w-5 h-5 object-contain opacity-40 grayscale" />{{ lv.nextName }}</span>
              </div>
              <div class="h-2.5 rounded-full bg-gray-100 overflow-hidden"><div class="h-full rounded-full bg-[#005399]" :style="{ width: Math.round(100 * lv.progress) + '%' }"></div></div>
              <p class="text-xs text-gray-500 mt-2 text-center"><b class="text-[#005399]">{{ idn(left) }} Jejak Kebaikan lagi</b> menuju {{ lv.nextName }}</p>
            </template>
            <p v-else class="text-sm text-center text-gray-600 font-medium py-1">🎉 Kamu sudah di level tertinggi!</p>
          </div>
        </div>

        <div v-if="levels.length" class="px-4 mt-6">
          <div class="flex items-center gap-2 mb-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-medal text-[#005399]"><path d="M7.21 15 2.66 7.14a2 2 0 0 1 .13-2.2L4.4 2.8A2 2 0 0 1 6 2h12a2 2 0 0 1 1.6.8l1.6 2.14a2 2 0 0 1 .14 2.2L16.79 15" /><path d="M11 12 5.12 2.2" /><path d="m13 12 5.88-9.8" /><path d="M8 7h8" /><circle cx="12" cy="17" r="5" /><path d="M12 18v-2h-.5" /></svg>
            <h2 class="font-bold text-gray-800 text-sm">Perjalanan Level</h2>
          </div>
          <div class="grid grid-cols-3 gap-2.5">
            <div v-for="(l, n) in levels" :key="l.name + n" class="bg-white rounded-2xl border p-2.5 text-center" :class="n === lv.currentIndex ? 'border-[#005399]' : 'border-gray-100'" :style="n === lv.currentIndex ? { boxShadow: '0 0 0 3px rgba(0,83,153,0.22)' } : undefined">
              <img v-if="l.badgeUrl" :src="l.badgeUrl" :alt="l.name" class="w-[52px] h-[52px] mx-auto mb-1.5 object-contain" :class="n <= lv.currentIndex ? '' : 'grayscale opacity-35'" />
              <div v-else class="w-[52px] h-[52px] mx-auto mb-1.5 flex items-center justify-center" :class="n <= lv.currentIndex ? '' : 'opacity-35'"><Icon name="trophy" class="w-7 h-7 text-[#005399]" /></div>
              <p class="text-[10.5px] leading-tight" :class="n <= lv.currentIndex ? 'font-bold text-gray-700' : 'font-semibold text-gray-400'">{{ l.name }}</p>
              <p class="text-[9.5px] text-gray-400 mt-0.5">{{ n <= lv.currentIndex ? 'tercapai' : '≥ ' + idn(l.threshold) + ' jejak' }}</p>
              <span v-if="n === lv.currentIndex" class="inline-block mt-1 px-2 py-0.5 rounded-full bg-[#1a1a1a] text-white text-[8.5px] font-extrabold">KAMU DI SINI</span>
            </div>
          </div>
        </div>

        <div class="px-4 mt-6">
          <div class="flex items-center gap-2 mb-3"><Icon name="gift" class="w-4 h-4 text-[#005399]" /><h2 class="font-bold text-gray-800 text-sm">Bingkisan Kebaikan</h2></div>
          <p v-if="!rewards.length" class="text-xs text-gray-400 italic text-center py-8">Belum ada bingkisan tersedia.</p>
          <div v-else class="grid grid-cols-2 gap-3">
            <div v-for="r in rewards" :key="r.id" class="bg-white rounded-2xl overflow-hidden border border-gray-100 flex flex-col">
              <div class="aspect-square bg-[#f0f6fc] flex items-center justify-center overflow-hidden"><img v-if="r.imageUrl" :src="r.imageUrl" :alt="r.name" class="w-full h-full object-cover" /><Icon v-else name="gift" class="w-8 h-8 text-[#005399]" /></div>
              <div class="p-2.5 flex flex-col flex-1">
                <p class="text-[13px] font-semibold text-gray-800 leading-tight line-clamp-2 min-h-[34px]">{{ r.name }}</p>
                <p class="text-xs font-bold text-[#005399] mt-1">{{ idn(r.pointCost) }} Jejak Kebaikan</p>
                <button class="mt-2 w-full py-2 px-1 rounded-lg text-[11px] font-bold leading-tight transition-colors disabled:cursor-default" :style="btn(r).ok ? { background: '#005399', color: '#1a1a1a' } : { background: '#f4f4ee', color: '#9ca3af' }" :disabled="!btn(r).ok" @click="pick(r)">{{ btn(r).label }}</button>
              </div>
            </div>
          </div>
          <p v-if="!g.claimEnabled" class="text-[11px] text-gray-400 text-center mt-4 flex items-center justify-center gap-1"><Icon name="lock" style="width: 11px; height: 11px" /> Penukaran bingkisan segera dibuka</p>
        </div>
      </div>
    </div>

    <!-- dialog klaim -->
    <div v-if="sel" class="fixed inset-0 z-50 flex items-end justify-center bg-black/40" @click="close">
      <div class="w-full max-w-[480px] bg-white rounded-t-3xl p-5 pb-8" @click.stop>
        <div class="flex items-center justify-between mb-1">
          <p class="font-bold text-gray-900">{{ claimed ? 'Berhasil ditukar' : 'Tukar bingkisan' }}</p>
          <button @click="close"><Icon name="x" class="text-gray-400" style="width: 20px; height: 20px" /></button>
        </div>
        <div v-if="claimed" class="text-center py-6">
          <div class="w-14 h-14 rounded-full bg-[#f0f6fc] flex items-center justify-center mx-auto mb-3"><Icon name="sparkles" class="w-7 h-7 text-[#005399]" /></div>
          <p class="text-sm text-gray-700">Klaim <b>{{ sel.name }}</b> diterima. Bingkisan akan dikirim ke alamatmu — pantau statusnya di Klaim Saya.</p>
          <button class="mt-5 w-full py-3 rounded-xl bg-[#005399] text-[#1a1a1a] font-bold text-sm" @click="done">Selesai</button>
        </div>
        <template v-else>
          <p class="text-xs text-gray-500 mb-4">{{ sel.name }} · <b class="text-[#005399]">{{ idn(sel.pointCost) }} Jejak Kebaikan</b></p>
          <div class="space-y-3">
            <input v-model="rcpName" placeholder="Nama penerima" class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-[#005399]" />
            <input v-model="rcpPhone" placeholder="Nomor HP (WhatsApp)" inputmode="tel" class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-[#005399]" />
            <div class="relative">
              <Icon name="mapPin" class="absolute left-3 top-3 text-gray-400" style="width: 15px; height: 15px" />
              <textarea v-model="address" rows="3" placeholder="Alamat lengkap pengiriman (jalan, kota, kode pos)" class="w-full pl-9 pr-3 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:border-[#005399] resize-none"></textarea>
            </div>
          </div>
          <p v-if="claimErr" class="text-xs text-red-600 mt-2">{{ claimErr }}</p>
          <button :disabled="claimBusy" class="mt-4 w-full py-3 rounded-xl bg-[#005399] text-[#1a1a1a] font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-50" @click="claim">
            <Icon v-if="claimBusy" name="loader" class="w-4 h-4 animate-spin" />
            <template v-else>Tukar sekarang <Icon name="chevronRight" style="width: 15px; height: 15px" /></template>
          </button>
          <p class="text-[11px] text-gray-400 text-center mt-2">Jejak Kebaikan akan dipotong {{ idn(sel.pointCost) }} setelah konfirmasi.</p>
        </template>
      </div>
    </div>
  </div>
  <BottomNav />
</template>
