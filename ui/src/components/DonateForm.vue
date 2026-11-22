<script setup>
import { ref, computed } from 'vue'
import Icon from './Icon.vue'
import payment from '../data/payment.json'
import { t, isEn } from '../i18n'
import { nf, shortRb, rpShort, parseDigits } from '../utils/format'
import { logo, minFor, groupMethods } from '../utils/payment'

const props = defineProps({
  presets: { type: Array, default: () => [10000, 25000, 50000, 100000] },
  // Replace with payment methods from your Frappe backend
  // payment methods from sedekah.id /api/payment/methods (replace with your gateway list)
  methods: { type: Array, default: () => payment },
  submitting: Boolean,
  // sheet: bentuk ringkas di bottom sheet halaman campaign (beda dari form beranda di sedekah.id)
  sheet: Boolean,
})
const emit = defineEmits(['submit'])

const codes = [['🇮🇩', '+62'], ['🇲🇾', '+60'], ['🇸🇬', '+65'], ['🇸🇦', '+966'], ['🇦🇪', '+971'], ['🇶🇦', '+974'], ['🇰🇼', '+965'], ['🇴🇲', '+968'], ['🇧🇭', '+973'], ['🇭🇰', '+852'], ['🇹🇼', '+886'], ['🇯🇵', '+81'], ['🇰🇷', '+82'], ['🇦🇺', '+61'], ['🇺🇸', '+1'], ['🇬🇧', '+44'], ['🇳🇱', '+31'], ['🇩🇪', '+49'], ['🇹🇷', '+90'], ['🇪🇬', '+20']]

const currency = ref('idr')
const amount = ref(25000)
const methodOpen = ref(false)
const focus = ref(false)
// sedekah.id memilih QRIS secara bawaan
const dflt = props.methods.find((m) => m.code === 'qris')
const method = ref(dflt ? dflt.name : '')
const methodCode = ref(dflt ? dflt.code : '')
const name = ref('')
const hide = ref(false)
const cc = ref('+62')
const phone = ref('')
const doa = ref('')
const chosen = computed(() => props.methods.find((m) => m.code === methodCode.value))

const amountText = computed({
  get: () => (amount.value ? nf(amount.value) : ''),
  set: (v) => { amount.value = parseDigits(v) },
})
// Teks form beranda: asli memakai string Inggris keras (bukan katalog) dengan pengecekan locale
const L = computed(() => (isEn.value
  ? { amount: 'Choose donation amount', other: 'Other amount', method: 'Payment Method', select: 'Select method', details: 'Your details', name: 'Full name', namePh: 'Your full name', hide: 'Donate anonymously', wa: 'WhatsApp No.', cc: 'Country code', waHint: 'Enter without the leading 0 (e.g. 812xxxx). Pick your country code if outside Indonesia.', msg: 'Message', opt: '(optional)', msgPh: 'Leave a note (optional)' }
  : { amount: 'Pilih Nominal Sedekah', other: 'Nominal Lain', method: 'Metode Pembayaran', select: 'Pilih Metode', details: 'Data Donatur', name: 'Nama Donatur', namePh: 'Nama Lengkap', hide: 'Sembunyikan nama saya (Teman Sedekah)', wa: 'No. WhatsApp', cc: 'Kode negara', waHint: 'Tanpa angka 0 di depan (cukup 812xxxx). Pilih kode negara bila di luar Indonesia.', msg: 'Tulis Doa', opt: '(opsional)', msgPh: 'Ya Allah, terimalah sedekah ini...' }))
const ctaSheet = computed(() => (isEn.value ? `Donate Rp ${short(amount.value || 0)} now` : `Donasi Rp ${short(amount.value || 0)} Sekarang`))
const amountEl = ref(null)
const ctaText = computed(() => { const n = nf(amount.value || 0); return isEn.value ? `Donate Rp${n} now` : `Sedekah Rp${n} Sekarang` })
const valid = computed(() => amount.value >= 1000 && phone.value.replace(/\D/g, '').length >= 8)
// minimal donasi per metode (sama dengan sedekah.id)
const short = shortRb
const rp = rpShort
const groups = computed(() => groupMethods(props.methods))
const expanded = ref({})

