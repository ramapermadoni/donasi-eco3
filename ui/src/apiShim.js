// Adaptor W7: menerjemahkan panggilan REST lama (/api/...) ke method Frappe donasionline.api.* (/api/method/...).
// Dipasang sekali di main.js bila VITE_REAL_API != '0'. Respons Frappe {message: X} dibuka menjadi X;
// galat Frappe dipetakan ke {error: "..."} agar kode halaman lama tetap jalan.
// VITE_API_BASE kosong = satu domain dengan Frappe (mode gabung); berisi URL = UI terpisah (mode pisah).
const BASE = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '')
const M = BASE + '/api/method/donasionline.api.'
const CRED = BASE ? 'include' : 'same-origin'
// [HTTP, regex path, method, pemeta argumen (match, query, body) -> params]
const R = [
  ['GET', /^\/api\/auth\/me$/, 'auth.me'],
  ['POST', /^\/api\/auth\/otp\/request$/, 'auth.request_otp'],
  ['POST', /^\/api\/auth\/otp\/verify$/, 'auth.verify_otp'],
  ['POST', /^\/api\/auth\/register$/, 'auth.register_donor'],
  ['POST', /^\/api\/auth\/logout$/, 'auth.logout'],
  ['POST', /^\/api\/auth\/delete-account$/, 'auth.delete_account'],
  ['POST', /^\/api\/donor\/avatar$/, 'auth.set_avatar'],
  ['GET', /^\/api\/auth\/google\/status$/, 'auth.google_status'],
  ['GET', /^\/api\/donor\/stats$/, 'donor.stats'],
  ['GET', /^\/api\/donor\/donations$/, 'donor.donations'],
  ['GET', /^\/api\/donor\/doa$/, 'donor.my_doa'],
  ['PUT', /^\/api\/donor\/profile$/, 'donor.update_profile', (m, q, b) => ({ full_name: b.name, email: b.email })],
  ['PATCH', /^\/api\/donor\/profile$/, 'donor.update_profile', (m, q, b) => ({ full_name: b.name, email: b.email })],
  ['GET', /^\/api\/donor\/gamification$/, 'gamification.get'],
  ['POST', /^\/api\/donor\/gamification\/claim$/, 'gamification.claim_reward'],
  ['GET', /^\/api\/campaigns\/feed$/, 'campaign.list_campaigns'],
  ['GET', /^\/api\/campaigns\/([^/]+)\/donors$/, 'campaign.donors', (m) => ({ slug: m[1] })],
  ['GET', /^\/api\/campaigns\/([^/]+)\/updates$/, 'campaign.updates', (m) => ({ slug: m[1] })],
  ['GET', /^\/api\/campaigns\/([^/]+)$/, 'campaign.detail', (m) => ({ slug: m[1] })],
  ['POST', /^\/api\/donations$/, 'donation.create'],
  ['POST', /^\/api\/payment\/create$/, 'payment.create'],
  ['GET', /^\/api\/donasi\/([^/]+)\/qr$/, 'payment.qr_png', (m) => ({ id: m[1] })],
  ['GET', /^\/api\/donasi\/([^/]+)$/, 'donation.status', (m) => ({ id: m[1] })],
  ['GET', /^\/api\/payment\/methods$/, 'payment.methods'],
  ['GET', /^\/api\/payment\/snap-config$/, 'payment.snap_config'],
  ['GET', /^\/api\/gold-price$/, 'zakat.gold_price'],
  ['GET', /^\/api\/penyaluran\/meta$/, 'content.penyaluran_meta'],
  ['GET', /^\/api\/penyaluran$/, 'content.penyaluran_list'],
  ['GET', /^\/api\/laporan$/, 'content.laporan_list'],
  ['GET', /^\/api\/doa\/untuk-diaminkan$/, 'doa.for_amin'],
  ['GET', /^\/api\/doa$/, 'doa.list_doa'],
  ['POST', /^\/api\/doa\/([^/]+)\/amin$/, 'doa.amin', (m, q, b) => ({ doa: m[1], delta: b.delta })],
  ['GET', /^\/api\/video\/latest$/, 'content.video_latest'],
  ['GET', /^\/api\/home\/popup-menu$/, 'content.popup_menu'],
  ['GET', /^\/api\/notifications$/, 'notification.list_notifications'],
  ['POST', /^\/api\/notifications$/, 'notification.mark_read'],
  ['GET', /^\/api\/satisfaction-survey$/, 'survey.get', (m, q) => ({ donation: q.donationId })],
  ['POST', /^\/api\/satisfaction-survey$/, 'survey.submit'],
  ['POST', /^\/api\/baik\/start$/, 'baik.start'],
  ['POST', /^\/api\/baik\/claim$/, 'baik.claim'],
  ['POST', /^\/api\/baik\/release$/, 'baik.release'],
  ['GET', /^\/api\/recurring\/schedules\/me$/, 'recurring.me'],
  ['GET', /^\/api\/recurring\/streak$/, 'recurring.streak'],
  ['POST', /^\/api\/recurring\/schedules\/save$/, 'recurring.save_schedule', (m, q, b) => ({ id: b.id, data: JSON.stringify(b.schedule) })],
  ['POST', /^\/api\/recurring\/schedules$/, 'recurring.create'],
  ['POST', /^\/api\/recurring\/schedules\/([^/]+)\/execute\/makeup$/, 'recurring.execute_makeup', (m, q, b) => ({ id: m[1], targetDate: b.targetDate })],
  ['POST', /^\/api\/recurring\/schedules\/([^/]+)\/execute$/, 'recurring.execute', (m, q, b) => ({ id: m[1], ...b })],
  ['POST', /^\/api\/recurring\/schedules\/([^/]+)\/(pause|resume|cancel)$/, 'recurring.set_state', (m) => ({ id: m[1], action: m[2] })],
  ['PATCH', /^\/api\/recurring\/schedules\/([^/]+)$/, 'recurring.update', (m, q, b) => ({ id: m[1], ...b })],
  ['GET', /^\/api\/artikel\/([^/]+)$/, 'content.artikel_detail', (m) => ({ slug: m[1] })],
  ['GET', /^\/api\/artikel$/, 'content.artikel_list'],
  ['GET', /^\/api\/wilayah$/, 'content.wilayah'],
  ['GET', /^\/api\/legal$/, 'content.legal'],
]

