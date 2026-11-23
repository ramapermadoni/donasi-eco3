<script setup>
import { rpSp, localPhone } from '../utils/format'
import { lp, t } from '../i18n'
import { ref, computed, watch } from 'vue'
import payment from '../data/payment.json'
import { logo, minFor, groupMethods } from '../utils/payment'
import Icon from '../components/Icon.vue'
import AppHeader from '../components/AppHeader.vue'
import PillTabs from '../components/PillTabs.vue'
import BottomNav from '../components/BottomNav.vue'
import { auth } from '../auth'

import missions, { sponsorMissions } from '../data/missions'
const TYPE_EMOJI = { TAP_COUNTER: '📿', TIMER: '📖', CONFIRM: '✅', SHARE: '📣' }
const isImg = (v) => !!v && (v.startsWith('http') || v.startsWith('/'))
const amalan = missions.map((m) => ({ id: m.slug, icon: m.icon, emoji: m.emoji || TYPE_EMOJI[m.type] || '🌟', title: m.title, nominal: m.voucherAmount, voucher: m.voucherLeft }))
const link = (id) => lp(auth.user ? '/jalankebaikan/' + id : '/akun?next=' + encodeURIComponent('/jalankebaikan/' + id))

const mode = ref('do')
const rupiah = rpSp

// ---- tab "Menjadi Jalan Kebaikan" (form sponsor voucher) ----
// Frappe hook (go()): asli = POST /api/donations {campaign_id: misi.campaignId, currency:'IDR', amount: voucher*voucherAmount, donor_name, donor_phone:'+62..', is_anonymous, message?, type:'one_time',
//   baik_mission_id: misi.id, ...penandaDonasi() (dari donate.js), [baik_funding_source:'MARKETING' bila marketing], [baik_replaces_pool_id]}, lalu POST /api/payment/create (tanpa penanda).
// Di tiruan ini TIDAK ada transaksi: data misi (missions.json) belum memuat id/campaignId server, jadi baik_mission_id tidak dikarang.
const COUNTS = [1, 5, 10, 25, 50, 100, 200]
const sel = ref(sponsorMissions[0]?.id ?? '')
const cnt = ref(25)
const custom = ref('')
const name = ref('')
const wa = ref('')
const editDonor = ref(false) // asli: C = !defaultDonor.phone; "Ubah" membuka isian Nama + WhatsApp
// asli: defaultDonor = {name, phone} dari sesi; nomor ditampilkan tanpa 62/0 di depan
const donorPhone = computed(() => (auth.user?.phone ? String(auth.user.phone).replace(/^\+?62/, '').replace(/^0/, '') : ''))
watch(() => auth.user, (u) => { if (u && !name.value) name.value = u.name || ''; if (u && !wa.value) wa.value = donorPhone.value }, { immediate: true })
const showFields = computed(() => !(auth.user?.phone && !editDonor.value))
const method = ref('') // kode metode
const methodOpen = ref(false)
const methods = ref([]) // GET /api/payment/methods (cadangan: data/payment.json)
const chosen = computed(() => methods.value.find((m) => m.code === method.value) || null)
const groups = computed(() => groupMethods(methods.value))
const expanded = ref({})
const FLAGS = [['id', 'Indonesia'], ['th', 'Thailand'], ['my', 'Malaysia'], ['sg', 'Singapore'], ['jp', 'Japan'], ['kr', 'South Korea'], ['cn', 'China']]
const isQris = (m) => m.code.toLowerCase() === 'qris' || m.type === 'qris'
const off = (m) => total.value > 0 && total.value < minFor(m)
const rpT = (n) => 'Rp' + n.toLocaleString('id-ID')
async function openMethods() {
  if (!methods.value.length) {
    try { const j = await fetch('/api/payment/methods').then((r) => r.json()); methods.value = j.methods || [] } catch { /* pakai cadangan */ }
    if (!methods.value.length) methods.value = payment
  }
  methodOpen.value = true
}
function chooseMethod(m) { method.value = m.code; methodOpen.value = false }
const msg = ref('')
const anon = ref(false)
const err = ref('')
const confirm = ref(false)
const sm = computed(() => sponsorMissions.find((x) => x.id === sel.value))
const nVoucher = computed(() => (custom.value ? Math.max(0, parseInt(custom.value.replace(/\D/g, ''), 10) || 0) : cnt.value))
const total = computed(() => nVoucher.value * (sm.value?.voucherAmount || 0))
function submit() {
  err.value = ''
  if (!sm.value) { err.value = 'Pilih kebaikan.'; return }
  if (nVoucher.value < 1) { err.value = 'Minimal 1 voucher.'; return }
  if (name.value.trim().length < 2) { err.value = 'Nama minimal 2 karakter.'; return }
  if (localPhone(wa.value).length < 8) { err.value = 'Nomor WhatsApp tidak valid.'; return }
  if (!method.value) { err.value = 'Pilih metode pembayaran dulu.'; return }
  const min = minFor(chosen.value || { code: method.value, type: '' })
  if (total.value < min) { err.value = `Metode ini minimal ${rupiah(min)}. Tambah jumlah voucher, atau pilih QRIS/e-wallet.`; return }
  confirm.value = true
}
function go() { confirm.value = false; alert('Demo: belum terhubung backend.') }
const inp = 'w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-[#005399]'
const lbl = 'block text-sm font-medium text-gray-700 mb-1.5'
</script>

