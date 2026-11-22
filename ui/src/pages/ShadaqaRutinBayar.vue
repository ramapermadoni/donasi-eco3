<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Icon from '../components/Icon.vue'
import AppHeader from '../components/AppHeader.vue'
import BottomNav from '../components/BottomNav.vue'
import { t, lp, bcp } from '../i18n'
import { rpTight } from '../utils/format'
import { groupMethods, minFor } from '../utils/payment'
import payment from '../data/payment.json'
import { statusOf, canMakeup, markPaid, isISODate } from '../rutin'
import { loadRutin, saveRutin, nowISO } from '../rutinStore'
import { auth, loadMe } from '../auth'

// Bayar SIMULASI (Demo): tidak ada request ke sedekah.id; "berhasil" hanya menandai kejadian lokal (donationId berawalan demo-).
// Aturan: docs/reference/shadaqa-rutin-flow.md
const router = useRouter(), route = useRoute()
const today = nowISO()
const ready = ref(false)
const sched = ref(null)
const occ = ref(null) // kejadian yang bisa dibayar, atau null
const method = ref('')
const step = ref('choose') // choose | waiting
const paying = ref(false) // dikunci setelah klik pertama
const done = ref(false) // kunci anti klik ganda "Simulasikan berhasil"
const doa = ref('')
const date = computed(() => (typeof route.query.date === 'string' ? route.query.date : ''))
onMounted(async () => {
  await loadMe()
  if (!auth.user) { router.replace(lp('/akun?next=' + encodeURIComponent('/shadaqa-rutin/bayar' + (date.value ? '?date=' + date.value : '')))); return }
  const cur = loadRutin(auth.user.phone, today)
  if (!cur.schedule || cur.schedule.status === 'CANCELLED') { router.replace(lp('/shadaqa-rutin/setup')); return }
  sched.value = cur.schedule
  const o = isISODate(date.value) ? cur.occs.find((x) => x.date === date.value) : null
  occ.value = o && (statusOf(o, today) === 'DUE' || canMakeup(o, today)) ? o : null
  ready.value = true
})
const isMakeup = computed(() => !!occ.value && statusOf(occ.value, today) === 'MISSED')
const money = (n) => rpTight(n || 0, bcp())
const dateLong = (iso) => new Intl.DateTimeFormat(bcp(), { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }).format(new Date(iso + 'T00:00:00Z'))
const targetLabel = computed(() => (occ.value?.target?.type === 'campaign' ? occ.value.target.title || occ.value.target.slug : t('shadaqaRutin.targetPilihan')))
const groups = computed(() => groupMethods(payment))
const usable = (m) => !!occ.value && occ.value.amount >= minFor(m)
const method0 = computed(() => payment.find((m) => m.code === method.value))
function pick(m) { if (usable(m) && step.value === 'choose') method.value = m.code }
function pay() { if (paying.value || !method0.value || !usable(method0.value)) return; paying.value = true; step.value = 'waiting' }
const newDonationId = () => 'demo-' + (globalThis.crypto?.randomUUID?.() || Date.now().toString(36))
function simulate() {
  if (done.value) return // klik ganda: hanya yang pertama berlaku (markPaid juga idempoten)
  done.value = true
  try {
    const cur = loadRutin(auth.user.phone, today)
    saveRutin(auth.user.phone, cur.schedule, markPaid(cur.occs, occ.value.date, newDonationId(), today))
  } catch { /* tidak bisa dibayar (mis. tab lain sudah membayar): kembali saja */ }
  router.replace(lp('/shadaqa-rutin'))
}
</script>

