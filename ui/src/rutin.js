// Mesin status Shadaqa Rutin: murni (tanpa Vue, tanpa storage). Semua tanggal 'YYYY-MM-DD' (WIB);
// 'todayISO' selalu argumen. Aturan: docs/superpowers/specs/2026-11-21-shadaqa-rutin-flow-design.md bagian 5.3/5.3a.
export const GRACE_DAYS = 7
export const HORIZON_DAYS = 35
export const MIN_AMOUNT = 3000

const FREQ = ['DAILY', 'WEEKLY', 'MONTHLY']
const DAY = 86400000
const PAID_SET = ['PAID', 'MAKEUP_PAID']

// ---- tanggal (aritmetika kalender UTC pada string, tanpa Date lokal) ----
const RE = /^(\d{4})-(\d{2})-(\d{2})$/
const toMs = (iso) => { const m = RE.exec(iso); return Date.UTC(+m[1], +m[2] - 1, +m[3]) }
const fromMs = (ms) => new Date(ms).toISOString().slice(0, 10)
export const addDays = (iso, n) => fromMs(toMs(iso) + n * DAY)
const diffDays = (a, b) => Math.round((toMs(a) - toMs(b)) / DAY)
const daysInMonth = (y, m) => new Date(Date.UTC(y, m, 0)).getUTCDate() // m: 1..12
export function isISODate(s) {
  if (typeof s !== 'string') return false
  const m = RE.exec(s)
  if (!m) return false
  const mo = +m[2], d = +m[3]
  return mo >= 1 && mo <= 12 && d >= 1 && d <= daysInMonth(+m[1], mo)
}

export const todayWIB = (now = new Date()) =>
  new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Jakarta', year: 'numeric', month: '2-digit', day: '2-digit' }).format(now)

let seq = 0
const newId = () => (globalThis.crypto?.randomUUID?.() || 'rt-' + Date.now().toString(36) + '-' + (++seq))

const validAmount = (a) => typeof a === 'number' && Number.isFinite(a) && a >= MIN_AMOUNT

export function makeSchedule(input, todayISO) {
  const i = input || {}
  if (!validAmount(i.amount)) throw new Error('amount')
  if (!isISODate(i.startDate)) throw new Error('startDate')
  if (!FREQ.includes(i.frequency)) throw new Error('frequency')
  const hour = Number.isInteger(i.hourLocal) && i.hourLocal >= 0 && i.hourLocal <= 23 ? i.hourLocal : 8
  const r = i.reminders || {}
  return {
    id: i.id || newId(),
    status: 'ACTIVE',
    frequency: i.frequency,
    startDate: i.startDate,
    genFrom: isISODate(i.genFrom) ? i.genFrom : i.startDate, // batas awal pembangkitan kejadian (ubah jadwal tidak membuat MISSED lampau baru)
    hourLocal: hour,
    amount: i.amount,
    target: i.target && i.target.type === 'campaign' ? { ...i.target } : { type: 'pilihan' },
    isAnonymous: !!i.isAnonymous,
    reminders: { bell: true, wa: !!r.wa, email: !!r.email },
    pauses: [],
    createdAt: todayISO,
  }
}

// Tanggal jatuh tempo (inklusif) pada [fromISO, toISO], urut naik, tidak sebelum startDate.
export function dueDates(schedule, fromISO, toISO) {
  const start = schedule.startDate
  const lo = fromISO > start ? fromISO : start
  if (lo > toISO) return []
  const out = []
  if (schedule.frequency === 'DAILY') {
    for (let d = lo; d <= toISO; d = addDays(d, 1)) out.push(d)
  } else if (schedule.frequency === 'WEEKLY') {
    const k = Math.max(0, Math.ceil(diffDays(lo, start) / 7))
    for (let d = addDays(start, k * 7); d <= toISO; d = addDays(d, 7)) out.push(d)
  } else {
    const sy = +start.slice(0, 4), sm = +start.slice(5, 7), sd = +start.slice(8, 10)
    let y = +lo.slice(0, 4), m = +lo.slice(5, 7)
    for (;;) {
      const d = y + '-' + String(m).padStart(2, '0') + '-' + String(Math.min(sd, daysInMonth(y, m))).padStart(2, '0')
      if (d > toISO) break
      if (d >= lo && d >= start) out.push(d)
      m++; if (m > 12) { m = 1; y++ }
      if (y < sy || (y === sy && m < sm)) break
    }
  }
  return out
}

export function statusOf(occ, todayISO) {
  if (PAID_SET.includes(occ.status)) return occ.status
  if (occ.date > todayISO) return 'UPCOMING'
  if (occ.date === todayISO) return 'DUE'
  return 'MISSED'
}

