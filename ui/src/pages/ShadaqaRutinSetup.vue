<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Icon from '../components/Icon.vue'
import AppHeader from '../components/AppHeader.vue'
import BottomNav from '../components/BottomNav.vue'
import { t, lp, bcp } from '../i18n'
import { pad2, rpTight, parseDigits, nf } from '../utils/format'
import data from '../data/sedekah'
import { MIN_AMOUNT, makeSchedule, editSchedule, syncOccurrences, isISODate } from '../rutin'
import { loadRutin, nowISO } from '../rutinStore'
import { auth, setRecurring, loadMe } from '../auth'

// Setup jadwal rancangan sendiri: disimpan hanya di localStorage lewat rutinStore (tanpa request ke sedekah.id).
// Metode bayar TIDAK dipilih di sini: dipilih saat membayar tiap pengingat. Aturan: docs/reference/shadaqa-rutin-flow.md
const router = useRouter(), route = useRoute()
const ready = ref(false)
const init = ref(null) // jadwal yang ada => mode ubah
const initOccs = ref([])
const today = nowISO()
const campaigns = (data.campaigns || []).filter((c) => c.slug && c.title)
onMounted(async () => {
  await loadMe()
  if (!auth.user) { router.replace(lp('/akun?next=' + encodeURIComponent('/shadaqa-rutin/setup'))); return } // situs asli: tamu diarahkan ke layar masuk
  const cur = loadRutin(auth.user.phone, today)
  init.value = cur.schedule && cur.schedule.status !== 'CANCELLED' ? cur.schedule : null
  initOccs.value = cur.occs
  const e = init.value, sg = route.query.suggest
  if (e) {
    freq.value = e.frequency; startDate.value = e.startDate; hour.value = pad2(e.hourLocal) + ':00'
    chip.value = QUICK.includes(e.amount) ? e.amount : 0; amtText.value = nf(e.amount, bcp())
    target.value = e.target?.type === 'campaign' ? e.target.slug : ''; anon.value = !!e.isAnonymous
    wa.value = !!e.reminders?.wa; em.value = !!e.reminders?.email
  } else if (['DAILY', 'WEEKLY', 'MONTHLY'].includes(sg)) freq.value = sg
  ready.value = true
})
const QUICK = [5000, 10000, 25000]
const inp = 'w-full rounded-xl border border-gray-200 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[color:color-mix(in_srgb,var(--lime)_30%,transparent)] focus:border-[color:var(--lime)] transition-colors'
const cats = computed(() => [['DAILY', 'Daily', 'Day'], ['WEEKLY', 'Weekly', 'Week'], ['MONTHLY', 'Monthly', 'Month']].map(([id, f, u]) => ({ id, label: t('shadaqaRutin.freq' + f), unit: t('shadaqaRutin.unit' + u) })))
const freq = ref(''), startDate = ref(today), hour = ref('08:00')
const chip = ref(5000), amtText = ref('5.000')
const target = ref(''), anon = ref(false)
const wa = ref(false), em = ref(false), phoneIn = ref('')
const busy = ref(false), err = ref('')
const isEdit = computed(() => !!init.value)
const needPhone = computed(() => !auth.user?.phone)
const email = computed(() => auth.user?.email || '')
const cat = computed(() => cats.value.find((c) => c.id === freq.value))
const amount = computed(() => (chip.value > 0 ? chip.value : parseDigits(amtText.value)))
function pickChip(p) { chip.value = p; amtText.value = nf(p, bcp()) }
function typeAmt(e) { const d = e.target.value.replace(/\D/g, ''); amtText.value = d ? nf(parseInt(d, 10), bcp()) : ''; chip.value = 0 }

// Validasi murni: kembalikan pesan galat (sudah lewat t()) atau ''.
function validate() {
  if (!Number.isFinite(amount.value) || amount.value < MIN_AMOUNT) return t('shadaqaRutin.errAmount', { min: rpTight(MIN_AMOUNT, bcp()) })
  if (!['DAILY', 'WEEKLY', 'MONTHLY'].includes(freq.value)) return t('shadaqaRutin.errFreq')
  if (!isISODate(startDate.value) || (!isEdit.value && startDate.value < today)) return t('shadaqaRutin.errStart')
  if (needPhone.value && wa.value && phoneIn.value.length < 9) return t('shadaqaRutin.errPhone')
  return ''
}
async function submit() {
  if (busy.value) return
  err.value = validate()
  if (err.value) return
  busy.value = true
  try {
    const camp = campaigns.find((c) => c.slug === target.value)
    const tgt = camp ? { type: 'campaign', slug: camp.slug, title: camp.title } : { type: 'pilihan' }
    const base = { frequency: freq.value, startDate: startDate.value, hourLocal: parseInt(hour.value, 10), amount: amount.value, target: tgt, isAnonymous: anon.value, reminders: { bell: true, wa: wa.value, email: em.value } }
    if (init.value) {
      const r = editSchedule(init.value, base, initOccs.value, today)
      await setRecurring(r.schedule, r.occs)
    } else {
      const sch = makeSchedule(base, today)
      await setRecurring(sch, syncOccurrences(sch, [], today))
    }
    router.push(lp('/shadaqa-rutin'))
  } catch { err.value = isEdit.value ? t('shadaqaRutin.errUpdateFailed') : t('shadaqaRutin.errCreateFailed'); busy.value = false }
}
</script>

