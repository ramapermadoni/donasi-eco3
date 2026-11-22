// Penyimpanan Shadaqa Rutin di localStorage per nomor (gagal-aman: tidak pernah melempar).
// Kunci: sedekah_recurring_<phone> (jadwal) dan sedekah_recurring_occ_<phone> (kejadian).
// Aturan/alur: docs/reference/shadaqa-rutin-flow.md
import { lsGet, lsSet, lsDel, ssGet, ssSet } from './utils/storage.js'
import { syncOccurrences, makeSchedule, isISODate, MIN_AMOUNT, todayWIB } from './rutin.js'

const SKEY = 'sedekah_recurring_'
const OKEY = 'sedekah_recurring_occ_'
const FREQ_OLD = { daily: 'DAILY', weekly: 'WEEKLY', monthly: 'MONTHLY' }
const STATUS = ['ACTIVE', 'PAUSED', 'CANCELLED']
const OSTATUS = ['UPCOMING', 'DUE', 'PAID', 'MISSED', 'MAKEUP_PAID']

const parse = (raw) => { try { return raw == null ? null : JSON.parse(raw) } catch { return null } }
const isObj = (x) => !!x && typeof x === 'object' && !Array.isArray(x)

// Bentuk lama (freq/hour/method/paused, atau bentuk API tanpa `reminders`) atau bentuk baru -> Schedule valid, atau null.
function toSchedule(r, todayISO) {
  if (!isObj(r)) return null
  const frequency = r.frequency || FREQ_OLD[String(r.freq).toLowerCase()]
  const startDate = isISODate(r.startDate) ? r.startDate : todayISO
  const hourRaw = r.hourLocal ?? r.hour
  const rem = isObj(r.reminders) ? r.reminders : { wa: r.waReminder ?? r.remindWa, email: r.emailReminder ?? r.remindEmail }
  let s
  try {
    s = makeSchedule({
      id: typeof r.id === 'string' && r.id ? r.id : undefined, frequency, startDate, hourLocal: hourRaw, amount: r.amount,
      target: r.target, isAnonymous: r.isAnonymous !== false, reminders: { bell: true, wa: !!rem.wa, email: !!rem.email },
    }, isISODate(r.createdAt) ? r.createdAt : todayISO)
  } catch { return null }
  const paused = r.status === 'PAUSED' || r.paused === true || r.isPaused === true
  const status = STATUS.includes(r.status) ? r.status : paused ? 'PAUSED' : 'ACTIVE'
  const pauses = Array.isArray(r.pauses) ? r.pauses.filter((p) => isObj(p) && isISODate(p.from) && isISODate(p.to)).map((p) => ({ from: p.from, to: p.to })) : []
  // format lama tanpa genFrom: jangan membangkitkan MISSED lampau yang tak pernah ada
  const out = { ...s, status, pauses, genFrom: isISODate(r.genFrom) ? r.genFrom : todayISO }
  if (status === 'PAUSED') out.pausedAt = isISODate(r.pausedAt) ? r.pausedAt : todayISO
  if (status === 'CANCELLED') out.cancelledAt = isISODate(r.cancelledAt) ? r.cancelledAt : todayISO
  return out
}

function cleanOccs(arr, scheduleId) {
  if (!Array.isArray(arr)) return []
  return arr.filter((o) => isObj(o) && o.scheduleId === scheduleId && isISODate(o.date) && OSTATUS.includes(o.status) && typeof o.amount === 'number' && o.amount >= MIN_AMOUNT)
}

export function loadRutin(phone, todayISO) {
  const empty = { schedule: null, occs: [] }
  try {
    if (!phone) return empty
    const schedule = toSchedule(parse(lsGet(SKEY + phone)), todayISO)
    if (!schedule) return empty
    const occs = syncOccurrences(schedule, cleanOccs(parse(lsGet(OKEY + phone)), schedule.id), todayISO)
    return { schedule, occs }
  } catch { return empty }
}

export function saveRutin(phone, schedule, occs) {
  try {
    if (!phone) return false
    if (!schedule) { lsDel(SKEY + phone); lsDel(OKEY + phone); return true }
    const a = lsSet(SKEY + phone, JSON.stringify(schedule))
    const b = lsSet(OKEY + phone, JSON.stringify(Array.isArray(occs) ? occs : []))
    return a && b
  } catch { return false /* gagal-aman */ }
}

// Satu-satunya sumber "hari ini" untuk halaman rutin. Di DEV saja, `?today=YYYY-MM-DD` memajukan hari (dipertahankan di
// sessionStorage selama tab terbuka agar tahan navigasi SPA); `?today=` kosong/tidak valid menghapusnya. Build produksi: selalu WIB nyata.
const SS_TODAY = 'rutin_dev_today'
export function nowISO() {
  if (import.meta.env?.DEV) {
    try {
      const q = new URLSearchParams(location.search)
      if (q.has('today')) { const v = q.get('today'); ssSet(SS_TODAY, isISODate(v) ? v : '') }
      const v = ssGet(SS_TODAY, '')
      if (isISODate(v)) return v
    } catch { /* abaikan */ }
  }
  return todayWIB()
}
