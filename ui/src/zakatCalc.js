// Rumus kalkulator zakat sedekah.id (spec: docs/reference/kalkulator-zakat-spec.md §5). Fungsi murni.
export const FALLBACK_GOLD = 2300000
export const SK_BULAN = 7640144 // SK Ketua BAZNAS No. 15 Tahun 2026
export const SK_TAHUN = 91681728
export const rateOf = (hijriah) => (hijriah ? 0.025 : 0.02577)
export const nishabEmas = (price) => { const eu = 85 * price; return { eu, em: Math.round(eu / 12) } }
export { parseDigits as parseRp } from './utils/format.js'

const idrF = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 })
const numF = new Intl.NumberFormat('id-ID')
export const idr = (x) => idrF.format(x)
export const num = (x) => numF.format(x)

/** s: state {tab, hijriah, price, periode, mode, acuan, modeEmas, v:{field:number}} -> {zakat, wajib, note} */
export function hitung(s) {
  const { eu, em } = nishabEmas(s.price ?? FALLBACK_GOLD)
  const r = rateOf(s.hijriah), v = s.v || {}, g = (k) => v[k] || 0
  const bulan = s.periode === 'bulan'
  let zakat = 0, wajib = false, note = ''
  if (s.tab === 'penghasilan') {
    const nishab = s.acuan === 'sk-baznas-2026' ? (bulan ? SK_BULAN : SK_TAHUN) : bulan ? em : eu
    let x = g('gaji') + g('lain')
    if (s.mode === 'netto') x -= g('pokok') + g('cicilan') + g('pengLain')
    wajib = x >= nishab && x > 0
    zakat = wajib ? Math.max(0, x * r) : 0
    note = `Penghasilan kena zakat ${idr(Math.max(0, x))} · nishab ${bulan ? 'bulanan' : 'tahunan'} ${idr(nishab)}`
  } else if (s.tab === 'maal') {
    const n = g('harta') - g('hutang')
    wajib = n >= eu && n > 0; zakat = wajib ? n * r : 0
    note = `Harta bersih ${idr(Math.max(0, n))} · nishab (85 gr emas) ${idr(eu)}`
  } else if (s.tab === 'emas') {
    if (s.modeEmas === 'rupiah') {
      wajib = g('nilai') >= eu; zakat = wajib ? g('nilai') * r : 0
      note = `Nilai emas ${idr(g('nilai'))} · nishab ${idr(eu)}`
    } else {
      const nilai = g('gram') * (s.price ?? FALLBACK_GOLD)
      wajib = g('gram') >= 85; zakat = wajib ? nilai * r : 0
      note = `${num(g('gram'))} gram × ${idr(s.price ?? FALLBACK_GOLD)}/gr = ${idr(nilai)} · nishab 85 gram`
    }
  } else if (s.tab === 'investasi') {
    const nishab = bulan ? em : eu, x = g('pendapatan') - g('biaya')
    wajib = x >= nishab && x > 0; zakat = wajib ? x * r : 0
    note = `Hasil bersih ${idr(Math.max(0, x))} · nishab ${idr(nishab)}`
  } else {
    const nishab = bulan ? em : eu
    const x = g('modal') + g('untung') + g('piutang') - (g('rugi') + g('hutang') + g('pengLain'))
    wajib = x >= nishab && x > 0; zakat = wajib ? x * r : 0
    note = `Aset niaga bersih ${idr(Math.max(0, x))} · nishab ${idr(nishab)}`
  }
  return { zakat: Math.round(zakat), wajib, note }
}