export function canMakeup(occ, todayISO) {
  return statusOf(occ, todayISO) === 'MISSED' && diffDays(todayISO, occ.date) <= GRACE_DAYS
}

// Apakah tanggal jatuh di masa tanpa kejadian (jeda/batal)? Jeda [from, to): setelah hari jeda sampai sebelum hari lanjut.
function inGap(s, date) {
  for (const p of s.pauses || []) if (date > p.from && date < p.to) return true
  if (s.status === 'PAUSED' && s.pausedAt && date > s.pausedAt) return true
  if (s.status === 'CANCELLED' && s.cancelledAt && date > s.cancelledAt) return true
  return false
}

export function syncOccurrences(schedule, occs, todayISO) {
  const horizon = addDays(todayISO, HORIZON_DAYS - 1) // jendela 35 hari termasuk hari ini (21 Nov s/d 25 Des)
  const keep = []
  const have = new Set()
  for (const o of occs || []) {
    const st = statusOf(o, todayISO)
    if (!PAID_SET.includes(st) && inGap(schedule, o.date)) continue // jeda/batal: kejadian belum dibayar di masa jeda dilepas
    keep.push(o.status === st ? o : { ...o, status: st })
    have.add(o.date)
  }
  if (schedule.status === 'ACTIVE' || schedule.status === 'PAUSED') {
    const gen = schedule.genFrom && schedule.genFrom > schedule.startDate ? schedule.genFrom : schedule.startDate
    for (const d of dueDates(schedule, gen, horizon)) {
      if (have.has(d) || inGap(schedule, d)) continue
      const o = { scheduleId: schedule.id, date: d, amount: schedule.amount, target: { ...schedule.target }, status: 'UPCOMING' }
      keep.push({ ...o, status: statusOf(o, todayISO) })
    }
  }
  return keep.sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0))
}

export function markPaid(occs, date, donationId, todayISO) {
  const i = (occs || []).findIndex((o) => o.date === date)
  if (i < 0) throw new Error('not-payable')
  const o = occs[i]
  if (PAID_SET.includes(o.status)) return occs // idempoten
  const st = statusOf(o, todayISO)
  let next
  if (st === 'DUE') next = 'PAID'
  else if (st === 'MISSED' && canMakeup(o, todayISO)) next = 'MAKEUP_PAID'
  else throw new Error('not-payable')
  const copy = occs.slice()
  copy[i] = { ...o, status: next, donationId, paidAt: todayISO }
  return copy
}

// Dari terbaru ke belakang: hitung PAID/MAKEUP_PAID; lewati UPCOMING, DUE, dan MISSED yang masih bisa digenapi;
// MISSED final (lewat jendela genapi) memutus.
export function streakOf(occs, todayISO) {
  const list = (occs || []).slice().sort((a, b) => (a.date < b.date ? 1 : -1))
  let n = 0
  for (const o of list) {
    const st = statusOf(o, todayISO)
    if (PAID_SET.includes(st)) n++
    else if (st === 'MISSED' && !canMakeup(o, todayISO)) break
  }
  return n
}

export function pause(s, todayISO) {
  return s.status === 'ACTIVE' ? { ...s, status: 'PAUSED', pausedAt: todayISO } : s
}

export function resume(s, todayISO) {
  if (s.status !== 'PAUSED') return s
  const { pausedAt, ...rest } = s
  return { ...rest, status: 'ACTIVE', pauses: [...(s.pauses || []), { from: pausedAt, to: todayISO }] }
}

export function cancel(s, todayISO) {
  return s.status === 'CANCELLED' ? s : { ...s, status: 'CANCELLED', cancelledAt: todayISO }
}

export function editSchedule(s, patch, occs, todayISO) {
  const p = patch || {}
  const merged = { ...s, ...p, id: s.id, status: s.status, pauses: s.pauses }
  if (!validAmount(merged.amount)) throw new Error('amount')
  if (!isISODate(merged.startDate)) throw new Error('startDate')
  if (!FREQ.includes(merged.frequency)) throw new Error('frequency')
  if (merged.frequency !== s.frequency || merged.startDate !== s.startDate) merged.genFrom = todayISO
  else merged.genFrom = s.genFrom
  merged.reminders = { bell: true, wa: !!(merged.reminders || {}).wa, email: !!(merged.reminders || {}).email }
  const kept = []
  for (const o of occs || []) {
    const st = statusOf(o, todayISO)
    if (st === 'UPCOMING') continue // dibuat ulang oleh sync
    if (st === 'DUE') kept.push({ ...o, amount: merged.amount, target: { ...merged.target } })
    else kept.push(o) // PAID, MAKEUP_PAID, MISSED tetap
  }
  return { schedule: merged, occs: syncOccurrences(merged, kept, todayISO) }
}
