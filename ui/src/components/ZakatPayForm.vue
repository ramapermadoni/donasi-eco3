<script setup>
// ZakatPayForm asli: form bayar zakat/wakaf (juga dipakai kalkulator). Tidak ada i18n di halaman; hanya sheet metode bayar (paymentModal.*).
import { lsGet, lsSet } from '../utils/storage'
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import Icon from './Icon.vue'
import payment from '../data/payment.json'
import { t, lp, bcp } from '../i18n'
import { rpSp, rpTight, localPhone } from '../utils/format'
import { postJson } from '../utils/net'
import { minFor, groupMethods } from '../utils/payment'
import { penandaDonasi } from '../donate'

const props = defineProps({ campaignId: String, campaignTitle: String, amount: Number, ctaLabel: { type: String, default: 'Tunaikan' }, footerNote: { type: String, default: 'Rincian pengelolaan dana ada di Syarat & Ketentuan.' } })
const router = useRouter()
const KEY = 'sedekah_donor_v1'
const rp = rpSp
const rpT = (n) => rpTight(n, bcp())
const FLAGS = [['id', 'Indonesia'], ['th', 'Thailand'], ['my', 'Malaysia'], ['sg', 'Singapore'], ['jp', 'Japan'], ['kr', 'South Korea'], ['cn', 'China']]
const isQris = (m) => m.code.toLowerCase() === 'qris' || m.type === 'qris'
const norm = (e) => { const a = e.replace(/\D/g, ''); return a.startsWith('62') ? a.slice(2) : a.replace(/^0/, '') }

const name = ref(''), phone = ref(''), anon = ref(false), method = ref('')
const methods = ref([]), showModal = ref(false), busy = ref(false), err = ref('')
const input = 'w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-[var(--lime)]'
const lab = 'block text-sm font-medium text-gray-700 mb-1.5'

onMounted(() => {
  try {
    const s = JSON.parse(lsGet(KEY) || 'null')
    if (s) {
      if (s.name) name.value ||= s.name
      if (s.whatsapp) phone.value ||= norm(String(s.whatsapp))
      if (typeof s.isAnonymous === 'boolean') anon.value = s.isAnonymous
      if (s.paymentMethod) method.value ||= s.paymentMethod
    }
  } catch {}
  fetch('/api/auth/me').then((r) => (r.ok ? r.json() : null)).then((a) => {
    if (a?.user) { if (a.user.name) name.value ||= a.user.name; if (a.user.phone) phone.value ||= norm(String(a.user.phone)) }
  }).catch(() => {})
})

const sel = computed(() => methods.value.find((m) => m.code === method.value) || null)
const minAmt = computed(() => (sel.value ? minFor(sel.value) : 0))
const okMin = computed(() => !sel.value || props.amount >= minAmt.value)
const canPay = computed(() => props.amount > 0 && !!method.value && okMin.value && !busy.value)

const groups = computed(() => groupMethods(methods.value))
const expanded = ref({})
const off = (m) => props.amount > 0 && props.amount < minFor(m)

async function openModal() {
  if (!methods.value.length) {
    try { const j = await fetch('/api/payment/methods').then((r) => r.json()); methods.value = j.methods || [] } catch {}
    if (!methods.value.length) methods.value = payment
    const g = groups.value.find((x) => x.items.slice(3).some((m) => m.code === method.value)); if (g) expanded.value[g.type] = true
  }
  showModal.value = true
}
const close = () => { showModal.value = false }
const choose = (m) => { method.value = m.code; showModal.value = false }
onBeforeUnmount(() => { document.body.style.overflow = '' })
watch(showModal, (v) => { document.body.style.overflow = v ? 'hidden' : '' })

