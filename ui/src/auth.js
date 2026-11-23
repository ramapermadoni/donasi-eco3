import { lsGet, lsSet, lsDel } from './utils/storage'
import { reactive } from 'vue'
import { t, locale } from './i18n'
import { loadRutin, saveRutin, nowISO } from './rutinStore'

// REAL mode (default in dev): calls /api/* which vite proxies to sedekah.id.
// DEMO mode (VITE_REAL_API=0): everything stays in localStorage.
const REAL = import.meta.env.VITE_REAL_API !== '0'
const digits = (p) => String(p || '').replace(/\D/g, '')

async function api(path, { method = 'GET', body, headers } = {}) {
  const res = await fetch(path, { method, headers: body || headers ? { ...(body ? { 'Content-Type': 'application/json' } : {}), ...headers } : undefined, body: body ? JSON.stringify(body) : undefined, credentials: 'same-origin' })
  let data = null
  try { data = await res.json() } catch { /* empty body */ }
  if (!res.ok) throw new Error((data && data.error) || t('akun.errGeneric'))
  return data
}

// DEMO auth, stored in localStorage. For Frappe replace each function body with a frappe.call, e.g.
//   sendOtp   -> your_app.api.send_otp(phone)
//   verifyOtp -> your_app.api.verify_otp(phone, code)  (returns user or {needs_register: true})
//   register  -> your_app.api.register_donor(data)
//   saveProfile / removeAccount -> your_app.api.update_profile / delete_account
const KEY = 'sedekah_demo_user'
const read = () => { try { return JSON.parse(lsGet(KEY)) } catch { return null } }
const write = (u) => { if (u) { const { recurring, ...rest } = u; lsSet(KEY, JSON.stringify(rest)) } else lsDel(KEY) } // jadwal rutin disimpan terpisah (rutinStore)
const hydrate = (u) => (u ? { ...u, recurring: recurringOf(u.phone) } : u)

export const auth = reactive({ user: REAL ? null : hydrate(read()), ready: !REAL }) // ready = sesi sudah dicek (REAL: setelah loadMe pertama)

const wait = (ms = 600) => new Promise((r) => setTimeout(r, ms))

async function demo_sendOtp(phone, { allowNew = false } = {}) {
  await wait()
  if (phone.replace(/\D/g, '').length < 9) throw new Error('Nomor WhatsApp tidak valid')
  const saved = read()
  if (!allowNew && !(saved && saved.phone === phone)) throw new Error('Nomor WhatsApp belum terdaftar. Silakan daftar terlebih dahulu.')
}
async function demo_verifyOtp(phone, code) {
  await wait()
  if (!/^\d{6}$/.test(code)) throw new Error('OTP tidak valid atau kedaluwarsa.')
  const saved = read()
  if (saved && saved.phone === phone) { auth.user = hydrate(saved); return auth.user }
  throw new Error('OTP tidak valid atau kedaluwarsa.')
}
async function demo_register(data) {
  await wait()
  if (!data.name?.trim()) throw new Error('Nama wajib diisi.')
  const ex = read()
  if (ex && ex.phone === data.phone) throw new Error('Nomor WhatsApp sudah terdaftar. Silakan login.')
  // real API: POST /api/auth/register {name, phone, email, birthdate, city, job, goal, source} -> {ok, phone}; then OTP
  const u = { ...data, avatar: '', total: 0, count: 0, history: [], donorSince: new Date().toISOString() } // /api/donor/stats -> {totalCount,totalAmount,donorSince}
  write(u) // saved but not logged in; verifyOtp() logs in
  return u.phone
}
async function demo_saveProfile(patch) {
  await wait(300)
  const u = { ...auth.user, ...patch }
  write(u); auth.user = u
}
function demo_logout() { auth.user = null }
async function demo_removeAccount() {
  await wait()
  write(null); auth.user = null
}

/* ---- Sedekah Rutin ----
   Jadwal/kejadian rancangan sendiri, hanya di localStorage via rutinStore (tanpa request ke /api/recurring/*).
   Alur dan aturan: docs/reference/shadaqa-rutin-flow.md */
export const isPaused = (s) => !!s && (s.status === 'PAUSED' || s.paused === true || s.isPaused === true)
function recurringOf(phone) { return loadRutin(phone, nowISO()).schedule }
export async function setRecurring(schedule, occs) {
  const phone = auth.user?.phone
  if (REAL) { // simpan ke server (divalidasi di sana), lalu segarkan cache lokal dari jawabannya
    const cur = auth.user?.recurring
    const payload = schedule ? schedule : cur ? { ...cur, status: 'CANCELLED', cancelledAt: nowISO() } : null
    if (payload) {
      const r = await api('/api/recurring/schedules/save', { method: 'POST', body: { id: isServerId(payload.id) ? payload.id : undefined, schedule: payload } })
      applyServerSchedules(phone, [r])
    }
    if (!schedule) saveRutin(phone, null, [])
    auth.user = { ...auth.user, recurring: schedule ? recurringOf(phone) : null }
    return
  }
  await wait(400)
  if (schedule) {
    const prev = loadRutin(phone, nowISO())
    // storage diblokir/penuh: lempar agar halaman menampilkan galat (bukan gagal diam-diam)
    if (!saveRutin(phone, schedule, Array.isArray(occs) ? occs : prev.schedule?.id === schedule.id ? prev.occs : [])) throw new Error('storage')
  } else saveRutin(phone, null, [])
  auth.user = { ...auth.user, recurring: schedule || null }
}

