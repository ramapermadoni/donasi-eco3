// Format angka/rupiah dan teks digit bersama. Penjagaan `n || 0` tetap di pemanggil.
export const nf = (n, loc = 'id-ID') => n.toLocaleString(loc) // "1.000" / en-US "1,000"
export const rpSp = (n) => 'Rp ' + n.toLocaleString('id-ID') // "Rp 1.000"
export const rpTight = (n, loc = 'id-ID') => 'Rp' + n.toLocaleString(loc) // "Rp1.000" / "Rp1,000"
export const shortRb = (n) => (n >= 1000 ? n / 1000 + ' rb' : n) // 5000 -> "5 rb" (tanpa jt, sengaja)
export const rpShort = (n) => 'Rp' + shortRb(n)
export const pad2 = (n) => String(n).padStart(2, '0')
export const parseDigits = (s) => { const d = String(s).replace(/\D/g, ''); return d ? parseInt(d, 10) : 0 }
export const localPhone = (s) => String(s).replace(/\D/g, '').replace(/^62/, '').replace(/^0/, '')
