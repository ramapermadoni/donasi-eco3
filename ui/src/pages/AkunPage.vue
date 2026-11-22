<script setup>
const demoMode = import.meta.env.VITE_REAL_API === '0'
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Icon from '../components/Icon.vue'
import BottomNav from '../components/BottomNav.vue'
import AkunPhoneCard from '../components/AkunPhoneCard.vue'
import AkunAvatarModal from '../components/AkunAvatarModal.vue'
import { t, tr, lp, bcp } from '../i18n'
import { rpTight } from '../utils/format'
import { auth, sendOtp, verifyOtp, saveProfile, logout, removeAccount, loadMe } from '../auth'

const router = useRouter()
const route = useRoute()

// ?next=/jalankebaikan/xyz → setelah login kembali ke halaman tujuan (hanya path internal)
const safeNext = () => { const n = route.query.next; return typeof n === 'string' && n.startsWith('/') && !n.startsWith('//') ? n : null }
watch(() => auth.user, (u) => { const n = u && safeNext(); if (n) router.replace(n) }, { immediate: true })

// view: login | otp | (profile when auth.user)
const view = ref('login')
const busy = ref(false)
const error = ref('')

/* ---------- login ---------- */
// Alur disalin dari chunk /akun asli: satu kolom kode 6 digit (bukan kotak per digit), kirim ulang tanpa hitung mundur (toast hijau), galat tampil di dalam form.
const phone = ref('')
const code = ref('')
const sentTo = ref('')
const googleErr = ref(route.query.error === 'google' ? t('akun.errGoogle') : '')
const toast = ref('')
// sama seperti sedekah.id: ketik 0812… / 812… / 62812… → selalu 62812…
function normPhone(v) { const d = v.replace(/\D/g, ''); return d.startsWith('62') ? d : d.startsWith('0') ? '62' + d.slice(1) : d ? '62' + d : d }
const fullPhone = computed(() => '+' + phone.value)
const onPhone = (e) => { phone.value = normPhone(e.target.value); e.target.value = phone.value; error.value = '' }
const onCode = (e) => { code.value = e.target.value.replace(/\D/g, '').slice(0, 6); e.target.value = code.value; error.value = '' }
async function run(fn) { busy.value = true; error.value = ''; try { await fn() } catch (e) { error.value = e.message || t('akun.errGeneric') } finally { busy.value = false } }

const requestCode = () => run(async () => {
  if (phone.value.length < 10) throw new Error(t('akun.errPhoneInvalid'))
  const sp = await sendOtp(fullPhone.value); sentTo.value = sp ?? (demoMode ? fullPhone.value : phone.value); view.value = 'otp'; code.value = '' })
const resend = async () => {
  code.value = ''; error.value = ''; busy.value = true
  try { await sendOtp(fullPhone.value); toast.value = t('akun.codeResent'); setTimeout(() => (toast.value = ''), 3000) } catch { /* asli: galat kirim ulang diabaikan */ } finally { busy.value = false }
}
const confirmCode = () => run(async () => { if (!code.value) throw new Error(t('akun.errCodeRequired')); await verifyOtp(fullPhone.value, code.value.trim()) })
const googleOn = ref(false) // asli: tombol Google hanya tampil bila GET /api/auth/google/status -> {enabled:true} dan bukan WebView
if (!/; wv\)/.test(navigator.userAgent)) fetch('/api/auth/google/status').then((r) => (r.ok ? r.json() : null)).then((d) => { if (d?.enabled) googleOn.value = true }).catch(() => {})
const google = () => { googleErr.value = t('akun.errGoogle') } // asli: tautan /api/auth/google?next=… (tidak bisa selesai di localhost: cookie terikat domain sedekah.id)

