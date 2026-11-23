<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Icon from '../components/Icon.vue'
import AppHeader from '../components/AppHeader.vue'
import BottomNav from '../components/BottomNav.vue'
import { t, lp, bcp, isEn } from '../i18n'
import { rpTight } from '../utils/format'
import { statusOf, canMakeup, streakOf, pause as pauseS, resume as resumeS, syncOccurrences, addDays } from '../rutin'
import { loadRutin, nowISO } from '../rutinStore'
import { auth, setRecurring, loadMe, isPaused } from '../auth'

// Dashboard rancangan sendiri: jadwal + kejadian dari localStorage (rutinStore). Tidak ada request ke sedekah.id.
// Pembayaran = simulasi (Demo) di /shadaqa-rutin/bayar. Aturan: docs/reference/shadaqa-rutin-flow.md
const router = useRouter()
const today = nowISO()
const ready = ref(false)
const s = ref(null)
const occs = ref([])
function reload() { const c = loadRutin(auth.user.phone, today); s.value = c.schedule && c.schedule.status !== 'CANCELLED' ? c.schedule : null; occs.value = c.occs }
onMounted(async () => {
  await loadMe()
  if (!auth.user) { router.replace(lp('/akun?next=' + encodeURIComponent('/shadaqa-rutin'))); return } // situs asli: tamu diarahkan ke layar masuk
  reload()
  if (!s.value) { router.replace(lp('/shadaqa-rutin/setup')); return } // tanpa jadwal -> setup
  ready.value = true
})
const paused = computed(() => isPaused(s.value))

