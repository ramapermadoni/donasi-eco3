// Konten halaman depan dari server (kampanye, banner, mitra, video) bila pemilik sudah membersihkan konten contoh.
// Selama belum (replace=false) atau server tak tersedia, UI memakai berkas statis bawaan di ui/src/data.
// Objek statis diubah di tempat (in place) sebelum aplikasi dipasang, jadi halaman tidak perlu diubah.
import sedekah from './data/sedekah'
import mitra from './data/mitra.json'
import videos from './data/videos.json'

const swap = (arr, next) => { arr.splice(0, arr.length, ...next) }

export async function muatKontenServer() {
  try {
    const r = await fetch('/api/content/bundle')
    if (!r.ok) return false
    const b = await r.json()
    if (!b || !b.replace) return false
    swap(sedekah.banners, b.banners || [])
    swap(sedekah.campaigns, b.campaigns || [])
    for (const k of Object.keys(sedekah.details)) delete sedekah.details[k]
    Object.assign(sedekah.details, b.details || {})
    sedekah.featured = b.featured || {}
    sedekah.totalCampaigns = b.totalCampaigns || 0
    swap(mitra, b.mitra || [])
    swap(videos, b.videos || [])
    return true
  } catch { return false } // tanpa server (mode demo): tetap statis
}