let csrf = ''
const realFetch = window.fetch.bind(window)

function pick(path, method) {
  for (const [meth, re, fn, map] of R) {
    const m = path.match(re)
    if (m && (meth === method || (meth === 'PUT' && method === 'PATCH'))) return { fn, map, m }
  }
  return null
}

async function shimmed(input, init = {}) {
  const url = new URL(typeof input === 'string' ? input : input.url, location.origin)
  const method = (init.method || 'GET').toUpperCase()
  if (!url.pathname.startsWith('/api/') || url.pathname.startsWith('/api/method/')) return realFetch(input, init)
  const hit = pick(url.pathname, method)
  if (!hit) return new Response(JSON.stringify({ error: 'Endpoint belum tersedia: ' + url.pathname }), { status: 404, headers: { 'Content-Type': 'application/json' } })
  const query = Object.fromEntries(url.searchParams)
  let body = {}
  try { body = init.body ? JSON.parse(init.body) : {} } catch { /* bukan JSON */ }
  const extra = hit.map ? hit.map(hit.m, query, body) : {}
  const base = method === 'GET' ? query : body
  const params = { ...base, ...extra }
  for (const k of Object.keys(params)) if (params[k] === undefined || params[k] === null) delete params[k]
  const headers = { ...(init.headers || {}) }
  let target = M + hit.fn, opts
  if (method === 'GET') {
    const qs = new URLSearchParams(params).toString()
    if (qs) target += '?' + qs
    opts = { method: 'GET', headers, credentials: CRED }
  } else if (init.body instanceof FormData) {
    // unggah berkas: biarkan browser mengisi Content-Type (batas multipart)
    delete headers['Content-Type']
    if (csrf) headers['X-Frappe-CSRF-Token'] = csrf
    opts = { method: 'POST', headers, body: init.body, credentials: CRED }
  } else {
    headers['Content-Type'] = 'application/json'
    if (csrf) headers['X-Frappe-CSRF-Token'] = csrf
    opts = { method: 'POST', headers, body: JSON.stringify(params), credentials: CRED, ...(init.keepalive === undefined ? {} : { keepalive: init.keepalive }) }
  }
  const res = await realFetch(target, opts)
  if (hit.fn === 'payment.qr_png') return res
  let j = {}
  try { j = await res.json() } catch { /* kosong */ }
  if (!res.ok) {
    let msg = ''
    try { msg = JSON.parse(j._server_messages || '[]').map((s) => JSON.parse(s).message).join(' ') } catch { /* abaikan */ }
    msg = (msg || j.exception || '').replace(/<[^>]+>/g, '').replace(/^[\w.]+Error: /, '') || `Gagal (${res.status})`
    return new Response(JSON.stringify({ error: msg }), { status: res.status, headers: { 'Content-Type': 'application/json' } })
  }
  const data = j.message === undefined ? j : j.message
  // berkas unggahan disimpan relatif (/files/...); pada UI terpisah awali dengan alamat server
  if (BASE && data) { for (const o of [data, data.user]) if (o && typeof o.avatarUrl === 'string' && o.avatarUrl.startsWith('/files/')) o.avatarUrl = BASE + o.avatarUrl }
  if (data && data.csrf_token) csrf = data.csrf_token
  if (data && data.dev_code) devBanner(data.dev_code)
  return new Response(JSON.stringify(data === null ? {} : data), { status: 200, headers: { 'Content-Type': 'application/json' } })
}

// Mode dev: server mengembalikan kode OTP (donasionline_otp_dev_echo) karena kanal WA/email belum ada.
function devBanner(code) {
  let el = document.getElementById('dev-otp')
  if (!el) { el = document.createElement('div'); el.id = 'dev-otp'; el.style.cssText = 'position:fixed;left:8px;bottom:8px;z-index:99999;background:#005399;color:#fff;padding:8px 12px;border-radius:8px;font:14px sans-serif'; document.body.appendChild(el) }
  el.textContent = 'Kode OTP (dev): ' + code
}

export function installApiShim() { window.fetch = shimmed }
