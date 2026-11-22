import { ref } from 'vue'
import router from './router'
import { apiHeaders, lp } from './i18n'
import { postJson } from './utils/net'

export const submitting = ref(false)

const API = '/api'
const GENERAL_ID = 'clt00testsedekah000001234' // kampanye umum "sedekah"
const REAL = import.meta.env.VITE_REAL_API !== '0'

let feed
async function campaignId(slug) {
  if (!slug || slug === 'sedekah') return GENERAL_ID
  try {
    feed = feed || (await fetch(`${API}/campaigns/feed?limit=200`).then((r) => r.json())).campaigns
    return feed.find((c) => c.slug === slug)?.id || GENERAL_ID
  } catch { return GENERAL_ID }
}

// X-Locale hanya dari beranda (tanpa slug); halaman campaign asli tidak mengirimnya.
async function post(path, body, slug) {
  const { r, j } = await postJson(API + path, body, { headers: slug ? {} : apiHeaders() })
  if (!r.ok) throw new Error(j.error || j.message || `Gagal (${r.status})`)
  return j
}

// Frappe hook: ganti isi fungsi ini dengan frappe.call(...) yang membuat Donation + Payment Request,
// lalu arahkan ke /donasi/<id>.
// eventSlug: di situs asli prop SSR `eventSlug` (server; null di 43 dari 43 halaman campaign yang diperiksa) pada CampaignDetail;
// bila terisi body ditambah {event_slug}. Beranda (ShadaqaPage) tidak mengirimnya. Di tiruan: field opsional `details[slug].eventSlug` di data/sedekah.js (Frappe: campaign.event).
export async function donate(payload, slug, eventSlug = null) {
  if (!payload.method_code) { alert('Pilih metode pembayaran dulu.'); return }
  if (!REAL) { alert('Mode demo: donasi tidak dikirim.'); return }
  submitting.value = true
  try {
    const campaign_id = await campaignId(slug)
    const title = (await fetch(`${API}/campaigns/feed?limit=200`).then((r) => r.json()).catch(() => ({ campaigns: [] }))).campaigns.find((c) => c.id === campaign_id)?.title || 'Jemput Keberkahan Dengan Sedekah'
    const { donation_id } = await post('/donations', {
      campaign_id, currency: 'IDR', amount: payload.amount,
      donor_name: payload.donor_name || 'Hamba Allah', donor_phone: payload.whatsapp,
      is_anonymous: !!payload.hide_name, type: 'one_time', ...(payload.doa && { message: payload.doa }), ...penandaDonasi(), ...(eventSlug ? { event_slug: eventSlug } : {}),
    }, slug)
    await post('/payment/create', {
      donation_id, payment_method: payload.method_code, donor_name: payload.donor_name || 'Hamba Allah',
      donor_phone: payload.whatsapp, campaign_title: title, amount: payload.amount,
    }, slug)
    router.push(lp('/donasi/' + donation_id))
  } catch (e) {
    alert(e.message)
  } finally {
    submitting.value = false
  }
}

// Penanda mitra/UTM (padanan ClickIdCapture + penandaDonasi() + hapusPenandaMitra() asli). Tidak ada banner/UI; tidak ada pixel dtaffiliate.id.
// tangkapPenanda(): sekali per muat penuh (main.js). ref menimpa (68 jam); lainnya first-touch (30 hari); src 2 jam. Cookie Path=/; SameSite=Lax.
const CAP = [['ref', 244800, 1], ['fbclid', 2592e3], ['ttclid', 2592e3], ['gclid', 2592e3], ['utm_source', 2592e3], ['utm_medium', 2592e3], ['utm_campaign', 2592e3], ['utm_term', 2592e3], ['utm_content', 2592e3]]
export function tangkapPenanda() {
  try {
    const q = new URLSearchParams(location.search), set = (n, v, age) => { document.cookie = `${n}=${encodeURIComponent(v)}; Max-Age=${age}; Path=/; SameSite=Lax` }
    for (const [k, age, overwrite] of CAP) {
      const v = q.get(k)
      if (v && v.length <= 255 && (overwrite || !document.cookie.split('; ').some((c) => c.startsWith(`dtp_${k}=`)))) set('dtp_' + k, v, age)
    }
    const src = q.get('src')
    if (src && /^[a-z0-9_-]{1,24}$/i.test(src)) set('dtp_src', src.toLowerCase(), 7200)
  } catch {}
}
export const hapusPenandaMitra = () => { try { document.cookie = 'dtp_ref=; Max-Age=0; Path=/; SameSite=Lax' } catch {} }
// Dikirim di body POST /api/donations (bukan /payment/create): query halaman mendahului cookie dtp_*.
const MARK = { ref: 30, utm_source: 100, utm_medium: 100, utm_campaign: 100, utm_content: 100, utm_term: 100 }
// Cookie rusak (decode gagal) hanya membuang kunci itu, seperti pembaca asli.
const cookie = (n) => { const m = document.cookie.split('; ').find((c) => c.startsWith(n + '=')); try { return m ? decodeURIComponent(m.slice(n.length + 1)) : null } catch { return null } }
export function penandaDonasi() {
  try {
    const q = new URLSearchParams(location.search), out = {}
    for (const [k, max] of Object.entries(MARK)) {
      const v = q.get(k) ?? cookie('dtp_' + k)
      if (v && v.length <= max && (k !== 'ref' || /^[a-z0-9-]{3,30}$/.test(v))) out[k] = v
    }
    return out
  } catch { return {} }
}
