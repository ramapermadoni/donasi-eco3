<script setup>
import { rpSp, pad2 } from '../utils/format'
import { postJson } from '../utils/net'
import { ref, computed, onBeforeUnmount, watch } from 'vue'
const REAL = import.meta.env.VITE_REAL_API !== '0'
import Icon from './Icon.vue'
import { lp } from '../i18n'

// Port of sedekah.id's MissionRunner. States: idle -> active -> done | expired.
// Server calls (replace in Frappe): POST /api/baik/start {missionSlug}, /api/baik/claim {sessionId,count}, /api/baik/release {sessionId}
const props = defineProps({ mission: { type: Object, required: true }, alreadyDone: Boolean })

const state = ref('idle')
const taps = ref(0)
const now = ref(Date.now())
const session = ref(null) // {startedAt, deadlineAt, minDurationSec}
const shared = ref(false)
const rhythm = ref(true)
const burst = ref(0)
const busy = ref(false)
const err = ref('')
const result = ref(null) // {voucherAmount, campaignTitle, sponsorName} dari /api/baik/claim
let sessionId = null
let timer = null

async function call(path, body, keepalive = false) {
  const { r, j } = await postJson('/api/baik/' + path, body, { keepalive })
  return { ok: r.ok, status: r.status, j }
}
function freeSession() { const id = sessionId; sessionId = null; if (id && REAL) call('release', { sessionId: id }, true).catch(() => {}) }

const money = rpSp
const mmss = (s) => { s = Math.max(0, Math.ceil(s)); return `${Math.floor(s / 60)}:${pad2(s % 60)}` }

const m = computed(() => props.mission)
const target = computed(() => m.value.targetCount || 0)
const goalSec = computed(() => m.value.targetDurationSec || m.value.minDurationSec)
const elapsed = computed(() => (session.value ? Math.max(0, Math.floor((now.value - session.value.startedAt) / 1000)) : 0))
// Asli: untuk TIMER ambang = max(minDurationSec sesi, targetDurationSec) (P di MissionRunner asli); lainnya = minDurationSec.
const minSec = computed(() => { const base = session.value ? session.value.minDurationSec : m.value.minDurationSec; return session.value && m.value.type === 'TIMER' ? Math.max(base, goalSec.value) : base })
const minLeft = computed(() => Math.max(0, minSec.value - elapsed.value))
const holdLeft = computed(() => (session.value ? Math.max(0, Math.ceil((session.value.deadlineAt - now.value) / 1000)) : m.value.maxDurationSec))
const minOk = computed(() => minLeft.value <= 0)
const countDone = computed(() => taps.value >= target.value)
const timerDone = computed(() => elapsed.value >= goalSec.value)
const ring = computed(() => (m.value.type === 'TAP_COUNTER' ? Math.min(1, target.value ? taps.value / target.value : 0) : m.value.type === 'TIMER' ? Math.min(1, elapsed.value / Math.max(1, goalSec.value)) : Math.min(1, elapsed.value / Math.max(1, minSec.value))))
const holdPct = computed(() => (session.value ? Math.min(100, Math.max(0, ((now.value - session.value.startedAt) / Math.max(1, session.value.deadlineAt - session.value.startedAt)) * 100)) : 0))
const beat = computed(() => (m.value.type !== 'TAP_COUNTER' || target.value <= 0 ? 1400 : Math.round(Math.min(2200, Math.max(850, (1000 * m.value.minDurationSec) / target.value)))))
const C = 2 * Math.PI * 100

watch(state, (s) => {
  clearInterval(timer)
  if (s === 'active') timer = setInterval(() => (now.value = Date.now()), 250)
})
watch(holdLeft, (v) => { if (state.value === 'active' && session.value && v <= 0) state.value = 'expired' })
onBeforeUnmount(() => { clearInterval(timer); if (state.value === 'active') freeSession() })
watch(state, (v) => { if (v === 'expired') freeSession() })