async function submit() {
  err.value = ''
  const nm = name.value.trim()
  if (nm.length < 2) { err.value = 'Nama minimal 2 karakter.'; return }
  const p = localPhone(phone.value)
  if (p.length < 8) { err.value = 'Nomor WhatsApp tidak valid.'; return }
  if (!method.value) { err.value = 'Pilih metode pembayaran dulu.'; return }
  if (!okMin.value) { err.value = `Metode ini minimal ${rp(minAmt.value)}.`; return }
  const donor_phone = '+62' + p
  try { let o = {}; try { o = JSON.parse(lsGet(KEY) || '{}') || {} } catch {}; lsSet(KEY, JSON.stringify({ ...o, name: nm, whatsapp: p, isAnonymous: anon.value, paymentMethod: method.value })) } catch {}
  busy.value = true
  try {
    const { r, j: b } = await postJson('/api/donations', { campaign_id: props.campaignId, currency: 'IDR', amount: props.amount, donor_name: nm, donor_phone, is_anonymous: anon.value, type: 'one_time', ...penandaDonasi() })
    if (!r.ok) { err.value = b.error ?? 'Gagal memproses.'; return }
    const { r: r2, j: b2 } = await postJson('/api/payment/create', { donation_id: b.donation_id, payment_method: method.value, donor_name: nm, donor_phone, campaign_title: props.campaignTitle, amount: props.amount })
    if (!r2.ok) { err.value = b2.error ?? 'Gagal membuat pembayaran. Coba metode lain.'; return }
    router.push('/donasi/' + b.donation_id)
  } catch { err.value = 'Terjadi kesalahan. Coba lagi.' } finally { busy.value = false }
}
</script>