<template>
  <div class="frame" style="background: #f5f6f8">
    <AppHeader />
    <div v-if="!ready" class="min-h-screen flex items-center justify-center bg-[#f5f6f8]">
      <div class="w-8 h-8 rounded-full border-4 border-gray-200 animate-spin" style="border-top-color: var(--lime)"></div>
    </div>

    <div v-else class="w-full max-w-[480px] mx-auto pt-3 pb-28">
      <div class="flex items-center gap-3 px-4 py-2 mb-2">
        <button class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors" :aria-label="t('shadaqaRutin.back')" @click="router.push(lp('/shadaqa-rutin'))"><Icon name="chevronLeft" class="w-5 h-5 text-gray-700" /></button>
        <span class="text-base font-bold text-[#1a1a1a]">{{ t('shadaqaRutin.bayarTitle') }}</span>
        <span data-t="demo-badge" class="ml-auto px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-700 border border-amber-300">{{ t('shadaqaRutin.demoBadge') }}</span>
      </div>

      <div v-if="!occ" data-t="not-payable" class="mx-3 rounded-2xl bg-white p-5 text-center" style="box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06)">
        <p class="text-sm text-gray-700 leading-snug">{{ t('shadaqaRutin.bayarNotPayable') }}</p>
        <button class="mt-4 w-full py-3 rounded-2xl text-sm font-bold bg-[color:var(--lime)] text-[#1a1a1a]" @click="router.push(lp('/shadaqa-rutin'))">{{ t('shadaqaRutin.bayarBack') }}</button>
      </div>

      <template v-else>
        <p class="mx-3 mb-3 text-[11px] text-amber-800 bg-amber-50 border border-amber-200 rounded-xl px-3 py-2">{{ t('shadaqaRutin.demoNote') }}</p>

        <div class="mx-3 rounded-2xl bg-white mb-3 overflow-hidden" style="box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06)">
          <div class="px-4 py-3 border-b border-gray-50 flex items-center justify-between">
            <span class="text-[13px] font-bold text-[#1a1a1a]">{{ t('shadaqaRutin.bayarSummary') }}</span>
            <span v-if="isMakeup" data-t="makeup-tag" class="text-[10px] font-bold px-2 py-0.5 rounded-full" style="background: rgba(255, 107, 157, 0.15); color: #c2185b">{{ t('shadaqaRutin.bayarMakeupTag') }}</span>
          </div>
          <div class="px-4 py-3 space-y-2 text-sm">
            <div class="flex justify-between"><span class="text-gray-500">{{ t('shadaqaRutin.nominalHeading') }}</span><b data-t="bayar-amount" class="text-gray-900">{{ money(occ.amount) }}</b></div>
            <div class="flex justify-between gap-3"><span class="text-gray-500">{{ t('shadaqaRutin.targetHeading') }}</span><b data-t="bayar-target" class="text-gray-900 text-right">{{ targetLabel }}</b></div>
            <div class="flex justify-between"><span class="text-gray-500">{{ t('shadaqaRutin.bayarDate') }}</span><b class="text-gray-900">{{ dateLong(occ.date) }}</b></div>
          </div>
        </div>

        <template v-if="step === 'choose'">
          <div class="mx-3 mb-3">
            <div class="rounded-xl bg-white px-4 py-3 border border-gray-100">
              <textarea v-model="doa" :placeholder="t('shadaqaRutin.doaPlaceholder')" rows="2" maxlength="500" class="w-full resize-none outline-none text-xs text-gray-700"></textarea>
            </div>
          </div>
          <div class="mx-3 rounded-2xl bg-white mb-3 px-4 py-3" style="box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06)">
            <p class="text-[13px] font-bold text-[#1a1a1a] mb-2">{{ t('shadaqaRutin.bayarMethodHeading') }}</p>
            <div v-for="g in groups" :key="g.type" class="mb-2">
              <p class="text-[11px] font-bold text-gray-400 tracking-wide mb-1.5">{{ t('paymentModal.type.' + g.type).toUpperCase() }}</p>
              <button v-for="m in g.items" :key="m.code" type="button" :data-t="'method-' + m.code" :disabled="!usable(m)" class="w-full flex items-center justify-between px-3 py-2.5 mb-1.5 rounded-xl border text-left text-sm transition-colors disabled:opacity-40" :class="method === m.code ? 'border-[color:var(--lime)] bg-[#f0f6fc]' : 'border-gray-200 bg-white'" @click="pick(m)">
                <span class="font-semibold text-gray-800">{{ m.name }}</span>
                <span v-if="!usable(m)" class="text-[10px] text-gray-400">{{ t('shadaqaRutin.bayarMinNote', { amount: money(minFor(m)) }) }}</span>
                <Icon v-else-if="method === m.code" name="check" class="w-4 h-4 text-[#005399]" />
              </button>
            </div>
          </div>
          <div class="mx-3">
            <button data-t="pay" class="w-full py-4 rounded-2xl text-sm font-bold bg-[#005399] text-[#1a1a1a] shadow-lg shadow-[#005399]/40 disabled:opacity-50 disabled:cursor-not-allowed" :disabled="!method || paying" @click="pay">{{ t('shadaqaRutin.bayarPay') }}</button>
            <p class="text-center mt-2 text-[10px] text-gray-400 italic">{{ t('shadaqaRutin.basmalah') }}</p>
          </div>
        </template>

        <div v-else data-t="waiting" class="mx-3 rounded-2xl bg-white p-6 text-center" style="box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06)">
          <div class="w-10 h-10 mx-auto rounded-full border-4 border-gray-200 animate-spin" style="border-top-color: var(--lime)"></div>
          <p class="mt-4 text-base font-bold text-gray-900">{{ t('shadaqaRutin.bayarWaitingTitle') }}</p>
          <p class="mt-1 text-sm text-gray-600 leading-snug">{{ t('shadaqaRutin.bayarWaitingDesc') }}</p>
          <button data-t="simulate" class="mt-5 w-full py-4 rounded-2xl text-sm font-bold bg-[#005399] text-[#1a1a1a] disabled:opacity-50" :disabled="done" @click="simulate">{{ t('shadaqaRutin.bayarSimulate') }}</button>
          <button class="mt-2 w-full py-3 rounded-2xl text-sm font-semibold bg-gray-100 text-gray-700" @click="router.push(lp('/shadaqa-rutin'))">{{ t('shadaqaRutin.bayarBack') }}</button>
        </div>
      </template>
    </div>
  </div>
  <BottomNav />
</template>