function pick(m) { method.value = m.name; methodCode.value = m.code; methodOpen.value = false }
function send() {
  if (!valid.value) return
  emit('submit', {
    currency: currency.value,
    amount: amount.value,
    method: method.value,
    method_code: methodCode.value,
    donor_name: hide.value ? 'Teman Sedekah' : name.value,
    hide_name: hide.value,
    whatsapp: cc.value + phone.value.replace(/\D/g, '').replace(/^0+/, ''),
    doa: doa.value,
  })
}
</script>

<template>
  <div :class="sheet ? 'max-w-[480px] mx-auto' : 'max-w-[480px] mx-auto sm:px-4 pb-4'" style="background: transparent">
    <div v-if="sheet">
      <div class="flex rounded-xl p-1 mb-3" style="background: #f3f4f6">
        <button class="flex-1 py-2 rounded-lg flex items-center justify-center gap-1.5 transition-all" style="background: #fff; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08); font-size: 12px; font-weight: 700; color: #111"><span style="font-size: 14px">🇮🇩</span> Rupiah</button>
        <button class="flex-1 py-2 rounded-lg flex items-center justify-center gap-1.5 transition-all" style="background: transparent; font-size: 12px; font-weight: 700; color: #6b7280"><Icon name="globe" class="w-3.5 h-3.5" /> International (USD)</button>
      </div>
      <div class="grid grid-cols-4 gap-2 mb-2.5">
        <button v-for="p in [10000, 25000, 50000, 100000, 150000, 250000]" :key="p" class="py-2 rounded-xl text-center transition-all text-[12px] font-semibold"
          :style="amount === p ? 'border:2px solid var(--lime-dark);background:#fff8ed;color:var(--lime-text)' : 'border:1.5px solid #e5e7eb;background:#fafafa;color:#374151'" @click="amount = p">Rp{{ short(p) }}</button>
        <button class="py-2 rounded-xl text-center transition-all text-[12px] font-semibold" style="border: 1.5px solid #e5e7eb; background: #fafafa; color: #374151" @click="amount = 0; amountEl.focus()">Nominal lainnya</button>
      </div>
      <div class="flex items-center rounded-xl px-3 py-2.5 mb-4 transition-all" :style="focus ? 'border:2px solid var(--lime-dark);background:#fff8ed' : 'border:1.5px solid #e5e7eb;background:#fafafa'">
        <span class="text-[13px] text-gray-400 mr-2">Rp</span>
        <input ref="amountEl" type="text" inputmode="numeric" class="flex-1 bg-transparent outline-none text-[15px] font-bold text-gray-900" :placeholder="isEn ? L.other : 'Nominal lain'" v-model="amountText" @focus="focus = true" @blur="focus = false" />
      </div>
      <p class="text-[12px] font-semibold text-gray-700 mb-2">{{ L.method }}</p>
      <button type="button" class="flex items-center gap-3 w-full px-4 py-3 rounded-xl mb-3 transition-all active:scale-[0.99]" style="border: 2px solid var(--lime-dark); background: #fff8ed" @click="methodOpen = true">
        <img v-if="chosen" :src="logo(chosen)" :alt="chosen.name" class="w-7 h-7 object-contain rounded" />
        <span class="text-[13px] font-bold text-[color:var(--lime-text)] flex-1 text-left">{{ method || L.select }}</span>
        <Icon name="chevronRight" class="w-4 h-4 flex-shrink-0" style="color: var(--lime-dark)" />
      </button>
      <input class="w-full px-3 py-2.5 rounded-xl border border-gray-200 outline-none bg-gray-50 focus:border-[color:var(--lime-dark)] transition-colors text-[14px] mb-2" type="text" :placeholder="isEn ? 'Full name *' : 'Nama donatur (opsional)'" v-model="name" />
      <label class="flex items-center gap-2 mb-3 cursor-pointer select-none w-fit"><input type="checkbox" class="w-3.5 h-3.5 rounded accent-[color:var(--lime-dark)] cursor-pointer flex-shrink-0" v-model="hide" /><span class="text-[11px] text-gray-500 font-medium">{{ isEn ? 'Donate anonymously' : 'Sembunyikan nama saya (Teman Sedekah)' }}</span></label>
      <div class="flex rounded-xl border border-gray-200 overflow-hidden focus-within:border-[color:var(--lime-dark)] transition-colors mb-3">
        <span class="pl-3 pr-1 bg-gray-100 border-r border-gray-200 flex items-center gap-1 text-[13px] text-gray-600 flex-shrink-0">
          <Icon name="smartphone" class="w-3.5 h-3.5" />
          <select :aria-label="L.cc" class="bg-transparent outline-none cursor-pointer py-2.5" style="font-size: 13px; color: #374151" v-model="cc"><option v-for="c in codes" :key="c[1]" :value="c[1]">{{ c[0] }} {{ c[1] }}</option></select>
        </span>
        <input type="tel" inputmode="numeric" class="flex-1 px-3 py-2.5 outline-none bg-gray-50 text-[14px] min-w-0" placeholder="812-xxxx-xxxx *" v-model="phone" />
      </div>
      <textarea rows="2" class="w-full px-3 py-2.5 rounded-xl border border-gray-200 outline-none bg-gray-50 focus:border-[color:var(--lime-dark)] transition-colors resize-none text-[13px] text-gray-800 mb-4" style="line-height: 1.5" :placeholder="isEn ? L.msgPh : 'Tulis doa... (opsional)'" v-model="doa"></textarea>
      <button class="w-full py-4 rounded-2xl font-bold text-[15px] transition-all active:scale-[0.98] flex items-center justify-center gap-2 disabled:cursor-not-allowed"
        :style="valid && !submitting ? 'background: linear-gradient(135deg, var(--lime-dark) 0%, var(--lime) 100%); color: #fff; box-shadow: 0 6px 24px color-mix(in srgb, var(--lime) 40%, transparent)' : 'background: #d1d5db; color: #fff; box-shadow: none'"
        :disabled="!valid || submitting" @click="send">{{ ctaSheet }}</button>
    </div>
    <div v-else class="bg-white sm:rounded-2xl overflow-hidden" style="box-shadow: 0 2px 16px rgba(0, 0, 0, 0.07)">
      <div class="p-4 space-y-5">
        <div class="flex rounded-xl p-1" style="background: #f3f4f6">
          <button class="flex-1 py-2 rounded-lg flex items-center justify-center gap-1.5 transition-all"
            :style="'font-size:12px;font-weight:700;' + (currency === 'idr' ? 'background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.08);color:#111' : 'background:transparent;box-shadow:none;color:#6b7280')" @click="currency = 'idr'"><span style="font-size: 14px">🇮🇩</span> Rupiah</button>
          <button class="flex-1 py-2 rounded-lg flex items-center justify-center gap-1.5 transition-all"
            :style="'font-size:12px;font-weight:700;' + (currency === 'intl' ? 'background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.08);color:#111' : 'background:transparent;box-shadow:none;color:#6b7280')" @click="currency = 'intl'"><Icon name="globe" class="w-3.5 h-3.5" /> International</button>
        </div>

        <div>
          <p style="font-size: 12px; font-weight: 600; color: #374151; margin-bottom: 10px">{{ L.amount }}</p>
          <div class="grid grid-cols-4 gap-2 mb-2.5">
            <button v-for="p in presets" :key="p" class="py-2 rounded-xl text-center transition-all"
              :style="'font-size:12px;font-weight:600;' + (amount === p ? 'border:2px solid var(--lime-dark);background:#fff8ed;color:var(--lime-text)' : 'border:1.5px solid #e5e7eb;background:#fafafa;color:#374151')" @click="amount = p">Rp{{ short(p) }}</button>
          </div>
          <label class="flex items-center rounded-xl px-3 py-2.5 transition-all" :style="focus ? 'border:2px solid var(--lime-dark);background:#fff8ed' : 'border:1.5px solid #e5e7eb;background:#fafafa'">
            <span style="font-size: 13px; color: #9ca3af; margin-right: 6px">Rp</span>
            <input type="text" inputmode="numeric" class="flex-1 bg-transparent outline-none" style="font-size: 15px; font-weight: 700; color: #111" :placeholder="isEn ? L.other : 'Nominal lain'" v-model="amountText" @focus="focus = true" @blur="focus = false" />
            <span style="font-size: 11px; color: var(--lime-dark); font-weight: 600">{{ L.other }}</span>
          </label>
        </div>

        <div v-if="currency === 'idr'">
          <p style="font-size: 12px; font-weight: 600; color: #374151; margin-bottom: 10px">{{ L.method }}</p>
          <button class="flex items-center gap-3 w-full px-4 py-3 rounded-xl transition-all active:scale-[0.99]" style="border: 2px solid var(--lime-dark); background: #fff8ed" @click="methodOpen = true">
            <div v-if="chosen" class="relative w-10 h-7 flex-shrink-0"><img :src="logo(chosen)" :alt="chosen.name" class="absolute inset-0 w-full h-full object-contain" /></div>
            <span style="font-size: 13px; font-weight: 700; color: var(--lime-text); flex: 1; text-align: left">{{ method || L.select }}</span>
            <Icon name="chevronRight" class="w-4 h-4 flex-shrink-0" style="color: var(--lime-dark)" />
          </button>
        </div>

        <div>
          <div class="flex items-center justify-between mb-2.5">
            <p style="font-size: 12px; font-weight: 600; color: #374151">{{ currency === 'idr' ? L.details : 'Your details' }}</p>
          </div>
          <div class="space-y-3">
            <div>
              <label style="font-size: 11px; color: #9ca3af; font-weight: 500" class="flex items-center gap-1">{{ L.name }}</label>
              <input class="w-full mt-1 px-3 py-2.5 rounded-xl border border-gray-200 outline-none transition-colors" style="font-size: 14px; color: #111; background: #fafafa; cursor: text" type="text" :placeholder="L.namePh" v-model="name" />
              <label class="flex items-center gap-2 mt-2 select-none w-fit cursor-pointer"><input type="checkbox" class="w-3.5 h-3.5 rounded accent-[color:var(--lime-dark)] cursor-pointer flex-shrink-0" v-model="hide" /><span style="font-size: 11px; color: #6b7280; font-weight: 500">{{ L.hide }}</span></label>
            </div>
            <div>
              <label style="font-size: 11px; color: #9ca3af; font-weight: 500" class="flex items-center gap-1">{{ L.wa }} <span style="color: #f59e0b">*</span></label>
              <div class="flex mt-1 rounded-xl border border-gray-200 overflow-hidden focus-within:border-[color:var(--lime-dark)] transition-colors">
                <span class="pl-3 pr-1.5 bg-gray-100 flex items-center gap-1 border-r border-gray-200 flex-shrink-0" style="color: #374151">
                  <Icon name="smartphone" class="w-3.5 h-3.5" />
                  <select :aria-label="L.cc" class="bg-transparent outline-none cursor-pointer py-2.5" style="font-size: 13px; color: #374151" v-model="cc">
                    <option v-for="c in codes" :key="c[1]" :value="c[1]">{{ c[0] }} {{ c[1] }}</option>
                  </select>
                </span>
                <input type="tel" inputmode="numeric" class="flex-1 px-3 py-2.5 outline-none min-w-0" style="font-size: 14px; color: #111; background: #f9fafb; cursor: text" placeholder="812-xxxx-xxxx" v-model="phone" />
              </div>
              <p style="font-size: 11px; color: #9ca3af; margin-top: 4px">{{ L.waHint }}</p>
            </div>
            <div>
              <label style="font-size: 11px; color: #9ca3af; font-weight: 500">{{ L.msg }} <span style="color: #d1d5db">{{ L.opt }}</span></label>
              <textarea rows="3" class="w-full mt-1 px-3 py-2.5 rounded-xl border border-gray-200 outline-none bg-gray-50 transition-colors resize-none" style="font-size: 13px; color: #111; line-height: 1.5" :placeholder="L.msgPh" v-model="doa"></textarea>
            </div>
            <button class="w-full py-4 rounded-2xl font-bold transition-all active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              style="background: linear-gradient(135deg, var(--lime-dark) 0%, var(--lime) 100%); color: #fff; font-size: 15px; font-weight: 700; box-shadow: 0 6px 24px color-mix(in srgb, var(--lime) 40%, transparent)"
              :disabled="submitting" @click="send">{{ ctaText }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom sheet metode pembayaran (sama dengan PaymentMethodModal sedekah.id) -->
    <div v-if="methodOpen" class="fixed inset-0 z-50 flex items-end justify-center" style="background: rgba(0, 0, 0, 0.45)" @click="methodOpen = false">
      <div class="w-full max-w-[480px] bg-white rounded-3xl overflow-hidden" style="max-height: calc(85vh - 76px); margin-bottom: 76px; display: flex; flex-direction: column" @click.stop>
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 flex-shrink-0">
          <span style="font-size: 15px; font-weight: 700; color: #111">{{ t('paymentModal.title') }}</span>
          <button class="w-8 h-8 rounded-full flex items-center justify-center" style="background: #f3f4f6" @click="methodOpen = false"><Icon name="x" class="w-4 h-4 text-gray-500" /></button>
        </div>
        <div class="overflow-y-auto flex-1 px-4 py-4 space-y-5">
          <p v-if="!groups.length" style="font-size: 13px; color: #9ca3af; text-align: center; padding: 40px 0">{{ t('paymentModal.empty') }}</p>
          <div v-for="g in groups" :key="g.type">
            <p style="font-size: 11px; font-weight: 700; color: #9ca3af; letter-spacing: 0.06em; margin-bottom: 10px">{{ t('paymentModal.type.' + g.type).toUpperCase() }}</p>
            <div class="space-y-2">
              <button v-for="m in (expanded[g.type] ? g.items : g.items.slice(0, 3))" :key="m.code" :disabled="amount > 0 && amount < minFor(m)" @click="pick(m)"
                class="flex items-center gap-3 w-full px-4 py-3 rounded-xl transition-all" :class="amount > 0 && amount < minFor(m) ? 'cursor-not-allowed' : 'active:scale-[0.98] cursor-pointer'"
                :style="{ border: methodCode === m.code ? '2px solid var(--lime-dark)' : '1.5px solid #e5e7eb', background: amount > 0 && amount < minFor(m) ? '#f5f5f5' : methodCode === m.code ? '#fff8ed' : '#fafafa', opacity: amount > 0 && amount < minFor(m) ? 0.55 : 1 }">
                <div class="relative w-10 h-7 flex-shrink-0" :style="amount > 0 && amount < minFor(m) ? 'filter:grayscale(1)' : ''"><img :src="logo(m)" :alt="m.name" class="absolute inset-0 w-full h-full object-contain" /></div>
                <div class="flex-1 min-w-0 text-left">
                  <span :style="'font-size:13px;font-weight:600;display:block;color:' + (amount > 0 && amount < minFor(m) ? '#9ca3af' : methodCode === m.code ? 'var(--lime-text)' : '#374151')">{{ m.name }}</span>
                  <span v-if="amount > 0 && amount < minFor(m)" style="font-size: 10px; color: #9ca3af">{{ t('paymentModal.min', { amount: rp(minFor(m)) }) }}</span>
                </div>
                <span v-if="methodCode === m.code && !(amount > 0 && amount < minFor(m))" class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0" style="background: var(--lime-dark)"><Icon name="check" class="w-3 h-3 text-white" /></span>
              </button>
            </div>
            <button v-if="g.items.length > 3" class="flex items-center justify-center gap-1.5 w-full mt-2 py-2 rounded-xl transition-colors" style="font-size: 12px; font-weight: 600; color: var(--lime-text); background: #fff8ed" @click="expanded[g.type] = !expanded[g.type]">
              <template v-if="expanded[g.type]"><Icon name="chevronUp" class="w-3.5 h-3.5" />{{ t('paymentModal.hide') }}</template>
              <template v-else><Icon name="chevronDown" class="w-3.5 h-3.5" />{{ t('paymentModal.moreMethods', { count: g.items.length - 3 }) }}</template>
            </button>
          </div>
          <div class="h-2"></div>
        </div>
      </div>
    </div>
  </div>
</template>
