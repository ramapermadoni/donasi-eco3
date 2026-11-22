// i18n tiruan next-intl (as-needed): id = tanpa prefiks, en = prefiks /en. URL satu-satunya penentu bahasa.
// Sumber katalog: docs/reference/sedekah-messages(.en).json (disalin ke src/data/i18n). Lihat docs/i18n-howto.md.
import { ref, computed } from 'vue'
import id from './data/i18n/id.json'
import en from './data/i18n/en.json'

const CATALOGS = { id, en }
const EN_RE = /^\/en(?=\/|$)/

/** Lokale aktif, reaktif. Diset dari rute (router.beforeEach) dan dari URL saat pertama dimuat. */
export const locale = ref(typeof location !== 'undefined' && EN_RE.test(location.pathname) ? 'en' : 'id')
export const isEn = computed(() => locale.value === 'en')
export const bcp = () => (locale.value === 'en' ? 'en-US' : 'id-ID') // BCP-47 untuk toLocale*; panggil di dalam computed/fungsi (reaktif)

export function setLocaleFromPath(path) {
  locale.value = EN_RE.test(path) ? 'en' : 'id'
  if (typeof document !== 'undefined') document.documentElement.lang = locale.value
}
setLocaleFromPath(typeof location !== 'undefined' ? location.pathname : '/')

/** '/en/akun' -> '/akun'; '/en' -> '/' (path tanpa prefiks). */
export const stripLocale = (p) => p.replace(EN_RE, '') || '/'
/** Path untuk lokale tertentu ('/akun' + 'en' -> '/en/akun'; '/' -> '/en'). */
export const pathFor = (p, loc) => { const b = stripLocale(p); return loc === 'en' ? (b === '/' ? '/en' : '/en' + b) : b }

/** Tautan internal: di /en beri prefiks. Hash, mailto, http(s) host lain, dan '//x' dibiarkan; sedekah.id absolut -> relatif. */
export function lp(href) {
  if (typeof href !== 'string' || locale.value !== 'en') return href
  const m = href.match(/^(?:https?:)?\/\/(?:www\.)?sedekah\.id(\/.*)?$/)
  if (m) href = m[1] || '/'
  if (!href.startsWith('/') || href.startsWith('//')) return href
  if (EN_RE.test(href) || href.startsWith('/donasi/') || href.startsWith('/api/')) return href // /donasi di luar prefiks seperti aslinya
  return href === '/' ? '/en' : '/en' + href
}

/** Ganti bahasa seperti LocaleSwitcher asli. Mengembalikan path tujuan (+query, tanpa hash) atau null bila sudah aktif. */
export function switchLocale(code, currentPath, search = '') {
  if (code === locale.value) return null
  try { document.cookie = `NEXT_LOCALE=${code};path=/;max-age=31536000;samesite=lax` } catch {}
  return pathFor(currentPath, code) + search
}

/** Header untuk POST /api/donations dan /api/payment/create saja (asli: X-Locale hanya di dua panggilan itu). */
export const apiHeaders = () => ({ 'X-Locale': locale.value })

// ---- formatter ICU mini: {name}, {n, plural, one {# x} other {# xs}} ----
const lookup = (cat, key) => key.split('.').reduce((o, k) => (o == null ? o : o[k]), cat)
function matchBrace(s, i) { let d = 0; for (let j = i; j < s.length; j++) { if (s[j] === '{') d++; else if (s[j] === '}' && --d === 0) return j } return -1 }
function format(msg, params) {
  let out = ''
  for (let i = 0; i < msg.length; i++) {
    if (msg[i] !== '{') { out += msg[i]; continue }
    const j = matchBrace(msg, i); if (j < 0) { out += msg.slice(i); break }
    const inner = msg.slice(i + 1, j), c1 = inner.indexOf(',')
    if (c1 < 0) out += params[inner.trim()] ?? `{${inner}}`
    else {
      const name = inner.slice(0, c1).trim(), rest = inner.slice(c1 + 1), c2 = rest.indexOf(',')
      const body = rest.slice(c2 + 1), n = Number(params[name]) || 0, opts = {}
      for (let k = 0; k < body.length;) { // "one {..} other {..}"
        const b = body.indexOf('{', k); if (b < 0) break
        const e = matchBrace(body, b); opts[body.slice(k, b).trim()] = body.slice(b + 1, e); k = e + 1
      }
      const form = n === 1 ? 'one' : 'other'
      out += format((opts[form] ?? opts.other ?? '').replace(/#/g, String(n)), params)
    }
    i = j
  }
  return out
}

/** Terjemahan: t('nav.akun') / t('home.x', { n: 3 }). Kunci hilang di lokale aktif -> pakai id -> kunci. Reaktif terhadap locale. */
export function t(key, params = {}) {
  const m = lookup(CATALOGS[locale.value], key) ?? lookup(id, key)
  return typeof m === 'string' ? format(m, params) : key
}
export const has = (key) => typeof lookup(CATALOGS[locale.value], key) === 'string'

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]))
/** Teks kaya (tag <b>, <br>, <em>, <terms>, ...) -> string HTML aman untuk v-html. Parameter di-escape.
 *  tags: { terms: (inner) => '<a href="...">'+inner+'</a>' }. Bawaan: b, em, br. Tag tak dikenal -> isinya saja. */
export function tr(key, params = {}, tags = {}) {
  const safe = Object.fromEntries(Object.entries(params).map(([k, v]) => [k, esc(v)]))
  const map = { b: (x) => `<b>${x}</b>`, em: (x) => `<em>${x}</em>`, ...tags }
  return format(lookup(CATALOGS[locale.value], key) ?? lookup(id, key) ?? key, safe)
    .replace(/<br\s*\/?>/g, '<br>')
    .replace(/<(\w+)>([\s\S]*?)<\/\1>/g, (_, n, x) => (map[n] ? map[n](x) : x))
}