async function start() {
  busy.value = true; err.value = ''
  try {
    let t = Date.now(), startedAt = t, deadlineAt = t + m.value.maxDurationSec * 1000, minDurationSec = m.value.minDurationSec
    if (REAL) {
      const { ok, j } = await call('start', { missionSlug: m.value.slug })
      if (!ok) { err.value = j.error || 'Gagal memulai.'; return }
      sessionId = j.sessionId
      const sn = Date.parse(j.serverNow), si = Date.parse(j.startedAt), sr = Date.parse(j.reservedUntil)
      t = Date.now()
      startedAt = t - (Number.isFinite(sn) && Number.isFinite(si) ? Math.max(0, sn - si) : 0)
      deadlineAt = t + (Number.isFinite(sr) && Number.isFinite(sn) ? Math.max(0, sr - sn) : (Number(j.maxDurationSec) || m.value.maxDurationSec) * 1000)
      minDurationSec = Number(j.minDurationSec) || minDurationSec
    } else await new Promise((r) => setTimeout(r, 500))
    session.value = { startedAt, deadlineAt, minDurationSec }
    now.value = Date.now(); taps.value = 0; shared.value = false; result.value = null; state.value = 'active'
  } catch { err.value = 'Koneksi bermasalah.' } finally { busy.value = false }
}
function tap() {
  if (state.value !== 'active' || countDone.value) return
  taps.value++; burst.value++
  navigator.vibrate && navigator.vibrate(10)
}
function release() { freeSession(); session.value = null; taps.value = 0; shared.value = false; err.value = ''; state.value = 'idle' }
async function claim() {
  if (busy.value || !minOk.value) return
  busy.value = true; err.value = ''
  try {
    if (REAL) {
      if (!sessionId) return
      const { ok, j } = await call('claim', { sessionId, count: m.value.type === 'TAP_COUNTER' ? taps.value : target.value || 1 })
      if (!ok) { if (j.code === 'EXPIRED') state.value = 'expired'; err.value = j.error || 'Gagal klaim.'; return }
      sessionId = null
      result.value = { voucherAmount: j.voucherAmount, campaignTitle: j.campaignTitle, sponsorName: j.sponsorName }
    } else await new Promise((r) => setTimeout(r, 600))
    state.value = 'done'
    navigator.vibrate && navigator.vibrate([20, 40, 20])
  } catch { err.value = 'Koneksi bermasalah.' } finally { busy.value = false }
}
async function share() {
  const url = m.value.shareUrl || location.origin
  const text = m.value.shareText || 'Yuk berbuat baik bareng di sedekah.id'
  try { navigator.share ? await navigator.share({ text, url }) : window.open(`https://wa.me/?text=${encodeURIComponent(text + ' ' + url)}`, '_blank'); shared.value = true } catch { /* cancelled */ }
}
</script>

