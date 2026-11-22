// Real mission data from sedekah.id (logged-in page payload). Replace with your Frappe "Mission" DocType.
import raw from './missions.json'

const EMOJI = { istighfar500x: '📿' }
export const sponsorMissions = raw.sponsor
export default raw.missions.map((m) => ({
  ...m,
  emoji: EMOJI[m.slug],
  voucherLeft: Math.floor((m.poolAvailable || 0) / (m.voucherAmount || 1)),
  sponsorName: 'Hamba Allah',
}))
