// Metode pembayaran bersama (DonateForm, ZakatPayForm, KalkulatorZakat).
export const typeOrder = ['qris', 'virtual_account', 'ewallet', 'retail', 'manual_transfer', 'credit_card']
export const logoMap = { qris: 'qris', bca_va: 'bca', bni_va: 'bni', bri_va: 'bri', mandiri_va: 'mandiri', other_va: 'mandiri', permata_va: 'permata', bsi_va: 'bsi', cimb_va: 'cimb_niaga', danamon_va: 'danamon', gopay: 'gopay', shopeepay: 'shopeepay', dana: 'dana', ovo: 'ovo', linkaja: 'linkaja', indomaret: 'indomaret', alfamart: 'alfamart' }
export const logo = (m) => m.iconUrl || 'https://sedekah.id/icons/bank/' + (logoMap[m.code] || 'qris') + '.png'
export const minFor = (m) => (['qris', 'gopay', 'shopeepay', 'dana', 'ovo', 'linkaja'].includes(m.code.toLowerCase()) || m.type === 'qris' || m.type === 'ewallet' ? 3000 : 25000)
export const groupMethods = (list) => typeOrder.map((ty) => ({ type: ty, items: list.filter((m) => m.type === ty) })).filter((g) => g.items.length)