<template>
  <!-- done -->
  <div v-if="state === 'done'" class="text-center py-8">
    <div class="text-5xl mb-3">✨</div>
    <h2 class="text-xl font-bold text-gray-900">Alhamdulillah!</h2>
    <p class="mt-2 text-gray-600 leading-relaxed px-4">Kebaikanmu telah mengalirkan sedekah <span class="font-bold text-[color:var(--lime-text)]">{{ money((result || m).voucherAmount || 0) }}</span> ke <span class="font-semibold">{{ (result || m).campaignTitle }}</span>, berkat kedermawanan <span class="font-semibold">{{ (result || m).sponsorName }}</span>.</p>
    <p class="mt-3 text-sm text-gray-400">Semoga menjadi amal jariyah untukmu dan sang dermawan 🌙</p>
    <router-link :to="lp('/jalankebaikan')" class="inline-block mt-6 px-6 py-3 rounded-xl bg-[color:var(--lime)] text-white font-bold text-sm">Kembali</router-link>
  </div>

  <!-- expired -->
  <div v-else-if="state === 'expired'" class="text-center py-10">
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-clock3 w-12 h-12 mx-auto text-amber-500"><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16.5 12" /></svg>
    <h2 class="mt-3 text-lg font-bold text-gray-900">Waktu misi sudah habis</h2>
    <p class="mt-2 text-sm text-gray-500 px-5">Voucher sudah otomatis dikembalikan agar dapat digunakan orang lain. Kamu bisa mulai lagi jika stok masih tersedia.</p>
    <p v-if="err" class="mt-2 text-xs text-amber-700">{{ err }}</p>
    <button class="mt-6 px-6 py-3 rounded-xl bg-[color:var(--lime)] text-white font-bold text-sm inline-flex items-center gap-2 disabled:opacity-50" :disabled="busy" @click="start"><Icon name="rotate" class="w-4 h-4" /> {{ busy ? 'Menyiapkan…' : 'Mulai Lagi' }}</button>
  </div>

  <!-- already done today -->
  <div v-else-if="alreadyDone && state === 'idle'" class="text-center py-10">
    <div class="text-4xl mb-3">🌙</div>
    <h2 class="text-lg font-bold text-gray-900">Kamu sudah menuntaskan kebaikan hari ini</h2>
    <p class="mt-2 text-sm text-gray-500">Kembali lagi besok untuk melanjutkan kebaikan.</p>
    <router-link :to="lp('/jalankebaikan')" class="inline-block mt-6 px-6 py-3 rounded-xl border border-gray-200 font-semibold text-sm text-gray-700">Lihat kebaikan lain</router-link>
  </div>

  <!-- idle / active -->
  <div v-else class="text-center">
    <template v-if="m.type === 'TAP_COUNTER'">
      <p v-if="m.arabicText" dir="rtl" class="text-3xl leading-relaxed text-gray-900 mt-2 font-serif">{{ m.arabicText }}</p>
      <p v-if="m.latinText" class="mt-2 text-sm font-medium text-gray-500 italic">{{ m.latinText }}</p>
      <p v-if="m.meaning" class="mt-1 text-xs text-gray-400 px-6">“{{ m.meaning }}”</p>
    </template>
    <template v-else>
      <div class="mt-2 flex justify-center"><img v-if="m.icon && (m.icon.startsWith('http') || m.icon.startsWith('/'))" :src="m.icon" alt="" class="w-12 h-12 object-contain" /><span v-else class="text-4xl">{{ m.icon || '🌟' }}</span></div>
      <p v-if="m.instruction" class="mt-2 text-base font-semibold text-gray-800 px-4">{{ m.instruction }}</p>
      <p v-if="m.meaning" class="mt-1 text-xs text-gray-400 px-6">{{ m.meaning }}</p>
    </template>

    <div v-if="state === 'active' && session" class="mt-5 rounded-2xl border border-[#c7dcf0] bg-[#f0f6fc] p-3.5">
      <div class="grid grid-cols-2 gap-3 text-left">
        <div>
          <p class="text-[10px] uppercase tracking-wide text-gray-400 font-bold">Durasi minimum</p>
          <p class="mt-0.5 text-sm font-bold" :class="minOk ? 'text-[color:var(--lime-text)]' : 'text-gray-800'">{{ minOk ? 'Terpenuhi ✓' : mmss(minLeft) }}</p>
        </div>
        <div class="text-right">
          <p class="text-[10px] uppercase tracking-wide text-gray-400 font-bold">Voucher ditahan</p>
          <p class="mt-0.5 text-sm font-bold" :class="holdLeft <= 60 ? 'text-amber-600' : 'text-gray-800'">{{ mmss(holdLeft) }}</p>
        </div>
      </div>
      <div class="mt-2.5 h-1.5 rounded-full bg-gray-200 overflow-hidden">
        <div :style="{ width: Math.round(holdPct) + '%' }" class="h-full bg-[color:var(--lime)] transition-[width] duration-300"></div>
      </div>
      <p class="mt-2 text-[10.5px] text-gray-500">Voucher ini sementara tidak bisa diambil orang lain.</p>
    </div>

    <div class="relative mx-auto my-6 w-[220px] h-[220px]">
      <template v-if="state === 'active' && m.type === 'TAP_COUNTER' && rhythm && !countDone">
        <div :style="{ animationDuration: beat + 'ms' }" class="baik-breathe absolute -inset-3 rounded-full border-[10px] border-[color:color-mix(in_srgb,var(--lime)_55%,transparent)] bg-[color:color-mix(in_srgb,var(--lime)_10%,transparent)] shadow-[0_0_28px_color-mix(in_srgb,var(--lime)_34%,transparent)] pointer-events-none"></div>
        <div :style="{ animationDuration: beat + 'ms', animationDelay: Math.round(0.42 * beat) + 'ms' }" class="baik-breathe absolute -inset-7 rounded-full border-[8px] border-[color:color-mix(in_srgb,var(--lime)_30%,transparent)] pointer-events-none"></div>
      </template>
      <div v-if="burst > 0 && state === 'active' && m.type === 'TAP_COUNTER'" :key="burst" class="baik-tap-burst absolute inset-8 rounded-full border-4 border-[color:var(--lime)] pointer-events-none"></div>
      <svg width="220" height="220" class="-rotate-90 absolute inset-0">
        <circle cx="110" cy="110" r="100" fill="none" stroke="#f0f6fc" stroke-width="12" />
        <circle cx="110" cy="110" r="100" fill="none" stroke="var(--lime)" stroke-width="12" stroke-linecap="round" :stroke-dasharray="C" :stroke-dashoffset="C * (1 - ring)" class="transition-[stroke-dashoffset] duration-300" />
      </svg>
      <div class="absolute inset-[18px] rounded-full bg-white shadow-sm flex flex-col items-center justify-center overflow-hidden">
        <template v-if="m.type === 'TAP_COUNTER'">
          <button v-if="state === 'active'" class="w-full h-full rounded-full flex flex-col items-center justify-center active:scale-95 transition-transform disabled:cursor-default" :disabled="countDone" @click="tap">
            <span class="text-5xl font-black text-gray-900">{{ taps }}</span>
            <span class="text-sm text-gray-400">/ {{ target }}×</span>
            <span v-if="!countDone" class="mt-2 text-[11px] font-bold text-[color:var(--lime-text)]">KETUK • DZIKIR</span>
          </button>
          <template v-else>
            <span class="text-5xl font-black text-gray-900">0</span>
            <span class="text-sm text-gray-400">/ {{ target }}×</span>
          </template>
        </template>
        <template v-else>
          <span class="text-4xl font-black text-gray-900">{{ mmss(elapsed) }}</span>
          <span v-if="m.type === 'TIMER'" class="text-sm text-gray-400">/ {{ mmss(goalSec) }}</span>
        </template>
      </div>
    </div>

    <button v-if="state === 'active' && m.type === 'TAP_COUNTER'" type="button" class="mb-4 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border" :class="rhythm ? 'border-[#b9d4ee] bg-[#f0f6fc] text-[#005399]' : 'border-gray-200 text-gray-400'" @click="rhythm = !rhythm"><Icon name="sparkles" class="w-3.5 h-3.5" /> {{ rhythm ? 'Ritme lembut aktif' : 'Aktifkan panduan ritme' }}</button>
    <div v-if="err" class="mb-4 mx-auto max-w-xs rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-sm px-4 py-2.5">{{ err }}</div>

    <template v-if="state === 'idle'">
      <div class="rounded-xl bg-[#f0f6fc] border border-[#c7dcf0] px-4 py-3 mb-5 mx-auto max-w-xs text-sm text-gray-600">Tuntaskan kebaikan ini → sedekah <b class="text-[color:var(--lime-text)]">{{ money(m.voucherAmount) }}</b> mengalir atas namamu ke <b>{{ m.campaignTitle }}</b>.</div>
      <button class="px-8 py-4 rounded-2xl bg-[color:var(--lime)] text-white font-bold text-base disabled:opacity-50" :disabled="busy" @click="start">{{ busy ? 'Menyiapkan voucher…' : 'Ambil Voucher & Mulai' }}</button>
      <p class="mt-3 text-[11px] text-gray-400">Voucher akan ditahan khusus untukmu selama waktu misi.</p>
    </template>
    <template v-else>
      <template v-if="m.type === 'TAP_COUNTER'">
        <button v-if="countDone && minOk" class="px-8 py-4 rounded-2xl bg-[color:var(--lime-text)] text-white font-bold text-base disabled:opacity-50 inline-flex items-center gap-2" :disabled="busy" @click="claim"><Icon name="badgeCheck" class="w-5 h-5" /> {{ busy ? 'Memproses…' : 'Salurkan Sedekah' }}</button>
        <p v-else-if="countDone" class="text-sm text-gray-500">Hitungan selesai. Tenangkan ritme selama {{ mmss(minLeft) }} lagi…</p>
        <p v-else class="text-sm text-gray-500">Ikuti denyut lingkaran, satu bacaan setiap ketukan.</p>
      </template>
      <template v-else-if="m.type === 'TIMER'">
        <button v-if="timerDone && minOk" class="px-8 py-4 rounded-2xl bg-[color:var(--lime-text)] text-white font-bold text-base disabled:opacity-50 inline-flex items-center gap-2" :disabled="busy" @click="claim"><Icon name="badgeCheck" class="w-5 h-5" /> {{ busy ? 'Memproses…' : 'Salurkan Sedekah' }}</button>
        <p v-else class="text-sm text-gray-500">Lanjutkan dengan tenang hingga durasi minimum terpenuhi…</p>
      </template>
      <template v-else-if="m.type === 'SHARE'">
        <div class="space-y-3">
          <button v-if="!shared" class="px-8 py-4 rounded-2xl bg-[color:var(--lime)] text-white font-bold text-base inline-flex items-center gap-2" @click="share"><Icon name="share" class="w-5 h-5" /> Bagikan Kebaikan</button>
          <button v-else class="px-8 py-4 rounded-2xl bg-[color:var(--lime-text)] text-white font-bold text-base disabled:opacity-50 inline-flex items-center gap-2" :disabled="busy || !minOk" @click="claim"><Icon name="badgeCheck" class="w-5 h-5" /> {{ busy ? 'Memproses…' : minOk ? 'Salurkan Sedekah' : 'Tunggu ' + mmss(minLeft) }}</button>
        </div>
      </template>
      <button v-else class="px-8 py-4 rounded-2xl bg-[color:var(--lime-text)] text-white font-bold text-base disabled:opacity-50 inline-flex items-center gap-2" :disabled="busy || !minOk" @click="claim"><Icon name="badgeCheck" class="w-5 h-5" /> {{ busy ? 'Memproses…' : minOk ? 'Saya Sudah Melakukannya' : 'Tunggu ' + mmss(minLeft) }}</button>
      <button type="button" class="mt-5 mx-auto flex items-center gap-1 text-xs text-gray-400 hover:text-red-500" @click="release"><Icon name="x" class="w-3.5 h-3.5" /> Batalkan dan kembalikan voucher</button>
    </template>
  </div>
</template>

<style scoped>
@keyframes baik-breathe { 0% { opacity: .72; transform: scale(.78); } 62% { opacity: .28; } to { opacity: 0; transform: scale(1.08); } }
@keyframes baik-tap-burst { 0% { opacity: .85; transform: scale(.72); } to { opacity: 0; transform: scale(1.34); } }
.baik-breathe { animation-name: baik-breathe; animation-timing-function: cubic-bezier(.22, .61, .36, 1); animation-iteration-count: infinite; }
.baik-tap-burst { animation: .45s ease-out forwards baik-tap-burst; }
@media (prefers-reduced-motion: reduce) { .baik-breathe, .baik-tap-burst { animation: none; } }
</style>