<template>
  <div class="bg-white rounded-2xl border border-gray-100 p-5 space-y-4">
    <p class="text-sm font-bold text-gray-900">{{ campaignTitle }}</p>
    <div><label :class="lab">Nama</label><input v-model="name" placeholder="Nama kamu" :class="input" /></div>
    <div>
      <label :class="lab">WhatsApp</label>
      <div class="flex items-center gap-2">
        <span class="px-3 py-2.5 rounded-lg bg-gray-100 text-sm text-gray-500">+62</span>
        <input v-model="phone" inputmode="numeric" placeholder="81234567890" :class="input" />
      </div>
    </div>
    <div>
      <label :class="lab">Metode Pembayaran</label>
      <button type="button" class="flex items-center gap-3 w-full px-4 py-3 rounded-xl transition-all active:scale-[0.99]"
        :style="{ border: method ? '2px solid var(--lime-dark)' : '1.5px solid #e5e7eb', background: method ? '#fff8ed' : '#fafafa' }" @click="openModal">
        <template v-if="sel">
          <img :src="logo(sel)" :alt="sel.name" class="w-7 h-7 object-contain rounded" @error="$event.target.style.display = 'none'" />
          <span class="text-[13px] font-bold text-[color:var(--lime-text)] flex-1 text-left">{{ sel.name }}</span>
          <Icon name="check" class="w-4 h-4 text-[color:var(--lime-dark)]" />
        </template>
        <span v-else class="text-[13px] font-semibold text-gray-500 flex-1 text-left">Pilih metode pembayaran</span>
        <Icon name="chevronRight" class="w-4 h-4 flex-shrink-0 text-gray-400" />
      </button>
      <p v-if="sel && !okMin" class="mt-1.5 text-[11px] text-amber-600">Metode ini minimal {{ rp(minAmt) }}. Pilih QRIS/e-wallet untuk nominal kecil.</p>
    </div>
    <label class="flex items-center gap-2 text-sm text-gray-600"><input v-model="anon" type="checkbox" class="accent-[color:var(--lime)]" /> Tampilkan sebagai anonim (Hamba Allah)</label>
    <div v-if="err" class="rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2.5">{{ err }}</div>
    <button class="w-full py-3.5 rounded-xl bg-[var(--lime)] text-[#fff] font-bold text-sm disabled:opacity-50 flex items-center justify-center gap-2" :disabled="!canPay" @click="submit">
      <Icon v-if="busy" name="loader" class="w-4 h-4 animate-spin" /><template v-else>{{ ctaLabel }} {{ rp(amount) }}</template>
    </button>
    <p class="text-center text-[11px] text-gray-400">{{ footerNote }}</p>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-end justify-center" style="background: rgba(0, 0, 0, 0.45)" @click="close">
      <div class="w-full max-w-[480px] bg-white rounded-3xl overflow-hidden" style="max-height: calc(85vh - 76px); margin-bottom: 76px; display: flex; flex-direction: column" @click.stop>
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 flex-shrink-0">
          <span style="font-size: 15px; font-weight: 700; color: #111">{{ t('paymentModal.title') }}</span>
          <button class="w-8 h-8 rounded-full flex items-center justify-center" style="background: #f3f4f6" @click="close"><Icon name="x" class="w-4 h-4 text-gray-500" /></button>
        </div>
        <div class="overflow-y-auto flex-1 px-4 py-4 space-y-5">
          <p v-if="!groups.length" style="font-size: 13px; color: #9ca3af; text-align: center; padding: 40px 0">{{ t('paymentModal.empty') }}</p>
          <div v-for="g in groups" :key="g.type">
            <p style="font-size: 11px; font-weight: 700; color: #9ca3af; letter-spacing: 0.06em; margin-bottom: 10px">{{ t('paymentModal.type.' + g.type).toUpperCase() }}</p>
            <div class="space-y-2">
              <button v-for="m in (expanded[g.type] ? g.items : g.items.slice(0, 3))" :key="m.code" type="button" :disabled="off(m)" :title="off(m) ? t('paymentModal.minDonationFor', { amount: rpT(minFor(m)) }) : undefined" @click="choose(m)"
                class="flex items-center gap-3 w-full px-4 py-3 rounded-xl transition-all" :class="off(m) ? 'cursor-not-allowed' : 'active:scale-[0.98] cursor-pointer'"
                :style="{ border: method === m.code ? '2px solid var(--lime-dark)' : '1.5px solid #e5e7eb', background: off(m) ? '#f5f5f5' : method === m.code ? '#fff8ed' : '#fafafa', opacity: off(m) ? 0.55 : 1 }">
                <div class="relative w-10 h-7 flex-shrink-0" :style="off(m) ? 'filter:grayscale(1)' : ''"><img :src="logo(m)" :alt="m.name" class="absolute inset-0 w-full h-full object-contain" /></div>
                <div class="flex-1 min-w-0 text-left">
                  <span :style="'font-size:13px;font-weight:600;display:block;color:' + (off(m) ? '#9ca3af' : method === m.code ? 'var(--lime-text)' : '#374151')">{{ m.name }}</span>
                  <span v-if="off(m)" style="font-size: 10px; color: #9ca3af">{{ t('paymentModal.min', { amount: rpT(minFor(m)) }) }}</span>
                  <span v-else-if="isQris(m)" class="flex items-center flex-wrap gap-x-1 gap-y-0.5" style="margin-top: 3px"><span style="font-size: 10px; font-weight: 500; color: #9ca3af">Can be used in</span><img v-for="f in FLAGS" :key="f[0]" :src="'https://sedekah.id/icons/flags/' + f[0] + '.svg'" :alt="f[1]" :title="f[1]" width="18" height="12" loading="lazy" style="border-radius: 2px; box-shadow: 0 0 0 0.5px rgba(0,0,0,0.15); display: inline-block" /></span>
                </div>
                <span v-if="method === m.code && !off(m)" class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0" style="background: var(--lime-dark)"><Icon name="check" class="w-3 h-3 text-white" /></span>
              </button>
            </div>
            <button v-if="g.items.length > 3" type="button" class="flex items-center justify-center gap-1.5 w-full mt-2 py-2 rounded-xl transition-colors" style="font-size: 12px; font-weight: 600; color: var(--lime-text); background: #fff8ed" @click="expanded[g.type] = !expanded[g.type]">
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