<template>
  <div class="frame" style="background: #f5f6f8">
    <AppHeader />
    <PillTabs />

    <div class="min-h-screen pb-28">
      <div class="max-w-[480px] mx-auto sm:px-4">
        <div class="overflow-hidden border border-gray-100">
          <img src="/jalankebaikan-hero.jpg" alt="Jalan Kebaikan — Wadah berbuat baik dan melakukan kebaikan atau menjadi jalan agar orang lain bisa berbuat baik" class="w-full h-auto block" width="2048" height="682" />
        </div>
      </div>

      <div class="max-w-[480px] mx-auto px-4">
        <div>
          <div class="grid grid-cols-2 gap-2.5 mt-4">
            <button type="button" class="rounded-2xl px-3 py-2.5 flex items-center gap-2 transition-all" :class="mode === 'do' ? 'bg-[color:var(--lime)] shadow-md' : 'bg-[#f0f6fc]'" @click="mode = 'do'">
              <span class="w-9 h-9 rounded-full flex items-center justify-center shrink-0" :style="{ background: mode === 'do' ? 'rgba(255,255,255,0.55)' : '#e2e6d6' }">
                <svg viewBox="0 0 64 64" width="22" height="22" fill="none" aria-hidden="true">
                  <path d="M32 56V28" :stroke="mode === 'do' ? '#005399' : '#b7bda0'" stroke-width="4" stroke-linecap="round" />
                  <path d="M31 34c-2-10-12-12-19-9-1 9 8 15 19 12" :fill="mode === 'do' ? 'var(--lime-text)' : '#c7dcf0'" />
                  <path d="M33 28c2-11 12-13 20-10 1 10-9 16-20 13" :fill="mode === 'do' ? '#005399' : '#d6e6f5'" />
                </svg>
              </span>
              <span class="text-[12.5px] font-bold text-left leading-tight" :class="mode === 'do' ? 'text-[#1a1a1a]' : 'text-gray-500'">Sedekah via Amal Sholeh</span>
            </button>
            <button type="button" class="rounded-2xl px-3 py-2.5 flex items-center gap-2 transition-all" :class="mode === 'give' ? 'bg-[color:var(--lime)] shadow-md' : 'bg-[#f0f6fc]'" @click="mode = 'give'">
              <span class="w-9 h-9 rounded-full flex items-center justify-center shrink-0" :style="{ background: mode === 'give' ? 'rgba(255,255,255,0.55)' : '#e2e6d6' }">
                <svg viewBox="0 0 64 64" width="22" height="22" fill="none" aria-hidden="true">
                  <path d="M19 56 L28 30 H36 L45 56 Z" :fill="mode === 'give' ? '#c7dcf0' : '#f0f6fc'" />
                  <path d="M31.5 36h1M31 44h2M30 51h4" :stroke="mode === 'give' ? 'var(--lime-dark)' : '#c6ccb6'" stroke-width="2.4" stroke-linecap="round" />
                  <path d="M32 12c-2.6-3.6-8.4-1.8-8.4 2.7 0 3.1 3.7 5.7 8.4 8.8 4.7-3.1 8.4-5.7 8.4-8.8 0-4.5-5.8-6.3-8.4-2.7Z" :fill="mode === 'give' ? 'var(--lime)' : '#cdd2bd'" />
                </svg>
              </span>
              <span class="text-[12.5px] font-bold text-left leading-tight" :class="mode === 'give' ? 'text-[#1a1a1a]' : 'text-gray-500'">Menjadi Jalan Kebaikan</span>
            </button>
          </div>

          <p class="mt-2.5 text-[11.5px] text-gray-500 leading-snug text-center px-1">{{ mode === 'do' ? 'Berbuat baik tak harus dengan uang. Tuntaskan amalan sederhana — dzikir, tilawah, dan lainnya — dan sedekah dari para dermawan tercatat atas namamu.' : 'Beri sedekah agar orang lain bisa berbuat baik. Kebaikan yang mereka tuntaskan tercatat, dan pahalanya mengalir juga untukmu.' }}</p>

          <div class="mt-5">
            <template v-if="mode === 'do'">
              <div v-if="!amalan.length" class="rounded-2xl border border-dashed border-gray-200 bg-white p-8 text-center text-sm text-gray-500">Belum ada kebaikan yang bisa dikerjakan sekarang. Nantikan ya.</div>
              <template v-else>
                <div class="grid grid-cols-3 gap-2.5">
                  <router-link v-for="a in amalan" :key="a.id" :to="link(a.id)" class="hover:shadow-md transition-shadow rounded-xl">
                    <div class="rounded-xl bg-white border border-gray-100 overflow-hidden flex flex-col h-full text-center">
                      <div class="p-3 flex-1 flex flex-col items-center">
                        <img v-if="isImg(a.icon)" :src="a.icon" alt="" class="w-10 h-10 object-contain" />
                        <span v-else class="text-3xl leading-none">{{ a.icon || a.emoji }}</span>
                        <p class="mt-1.5 font-bold text-[12px] text-gray-900 leading-tight line-clamp-2 min-h-[30px]">{{ a.title }}</p>
                        <div class="mt-auto pt-1.5">
                          <p class="text-[8.5px] font-semibold uppercase tracking-wide text-gray-400 leading-none">Nominal Sedekah</p>
                          <p class="mt-0.5 font-bold text-sm" style="color: var(--lime-text)">{{ rupiah(a.nominal) }}</p>
                        </div>
                      </div>
                      <div v-if="a.voucher > 0" class="bg-[color:var(--lime)] text-white text-[10px] font-extrabold py-1.5 px-1 leading-[1.15]">{{ a.voucher }} Voucher Amal<br />Tersedia</div>
                    </div>
                  </router-link>
                </div>
                <p v-if="!auth.user" class="mt-3 text-center text-[11px] text-gray-400">Pilih kebaikan, lalu masuk sebentar — sedekah akan tercatat atas namamu.</p>
              </template>
            </template>

            <div v-else class="rounded-2xl bg-white border border-gray-100 p-5">
              <p v-if="!sponsorMissions.length" class="text-center text-sm text-gray-500 py-8">Belum ada kebaikan yang bisa kamu bantu saat ini.</p>
              <div v-else class="space-y-4">
                <div>
                  <label :class="lbl">Kebaikan yang ingin kamu bantu</label>
                  <div class="grid grid-cols-3 gap-2.5">
                    <button v-for="s in sponsorMissions" :key="s.id" type="button" class="rounded-xl overflow-hidden flex flex-col text-center transition-all" :class="sel === s.id ? 'border-2 border-[color:var(--lime)] bg-[#f0f6fc]' : 'border border-gray-200 bg-white'" @click="sel = s.id; custom = ''">
                      <div class="bg-[color:var(--lime)] text-white text-sm font-extrabold py-1.5 px-1 leading-tight">{{ rupiah(s.voucherAmount) }}</div>
                      <div class="p-3 flex-1 flex flex-col items-center justify-center">
                        <img v-if="isImg(s.icon)" :src="s.icon" alt="" class="w-10 h-10 object-contain" />
                        <span v-else class="text-3xl leading-none">{{ s.icon || TYPE_EMOJI[s.type] || '🌟' }}</span>
                        <p class="mt-1.5 text-[9px] font-semibold uppercase tracking-wide text-gray-400 leading-none">untuk amalan</p>
                        <p class="mt-0.5 font-bold text-[12px] text-gray-900 leading-tight line-clamp-2 min-h-[30px]">{{ s.title }}</p>
                      </div>
                    </button>
                  </div>
                </div>
                <div>
                  <label :class="lbl">Berapa voucher yang ingin kamu beri?</label>
                  <div class="grid grid-cols-4 gap-2 mb-2">
                    <button v-for="c in COUNTS" :key="c" type="button" class="py-2 rounded-lg text-sm font-semibold border" :class="!custom && cnt === c ? 'bg-[color:var(--lime)] border-[color:var(--lime)] text-white' : 'bg-white border-gray-200 text-gray-600'" @click="cnt = c; custom = ''">{{ c }}</button>
                  </div>
                  <input v-model="custom" inputmode="numeric" placeholder="Jumlah voucher lain" :class="inp" />
                  <p class="mt-1.5 text-xs text-gray-500">{{ nVoucher }} voucher × {{ rupiah(sm?.voucherAmount || 0) }} = <b class="text-gray-800">{{ rupiah(total) }}</b>. Tiap voucher jadi 1 sedekah lewat kebaikan seseorang untuk <b>{{ sm?.campaignTitle }}</b>.</p>
                </div>
                <div v-if="!showFields" class="rounded-lg bg-gray-50 border border-gray-200 px-4 py-3 flex items-center justify-between text-sm">
                  <span class="text-gray-700">Berdonasi sebagai <b>{{ name }}</b></span>
                  <button type="button" class="text-[#005399] font-semibold text-xs" @click="editDonor = true">Ubah</button>
                </div>
                <template v-else>
                  <div>
                    <label :class="lbl">Nama</label>
                    <input v-model="name" placeholder="Nama kamu" :class="inp" />
                  </div>
                  <div>
                    <label :class="lbl">WhatsApp</label>
                    <div class="flex items-center gap-2">
                      <span class="px-3 py-2.5 rounded-lg bg-gray-100 text-sm text-gray-500">+62</span>
                      <input v-model="wa" inputmode="numeric" placeholder="81234567890" :class="inp" />
                    </div>
                  </div>
                </template>
                <div>
                  <label :class="lbl">Metode Pembayaran</label>
                  <button type="button" class="flex items-center gap-3 w-full px-4 py-3 rounded-xl transition-all active:scale-[0.99]" :style="{ border: method ? '2px solid #003f75' : '1.5px solid #e5e7eb', background: method ? '#fff8ed' : '#fafafa' }" @click="openMethods">
                    <template v-if="chosen">
                      <img :src="logo(chosen)" :alt="chosen.name" class="w-7 h-7 object-contain rounded" />
                      <span class="text-[13px] font-bold text-[#005399] flex-1 text-left">{{ chosen.name }}</span>
                      <Icon name="check" class="w-4 h-4 text-[#003f75]" />
                    </template>
                    <span v-else class="text-[13px] font-semibold text-gray-500 flex-1 text-left">Pilih metode pembayaran</span>
                    <Icon name="chevronRight" class="w-4 h-4 flex-shrink-0 text-gray-400" />
                  </button>
                </div>
                <div>
                  <label :class="lbl">Pesan / Doa <span class="text-gray-400 font-normal">(opsional)</span></label>
                  <textarea v-model="msg" rows="2" :class="inp"></textarea>
                </div>
                <label class="flex items-center gap-2 text-sm text-gray-600">
                  <input v-model="anon" type="checkbox" class="accent-[color:var(--lime)]" /> Tampilkan sebagai anonim
                </label>
                <div v-if="err" class="rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2.5">{{ err }}</div>
                <button class="w-full py-3.5 rounded-xl bg-[color:var(--lime)] text-white font-bold text-sm disabled:opacity-50 flex items-center justify-center gap-2" @click="submit">Beri {{ nVoucher }} Voucher · {{ rupiah(total) }}</button>
                <p class="text-center text-[11px] text-gray-400">Sedekahmu langsung mengalir ke program, lalu orang lain menyalurkannya lewat kebaikan. Pahalanya mengalir juga untukmu.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom sheet metode pembayaran (PaymentMethodModal sedekah.id; sama dengan ZakatPayForm) -->
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
              <button v-for="m in (expanded[g.type] ? g.items : g.items.slice(0, 3))" :key="m.code" type="button" :disabled="off(m)" :title="off(m) ? t('paymentModal.minDonationFor', { amount: rpT(minFor(m)) }) : undefined" @click="chooseMethod(m)"
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

    <div v-if="confirm" class="fixed inset-0 z-[80] flex items-end sm:items-center justify-center" style="background: rgba(8, 15, 44, 0.6); backdrop-filter: blur(2px)" role="dialog" aria-modal="true" @click="confirm = false">
      <div class="w-full sm:w-auto sm:max-w-sm bg-white rounded-t-3xl sm:rounded-3xl p-6 shadow-2xl" @click.stop>
        <div class="text-3xl text-center">🌿</div>
        <h3 class="mt-2 text-center text-base font-bold text-gray-900">Sebelum melanjutkan</h3>
        <p class="mt-2 text-sm text-gray-600 leading-relaxed text-center">Sedekah ini akan <b class="text-gray-800">tercatat atas nama orang yang menyelesaikan misi kebaikan</b>. Kamu berperan membuka jalannya. Insya Allah pahala tetap mengalir untukmu sebagai yang memudahkan kebaikan. 🤍</p>
        <div class="mt-5 grid grid-cols-2 gap-2.5">
          <button type="button" class="py-3 rounded-xl border border-gray-200 text-gray-600 font-semibold text-sm" @click="confirm = false">Tidak</button>
          <button type="button" class="py-3 rounded-xl bg-[color:var(--lime)] text-white font-bold text-sm" @click="go">Ya, Saya Setuju</button>
        </div>
      </div>
    </div>
  </div>
  <BottomNav />
</template>