/* ---------- profile ---------- */
const editing = ref(false)
const draft = reactive({ name: '', email: '' })
const rupiah = (n) => rpTight(n || 0, bcp()) // asli: formatRupiahTight(n, locale) -> "Rp3.000" / en "Rp3,000"
const ST = { paid: ['#dcfce7', '#15803d'], pending: ['#fef3c7', '#a16207'], failed: ['#fee2e2', '#b91c1c'], expired: ['#f3f4f6', '#6b7280'], refunded: ['#ede9fe', '#6d28d9'] }
function startEdit() { draft.name = auth.user.name; draft.email = auth.user.email || ''; editing.value = true }
function cancelEdit() { editing.value = false; error.value = '' }
const saveEdit = () => run(async () => { await saveProfile({ name: draft.name.trim(), email: draft.email.trim() }); editing.value = false })
const since = computed(() => { try { return new Date(auth.user.donorSince).toLocaleDateString(bcp(), { day: 'numeric', month: 'long', year: 'numeric' }) } catch { return '' } })
const PRESETS = ['300b474a-aa73-4a20-8096-2586b8ec8b5e','f12c871f-fb94-4305-8bff-fd43406653bd','62990a50-5ab8-4606-a604-5d7a52f42725','7a968e53-3c7b-4035-9973-d6097184131b','e4ceabe5-5159-43ee-ab57-253a49672a96','ba2db7c9-7e85-4ce2-ba2d-9b3fe54f9388','f6171463-a235-4716-934b-adaefaec91c7','ca95dd83-3ca6-46c9-af27-a7d670226394','190617e2-6846-4718-a772-720e686acc9f','46dc7a66-8f2e-45ac-aa0c-dd32d25bbf30','03fae261-8afa-4b9c-810c-4e85e643a8cc','ebf3fff5-7460-4850-a7ef-482821450a97','1cff1bbb-ce42-4b5c-8357-dae50e2c519c','8c2f0623-da9f-4941-8f1c-4e47bcb08c9a','634986b0-976d-4166-8bcc-e9c8d0c09615','719cc4c9-e832-484d-8e85-e03953cf2df9','dc37c4ca-dd4e-49f4-b724-250fb8c14aa0'].map((id) => `https://sedekah.id/api/media/media/2026/08/${id}.webp`)
// avatar bawaan: hash dari telepon/email/nama (persis defaultAvatar di sedekah.id)
function defaultAvatar(seed) { let a = 0; for (let i = 0; i < seed.length; i++) a = (31 * a + seed.charCodeAt(i)) | 0; return PRESETS[Math.abs(a) % PRESETS.length] }
const avatar = computed(() => auth.user?.avatarUrl || defaultAvatar(String(auth.user?.phone || auth.user?.email || auth.user?.name || 'u')))
const doas = computed(() => auth.user?.doas || [])
const doaShown = ref(5)

const shown = ref(5)
const st = (x) => { const k = ST[x] ? x : 'pending'; return [t('akun.status.' + k), ST[k][0], ST[k][1]] }
function ago(tm) {
  const ms = Date.now() - new Date(tm).getTime()
  if (!tm) return ''
  if (isNaN(ms)) return String(tm)
  const m = Math.floor(ms / 6e4), h = Math.floor(ms / 36e5), d = Math.floor(ms / 864e5)
  return m < 1 ? t('akun.justNow') : m < 60 ? t('akun.minsAgo', { n: m }) : h < 24 ? t('akun.hoursAgo', { n: h }) : d < 30 ? t('akun.daysAgo', { n: d }) : new Date(tm).toLocaleDateString(bcp(), { day: 'numeric', month: 'long', year: 'numeric' })
}
onMounted(() => { if (auth.user) loadMe() })
// kartu ajakan Sedekah Rutin tampil bila masuk dan belum punya jadwal (rutinStore lokal, tanpa request /api/recurring/*)
const showRecurring = computed(() => !!auth.user && !auth.user.recurring)
const avatarOpen = ref(false)
const onAvatarSaved = (url) => { auth.user = { ...auth.user, avatarUrl: url }; avatarOpen.value = false }
const histShown = shown
const history = computed(() => auth.user?.history || [])

const delOpen = ref(false)
const delOk = ref(false)
const doDelete = () => run(async () => { await removeAccount(); delOpen.value = false; view.value = 'login'; phone.value = '' })
const doLogout = () => { logout(); view.value = 'login'; phone.value = ''; code.value = '' }

</script>

