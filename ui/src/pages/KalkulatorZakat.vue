<script setup>
// Kalkulator zakat (sedekah.id /kalkulatorzakat). Rumus di ../zakatCalc.js; spec: docs/reference/kalkulator-zakat-spec.md.
// Frappe hook: /api/gold-price -> harga emas; POST /api/donations + /api/payment/create -> bayar (lihat submit()).
import { lsGet, lsSet } from '../utils/storage'
import { reactive, ref, computed, onMounted } from 'vue'
import Icon from '../components/Icon.vue'
import payment from '../data/payment.json'
import { t, lp, apiHeaders } from '../i18n'
import { rpShort, rpSp, localPhone } from '../utils/format'
import { postJson } from '../utils/net'
import { logo, minFor, groupMethods } from '../utils/payment'
import { penandaDonasi } from '../donate'
import { hitung, rateOf, nishabEmas, parseRp, idr, num, FALLBACK_GOLD } from '../zakatCalc'

const TABS = [['penghasilan', '💼', 'Penghasilan'], ['maal', '💰', 'Maal'], ['emas', '🪙', 'Emas'], ['investasi', '📈', 'Investasi'], ['perniagaan', '🏪', 'Perniagaan']]
const CAMP = { penghasilan: ['zakatcamp-penghasilan-01', 'Zakat Penghasilan'], maal: ['zakatcamp-maal-000000001', 'Zakat Maal'], emas: ['zakatcamp-emas-000000001', 'Zakat Emas & Perak'], investasi: ['zakatcamp-investasi-0001', 'Zakat Investasi'], perniagaan: ['zakatcamp-perniagaan-001', 'Zakat Perniagaan'] }
const FIELDS = {
  maal: [['harta', 'Total harta simpanan (tabungan, deposito, aset likuid) yang tersimpan ≥ 1 tahun'], ['hutang', 'Hutang jatuh tempo']],
  investasi: [['pendapatan', 'Pendapatan hasil investasi'], ['biaya', 'Biaya operasional']],
  perniagaan: [['modal', 'Modal diputar'], ['untung', 'Keuntungan'], ['piutang', 'Piutang dagang'], ['rugi', 'Kerugian'], ['hutang', 'Hutang jatuh tempo'], ['pengLain', 'Pengeluaran lain']],
}
const s = reactive({ tab: 'penghasilan', hijriah: true, mode: 'bruto', acuan: '24karat', modeEmas: 'gram', pp: 'bulan', pi: 'tahun', pn: 'tahun', v: {} })
// state satu tempat seperti aslinya: isian disimpan per jenis zakat (kunci 'tab:field'), tidak direset saat ganti tab
const key = (k) => s.tab + ':' + k
const gold = ref(null)
onMounted(() => { fetch('/api/gold-price').then((r) => r.json()).then((j) => { gold.value = j }).catch(() => {}) })
const price = computed(() => gold.value?.pricePerGram ?? FALLBACK_GOLD)
const eu = computed(() => nishabEmas(price.value).eu)
const periode = computed(() => (s.tab === 'penghasilan' ? s.pp : s.tab === 'investasi' ? s.pi : s.pn))
const setPeriode = (p) => { s[s.tab === 'penghasilan' ? 'pp' : s.tab === 'investasi' ? 'pi' : 'pn'] = p }
const view = computed(() => { const v = {}, pre = s.tab + ':'; for (const k in s.v) if (k.startsWith(pre)) v[k.slice(pre.length)] = s.v[k]; return v })
const res = computed(() => hitung({ tab: s.tab, hijriah: s.hijriah, price: price.value, periode: periode.value, mode: s.mode, acuan: s.acuan, modeEmas: s.modeEmas, v: view.value }))
const fmt = (k) => (s.v[key(k)] ? num(s.v[key(k)]) : '')
const setV = (k, e) => { const n = parseRp(e.target.value); s.v[key(k)] = n; e.target.value = n ? num(n) : '' }
const penFields = computed(() => [['gaji', `Gaji / penghasilan ${s.pp === 'bulan' ? 'per bulan' : 'per tahun'}`], ['lain', 'Penghasilan lain (bonus, THR, honor)'], ...(s.mode === 'netto' ? [['pokok', 'Kebutuhan pokok'], ['cicilan', 'Cicilan hutang jatuh tempo'], ['pengLain', 'Pengeluaran lain']] : [])])
const fields = computed(() => (s.tab === 'penghasilan' ? penFields.value : FIELDS[s.tab] || []))
const seg = (on) => 'px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors ' + (on ? 'bg-white shadow text-gray-900' : 'text-gray-500')