// teks bulan/hari tetap seperti kode asli (bukan toLocale*)
const MONTHS = { id: ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'], en: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'] }
const DAYS = { id: ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'], en: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] }
const lk = computed(() => (isEn.value ? 'en' : 'id'))
const FREQ_KEY = { DAILY: 'freqDaily', WEEKLY: 'freqWeekly', MONTHLY: 'freqMonthly' }
const UNIT_KEY = { DAILY: 'unitDay', WEEKLY: 'unitWeek', MONTHLY: 'unitMonth' }
const money = (n) => rpTight(n || 0, bcp())
const dateShort = (iso) => { const [, m, d] = iso.split('-').map(Number); return `${d} ${MONTHS[lk.value][m - 1]}` }
const dateLong = (iso) => `${dateShort(iso)} ${iso.slice(0, 4)}`
const monthTitle = computed(() => { const [y, m] = today.split('-').map(Number); return `${MONTHS[lk.value][m - 1]} ${y} \u00b7 ${t('shadaqaRutin.' + FREQ_KEY[s.value?.frequency])}` })
const targetLabel = computed(() => (s.value?.target?.type === 'campaign' ? s.value.target.title || s.value.target.slug : t('shadaqaRutin.targetPilihan')))

const streak = computed(() => streakOf(occs.value, today))
const dueOcc = computed(() => occs.value.find((o) => o.date === today && statusOf(o, today) === 'DUE') || null)
const paidToday = computed(() => occs.value.some((o) => o.date === today && ['PAID', 'MAKEUP_PAID'].includes(o.status)))
const missed = computed(() => occs.value.filter((o) => canMakeup(o, today)).sort((a, b) => (a.date < b.date ? 1 : -1)))
const nextReminder = computed(() => {
  const o = occs.value.find((x) => x.date >= today && ['DUE', 'UPCOMING'].includes(statusOf(x, today)))
  return o ? `${dateLong(o.date)}, ${String(s.value.hourLocal).padStart(2, '0')}:00 WIB` : ''
})

// kalender 35 hari (5 baris Sen-Min): mulai Senin dari 14 hari sebelum hari ini
const winStart = computed(() => { const d = addDays(today, -14); const wd = (new Date(d + 'T00:00:00Z').getUTCDay() + 6) % 7; return addDays(d, -wd) })
const cells = computed(() => {
  const by = new Map(occs.value.map((o) => [o.date, o]))
  return Array.from({ length: 35 }, (_, i) => {
    const date = addDays(winStart.value, i), o = by.get(date), st = o ? statusOf(o, today) : null
    const status = st === 'PAID' ? 'DONE' : st === 'MAKEUP_PAID' ? 'MAKEUP_DONE' : st === 'DUE' ? 'TODAY' : st === 'MISSED' ? 'MISSED' : 'UPCOMING'
    return { date, status, raw: st || 'NONE', isToday: date === today, beforeStart: date < s.value.startDate, canMakeup: !!o && canMakeup(o, today) }
  })
})
const rows = computed(() => { const out = []; for (let i = 0; i < 35; i += 7) out.push(cells.value.slice(i, i + 7)); return out })
const dayNum = (c) => parseInt(c.date.split('-')[2], 10)
const cellStyle = (c) => {
  const o = c.status === 'TODAY', d = c.status === 'DONE', x = c.status === 'MAKEUP_DONE', m = c.status === 'MISSED', h = c.beforeStart, p = c.isToday && !o
  return { background: h ? 'transparent' : o ? '#005399' : d ? 'rgba(0,83,153,0.12)' : x ? 'rgba(255,107,157,0.10)' : 'transparent', border: h ? '1px dashed rgba(0,0,0,0.05)' : p ? '2px solid #005399' : o || d || x ? 'none' : m ? '1px solid rgba(255,107,157,0.35)' : '1px solid rgba(0,0,0,0.08)', opacity: h ? 0.4 : 1 }
}
const numStyle = (c) => ({ fontSize: '12px', fontWeight: c.status === 'TODAY' ? 800 : 500, color: c.status === 'TODAY' ? '#1a1a1a' : c.beforeStart ? '#cbd5e1' : '#6b7280' })

const cancelOpen = ref(false)
const busy = ref(false)
const err = ref('')
const makeup = ref(null)
const goPay = (date) => router.push(lp('/shadaqa-rutin/bayar?date=' + date))

async function mutate(fn, msgKey) {
  busy.value = true; err.value = ''
  try { await fn() } catch { err.value = t('shadaqaRutin.' + msgKey) } finally { busy.value = false }
}
const pause = () => mutate(async () => {
  const next = paused.value ? resumeS(s.value, today) : pauseS(s.value, today)
  await setRecurring(next, syncOccurrences(next, occs.value, today))
  reload()
}, paused.value ? 'errResume' : 'errScheduleAction')
const cancel = async () => { await mutate(() => setRecurring(null), 'errCancel'); cancelOpen.value = false; if (!auth.user?.recurring) router.push(lp('/')) }
const toggleAnon = () => mutate(async () => { await setRecurring({ ...s.value, isAnonymous: !s.value.isAnonymous }, occs.value); reload() }, 'errAnonUpdate')
</script>

<template>
  <div class="frame" style="background: #f5f6f8">
    <AppHeader />
    <!-- memuat / tamu / tanpa jadwal (diarahkan) -->
    <div v-if="!ready || !s" class="min-h-screen flex items-center justify-center bg-[#f5f6f8]">
      <div class="w-8 h-8 rounded-full border-4 border-gray-200 animate-spin" style="border-top-color: var(--lime)"></div>
    </div>

    <!-- dijeda (susunan dari i18n; layar asli belum teramati) -->
    <div v-else-if="paused" class="min-h-screen max-w-[480px] mx-auto bg-white pb-32">
      <div class="flex items-center gap-3 px-4 py-4 border-b border-gray-100">
        <button class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors" :aria-label="t('shadaqaRutin.back')" @click="router.push(lp('/'))"><Icon name="chevronLeft" class="w-5 h-5 text-gray-700" /></button>
        <span class="text-base font-bold text-[#1a1a1a]">{{ t('shadaqaRutin.resumeHeader') }}</span>
        <span class="ml-auto px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-700 border border-amber-300">{{ t('shadaqaRutin.demoBadge') }}</span>
      </div>
      <div class="px-4 py-6 text-center">
        <p class="text-base font-bold text-gray-900">{{ t('shadaqaRutin.resumeTitle') }}</p>
        <p class="mt-2 text-sm text-gray-600 leading-snug">{{ t('shadaqaRutin.resumeDescNoDate') }}</p>
        <div class="mt-5 rounded-2xl bg-[#f0f6fc] border border-[#c7dcf0] p-4 text-left space-y-2 text-sm">
          <div class="flex justify-between"><span class="text-gray-500">{{ t('shadaqaRutin.freqHeading') }}</span><b class="text-gray-900">{{ t('shadaqaRutin.' + FREQ_KEY[s.frequency]) }}</b></div>
          <div class="flex justify-between"><span class="text-gray-500">{{ t('shadaqaRutin.nominalHeading') }}</span><b class="text-gray-900">{{ money(s.amount) }}</b></div>
          <div class="flex justify-between"><span class="text-gray-500">{{ t('shadaqaRutin.targetHeading') }}</span><b class="text-gray-900 text-right">{{ targetLabel }}</b></div>
        </div>
        <div v-if="err" class="mt-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2.5 text-left">{{ err }}</div>
        <button data-t="resume" class="mt-5 w-full py-4 rounded-2xl text-sm font-bold bg-[color:var(--lime)] text-white shadow-lg shadow-[color:color-mix(in_srgb,var(--lime)_40%,transparent)] disabled:opacity-60" :disabled="busy" @click="pause">{{ busy ? t('shadaqaRutin.activating') : t('shadaqaRutin.resumeBtn') }}</button>
        <button class="mt-2 w-full py-3 rounded-2xl text-sm font-semibold bg-gray-100 text-gray-700" @click="router.push(lp('/shadaqa-rutin/setup'))">{{ t('shadaqaRutin.setupNew') }}</button>
      </div>
    </div>

    <!-- aktif (dari komponen Dashboard asli) -->
    <div v-else class="w-full max-w-[480px] mx-auto pt-3 pb-28">
      <div class="flex items-center gap-3 px-4 py-2 mb-2">
        <button class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors" :aria-label="t('shadaqaRutin.back')" @click="router.push(lp('/'))"><Icon name="chevronLeft" class="w-5 h-5 text-gray-700" /></button>
        <span class="text-base font-bold text-[#1a1a1a]">{{ t('shadaqaRutin.title') }}</span>
        <span data-t="demo-badge" class="ml-auto px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-700 border border-amber-300">{{ t('shadaqaRutin.demoBadge') }}</span>
      </div>
      <p class="mx-3 mb-3 text-[11px] text-amber-800 bg-amber-50 border border-amber-200 rounded-xl px-3 py-2">{{ t('shadaqaRutin.demoNote') }}</p>

      <div v-if="dueOcc" data-t="due-card" class="mx-3 rounded-2xl bg-white mb-3 p-4" style="box-shadow: 0 4px 20px rgba(0, 83, 153, 0.35); border: 2px solid #005399">
        <p class="text-base font-bold text-[#1a1a1a]">{{ t('shadaqaRutin.dueTitle', { amount: money(dueOcc.amount) }) }}</p>
        <p class="mt-1 text-xs text-gray-600 leading-snug">{{ t('shadaqaRutin.dueDesc', { date: dateLong(dueOcc.date) }) }}</p>
        <button data-t="due-cta" class="mt-3 w-full py-3.5 rounded-2xl text-sm font-bold bg-[#005399] text-white hover:bg-[#003f75] shadow-lg shadow-[#005399]/40" @click="goPay(dueOcc.date)">{{ t('shadaqaRutin.dueCta') }}</button>
      </div>
      <div v-else-if="paidToday" data-t="paid-today" class="mx-3 rounded-2xl bg-[#f0f6fc] border border-[#c7dcf0] mb-3 px-4 py-3 text-sm font-semibold text-[#005399]">{{ t('shadaqaRutin.dueDone') }}</div>

      <div class="mx-3 rounded-2xl overflow-hidden mb-3" style="box-shadow: 0 4px 20px rgba(0, 83, 153, 0.25)">
        <div class="px-4 py-3 flex items-center justify-between" style="background: linear-gradient(90deg, #005399 0%, #003f75 100%)">
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-white shadow"></div>
            <span class="text-[13px] font-bold text-[#1a1a1a]">{{ t('shadaqaRutin.activeBanner') }}</span>
          </div>
        </div>
        <div class="bg-gradient-to-b from-[#f0f6fc] to-white px-4 pt-3 pb-4">
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs font-semibold text-gray-700">{{ monthTitle }}</span>
            <div v-if="streak > 0" data-t="streak" class="flex items-center gap-1 px-2 py-0.5 rounded-full" style="background: rgba(255, 175, 35, 0.18); border: 1px solid rgba(255, 175, 35, 0.5)">
              <span class="text-[10px]">🔥</span>
              <span class="text-[11px] font-bold text-[#c47b00]">{{ t('shadaqaRutin.streakCount', { n: streak, unit: t('shadaqaRutin.' + UNIT_KEY[s.frequency]) }) }}</span>
            </div>
          </div>
          <div class="space-y-1">
            <div v-for="(w, wi) in rows" :key="wi" class="grid grid-cols-7 gap-1">
              <component :is="c.canMakeup ? 'button' : 'div'" v-for="(c, ci) in w" :key="c.date" :data-t="'day-' + c.date" :data-s="c.raw" class="flex flex-col items-center gap-1" :class="c.canMakeup ? 'active:scale-95 transition-transform' : ''" v-bind="c.canMakeup ? { type: 'button', 'aria-label': t('shadaqaRutin.calMakeupAria', { day: dayNum(c) }) } : {}" @click="c.canMakeup && (makeup = c.date)">
                <span v-if="wi === 0" class="text-[9px] font-medium text-gray-500">{{ DAYS[lk][ci] }}</span>
                <div class="w-9 h-9 rounded-xl flex items-center justify-center relative" :style="cellStyle(c)">
                  <span v-if="c.status === 'DONE'" :style="{ fontSize: '16px', lineHeight: 1 }">❤️</span>
                  <span v-else-if="c.status === 'MAKEUP_DONE'" :style="{ fontSize: '16px', lineHeight: 1 }">❤️‍🩹</span>
                  <span v-else-if="c.status === 'MISSED'" :style="{ fontSize: '14px', lineHeight: 1 }">💔</span>
                  <span v-else :style="numStyle(c)">{{ dayNum(c) }}</span>
                </div>
                <span v-if="['DONE', 'MAKEUP_DONE', 'MISSED'].includes(c.status)" class="text-[8px] text-gray-400 -mt-0.5">{{ dayNum(c) }}</span>
              </component>
            </div>
          </div>
          <div v-if="nextReminder" class="mt-3 pt-3 border-t border-[#005399]/20">
            <p class="text-[10px] text-gray-500">{{ t('shadaqaRutin.reminderNext') }}:</p>
            <p class="text-xs font-semibold text-gray-800">{{ nextReminder }}</p>
          </div>
        </div>
      </div>

      <div class="mx-3 rounded-2xl bg-white mb-3 overflow-hidden" style="box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06)">
        <div class="flex items-center justify-between px-4 py-3 border-b border-gray-50">
          <span class="text-[13px] font-bold text-[#1a1a1a]">{{ t('shadaqaRutin.dataTitle') }}</span>
        </div>
        <div class="px-4 py-3 space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <span class="text-xs text-gray-500">{{ t('shadaqaRutin.amountInline') + ' ' }}</span>
              <span class="text-sm font-bold text-[#1a1a1a]">{{ money(s.amount) }}</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="text-[11px] text-gray-500">{{ t('shadaqaRutin.targetHeading') }}</span>
              <div class="px-2.5 py-1 rounded-full" style="background: #00539915; border: 1px solid #00539930">
                <span class="text-xs font-bold text-[#005399]">{{ targetLabel }}</span>
              </div>
            </div>
          </div>
          <div class="border-t border-gray-50"></div>
          <div class="flex items-center justify-between gap-3">
            <div class="min-w-0">
              <p class="text-sm font-semibold text-[#1a1a1a] truncate">{{ auth.user.name }}</p>
              <p v-if="auth.user.phone" class="text-[11px] text-gray-500">+{{ String(auth.user.phone).replace(/^\+/, '') }}</p>
            </div>
            <button class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl transition-all" :disabled="busy" :class="s.isAnonymous ? 'bg-[#005399]/15 border border-[#005399]/40' : 'bg-gray-50 border border-gray-200'" @click="toggleAnon">
              <div class="w-4 h-4 rounded flex items-center justify-center border" :class="s.isAnonymous ? 'bg-[#005399] border-[#005399]' : 'bg-white border-gray-300'">
                <svg v-if="s.isAnonymous" width="9" height="7" viewBox="0 0 9 7" fill="none"><path d="M1 3.5L3.5 6L8 1" stroke="#1a1a1a" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" /></svg>
              </div>
              <span class="text-[11px] font-semibold leading-tight text-left" :class="s.isAnonymous ? 'text-[#005399]' : 'text-gray-600'">{{ t('shadaqaRutin.anonAs1') }}<br />{{ t('shadaqaRutin.anonAs2') }}</span>
            </button>
          </div>
        </div>
      </div>

      <div v-if="err" class="mx-3 mb-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2.5 flex items-start gap-2">
        <Icon name="alertCircle" class="w-4 h-4 flex-shrink-0 mt-0.5" />
        <span>{{ err }}</span>
      </div>

      <div v-if="missed.length" data-t="missed-list" class="mx-3 rounded-2xl bg-white mb-3 overflow-hidden" style="box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06)">
        <div class="px-4 py-3 border-b border-gray-50"><span class="text-[13px] font-bold text-[#1a1a1a]">{{ t('shadaqaRutin.missedHeading') }}</span></div>
        <div v-for="o in missed" :key="o.date" class="flex items-center justify-between px-4 py-2.5 border-b border-gray-50 last:border-0">
          <span class="text-sm text-gray-800">💔 {{ dateShort(o.date) }} · {{ money(o.amount) }}</span>
          <button :data-t="'makeup-' + o.date" class="px-3 py-1.5 rounded-xl text-xs font-bold bg-[#005399] text-white" @click="goPay(o.date)">{{ t('shadaqaRutin.makeupConfirm') }}</button>
        </div>
      </div>

      <div class="mx-3 mb-3 grid grid-cols-3 gap-2">
        <button class="flex flex-col items-center gap-1 py-2.5 rounded-xl bg-white border border-gray-200 text-gray-700 hover:border-gray-300 disabled:opacity-50" :disabled="busy" :title="t('shadaqaRutin.editHint')" @click="router.push(lp('/shadaqa-rutin/setup'))">
          <Icon name="pencil" class="w-4 h-4" />
          <span class="text-[10px] font-semibold">{{ t('shadaqaRutin.edit') }}</span>
        </button>
        <button data-t="pause" class="flex flex-col items-center gap-1 py-2.5 rounded-xl bg-white border border-gray-200 text-gray-700 hover:border-gray-300 disabled:opacity-50" :disabled="busy" @click="pause">
          <Icon name="pause" class="w-4 h-4" />
          <span class="text-[10px] font-semibold">{{ t('shadaqaRutin.pause') }}</span>
        </button>
        <button data-t="cancel" class="flex flex-col items-center gap-1 py-2.5 rounded-xl bg-white border border-red-200 text-red-600 hover:bg-red-50 disabled:opacity-50" :disabled="busy" @click="cancelOpen = true">
          <Icon name="trash2" class="w-4 h-4" />
          <span class="text-[10px] font-semibold">{{ t('shadaqaRutin.cancel') }}</span>
        </button>
      </div>
    </div>

    <transition name="fade">
      <div v-if="cancelOpen" class="fixed inset-0 z-50 flex items-center justify-center px-8" style="background: rgba(0, 0, 0, 0.4)">
        <div class="bg-white rounded-3xl p-6 flex flex-col items-center text-center w-full max-w-xs shadow-2xl">
          <div class="w-14 h-14 rounded-full flex items-center justify-center mb-4 bg-red-50"><Icon name="trash2" class="w-7 h-7 text-red-600" /></div>
          <p class="text-base font-bold text-gray-900 mb-1">{{ t('shadaqaRutin.cancelConfirmTitle') }}</p>
          <p class="text-sm text-gray-600 mb-5">{{ t('shadaqaRutin.cancelConfirmDesc') }}</p>
          <div class="grid grid-cols-2 gap-2 w-full">
            <button class="py-3 rounded-xl bg-gray-100 text-gray-700 text-sm font-semibold hover:bg-gray-200 disabled:opacity-50" :disabled="busy" @click="cancelOpen = false">{{ t('shadaqaRutin.batal') }}</button>
            <button data-t="cancel-yes" class="py-3 rounded-xl bg-red-600 text-white text-sm font-semibold hover:bg-red-700 disabled:opacity-50" :disabled="busy" @click="cancel">{{ t('shadaqaRutin.cancelConfirmYes') }}</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- popup genapi (hari terlewat) -->
    <div v-if="makeup" class="fixed inset-0 z-50 flex items-center justify-center px-6" style="background: rgba(0, 0, 0, 0.5); backdrop-filter: blur(2px)" @click.self="makeup = null">
      <div class="bg-white rounded-3xl p-6 flex flex-col items-center text-center w-full max-w-sm shadow-2xl relative">
        <button class="absolute top-3 right-3 w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100" :aria-label="t('shadaqaRutin.close')" @click="makeup = null"><Icon name="x" class="w-4 h-4 text-gray-500" /></button>
        <div class="w-16 h-16 rounded-full flex items-center justify-center mb-3" style="background: rgba(255, 107, 157, 0.15)"><span style="font-size: 32px">💔</span></div>
        <p class="text-base font-bold text-gray-900 mb-1">{{ t('shadaqaRutin.makeupTitle', { date: dateShort(makeup) }) }}</p>
        <p class="text-sm text-gray-600 leading-snug mb-1">{{ t('shadaqaRutin.makeupDesc', { amount: money((occs.find((o) => o.date === makeup) || s).amount) }) }}</p>
        <p class="text-[11px] text-gray-400 italic mb-5">{{ t('shadaqaRutin.makeupHadith') }}</p>
        <div class="grid grid-cols-2 gap-2 w-full">
          <button class="py-3 rounded-xl bg-gray-100 text-gray-700 text-sm font-semibold hover:bg-gray-200" @click="makeup = null">{{ t('shadaqaRutin.later') }}</button>
          <button class="py-3 rounded-xl text-white text-sm font-bold flex items-center justify-center gap-2" style="background: #005399" @click="goPay(makeup)"><Icon name="heart" class="w-4 h-4" style="fill: #ff6b9d; stroke: #ff6b9d" />{{ t('shadaqaRutin.makeupConfirm') }}</button>
        </div>
      </div>
    </div>
  </div>
  <BottomNav />
</template>
