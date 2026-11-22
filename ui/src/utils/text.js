// Masker nama donor: kata <= 2 huruf utuh, selain itu huruf pertama + maks 3 bintang. null bila kosong.
export const maskName = (n) => (n ? n.split(' ').map((w) => (w.length <= 2 ? w : w[0] + '*'.repeat(Math.min(w.length - 1, 3)))).join(' ') : null)
export const initial = (s) => s.charAt(0).toUpperCase()