// ---- form bayar (ZakatPayForm) ----
const f = reactive({ name: '', wa: '', anon: false, method: null })
const err = ref(''), busy = ref(false), open = ref(false), methods = ref(payment), expanded = ref({})
try { const d = JSON.parse(lsGet('sedekah_donor_v1') || 'null'); if (d) { f.name = d.name || ''; f.wa = d.whatsapp || ''; f.anon = !!d.isAnonymous; f.method = d.paymentMethod || null } } catch {}
const digits = localPhone
const mObj = computed(() => methods.value.find((m) => m.code === f.method))
const min = computed(() => (mObj.value ? minFor(mObj.value) : 0))
const amount = computed(() => res.value.zakat)
const canPay = computed(() => amount.value > 0 && f.method && amount.value >= min.value && !busy.value)
const groups = computed(() => groupMethods(methods.value))
const rp = rpShort
const rpn = rpSp
async function openModal() {
  open.value = true
  try { const j = await fetch('/api/payment/methods').then((r) => r.json()); if (j.methods?.length) methods.value = j.methods } catch {}
}
async function post(path, body) {
  const { r, j } = await postJson('/api' + path, body, { headers: apiHeaders() })
  return { ok: r.ok, j }
}
async function submit() {
  err.value = ''
  const d = digits(f.wa)
  if (f.name.trim().length < 2) return (err.value = 'Nama minimal 2 karakter.')
  if (d.length < 8) return (err.value = 'Nomor WhatsApp tidak valid.')
  if (!f.method) return (err.value = 'Pilih metode pembayaran dulu.')
  if (amount.value < min.value) return (err.value = `Metode ini minimal ${rpn(min.value)}.`)
  busy.value = true
  try {
    lsSet('sedekah_donor_v1', JSON.stringify({ name: f.name, whatsapp: d, isAnonymous: f.anon, paymentMethod: f.method }))
    const [cid, title] = CAMP[s.tab], phone = '+62' + d
    const a = await post('/donations', { campaign_id: cid, currency: 'IDR', amount: amount.value, donor_name: f.name, donor_phone: phone, is_anonymous: f.anon, type: 'one_time', ...penandaDonasi() })
    if (!a.ok || !a.j.donation_id) return (err.value = a.j.error ?? 'Gagal memproses.')
    const b = await post('/payment/create', { donation_id: a.j.donation_id, payment_method: f.method, donor_name: f.name, donor_phone: phone, campaign_title: title, amount: amount.value })
    if (!b.ok) return (err.value = b.j.error ?? 'Gagal membuat pembayaran. Coba metode lain.')
    window.location.href = '/donasi/' + a.j.donation_id
  } catch { err.value = 'Terjadi kesalahan. Coba lagi.' } finally { busy.value = false }
}
</script>