<template>
  <div class="frame" style="background: #fff">
    <AppHeader />
    <div v-if="!ready || !auth.user" class="min-h-screen flex items-center justify-center bg-[#f5f6f8]">
      <div class="w-8 h-8 rounded-full border-4 border-gray-200 animate-spin" style="border-top-color: var(--lime)"></div>
    </div>

    <div v-else class="min-h-screen max-w-[480px] mx-auto bg-white relative pb-32">
      <div class="flex items-center gap-3 px-4 py-4 border-b border-gray-100 sticky top-0 bg-white z-10">
        <button class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors" :aria-label="t('shadaqaRutin.back')" @click="router.back()"><Icon name="chevronLeft" class="w-5 h-5 text-gray-700" /></button>
        <span class="text-base font-bold text-[#1a1a1a]">{{ isEdit ? t('shadaqaRutin.editTitle') : t('shadaqaRutin.setupTitle') }}</span>
      </div>

      <div class="px-4 py-4">
        <div class="rounded-xl p-3 mb-5 flex gap-2 bg-[#005399]/8 border border-[#005399]/30">
          <Icon name="alertCircle" class="w-4 h-4 flex-shrink-0 mt-0.5 text-[#005399]" />
          <div>
            <p class="text-xs font-bold text-[#005399] mb-0.5">{{ t('shadaqaRutin.infoTitle') }}</p>
            <p class="text-[11px] text-gray-700 leading-relaxed">{{ t('shadaqaRutin.categoryLabel') }} <span class="text-[#005399] font-semibold">{{ cat ? t('shadaqaRutin.categoryInfo', { label: cat.label, unit: cat.unit }) : t('shadaqaRutin.categoryPrompt') }}</span></p>
            <p data-t="explain" class="text-[11px] text-gray-700 leading-relaxed mt-1">{{ t('shadaqaRutin.setupExplain') }}</p>
          </div>
        </div>

        <p class="text-sm font-bold text-[#1a1a1a] mb-2.5">{{ t('shadaqaRutin.scheduleHeading') }}</p>
        <div class="space-y-2.5 mb-5">
          <div class="relative">
            <select v-model="freq" data-t="freq" :class="[inp, 'appearance-none', freq ? 'text-gray-700' : 'text-gray-400']">
              <option value="" disabled>{{ t('shadaqaRutin.categoryPlaceholder') }}</option>
              <option v-for="c in cats" :key="c.id" :value="c.id">{{ c.label }}</option>
            </select>
            <Icon name="chevronDown" class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
          <label class="block text-[11px] text-gray-500 -mb-1">{{ t('shadaqaRutin.startLabel') }}</label>
          <input type="date" v-model="startDate" data-t="start" :min="isEdit ? undefined : today" :class="inp" />
          <div class="relative">
            <select v-model="hour" data-t="hour" :class="[inp, 'appearance-none', hour ? 'text-gray-700' : 'text-gray-400']">
              <option value="" disabled>{{ t('shadaqaRutin.hourPlaceholder') }}</option>
              <option v-for="h in 24" :key="h" :value="pad2(h - 1) + ':00'">{{ pad2(h - 1) }}:00</option>
            </select>
            <Icon name="chevronDown" class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          </div>
        </div>

        <p class="text-sm font-bold text-[#1a1a1a] mb-2.5">{{ t('shadaqaRutin.amountHeading') }}</p>
        <div class="grid grid-cols-3 gap-2 mb-2.5">
          <button v-for="p in QUICK" :key="p" type="button" class="py-2.5 rounded-xl border text-xs font-semibold transition-all" :class="chip === p ? 'bg-[#005399] text-white border-[#005399]' : 'bg-white text-gray-700 border-gray-200 hover:border-[#005399]'" @click="pickChip(p)">{{ t('shadaqaRutin.chipAmount', { n: p / 1000 }) }}</button>
        </div>
        <div class="flex items-center gap-2 px-4 py-3 rounded-xl border border-gray-200 mb-1 focus-within:border-[#005399] focus-within:ring-2 focus-within:ring-[#005399]/30">
          <span class="text-sm font-semibold text-gray-700">Rp</span>
          <input type="text" inputmode="numeric" data-t="amount" :value="amtText" class="flex-1 text-right outline-none text-sm text-gray-700 bg-transparent" @input="typeAmt" />
        </div>
        <p class="text-[11px] text-gray-400 mb-5">{{ t('shadaqaRutin.amountMinHint', { min: rpTight(MIN_AMOUNT, bcp()) }) }}</p>

        <p class="text-sm font-bold text-[#1a1a1a] mb-2.5">{{ t('shadaqaRutin.targetHeading') }}</p>
        <div class="relative mb-3">
          <select v-model="target" data-t="target" :class="[inp, 'appearance-none text-gray-700']">
            <option value="">{{ t('shadaqaRutin.targetPilihan') }}</option>
            <option v-for="c in campaigns" :key="c.slug" :value="c.slug">{{ c.title }}</option>
          </select>
          <Icon name="chevronDown" class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        </div>
        <button type="button" data-t="anon" class="flex items-center gap-3 mb-5" @click="anon = !anon">
          <div class="w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-all" :class="anon ? 'bg-[#005399] border-[#005399]' : 'border-gray-300 bg-white'"><Icon v-if="anon" name="check" class="w-3 h-3 text-white" /></div>
          <span class="text-sm text-gray-700">{{ t('shadaqaRutin.anonLabel') }}</span>
        </button>

        <p class="text-sm font-bold text-[#1a1a1a] mb-2.5">{{ t('shadaqaRutin.remindHeading') }}</p>
        <div data-t="remind-bell" aria-disabled="true" class="flex items-center gap-3 opacity-80">
          <div class="w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 bg-[#005399] border-[#005399]"><Icon name="check" class="w-3 h-3 text-white" /></div>
          <div class="flex flex-col items-start">
            <span class="text-sm text-gray-700">{{ t('shadaqaRutin.remindBell') }}</span>
            <span class="text-[10px] text-gray-400">{{ t('shadaqaRutin.remindBellNote') }}</span>
          </div>
        </div>
        <button type="button" data-t="remind-wa" class="flex items-center gap-3 mt-3" @click="wa = !wa">
          <div class="w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-all" :class="wa ? 'bg-[#005399] border-[#005399]' : 'border-gray-300 bg-white'"><Icon v-if="wa" name="check" class="w-3 h-3 text-white" /></div>
          <div class="flex flex-col items-start">
            <span class="text-sm text-gray-700">{{ t('shadaqaRutin.remindWa') }}</span>
            <span class="text-[10px] text-gray-400">{{ t('shadaqaRutin.remindWaNote') }}</span>
          </div>
        </button>
        <div v-if="needPhone && wa" class="mt-3">
          <div class="flex items-center rounded-xl border border-gray-200 overflow-hidden focus-within:border-[#005399] focus-within:ring-2 focus-within:ring-[#005399]/30">
            <span class="px-3 py-3 bg-gray-100 text-sm font-semibold text-gray-600 border-r border-gray-200 flex-shrink-0">+62</span>
            <input type="tel" data-t="phone" :value="phoneIn" placeholder="812xxxxxxxx" class="flex-1 px-3 py-3 text-sm outline-none bg-transparent" @input="phoneIn = $event.target.value.replace(/\D/g, '')" />
          </div>
          <p class="text-[11px] text-gray-400 mt-1.5">{{ t('shadaqaRutin.whatsappNote') }}</p>
        </div>
        <button type="button" data-t="remind-email" :disabled="!email" class="flex items-center gap-3 mt-3 disabled:opacity-50 disabled:cursor-not-allowed" @click="em = !em">
          <div class="w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-all" :class="em ? 'bg-[#005399] border-[#005399]' : 'border-gray-300 bg-white'"><Icon v-if="em" name="check" class="w-3 h-3 text-white" /></div>
          <div class="flex flex-col items-start">
            <span class="text-sm text-gray-700">{{ t('shadaqaRutin.remindEmail') }}</span>
            <span class="text-[10px] text-gray-400">{{ email ? t('shadaqaRutin.remindEmailTo', { email }) : t('shadaqaRutin.remindEmailMissing') }}</span>
          </div>
        </button>

        <div v-if="err" data-t="err" role="alert" class="mt-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2.5">{{ err }}</div>
      </div>

      <div class="fixed bottom-0 left-0 right-0 max-w-[480px] mx-auto px-4 pb-24 pt-3 bg-white border-t border-gray-100">
        <button data-t="save" class="w-full py-4 rounded-2xl flex items-center justify-center gap-2 transition-all text-sm font-bold bg-[#005399] text-white hover:bg-[#003f75] shadow-lg shadow-[#005399]/40" :disabled="busy" @click="submit">
          <template v-if="busy"><Icon name="loader" class="w-4 h-4 animate-spin" /> {{ t('shadaqaRutin.processing') }}</template>
          <template v-else>{{ isEdit ? t('shadaqaRutin.saveChanges') : t('shadaqaRutin.createRecurring') }} <Icon name="bell" class="w-4 h-4" /></template>
        </button>
      </div>
    </div>
  </div>
  <BottomNav />
</template>
