// Teks campaign yang diterjemahkan oleh CMS sedekah.id di /en (hanya sebagian campaign punya judul/deskripsi bahasa Inggris).
// Sisanya tetap Indonesia, persis seperti situs asli. Data: data/campaigns-en.json { slug: { title?, description?, body? } }.
import en from './data/campaigns-en.json'
import { isEn } from './i18n'

export const ctitle = (c) => (isEn.value && en[c.slug]?.title) || c.title
export const cexcerpt = (slug, d) => (isEn.value && en[slug]?.description) || d
export const cbody = (slug, d) => (isEn.value && en[slug]?.body) || d
/** 'Rp 1.7 jt' -> 'Rp 1.7M', 'Rp 545 rb' -> 'Rp 545K' (formatCompactRupiah locale en); Indonesia tak berubah. */
export const compact = (s) => (isEn.value ? s.replace(/ jt$/, 'M').replace(/ rb$/, 'K').replace(/ M$/, 'B') : s)