<template>
  <div class="frame">
    <!-- ============ MEMUAT SESI (asli: spinner layar penuh sampai /api/auth/me menjawab) ============ -->
    <div v-if="!auth.ready" style="background: #f5f6f8; min-height: 100vh">
      <div class="flex items-center justify-center" style="height: 100vh"><div class="w-8 h-8 rounded-full border-4 border-gray-200 animate-spin" style="border-top-color: var(--lime)"></div></div>
    </div>

    <!-- ============ PROFILE ============ -->
    <div v-else-if="auth.user" style="background: #f5f6f8; min-height: 100vh">
      <div class="max-w-[480px] mx-auto pb-28">
        <div class="px-5 pt-8 pb-16 relative" style="background: url(/akun-hero.webp) center/cover no-repeat, linear-gradient(180deg, var(--lime) 0%, var(--lime-dark) 100%)">
          <div class="flex items-center justify-between mb-4">
            <img class="h-9 w-auto" style="filter: brightness(0) invert(0); mix-blend-mode: multiply" alt="donasi" src="/logo-donasi.svg" />
            <button class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg backdrop-blur-sm" style="background: rgba(0, 0, 0, 0.08); font-size: 12px; font-weight: 600; color: #1a1a1a" @click="doLogout"><Icon name="logout" class="w-[13px] h-[13px]" /> {{ t('akun.signOut') }}</button>
          </div>
          <div class="flex flex-col items-center text-center mt-2">
            <div class="relative mb-3">
              <img :src="avatar" alt="" class="w-20 h-20 rounded-full object-cover" style="box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2); border: 4px solid white; background: #fff" />
              <button :aria-label="t('akun.avatarTitle')" class="absolute -bottom-1 -right-1 w-7 h-7 rounded-full bg-[#1a1a1a] flex items-center justify-center" style="border: 2px solid white" @click="avatarOpen = true"><Icon name="pencil" class="w-3 h-3 text-white" /></button>
            </div>
            <p style="font-size: 20px; font-weight: 800; color: #1a1a1a">{{ auth.user.name || t('akun.donorFallback') }}</p>
            <div class="flex flex-col items-center gap-0.5 mt-1">
              <p v-if="auth.user.phone" style="font-size: 12px; color: rgba(26, 26, 26, 0.7)">+{{ auth.user.phone }}</p>
              <p v-if="auth.user.email" style="font-size: 12px; color: rgba(26, 26, 26, 0.7)">{{ auth.user.email }}</p>
            </div>
          </div>
        </div>

        <div class="px-4 -mt-10 relative z-10">
          <div class="bg-white rounded-2xl p-5" style="box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08)">
            <div class="grid grid-cols-2 divide-x divide-gray-100">
              <div class="text-center pr-3">
                <div class="flex items-center justify-center gap-1.5 mb-1"><Icon name="heart" class="w-3.5 h-3.5" style="color: var(--lime-text); fill: var(--lime)" /><p style="font-size: 10px; color: #9ca3af; font-weight: 600; letter-spacing: 0.05em">{{ t('akun.totalDonations') }}</p></div>
                <p style="font-size: 22px; font-weight: 900; color: #1a1a1a">{{ auth.user.count ?? '–' }}</p>
                <p style="font-size: 11px; color: #9ca3af">{{ t('akun.timesShared') }}</p>
              </div>
              <div class="text-center pl-3">
                <div class="flex items-center justify-center gap-1.5 mb-1"><Icon name="calendar" class="w-3.5 h-3.5" style="color: var(--lime-text)" /><p style="font-size: 10px; color: #9ca3af; font-weight: 600; letter-spacing: 0.05em">{{ t('akun.amountLabel') }}</p></div>
                <p style="font-size: 18px; font-weight: 900; color: #1a1a1a; line-height: 1.2">{{ auth.user.total != null ? rupiah(auth.user.total) : '–' }}</p>
                <p style="font-size: 11px; color: #9ca3af">{{ t('akun.collected') }}</p>
              </div>
            </div>
            <p v-if="auth.user.donorSince" class="text-center mt-3 pt-3 border-t border-gray-100" style="font-size: 11px; color: #9ca3af" v-html="tr('akun.joinedSince', { date: since }, { b: (i) => '<span style=&quot;color: #1a1a1a; font-weight: 600&quot;>' + i + '</span>' })"></p>
          </div>
        </div>

        <div v-if="!auth.user.phone" class="px-4 mt-5"><AkunPhoneCard /></div>

        <div class="px-4 mt-5">
          <div class="bg-white rounded-2xl p-5" style="box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05)">
            <div class="flex items-center justify-between mb-4">
              <p style="font-size: 14px; font-weight: 800; color: #1a1a1a">{{ t('akun.myProfile') }}</p>
              <button v-if="!editing" class="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold" style="background: #f0f6fc; color: var(--lime-text); border: 1px solid #c7dcf0" @click="startEdit"><Icon name="pencil" class="w-3 h-3" /> {{ t('akun.edit') }}</button>
              <button v-else class="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold text-gray-500 border border-gray-200" @click="cancelEdit"><Icon name="x" class="w-3 h-3" /> {{ t('akun.cancel') }}</button>
            </div>
            <form v-if="editing" class="space-y-3" @submit.prevent="saveEdit">
              <div>
                <label style="display: block; font-size: 11px; font-weight: 600; color: #9ca3af; margin-bottom: 4px; letter-spacing: 0.04em">{{ t('akun.fullNameUpper') }}</label>
                <input v-model="draft.name" :placeholder="t('akun.fullNamePlaceholder')" required minlength="2" class="w-full px-3 py-2.5 border border-gray-200 rounded-xl outline-none focus:border-[color:var(--lime)] focus:ring-2 focus:ring-[color:color-mix(in_srgb,var(--lime)_20%,transparent)]" style="font-size: 14px" />
              </div>
              <div>
                <label style="display: block; font-size: 11px; font-weight: 600; color: #9ca3af; margin-bottom: 4px; letter-spacing: 0.04em">{{ t('akun.emailOptionalUpper') }}</label>
                <input v-model="draft.email" type="email" :placeholder="t('akun.emailPlaceholder')" class="w-full px-3 py-2.5 border border-gray-200 rounded-xl outline-none focus:border-[color:var(--lime)] focus:ring-2 focus:ring-[color:color-mix(in_srgb,var(--lime)_20%,transparent)]" style="font-size: 14px" />
              </div>
              <p style="font-size: 11px; color: #9ca3af">{{ t('akun.emailHint') }}</p>
              <div v-if="error" class="rounded-lg px-3 py-2 bg-red-50 border border-red-200"><p style="font-size: 12px; color: #dc2626">{{ error }}</p></div>
              <button type="submit" :disabled="busy" class="w-full py-3 rounded-xl text-[#fff] font-bold flex items-center justify-center gap-2 disabled:opacity-50" style="background: linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%); font-size: 14px"><Icon v-if="busy" name="loader" class="w-4 h-4 animate-spin" /><template v-else><Icon name="check" class="w-3.5 h-3.5" /> {{ t('akun.save') }}</template></button>
            </form>
            <div v-else class="space-y-3">
              <div v-for="r in [['user', t('akun.fullName'), auth.user.name || '–'], ['phone', t('akun.whatsapp'), auth.user.phone ? '+' + auth.user.phone : '–', t('akun.whatsappCantChange')], ['mail', t('akun.email'), auth.user.email || t('akun.emailEmpty')]]" :key="r[1]" class="flex items-start gap-3">
                <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style="background: #f0f6fc"><Icon :name="r[0]" class="w-4 h-4" style="color: var(--lime-text)" /></div>
                <div class="min-w-0 flex-1">
                  <p style="font-size: 11px; color: #9ca3af; font-weight: 600; letter-spacing: 0.04em">{{ r[1].toUpperCase() }}</p>
                  <p class="truncate" style="font-size: 14px; color: #1a1a1a; font-weight: 600; margin-top: 2px">{{ r[2] }}</p>
                  <p v-if="r[3]" style="font-size: 10px; color: #9ca3af; margin-top: 1px">{{ r[3] }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="showRecurring" class="px-4 mt-5">
          <router-link :to="lp('/shadaqa-rutin/setup')" class="flex items-center gap-3 rounded-2xl px-3 py-2.5 active:scale-[0.99] transition-transform" style="background: linear-gradient(135deg, #f0f6fc 0%, #ffffff 70%); border: 1px solid #c7dcf0; box-shadow: 0 1px 5px color-mix(in srgb, var(--lime) 13%, transparent)">
            <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" aria-hidden="true" style="background: linear-gradient(135deg, var(--lime), var(--lime-dark))"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5 text-white"><path d="m17 2 4 4-4 4" /><path d="M3 11v-1a4 4 0 0 1 4-4h14" /><path d="m7 22-4-4 4-4" /><path d="M21 13v1a4 4 0 0 1-4 4H3" /></svg></div>
            <div class="flex-1 min-w-0">
              <p class="truncate" style="font-size: 13px; font-weight: 800; color: #1a1a1a">{{ t('akun.recurringTitle') }}</p>
              <p class="truncate" style="font-size: 11px; color: #6b7280; margin-top: 1px">{{ t('akun.recurringSubtitle') }}</p>
            </div>
            <span class="flex items-center gap-0.5 pl-2.5 pr-2 py-1.5 rounded-lg flex-shrink-0" style="background: var(--lime); font-size: 11.5px; font-weight: 800; color: #fff">{{ t('akun.recurringStart') }}<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="w-3.5 h-3.5"><path d="m9 18 6-6-6-6" /></svg></span>
          </router-link>
        </div>

        <router-link :to="lp('/jejak-kebaikan')" class="block px-4 mt-5 active:scale-[0.99] transition-transform">
          <div class="relative w-full h-[112px] rounded-2xl overflow-hidden"><img src="/promo/jejak-kebaikan-banner.png" :alt="t('akun.jejakKebaikanTitle')" class="absolute inset-0 w-full h-full object-cover" /></div>
        </router-link>

        <div class="px-4 mt-5">
          <div class="bg-white rounded-2xl p-5" style="box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05)">
            <div class="flex items-center justify-between mb-3">
              <p style="font-size: 14px; font-weight: 800; color: #1a1a1a">{{ t('akun.donationHistory') }}</p>
              <span style="font-size: 11px; color: #9ca3af">{{ t('akun.historyTotal', { count: history.length }) }}</span>
            </div>
            <div v-if="!history.length" class="py-8 text-center">
              <Icon name="history" class="w-10 h-10 mx-auto mb-2 text-gray-200" />
              <p style="font-size: 13px; color: #9ca3af">{{ t('akun.noDonations') }}</p>
              <router-link :to="lp('/')" class="inline-block mt-3 px-4 py-2 rounded-lg text-[#fff] text-xs font-bold" style="background: var(--lime)">{{ t('akun.startDonating') }}</router-link>
            </div>
            <template v-else>
              <div class="space-y-2.5">
                <component :is="h.id ? 'router-link' : 'div'" v-for="(h, n) in history.slice(0, histShown)" :key="h.id || n" :to="h.id ? '/donasi/' + h.id : undefined" class="block rounded-xl border border-gray-100 p-3 hover:border-[color:var(--lime)] transition-colors">
                  <div class="flex items-start justify-between gap-2 mb-1">
                    <div class="min-w-0 flex-1">
                      <p style="font-size: 14px; font-weight: 700; color: #1a1a1a">{{ h.currency === 'USD' ? '$' + (h.amount / 100).toFixed(2) : rupiah(h.amount) }}<span v-if="h.currency === 'USD' && h.idr" style="font-size: 11px; color: #9ca3af; font-weight: 500; margin-left: 6px">≈ {{ rupiah(h.idr) }}</span></p>
                      <p class="truncate" style="font-size: 12px; color: #6b7280; margin-top: 2px">{{ h.campaign || t('akun.generalDonation') }}</p>
                    </div>
                    <span class="flex-shrink-0 px-2 py-0.5 rounded-full text-[10px] font-semibold" :style="{ background: st(h.status)[1], color: st(h.status)[2] }">{{ st(h.status)[0] }}</span>
                  </div>
                  <p style="font-size: 11px; color: #9ca3af; margin-top: 4px">{{ ago(h.when) }}<span v-if="h.channel"> • {{ h.channel.toUpperCase() }}</span></p>
                </component>
              </div>
              <button v-if="history.length > histShown" class="w-full mt-3 py-2 rounded-lg text-xs font-bold border border-gray-200 hover:border-[color:var(--lime)] hover:bg-[#f0f6fc] transition-colors" style="color: var(--lime-text)" @click="shown += 10">{{ t('akun.viewMore', { count: history.length - histShown }) }}</button>
            </template>
          </div>
        </div>

        <div v-if="doas.length" class="px-4 mt-5">
          <div class="bg-white rounded-2xl p-5" style="box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05)">
            <div class="flex items-center justify-between mb-3">
              <p style="font-size: 14px; font-weight: 800; color: #1a1a1a">Doa Saya</p>
              <span style="font-size: 11px; color: #9ca3af">{{ doas.length }} doa</span>
            </div>
            <div class="space-y-2.5">
              <div v-for="d in doas.slice(0, doaShown)" :key="d.id" class="rounded-xl border border-gray-100 p-3">
                <p class="line-clamp-3 italic" style="font-size: 13px; color: #374151; line-height: 1.5">“{{ d.message }}”</p>
                <div class="flex items-center gap-2 mt-2 flex-wrap">
                  <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full" style="background: #f0f6fc; color: var(--lime-text); font-size: 11px; font-weight: 700"><Icon name="sparkles" class="w-3 h-3" /> {{ d.amin_count }} amin</span>
                  <span v-if="d.aminers?.length" class="truncate" style="font-size: 11px; color: #9ca3af">oleh {{ d.aminers.join(', ') }}{{ d.amin_count > d.aminers.length ? ' …' : '' }}</span>
                </div>
              </div>
            </div>
            <button v-if="doas.length > doaShown" class="w-full mt-3 py-2 rounded-lg text-xs font-bold border border-gray-200 hover:border-[color:var(--lime)] hover:bg-[#f0f6fc] transition-colors" style="color: var(--lime-text)" @click="doaShown += 10">Lihat lebih banyak</button>
          </div>
        </div>

        <div class="px-4 mt-8 text-center">
          <button class="inline-flex items-center gap-1.5 hover:underline" style="font-size: 12px; color: #b91c1c; font-weight: 600" @click="delOpen = true; delOk = false"><Icon name="trash" class="w-[13px] h-[13px]" /> {{ t('akun.deleteAccount') }}</button>
        </div>
      </div>

      <div v-if="delOpen" class="fixed inset-0 z-50 flex items-center justify-center px-4" style="background: rgba(0, 0, 0, 0.5)">
        <div class="bg-white rounded-2xl p-5 w-full max-w-[400px]" style="box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25)">
          <p style="font-size: 16px; font-weight: 800; color: #1a1a1a">{{ t('akun.deleteTitle') }}</p>
          <p class="mt-3" style="font-size: 13px; color: #374151; line-height: 1.6">{{ t('akun.deleteWarn1') }}</p>
          <p class="mt-2" style="font-size: 13px; color: #6b7280; line-height: 1.6">{{ t('akun.deleteWarn2') }}</p>
          <label class="flex items-start gap-2.5 mt-4 cursor-pointer"><input v-model="delOk" type="checkbox" class="mt-0.5 w-4 h-4 accent-red-600" /><span style="font-size: 13px; color: #1a1a1a; font-weight: 600; line-height: 1.5">{{ t('akun.deleteConfirmLabel') }}</span></label>
          <div v-if="error" class="mt-3 rounded-lg px-3 py-2 bg-red-50 border border-red-200"><p style="font-size: 12px; color: #dc2626">{{ error }}</p></div>
          <div class="flex gap-2 mt-5">
            <button :disabled="busy" class="flex-1 py-3 rounded-xl font-bold border border-gray-200 text-gray-600 disabled:opacity-50" style="font-size: 13px" @click="delOpen = false">{{ t('akun.cancel') }}</button>
            <button :disabled="!delOk || busy" class="flex-1 py-3 rounded-xl font-bold text-white disabled:opacity-40 flex items-center justify-center gap-2" style="background: #dc2626; font-size: 13px" @click="doDelete">{{ busy ? t('akun.deleteDeleting') : t('akun.deleteConfirmBtn') }}</button>
          </div>
        </div>
      </div>
      <AkunAvatarModal v-if="avatarOpen" :current="avatar" :presets="PRESETS" @close="avatarOpen = false" @saved="onAvatarSaved" />
    </div>

    <!-- ============ LOGIN / OTP ============ -->
    <div v-else class="min-h-screen flex flex-col relative overflow-hidden" style="background: linear-gradient(180deg, #f0f6fc 0%, #f0f6fc 30%, #ffffff 70%)">
      <div class="absolute top-10 left-6 text-3xl opacity-30 select-none animate-pulse">✨</div>
      <div class="absolute top-32 right-8 text-2xl opacity-20 select-none">💚</div>
      <div class="absolute bottom-32 left-10 text-2xl opacity-25 select-none">🌿</div>
      <div class="absolute top-52 left-1/2 text-xl opacity-20 select-none">⭐</div>
      <div class="flex-1 flex flex-col items-center justify-center px-4 py-6 relative z-10" style="padding-bottom:24px">
        <div class="w-full max-w-[400px]">
          <div class="text-center mb-6">
            <div class="inline-block mb-5"><img alt="donasi" width="285" height="60" class="h-11 w-auto mx-auto" src="/logo-donasi.svg" /></div>
            <h1 style="font-size: 24px; font-weight: 900; color: #1a1a1a; letter-spacing: -0.5px">{{ t('akun.welcome') }}</h1>
            <p style="font-size: 13px; color: #6b7280; margin-top: 6px; line-height: 1.5">{{ t('akun.welcomeSub') }}</p>
          </div>

          <div class="bg-white rounded-3xl p-6" style="box-shadow: 0 12px 40px color-mix(in srgb, var(--lime) 15%, transparent), 0 1px 3px rgba(0, 0, 0, 0.04); border: 1px solid #f0f6fc">
            <div v-if="googleErr" class="mb-4 bg-red-50 border border-red-200 rounded-xl px-4 py-3"><p style="font-size: 13px; color: #dc2626; text-align: center">{{ googleErr }}</p></div>

            <form v-if="view === 'otp'" class="space-y-4" @submit.prevent="confirmCode">
              <div class="rounded-xl px-4 py-3 text-center" style="background: #f0f6fc; border: 1px solid #c7dcf0">
                <p style="font-size: 12px; color: var(--lime-text); margin-bottom: 4px; font-weight: 600">{{ t('akun.codeSentTo') }}</p>
                <p style="font-size: 14px; font-weight: 700; color: #1a1a1a">{{ sentTo }}</p>
                <button type="button" class="hover:underline" style="font-size: 12px; color: var(--lime-text); margin-top: 4px; font-weight: 600" @click="view = 'login'; code = ''; error = ''">{{ t('akun.changeNumber') }}</button>
              </div>
              <div>
                <label style="display: block; font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 6px">{{ t('akun.enterCode') }}</label>
                <input type="text" inputmode="numeric" :value="code" placeholder="• • • • • •" maxlength="6" autofocus class="w-full px-4 py-4 text-center border border-gray-200 rounded-xl outline-none transition-all focus:border-[color:var(--lime)] focus:ring-[3px] focus:ring-[color:color-mix(in_srgb,var(--lime)_10%,transparent)]" style="font-size: 28px; font-weight: 800; letter-spacing: 0.5em; color: #1a1a1a" @input="onCode" />
                <p v-if="demoMode" style="font-size: 11px; color: #9ca3af; margin-top: 5px; text-align: center">demo: isi 6 angka apa saja</p>
              </div>
              <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl px-4 py-3"><p style="font-size: 13px; color: #dc2626; text-align: center">{{ error }}</p></div>
              <button type="submit" :disabled="busy || code.length < 6" class="w-full py-3.5 rounded-2xl text-[#fff] font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]" style="background: linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%); font-size: 15px; box-shadow: 0 4px 16px color-mix(in srgb, var(--lime) 30%, transparent)">
                <span v-if="busy" class="flex items-center justify-center gap-2"><span class="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin"></span>{{ t('akun.verifying') }}</span><template v-else>{{ t('akun.signIn') }}</template>
              </button>
              <div class="text-center"><button type="button" :disabled="busy" class="disabled:opacity-50 hover:underline" style="font-size: 13px; color: var(--lime-text); font-weight: 600" @click="resend">{{ t('akun.resendCode') }}</button></div>
            </form>

            <form v-else class="space-y-4" @submit.prevent="requestCode">
              <div>
                <label style="display: block; font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 6px">{{ t('akun.whatsappNumber') }}</label>
                <div class="relative">
                  <Icon name="phone" class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input type="tel" autocomplete="tel" placeholder="628123456789" :value="phone" class="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl outline-none transition-all focus:border-[color:var(--lime)] focus:ring-[3px] focus:ring-[color:color-mix(in_srgb,var(--lime)_10%,transparent)]" style="font-size: 14px" @input="onPhone" />
                </div>
                <p style="font-size: 11px; color: #9ca3af; margin-top: 5px">{{ t('akun.otpWillSend') }}</p>
              </div>
              <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl px-4 py-3"><p style="font-size: 13px; color: #dc2626; text-align: center">{{ error }}</p></div>
              <button type="submit" :disabled="busy" class="w-full py-3.5 rounded-2xl text-[#fff] font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]" style="background: linear-gradient(135deg, var(--lime) 0%, var(--lime-dark) 100%); font-size: 15px; box-shadow: 0 4px 16px color-mix(in srgb, var(--lime) 30%, transparent)">
                <span v-if="busy" class="flex items-center justify-center gap-2"><span class="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin"></span>{{ t('akun.sendingCode') }}</span><template v-else>{{ t('akun.continue') }}</template>
              </button>
            </form>

            <template v-if="view === 'login'">
              <div class="relative my-5">
                <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-gray-100"></div></div>
                <div class="relative flex justify-center"><span class="px-3 bg-white" style="font-size: 12px; color: #9ca3af">{{ t('akun.or') }}</span></div>
              </div>
              <a v-if="googleOn" :href="'/api/auth/google?next=' + encodeURIComponent(safeNext() || lp('/akun'))" class="flex items-center justify-center gap-2.5 w-full py-3 rounded-2xl border border-gray-200 hover:bg-gray-50 transition-colors mb-4" @click.prevent="google">
                <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path fill="#4285F4" d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.72v2.26h2.92c1.71-1.57 2.68-3.88 2.68-6.62z" /><path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.92-2.26c-.81.54-1.84.86-3.04.86-2.34 0-4.32-1.58-5.03-3.7H.96v2.33A9 9 0 0 0 9 18z" /><path fill="#FBBC05" d="M3.97 10.72A5.4 5.4 0 0 1 3.68 9c0-.6.11-1.18.29-1.72V4.95H.96A9 9 0 0 0 0 9c0 1.45.35 2.82.96 4.05l3.01-2.33z" /><path fill="#EA4335" d="M9 3.58c1.32 0 2.5.45 3.44 1.35l2.58-2.59C13.46.89 11.43 0 9 0A9 9 0 0 0 .96 4.95l3.01 2.33C4.68 5.16 6.66 3.58 9 3.58z" /></svg>
                <span style="font-size: 14px; font-weight: 600; color: #374151">{{ t('akun.continueGoogle') }}</span>
              </a>
              <p class="text-center" style="font-size: 13px; color: #6b7280">{{ t('akun.notMember') }} <router-link :to="lp('/auth/register')" class="font-bold hover:underline" style="color: var(--lime-text)">{{ t('akun.registerHere') }}</router-link></p>
            </template>
          </div>

          <div class="mt-5 text-center"><router-link :to="lp('/')" class="hover:underline" style="font-size: 13px; color: #6b7280">{{ t('akun.browseGuest').replace(' →', '') }} <span style="font-family: Arial, Helvetica, sans-serif">→</span></router-link></div>
          <p class="text-center mt-4" style="font-size: 11px; color: #9ca3af; line-height: 1.6" v-html="tr('akun.terms', {}, { terms: (i) => '<a href=&quot;' + lp('/syarat-ketentuan') + '&quot; class=&quot;hover:underline&quot; style=&quot;color: var(--lime-text)&quot;>' + i + '</a>', privacy: (i) => '<a href=&quot;' + lp('/kebijakan-privasi') + '&quot; class=&quot;hover:underline&quot; style=&quot;color: var(--lime-text)&quot;>' + i + '</a>' })"></p>
        </div>
      </div>
      <div class="w-full" style="margin-top: -2px">
        <svg viewBox="0 0 448 80" class="w-full" style="display: block"><ellipse cx="60" cy="80" rx="90" ry="50" fill="#00b49a" opacity="0.55" /><ellipse cx="160" cy="90" rx="80" ry="45" fill="#00c8af" opacity="0.45" /><ellipse cx="260" cy="80" rx="100" ry="55" fill="#00b49a" opacity="0.5" /><ellipse cx="380" cy="85" rx="90" ry="48" fill="#00c8af" opacity="0.55" /><ellipse cx="440" cy="80" rx="70" ry="42" fill="#00b49a" opacity="0.45" /></svg>
      </div>
    </div>
  </div>
  <div v-if="toast" class="fixed top-4 left-1/2 -translate-x-1/2 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 text-sm font-semibold">{{ toast }}</div>
  <BottomNav v-if="auth.ready" />
</template>
