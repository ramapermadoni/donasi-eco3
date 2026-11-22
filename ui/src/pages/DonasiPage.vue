<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import Icon from '../components/Icon.vue'
import AppHeader from '../components/AppHeader.vue'
import BottomNav from '../components/BottomNav.vue'
import SurveyPopup from '../components/SurveyPopup.vue'
import instruksi from '../data/instruksi.json'
import { t, tr, lp } from '../i18n'
import { pad2, nf } from '../utils/format'
import { hapusPenandaMitra } from '../donate'

// Port dari InstruksiBayar sedekah.id (chunk halaman /donasi/[id], dibaca sebagai teks). Hanya versi Indonesia
// (/en/donasi/* dialihkan ke '/' seperti asli). Blok `qurban` (pekurban) sengaja tidak ditiru.
const route = useRoute()
let id = route.params.id // diperbarui oleh watch bila komponen dipakai ulang antar /donasi/:id
const surveyPreview = import.meta.env.DEV && route.query.survey === 'preview' // dev: popup tanpa POST & tanpa kunci
const d = ref(null)
const err = ref('')
const copied = ref(null)
const open = ref(0)
const busyQr = ref(false)
const snapReady = ref(false)
const now = ref(Date.now())
let t1, t2, tCopy

const BANK = { bca: 'BCA', bni: 'BNI', bri: 'BRI', mandiri: 'Mandiri', permata: 'Permata', bsi: 'BSI', cimb: 'CIMB', danamon: 'Danamon', maybank: 'Maybank' }
const NOTE = {
  bsi_va: 'Di <b>BSI Mobile / BYOND</b>: pilih menu <b>Bayar &rarr; Institusi</b>, cari <b>Winpay</b> (kode <b>9042</b>), lalu masukkan nomor VA di atas. Lewat <b>ATM</b> atau <b>transfer dari bank lain</b>, nomornya diawali <b>9042</b> &mdash; ikuti langkah di bawah.',
  mandiri_va: 'Di <b>Livin\' / ATM Mandiri</b>: pilih menu <b>Multi Payment</b>, cari penyedia jasa <b>Winpay</b> (kode <b>8898</b>), lalu masukkan nomor VA di atas.',
}
const rp = (n) => 'Rp' + nf(n)
const m = computed(() => d.value?.metadata || {})
const status = computed(() => d.value?.status)
const vaRaw = computed(() => { const v = m.value.va_numbers?.[0]?.va_number ?? m.value.vaNumber; return v == null ? null : String(v).trim() || null })
const bank = computed(() => { const b = m.value.va_numbers?.[0]?.bank ?? (m.value.payment_method?.endsWith('_va') ? m.value.payment_method.slice(0, -3) : null); return b || null })
// Kunci instruksi (G di asli): payment_method bila dikenal; *_va lain -> other_va; bila tidak, dari payment_type (+ bank untuk bank_transfer).
const key = computed(() => {
  const pm = m.value.payment_method, pt = m.value.payment_type, b = bank.value ?? undefined
  if (pm && pm in instruksi) return pm
  if (pm?.endsWith('_va')) return 'other_va'
  if (!pt) return ''
  if (pt === 'bank_transfer') return ['bca', 'bni', 'bri', 'permata', 'mandiri'].includes(b) ? b + '_va' : 'other_va'
  return pt in instruksi ? pt : ''
})
const va = computed(() => (key.value === 'bsi_va' && vaRaw.value?.startsWith('9042') ? vaRaw.value.slice(4) : vaRaw.value))
const isVA = computed(() => m.value.payment_type === 'bank_transfer' || m.value.payment_method?.endsWith('_va'))
const isGopay = computed(() => m.value.payment_method === 'gopay' || m.value.payment_type === 'gopay')
const qrSrc = computed(() => m.value.qr_code_url ?? (m.value.qrString ? `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(m.value.qrString)}` : null))
const groups = computed(() => instruksi[key.value] ?? [])
const expMs = computed(() => (d.value?.expired_at ? new Date(d.value.expired_at).getTime() : NaN))
const rest = computed(() => (Number.isFinite(expMs.value) ? expMs.value - now.value : 0))
const left = computed(() => {
  if (rest.value <= 0) return t('instruksiBayar.expired')
  const s = Math.floor(rest.value / 1000)
  return `${pad2(Math.floor(s / 3600))}:${pad2(Math.floor((s % 3600) / 60))}:${pad2(s % 60)}`
})
const until = computed(() => Number.isFinite(expMs.value) ? new Date(expMs.value).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Jakarta' }) + ' WIB' : '')
const who = computed(() => (d.value?.is_anonymous ? 'Hamba Allah' : d.value?.donor_name))
// Nominal: "Rp" + angka, tiga digit terakhir berwarna lime-text (P di asli).
const amt = computed(() => { const n = nf(d.value?.amount || 0); return n.length <= 3 ? { head: 'Rp', tail: n } : { head: 'Rp' + n.slice(0, -3), tail: n.slice(-3) } })
const fill = (h) => h.replace(/\{va_number\}/g, va.value ?? '-').replace(/\{amount\}/g, rp(d.value?.amount || 0))

async function load(first) {
  try {
    const r = await fetch(`/api/donasi/${id}`)
    if (!r.ok) { if (first) err.value = r.status === 404 ? 'Donasi tidak ditemukan' : 'Gagal memuat donasi'; return }
    const j = await r.json()
    if (j.status === 'paid') hapusPenandaMitra()
    d.value = first || !d.value ? j : { ...d.value, status: j.status, metadata: j.metadata || d.value.metadata }
  } catch { if (first) err.value = 'Gagal memuat donasi' }
}
function flashCopied(k) { copied.value = k; clearTimeout(tCopy); tCopy = setTimeout(() => (copied.value = null), 2500) }
function copyFallback(text) {
  // WebView lama / izin clipboard ditolak: textarea sementara + execCommand
  const ta = document.createElement('textarea')
  ta.value = text; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0'
  document.body.appendChild(ta); ta.select()
  let ok = false
  try { ok = document.execCommand('copy') } catch {}
  ta.remove()
  return ok
}
function copy(text, k) {
  const done = () => flashCopied(k)
  const fb = () => { if (copyFallback(text)) done() }
  try {
    if (navigator.clipboard?.writeText) navigator.clipboard.writeText(text).then(done, fb)
    else fb()
  } catch { fb() }
}
function pay() {
  const mm = m.value
  if (!mm.snap_token) { if (mm.redirect_url) window.location.href = mm.redirect_url; return }
  if (window.snap?.pay) window.snap.pay(mm.snap_token, { onSuccess: () => location.reload(), onPending: () => location.reload(), onError() {}, onClose() {} })
  else if (mm.redirect_url) window.location.href = mm.redirect_url // cadangan (asli: snap?.pay diam-diam gagal)
}
async function saveQr() {
  if (busyQr.value) return
  busyQr.value = true
  try {
    const r = await fetch(`/api/donasi/${id}/qr`)
    if (!r.ok) throw new Error('fetch failed')
    const u = URL.createObjectURL(await r.blob())
    const a = document.createElement('a'); a.href = u; a.download = `qris-${id}.png`; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(u)
  } catch { window.open(`/api/donasi/${id}/qr`, '_blank') } finally { busyQr.value = false }
}
// Midtrans Snap: dimuat dari /api/payment/snap-config (clientKey publik); dibuka otomatis sekali per donasi bila ada snap_token.
function loadSnap() {
  fetch('/api/payment/snap-config').then((r) => r.json()).then((c) => {
    if (!c.clientKey) return
    const src = c.isProduction ? 'https://app.midtrans.com/snap/snap.js' : 'https://app.sandbox.midtrans.com/snap/snap.js'
    const ready = () => { snapReady.value = true; autoSnap() }
    const ada = document.querySelector(`script[src="${src}"]`)
    if (window.snap?.pay) { ready(); return } // sudah termuat penuh (pindah antar donasi lewat SPA)
    if (ada) { ada.addEventListener('load', ready, { once: true }); return } // tag ada tetapi belum selesai: tunggu onload
    const s = document.createElement('script'); s.src = src; s.setAttribute('data-client-key', c.clientKey); s.async = true; s.onload = ready
    document.head.appendChild(s)
  }).catch(() => {})
}
function autoSnap() {
  if (status.value !== 'pending' || !m.value.snap_token) return
  const k = `snap_opened_${id}`
  try { if (sessionStorage.getItem(k)) return; sessionStorage.setItem(k, '1') } catch {}
  pay()
}

function start() { d.value = null; err.value = ''; open.value = 0; copied.value = null; load(true).then(loadSnap) }
// Polling 5 dtk (sama dengan asli); setelah lewat batas waktu bayar diperlambat jadi 30 dtk agar tidak membombardir server bila webhook tidak datang.
let tick = 0
onMounted(() => {
  start()
  t1 = setInterval(() => (now.value = Date.now()), 1000)
  t2 = setInterval(() => {
    tick++
    if (!d.value || ['paid', 'failed', 'expired'].includes(status.value)) return
    if (rest.value <= 0 && Number.isFinite(expMs.value) && tick % 6) return
    load()
  }, 5000)
})
watch(() => route.params.id, (nv) => { if (nv && nv !== id) { id = nv; start() } })
onUnmounted(() => { clearInterval(t1); clearInterval(t2); clearTimeout(tCopy) })
</script>

<template>
  <div class="frame" style="background: #f5f6f8; min-height: 100vh">
    <AppHeader />

    <p v-if="err" class="d-empty" style="padding: 80px 16px">{{ err }}</p>
    <p v-else-if="!d" class="d-empty" style="padding: 80px 16px">{{ t('common.loading') }}</p>

    <!-- paid -->
    <div v-else-if="status === 'paid'" class="max-w-[480px] mx-auto px-4 pt-10 pb-28">
      <SurveyPopup :donation-id="d.id || id" :preview="surveyPreview" />
      <div class="rounded-2xl overflow-hidden" style="background: white; box-shadow: 0 4px 24px rgba(0,0,0,0.07)">
        <div class="px-6 py-10 text-center relative overflow-hidden" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%)">
          <div class="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4 relative z-10" style="background: white">
            <svg width="44" height="44" viewBox="0 0 44 44"><path d="M10 22 L19 31 L34 14" fill="none" stroke="#10b981" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" /></svg>
          </div>
          <p style="font-size: 24px; font-weight: 800; color: white; letter-spacing: 0.5px">Alhamdulillah</p>
          <p style="font-size: 14px; color: rgba(255,255,255,0.9); margin-top: 4px">Pembayaran diterima</p>
          <p style="font-size: 12px; color: rgba(255,255,255,0.7); margin-top: 8px">Terimakasih, {{ who }}</p>
        </div>
        <div class="px-6 py-6 space-y-4">
          <div v-if="d.returning_veteran" class="rounded-2xl px-5 py-4" style="background: #fff8ed; border: 1px solid rgba(0,83,153,0.25)">
            <p style="font-size: 13px; color: #374151; line-height: 1.65" v-html="tr('instruksiBayar.veteranLine1', { name: d.returning_veteran.name, year: String(d.returning_veteran.registered_year), duration: d.returning_veteran.duration }, { nameb: (x) => '<b style=&quot;color: #1a1a1a&quot;>' + x + '</b>', yearb: (x) => '<b style=&quot;color: #005399&quot;>' + x + '</b>' })"></p>
            <p style="font-size: 12.5px; color: #4b5563; line-height: 1.65; margin-top: 10px; font-style: italic">{{ t('instruksiBayar.veteranLine2') }}</p>
          </div>
          <div class="text-center">
            <p style="font-size: 12px; color: #9ca3af">Program</p>
            <p style="font-size: 15px; font-weight: 700; color: #1a1a1a; margin-top: 2px">{{ d.campaign?.title ?? 'Donasi' }}</p>
          </div>
          <div class="rounded-2xl px-5 py-4 text-center" style="background: #f0fdf4; border: 1px solid #bbf7d0">
            <p style="font-size: 12px; color: #6b7280">{{ d.upsell_breakdown ? t('instruksiBayar.totalPaid') : 'Nominal Donasi' }}</p>
            <p style="font-size: 28px; margin-top: 4px"><span style="font-weight: 800; color: #1a1a1a">{{ amt.head }}<span style="color: #005399">{{ amt.tail }}</span></span></p>
            <div v-if="d.upsell_breakdown" class="mt-3 pt-3 border-t border-emerald-200/50 text-left space-y-1">
              <div class="flex items-center justify-between" style="font-size: 11px"><span style="color: #6b7280">{{ d.campaign?.title ?? 'Donasi' }}</span><span style="color: #1a1a1a; font-weight: 600">{{ rp(d.upsell_breakdown.main_amount) }}</span></div>
              <div class="flex items-center justify-between" style="font-size: 11px"><span style="color: #6b7280">{{ d.upsell_breakdown.upsell_label }}</span><span style="color: #005399; font-weight: 600">+ {{ rp(d.upsell_breakdown.upsell_amount) }}</span></div>
            </div>
          </div>
          <p style="font-size: 12px; color: #9ca3af; text-align: center; font-style: italic">Semoga Allah membalas kebaikan Anda dengan berlipat ganda. آمِيْنُ</p>
          <router-link :to="lp('/')" class="block w-full py-3.5 rounded-2xl text-[#fff] text-center font-bold transition-all active:scale-[0.98]" style="background: linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%); font-size: 14px; font-weight: 700; box-shadow: 0 4px 16px color-mix(in srgb, var(--lime) 35%, transparent)">Lanjutkan</router-link>
        </div>
      </div>
    </div>

    <!-- failed / expired -->
    <div v-else-if="status === 'failed' || status === 'expired'" class="max-w-[480px] mx-auto px-4 pt-10 pb-28">
      <div class="rounded-2xl overflow-hidden" style="background: white; box-shadow: 0 4px 24px rgba(0,0,0,0.07)">
        <div class="px-6 py-8 text-center" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%)">
          <div class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4" style="background: rgba(255,255,255,0.2)"><Icon name="alertCircle" class="w-8 h-8 text-white" /></div>
          <p style="font-size: 20px; font-weight: 800; color: white">{{ t(status === 'expired' ? 'instruksiBayar.paymentExpired' : 'instruksiBayar.paymentFailed') }}</p>
        </div>
        <div class="px-6 py-6 text-center space-y-4">
          <p style="font-size: 13px; color: #6b7280">{{ t(status === 'expired' ? 'instruksiBayar.expiredMsg' : 'instruksiBayar.failedMsg') }}</p>
          <router-link :to="lp('/')" class="block w-full py-3.5 rounded-2xl text-[#fff] text-center font-bold transition-all" style="background: linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%); font-size: 14px; font-weight: 700">{{ t('instruksiBayar.donateAgain') }}</router-link>
        </div>
      </div>
    </div>

    <!-- pending -->
    <div v-else class="max-w-[480px] mx-auto pb-28">
      <div class="relative overflow-hidden px-4 pt-5 pb-5" style="background: linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%)">
        <div class="absolute -top-6 -right-6 w-28 h-28 rounded-full bg-white/10"></div>
        <div class="absolute -bottom-4 -left-4 w-20 h-20 rounded-full bg-black/10"></div>
        <div class="relative z-10">
          <p style="font-size: 11px; color: rgba(255,255,255,0.75); font-weight: 600">{{ t('instruksiBayar.paymentInstructions') }}</p>
          <p style="font-size: 16px; font-weight: 800; color: white; margin-top: 2px; line-height: 1.3">{{ d.campaign?.title ?? 'Donasi' }}</p>
          <p style="font-size: 12px; color: rgba(255,255,255,0.85); margin-top: 6px">Terimakasih, <b>{{ who }}</b></p>
        </div>
      </div>
      <div class="px-4 mt-4 space-y-3">
        <!-- total -->
        <div class="rounded-2xl px-5 py-4" style="background: white; box-shadow: 0 2px 16px color-mix(in srgb, var(--lime) 8%, transparent); border: 1px solid color-mix(in srgb, var(--lime) 10%, transparent)">
          <div class="flex items-center justify-between">
            <div>
              <p style="font-size: 11px; color: #9ca3af; font-weight: 500">Total Pembayaran</p>
              <p style="font-size: 26px; margin-top: 4px"><span style="font-weight: 800; color: #1a1a1a">{{ amt.head }}<span style="color: #005399">{{ amt.tail }}</span></span></p>
              <p v-if="!d.upsell_breakdown" style="font-size: 10px; color: #9ca3af; margin-top: 2px">{{ t('instruksiBayar.payExactAmount') }}</p>
              <p v-else style="font-size: 10px; color: #9ca3af; margin-top: 2px">{{ rp(d.upsell_breakdown.main_amount) }} + {{ rp(d.upsell_breakdown.upsell_amount) }} {{ d.upsell_breakdown.upsell_label }}</p>
            </div>
            <button class="flex items-center gap-1.5 px-3 py-2 rounded-xl transition-all active:scale-95" :style="{ background: copied === 'amount' ? '#dcfce7' : 'color-mix(in srgb, var(--lime) 8%, transparent)', border: '1px solid', borderColor: copied === 'amount' ? '#86efac' : 'color-mix(in srgb, var(--lime) 20%, transparent)' }" @click="copy(String(d.amount), 'amount')">
              <Icon :name="copied === 'amount' ? 'check' : 'copy'" class="w-3.5 h-3.5" :style="{ color: copied === 'amount' ? '#16a34a' : '#005399' }" />
              <span :style="{ fontSize: '11px', fontWeight: 600, color: copied === 'amount' ? '#16a34a' : '#005399' }">{{ t(copied === 'amount' ? 'instruksiBayar.copied' : 'instruksiBayar.copy') }}</span>
            </button>
          </div>
        </div>

        <!-- VA / kode pembayaran -->
        <div v-if="va" class="rounded-2xl overflow-hidden" style="background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%); box-shadow: 0 4px 20px rgba(30,64,175,0.25)">
          <div class="px-5 py-4">
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <p style="font-size: 11px; color: rgba(255,255,255,0.6); font-weight: 500">{{ t(isVA ? 'instruksiBayar.vaNumber' : 'instruksiBayar.paymentCode') }}</p>
                <p v-if="bank" style="font-size: 11px; color: #93c5fd; font-weight: 700; margin-top: 2px">{{ BANK[bank] ?? bank.toUpperCase() }}</p>
                <p style="font-size: 22px; font-weight: 800; color: white; margin-top: 4px; letter-spacing: 0.5px">{{ va }}</p>
              </div>
              <button class="flex items-center gap-1.5 px-3 py-2 rounded-xl transition-all active:scale-95 flex-shrink-0 ml-3" :style="{ background: copied === 'va' ? 'rgba(134,239,172,0.2)' : 'rgba(255,255,255,0.15)', border: '1px solid', borderColor: copied === 'va' ? '#86efac' : 'rgba(255,255,255,0.2)' }" @click="copy(va, 'va')">
                <Icon :name="copied === 'va' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="copied === 'va' ? 'text-green-300' : 'text-white/70'" />
                <span :style="{ fontSize: '11px', fontWeight: 600, color: copied === 'va' ? '#86efac' : 'rgba(255,255,255,0.8)' }">{{ t(copied === 'va' ? 'instruksiBayar.copied' : 'instruksiBayar.copy') }}</span>
              </button>
            </div>
          </div>
        </div>
        <div v-if="va && NOTE[key]" class="rounded-2xl px-4 py-3 flex gap-2.5" style="background: #eff6ff; border: 1px solid #bfdbfe">
          <Icon name="alertCircle" class="w-4 h-4 flex-shrink-0 mt-0.5" style="color: #2563eb" />
          <p style="font-size: 11.5px; color: #1e40af; line-height: 1.55" v-html="NOTE[key]"></p>
        </div>

        <!-- QR -->
        <div v-if="qrSrc" class="rounded-2xl px-5 py-5 text-center" style="background: white; box-shadow: 0 2px 16px rgba(0,0,0,0.06); border: 1px solid #e5e7eb">
          <p style="font-size: 12px; font-weight: 600; color: #374151; margin-bottom: 12px">Scan QR Code</p>
          <img :src="qrSrc" alt="QR Code QRIS" width="200" height="200" class="mx-auto rounded-xl" style="object-fit: contain" />
          <button class="mt-3 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl transition-all active:scale-95 disabled:opacity-60" :disabled="busyQr" style="background: color-mix(in srgb, var(--lime) 10%, transparent); border: 1px solid color-mix(in srgb, var(--lime) 30%, transparent)" @click="saveQr">
            <Icon :name="busyQr ? 'loader' : 'download'" class="w-4 h-4" :class="{ 'animate-spin': busyQr }" style="color: #005399" />
            <span style="font-size: 12px; font-weight: 700; color: #005399">{{ busyQr ? t('instruksiBayar.preparing') : 'Download QR Code' }}</span>
          </button>
          <p style="font-size: 11px; color: #9ca3af; margin-top: 12px">{{ m.intl_qris ? 'Scan with your local bank or e-wallet app (QRIS cross-border). The app will show the amount in your local currency before you confirm. You can also download the QR and scan it from your gallery.' : t('instruksiBayar.scanQrisHint') }}</p>
        </div>

        <!-- e-wallet / lanjut bayar -->
        <template v-if="status === 'pending'">
          <button v-if="m.snap_token || m.redirect_url" class="w-full py-4 rounded-2xl text-white flex items-center justify-center gap-2 transition-all active:scale-[0.98]" style="background: linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%); font-size: 15px; font-weight: 700; box-shadow: 0 6px 24px color-mix(in srgb, var(--lime) 40%, transparent)" @click="pay">
            <template v-if="isGopay">
              <span class="relative inline-block flex-shrink-0" style="width: 44px; height: 22px; background: #fff; border-radius: 6px"><img src="https://sedekah.id/icons/bank/gopay.png" alt="GoPay" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; padding: 3px" /></span>
              {{ t('instruksiBayar.openGopay') }}
            </template>
            <template v-else><Icon name="externalLink" class="w-4 h-4" />{{ t('instruksiBayar.continuePayment') }}</template>
          </button>
          <div v-else-if="!(m.vaNumber || m.va_numbers || m.qrString || m.qr_code_url)" class="rounded-2xl px-5 py-4 text-center" style="background: #fef9c3; border: 1px solid #fde047">
            <p style="font-size: 13px; font-weight: 700; color: #854d0e">{{ t('instruksiBayar.donationRecorded') }}</p>
            <p style="font-size: 11px; color: #92400e; margin-top: 4px">{{ t('instruksiBayar.contactAdmin') }}</p>
          </div>
        </template>

        <!-- batas waktu -->
        <div v-if="until" class="rounded-2xl px-5 py-3.5 flex items-center gap-3" style="background: #fff8ed; border: 1px solid color-mix(in srgb, var(--lime) 20%, transparent)">
          <Icon name="clock" class="w-5 h-5 flex-shrink-0" style="color: #005399" />
          <div>
            <p style="font-size: 11px; color: #9ca3af; font-weight: 500">{{ t('instruksiBayar.payBefore') }}</p>
            <p style="font-size: 13px; font-weight: 700; color: #1a1a1a">{{ until }}</p>
          </div>
          <div class="ml-auto text-right flex-shrink-0">
            <p style="font-size: 11px; color: #9ca3af">{{ t('instruksiBayar.timeLeft') }}</p>
            <p style="font-size: 13px; font-weight: 700; color: #005399"><span>{{ left }}</span></p>
          </div>
        </div>

        <!-- cara bayar -->
        <div v-if="groups.length" class="rounded-2xl overflow-hidden" style="background: white; box-shadow: 0 2px 16px rgba(0,0,0,0.05); border: 1px solid #e5e7eb">
          <div class="px-5 py-4" style="border-bottom: 1px solid #f3f4f6"><p style="font-size: 13px; font-weight: 700; color: #374151">{{ t('instruksiBayar.howToPay') }}</p></div>
          <div v-for="(g, i) in groups" :key="g.title" :style="{ borderBottom: i < groups.length - 1 ? '1px solid #f3f4f6' : 'none' }">
            <button class="w-full flex items-center justify-between px-5 py-3.5 transition-colors text-left" :style="{ background: open === i ? 'color-mix(in srgb, var(--lime) 6%, transparent)' : 'transparent' }" @click="open = open === i ? null : i">
              <span :style="{ fontSize: '13px', fontWeight: 600, color: open === i ? '#005399' : '#374151' }">{{ g.title }}</span>
              <Icon :name="open === i ? 'chevronUp' : 'chevronDown'" class="w-4 h-4 flex-shrink-0" :class="open === i ? '' : 'text-gray-400'" :style="open === i ? { color: '#005399' } : {}" />
            </button>
            <div v-if="open === i" class="px-5 pb-4 space-y-2">
              <div v-for="(s, j) in g.steps" :key="j" class="flex gap-2" style="font-size: 12px; color: #374151; line-height: 1.6">
                <span style="flex-shrink: 0; font-weight: 600; color: #005399; min-width: 18px">{{ j + 1 }}.</span>
                <span v-html="fill(s)"></span>
              </div>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-center gap-2 py-2">
          <Icon name="refreshCw" class="w-3.5 h-3.5 animate-spin" style="color: #d1d5db" />
          <p style="font-size: 11px; color: #d1d5db">{{ t('instruksiBayar.checkingStatus') }}</p>
        </div>
      </div>
    </div>
  </div>
  <BottomNav />
</template>
