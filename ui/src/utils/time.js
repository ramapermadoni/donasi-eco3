import { isEn } from '../i18n'

// Waktu relatif sama persis dengan fungsi asli sedekah.id `timeAgo(iso, lang)` (dibaca dari chunk util formatter, 2026-11):
//   id: "Baru saja" | "N mnt lalu" | "N jam lalu" | "N hari lalu" (<30 hari) | tanggal "5 Nov" (id-ID, day numeric + month short)
//   en: "Just now" | "Nm ago" | "Nh ago" | "Nd ago" (<30 hari) | tanggal "Nov 5" (en-US)
// Batas memakai floor per satuan (menit<1 = baru saja; <60 mnt; <24 jam; <30 hari). Tidak ada clamp masa depan
// (selisih negatif -> floor negatif -> <1 -> "Baru saja"). Tanggal tak valid mengikuti asli: "Invalid Date".
// Reaktif terhadap locale lewat isEn.
export function timeAgo(iso) {
  const t = Date.now() - new Date(iso).getTime()
  const n = Math.floor(t / 6e4), h = Math.floor(t / 36e5), d = Math.floor(t / 864e5)
  const en = isEn.value
  if (en) return n < 1 ? 'Just now' : n < 60 ? `${n}m ago` : h < 24 ? `${h}h ago` : d < 30 ? `${d}d ago` : new Date(iso).toLocaleDateString('en-US', { day: 'numeric', month: 'short' })
  return n < 1 ? 'Baru saja' : n < 60 ? `${n} mnt lalu` : h < 24 ? `${h} jam lalu` : d < 30 ? `${d} hari lalu` : new Date(iso).toLocaleDateString('id-ID', { day: 'numeric', month: 'short' })
}