/* ---- Sedekah Rutin, mode terhubung: server = sumber kebenaran jadwal + kejadian DIBAYAR; mesin rutin.js tetap membangkitkan
   UPCOMING/DUE/MISSED dari jadwal. Cache di rutinStore (per nomor) agar halaman lama tetap sinkron. ---- */
const FREQ_UP = { daily: 'DAILY', weekly: 'WEEKLY', monthly: 'MONTHLY' }
const ST_UP = { Aktif: 'ACTIVE', Dijeda: 'PAUSED', Dibatalkan: 'CANCELLED' }
const isServerId = (id) => typeof id === 'string' && /^RTN-/.test(id)
function applyServerSchedules(phone, list) {
  const x = (Array.isArray(list) ? list : []).find((r) => r.status !== 'Dibatalkan')
  if (!x) { saveRutin(phone, null, []); return }
  const sch = {
    id: x.id, status: ST_UP[x.status] || 'ACTIVE', frequency: FREQ_UP[x.freq], startDate: x.start_date, genFrom: x.gen_from || x.start_date, hourLocal: x.hour,
    amount: x.amount, target: x.target || { type: 'pilihan' }, isAnonymous: !!x.is_anonymous, reminders: { bell: true, wa: !!x.remind_wa, email: !!x.remind_email },
    pauses: x.pauses || [], createdAt: x.created_at || x.start_date,
    ...(x.paused_at ? { pausedAt: x.paused_at } : {}), ...(x.cancelled_at ? { cancelledAt: x.cancelled_at } : {}),
  }
  const occs = (x.executions || []).filter((e) => e.status === 'Dibayar').map((e) => ({
    scheduleId: x.id, date: e.date, amount: x.amount, target: sch.target, status: e.is_makeup ? 'MAKEUP_PAID' : 'PAID', donationId: e.donation, paidAt: e.date,
  }))
  saveRutin(phone, sch, occs)
}

/* ================= real API wrappers (exports) ================= */
export async function loadMe() {
  if (!REAL) return
  try {
    const me = await api('/api/auth/me')
    if (!me || !me.user) { auth.user = null; return }
    const [stats, donations, doa, rutin] = await Promise.all([api('/api/donor/stats').catch(() => ({})), api('/api/donor/donations', { headers: { 'X-Locale': locale.value } }).catch(() => []), api('/api/donor/doa').catch(() => null), api('/api/recurring/schedules/me').catch(() => null)])
    if (rutin) applyServerSchedules(me.user.phone, rutin.schedules)
    const prev = auth.user || {}
    auth.user = {
      ...prev, id: me.user.id, name: me.user.name || 'Donatur', phone: me.user.phone, email: me.user.email || '', avatarUrl: me.user.avatarUrl,
      doas: Array.isArray(doa?.doas) ? doa.doas : [],
      total: stats.totalAmount || 0, count: stats.totalCount || 0, donorSince: stats.donorSince,
      recurring: recurringOf(me.user.phone),
      history: (Array.isArray(donations) ? donations : []).map((d) => ({
        id: d.id, campaign: d.campaign?.title, amount: d.amount, currency: d.currency, idr: d.idr_equivalent,
        when: d.paid_at || d.created_at, status: d.status, channel: d.payment_channel,
      })),
    }
  } catch { auth.user = null } finally { auth.ready = true }
}
if (REAL) loadMe()

export async function sendOtp(phone, opts) {
  if (!REAL) return demo_sendOtp(phone, opts)
  if (opts && opts.skip) return // register() already triggers the OTP on the real API
  if (digits(phone).length < 10) throw new Error('Nomor WhatsApp tidak valid')
  const r = await api('/api/auth/otp/request', { method: 'POST', body: { phone: digits(phone) } })
  return r && r.phone // nomor kanonik dari server (asli menampilkannya di langkah kode)
}
export async function verifyOtp(phone, code) {
  if (!REAL) return demo_verifyOtp(phone, code)
  await api('/api/auth/otp/verify', { method: 'POST', body: { phone: digits(phone), code } })
  await loadMe()
  return auth.user
}
export async function register(data) {
  if (!REAL) return demo_register(data)
  const r = await api('/api/auth/register', { method: 'POST', body: { name: data.name, phone: digits(data.phone), email: data.email || null, birthdate: data.birthdate || null, city: data.city || null, job: data.job || null, goal: data.goal || null, source: data.source || null } })
  return r.phone || digits(data.phone)
}
export async function saveProfile(patch) {
  if (!REAL) return demo_saveProfile(patch)
  // asli (chunk /akun): PUT /api/donor/profile {name, email} -> {ok, user:{name,email}}; email kosong dikirim '' (bukan null)
  const r = await api('/api/donor/profile', { method: 'PUT', body: { name: patch.name, email: patch.email || '' } })
  if (!r || !r.ok) throw new Error((r && r.error) || t('akun.errSaveFailed'))
  auth.user = { ...auth.user, name: r.user.name, email: r.user.email || '' }
}
export function logout() {
  if (!REAL) return demo_logout()
  auth.user = null
  api('/api/auth/logout', { method: 'POST' }).catch(() => {})
}
export async function removeAccount() {
  // Deliberately NOT wired to the real /api/auth/delete-account: it would delete the real sedekah.id account.
  if (REAL) throw new Error('Hapus akun dinonaktifkan di mode terhubung ke sedekah.id asli.')
  return demo_removeAccount()
}
