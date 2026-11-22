// SAMPLE DATA — sedekah.id's /qurban is closed outside Idul Adha season, so real packages/prices were not visible.
// Replace with your Frappe "Qurban Package" DocType.
export const eidDate = new Date('2027-05-16T00:00:00+07:00') // approx. 10 Dzulhijjah 1448 H — confirm with official calendar
export const regions = ['Jawa Barat', 'Jawa Tengah', 'NTT', 'Sulawesi Selatan', 'Palestina']
export const packages = [
  { id: 'kambing-a', name: 'Kambing Standar', animal: 'goat', mode: 'whole', region: 'Jawa Barat', price: 2300000, quota: 40, limited: false, weight: '23–25 kg' },
  { id: 'domba-a', name: 'Domba Premium', animal: 'sheep', mode: 'whole', region: 'Jawa Tengah', price: 2700000, quota: 25, limited: true, weight: '28–30 kg' },
  { id: 'kambing-b', name: 'Kambing Super', animal: 'goat', mode: 'whole', region: 'NTT', price: 3100000, quota: 12, limited: true, weight: '30–33 kg' },
  { id: 'sapi-patungan', name: 'Sapi Patungan (1/7)', animal: 'cow', mode: 'shared', region: 'Jawa Barat', price: 2850000, quota: 70, limited: false, weight: '1/7 ekor' },
  { id: 'sapi-ekor', name: 'Sapi 1 Ekor', animal: 'cow', mode: 'whole', region: 'Sulawesi Selatan', price: 19950000, quota: 8, limited: true, weight: '± 280 kg' },
  { id: 'unta-patungan', name: 'Unta Patungan (1/7)', animal: 'camel', mode: 'shared', region: 'Palestina', price: 3900000, quota: 21, limited: false, weight: '1/7 ekor' },
]
export const animalLabel = { goat: 'Kambing', sheep: 'Domba', cow: 'Sapi', camel: 'Unta' }
export const animalEmoji = { goat: '🐐', sheep: '🐑', cow: '🐄', camel: '🐪' }