<template>
  <div class="frame">
    <div class="min-h-screen bg-[#f6f7f2]">
      <div class="max-w-lg mx-auto px-4 pt-6 pb-16">
        <div class="flex items-center gap-3 mb-1">
          <router-link class="w-9 h-9 rounded-full bg-white border border-gray-200 flex items-center justify-center text-gray-500" aria-label="Kembali" :to="lp('/zakat')">←</router-link>
          <h1 class="text-xl font-extrabold text-gray-900">Kalkulator Zakat</h1>
        </div>
        <p class="text-sm text-gray-500 ml-12 mb-5">Hitung kewajiban zakatmu, lalu tunaikan langsung. Dikelola DT Peduli (LAZNAS).</p>
        <div class="space-y-4">
          <div class="bg-white rounded-2xl border border-gray-100 p-4">
            <p class="text-xs font-semibold text-gray-700 mb-1.5">Kalender haul</p>
            <div class="inline-flex rounded-xl bg-gray-100 p-1">
              <button type="button" :class="seg(s.hijriah)" @click="s.hijriah = true">Hijriah · 2,5%</button>
              <button type="button" :class="seg(!s.hijriah)" @click="s.hijriah = false">Masehi · 2,577%</button>
            </div>
            <div class="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between gap-3">
              <div class="min-w-0">
                <p class="text-xs font-semibold text-gray-700">Harga emas/gram</p>
                <p class="text-[10px] truncate" :class="gold?.stale === false ? 'text-green-600' : 'text-gray-400'">{{ gold ? (gold.stale ? 'acuan internal' : gold.source) : 'memuat…' }}</p>
              </div>
              <p class="shrink-0 text-base font-bold text-gray-900">{{ idr(price) }}</p>
            </div>
          </div>

          <div class="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
            <button v-for="tb in TABS" :key="tb[0]" type="button" class="shrink-0 px-3.5 py-2 rounded-xl text-sm font-semibold border transition-colors"
              :class="s.tab === tb[0] ? 'bg-[var(--lime)] border-[var(--lime)] text-[#fff]' : 'bg-white border-gray-200 text-gray-600'" @click="s.tab = tb[0]"><span class="mr-1">{{ tb[1] }}</span>{{ tb[2] }}</button>
          </div>

          <div class="bg-white rounded-2xl border border-gray-100 p-5 space-y-4">
            <template v-if="s.tab === 'penghasilan'">
              <div class="flex items-center justify-between flex-wrap gap-2">
                <div class="inline-flex rounded-xl bg-gray-100 p-1"><button type="button" :class="seg(s.pp === 'bulan')" @click="s.pp = 'bulan'">Per Bulan</button><button type="button" :class="seg(s.pp === 'tahun')" @click="s.pp = 'tahun'">Per Tahun</button></div>
                <div class="inline-flex rounded-xl bg-gray-100 p-1"><button type="button" :class="seg(s.mode === 'bruto')" @click="s.mode = 'bruto'">Bruto</button><button type="button" :class="seg(s.mode === 'netto')" @click="s.mode = 'netto'">Netto</button></div>
              </div>
              <div>
                <p class="block text-xs font-semibold text-gray-700 mb-1.5">Acuan nishab</p>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <button type="button" class="text-left rounded-xl border p-3" :class="s.acuan === '24karat' ? 'border-[var(--lime)] bg-[color-mix(in_srgb,var(--lime)_8%,white)]' : 'border-gray-200'" @click="s.acuan = '24karat'">
                    <p class="text-xs font-bold text-gray-800">Harga emas 24 karat</p><p class="text-[11px] text-gray-500 mt-0.5">85 gr/tahun ≈ {{ idr(eu) }}</p></button>
                  <button type="button" class="text-left rounded-xl border p-3" :class="s.acuan === 'sk-baznas-2026' ? 'border-[var(--lime)] bg-[color-mix(in_srgb,var(--lime)_8%,white)]' : 'border-gray-200'" @click="s.acuan = 'sk-baznas-2026'">
                    <p class="text-xs font-bold text-gray-800">SK BAZNAS No. 15/2026</p><p class="text-[11px] text-gray-500 mt-0.5">Rp 91.681.728/tahun</p></button>
                </div>
              </div>
            </template>
            <div v-else-if="s.tab === 'investasi' || s.tab === 'perniagaan'" class="inline-flex rounded-xl bg-gray-100 p-1">
              <button type="button" :class="seg(periode === 'bulan')" @click="setPeriode('bulan')">Per Bulan</button><button type="button" :class="seg(periode === 'tahun')" @click="setPeriode('tahun')">Per Tahun</button>
            </div>
            <div v-else-if="s.tab === 'emas'" class="inline-flex rounded-xl bg-gray-100 p-1">
              <button type="button" :class="seg(s.modeEmas === 'gram')" @click="s.modeEmas = 'gram'">Input Gram</button><button type="button" :class="seg(s.modeEmas === 'rupiah')" @click="s.modeEmas = 'rupiah'">Input Rupiah</button>
            </div>

            <template v-if="s.tab === 'emas'">
              <div v-if="s.modeEmas === 'gram'">
                <p class="block text-xs font-semibold text-gray-700 mb-1.5">Total emas/perak yang dimiliki ≥ 1 tahun</p>
                <div class="flex items-center rounded-xl border border-gray-200 bg-white focus-within:border-[var(--lime)] overflow-hidden"><input inputmode="numeric" :value="fmt('gram')" placeholder="0" class="w-full px-3 py-2.5 text-sm focus:outline-none" @input="setV('gram', $event)" /><span class="px-3 py-2.5 text-sm text-gray-400 bg-gray-50 border-l border-gray-100">gram</span></div>
              </div>
              <div v-else>
                <p class="block text-xs font-semibold text-gray-700 mb-1.5">Nilai emas/perak dalam Rupiah</p>
                <div class="flex items-center rounded-xl border border-gray-200 bg-white focus-within:border-[var(--lime)] overflow-hidden"><span class="px-3 py-2.5 text-sm text-gray-400 bg-gray-50 border-r border-gray-100">Rp</span><input inputmode="numeric" :value="fmt('nilai')" placeholder="0" class="w-full px-3 py-2.5 text-sm focus:outline-none" @input="setV('nilai', $event)" /></div>
              </div>
            </template>
            <template v-else><div v-for="fl in fields" :key="s.tab + fl[0]">
              <p class="block text-xs font-semibold text-gray-700 mb-1.5">{{ fl[1] }}</p>
              <div class="flex items-center rounded-xl border border-gray-200 bg-white focus-within:border-[var(--lime)] overflow-hidden"><span class="px-3 py-2.5 text-sm text-gray-400 bg-gray-50 border-r border-gray-100">Rp</span><input inputmode="numeric" :value="fmt(fl[0])" placeholder="0" class="w-full px-3 py-2.5 text-sm focus:outline-none" @input="setV(fl[0], $event)" /></div>
            </div></template>
          </div>

          <div class="rounded-2xl border p-5" :class="res.wajib ? 'border-[var(--lime)] bg-[color-mix(in_srgb,var(--lime)_8%,white)]' : 'border-gray-200 bg-white'">
            <div class="flex items-center justify-between">
              <p class="text-xs font-bold uppercase tracking-wide text-gray-500">{{ res.wajib ? 'Wajib Dibayar' : 'Belum Wajib Zakat' }}</p>
              <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">{{ s.hijriah ? '2,5%' : '2,577%' }}</span>
            </div>
            <p class="mt-1 text-2xl font-extrabold text-gray-900">{{ idr(res.zakat) }}</p>
            <p class="mt-1 text-[11px] text-gray-500">{{ res.note }}</p>
          </div>

          <div v-if="res.wajib && amount > 0" class="bg-white rounded-2xl border border-gray-100 p-5 space-y-4">
            <p class="text-sm font-bold text-gray-900">Tunaikan sekarang — {{ CAMP[s.tab][1] }}</p>
            <div><label class="block text-sm font-medium text-gray-700 mb-1.5">Nama</label><input v-model="f.name" placeholder="Nama kamu" class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-[var(--lime)]" /></div>
            <div><label class="block text-sm font-medium text-gray-700 mb-1.5">WhatsApp</label><div class="flex items-center gap-2"><span class="px-3 py-2.5 rounded-lg bg-gray-100 text-sm text-gray-500">+62</span><input v-model="f.wa" inputmode="numeric" placeholder="81234567890" class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-[var(--lime)]" /></div></div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Metode Pembayaran</label>
              <button v-if="!mObj" type="button" class="flex items-center gap-3 w-full px-4 py-3 rounded-xl transition-all active:scale-[0.99]" style="border: 1.5px solid #e5e7eb; background: #fafafa" @click="openModal"><span class="text-[13px] font-semibold text-gray-500 flex-1 text-left">Pilih metode pembayaran</span><Icon name="chevronRight" class="w-4 h-4 flex-shrink-0 text-gray-400" /></button>
              <button v-else type="button" class="flex items-center gap-3 w-full px-4 py-3 rounded-xl transition-all active:scale-[0.99]" style="border: 2px solid var(--lime-dark); background: color-mix(in srgb, var(--lime) 8%, white)" @click="openModal"><img :src="logo(mObj)" :alt="mObj.name" class="w-7 h-7 object-contain rounded" /><span class="text-[13px] font-bold flex-1 text-left" style="color: var(--lime-text)">{{ mObj.name }}</span><Icon name="check" class="w-4 h-4 flex-shrink-0" style="color: var(--lime-dark)" /></button>
              <p v-if="mObj && amount < min" class="mt-1.5 text-[11px] text-amber-600">Metode ini minimal {{ rpn(min) }}. Pilih QRIS/e-wallet untuk nominal kecil.</p>
            </div>
            <label class="flex items-center gap-2 text-sm text-gray-600"><input v-model="f.anon" class="accent-[var(--lime-dark)]" type="checkbox" /> Tampilkan sebagai anonim (Hamba Allah)</label>
            <div v-if="err" class="rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2.5">{{ err }}</div>
            <button :disabled="!canPay" class="w-full py-3.5 rounded-xl bg-[var(--lime)] text-[#fff] font-bold text-sm disabled:opacity-50 flex items-center justify-center gap-2" @click="submit"><Icon v-if="busy" name="loader" class="w-4 h-4 animate-spin" /><template v-else>Tunaikan {{ rpn(amount) }}</template></button>
            <p class="text-center text-[11px] text-gray-400">Zakat dikelola & disalurkan oleh DT Peduli (LAZNAS resmi).</p>
          </div>
        </div>
        <p class="mt-8 text-center text-[11px] text-gray-400 leading-relaxed">Nishab emas mengikuti harga emas terkini (85 gram, Antam buyback). Skema nishab penghasilan juga tersedia mengikuti SK Ketua BAZNAS No. 15 Tahun 2026. Sudah tahu nominalnya? <router-link class="underline" :to="lp('/zakat')">Bayar langsung di /zakat</router-link>.</p>
      </div>
    </div>

    <div v-if="open" class="fixed inset-0 z-50 flex items-end justify-center" style="background: rgba(0, 0, 0, 0.45)" @click="open = false">
      <div class="w-full max-w-[480px] bg-white rounded-3xl overflow-hidden" style="max-height: 85vh; display: flex; flex-direction: column" @click.stop>
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100 flex-shrink-0">
          <span style="font-size: 15px; font-weight: 700; color: #111">{{ t('paymentModal.title') }}</span>
          <button class="w-8 h-8 rounded-full flex items-center justify-center" style="background: #f3f4f6" @click="open = false"><Icon name="x" class="w-4 h-4 text-gray-500" /></button>
        </div>
        <div class="overflow-y-auto flex-1 px-4 py-4 space-y-5">
          <div v-for="g in groups" :key="g.type">
            <p style="font-size: 11px; font-weight: 700; color: #9ca3af; letter-spacing: 0.06em; margin-bottom: 10px">{{ t('paymentModal.type.' + g.type).toUpperCase() }}</p>
            <div class="space-y-2">
              <button v-for="m in (expanded[g.type] ? g.items : g.items.slice(0, 3))" :key="m.code" :disabled="amount > 0 && amount < minFor(m)" class="flex items-center gap-3 w-full px-4 py-3 rounded-xl transition-all"
                :style="{ border: f.method === m.code ? '2px solid var(--lime-dark)' : '1.5px solid #e5e7eb', background: amount < minFor(m) ? '#f5f5f5' : f.method === m.code ? '#fff8ed' : '#fafafa', opacity: amount < minFor(m) ? 0.55 : 1 }" @click="f.method = m.code; open = false">
                <div class="relative w-10 h-7 flex-shrink-0"><img :src="logo(m)" :alt="m.name" class="absolute inset-0 w-full h-full object-contain" /></div>
                <div class="flex-1 min-w-0 text-left"><span style="font-size: 13px; font-weight: 600; display: block; color: #374151">{{ m.name }}</span><span v-if="amount < minFor(m)" style="font-size: 10px; color: #9ca3af">{{ t('paymentModal.min', { amount: rp(minFor(m)) }) }}</span></div>
              </button>
            </div>
            <button v-if="g.items.length > 3" class="flex items-center justify-center gap-1.5 w-full mt-2 py-2 rounded-xl" style="font-size: 12px; font-weight: 600; color: var(--lime-text); background: #fff8ed" @click="expanded[g.type] = !expanded[g.type]">{{ expanded[g.type] ? t('paymentModal.hide') : t('paymentModal.moreMethods', { count: g.items.length - 3 }) }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
