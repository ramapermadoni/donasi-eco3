# Keputusan Proyek donasi-eco3

Dicatat: 2026-11-22 (W0). Tanpa rahasia. Semua aturan akuntansi berstatus USULAN/PROVISIONAL sampai akuntan/ahli syariah menjawab F1-F29.

## Dijawab pengguna
| Topik | Keputusan |
|---|---|
| Nama merek | Merek tampilan "sedekah.id" diganti menjadi **"donasi"** (UI, teks, judul, i18n id/en). Nama teknis app tetap `donasionline`. |
| Warna utama | **#005399** menjadi warna primer palet. Variabel CSS "lime" di UI diganti turunan #005399 (lihat catatan W7). |

## Default (belum dikonfirmasi pengguna; PROVISIONAL)
| Kode | Keputusan |
|---|---|
| F1 | Model A: platform = amil/PUB berizin |
| F4 | Wakaf diblokir |
| F7 | Akun clearing = Kas |
| F25 | Fee non-ZIS ditahan |
| Peran Frappe | "Petugas Donasi", "Akuntan Donasi" (usul) |
| Retensi | Occurrence & Reminder Log 24 bulan; OTP & log atribusi 90 hari (usul) |
| Kanal pengingat | Belum diputuskan (tidak menghalangi W0-W4) |
| Port host | 8082 (dicek bebas 2026-11-22) |

## Catatan W7 (UI)
- Tema warna: primer #005399; turunan (hover/gelap/terang/latar) dihitung dari warna itu dan harus lolos kontras WCAG AA untuk teks.
- Penggantian "sedekah.id" -> "donasi" hanya di salinan `ui/`, bukan di `sedekah-vue` asli. Tautan/URL nyata ke sedekah.id tidak diubah menjadi domain baru tanpa keputusan pengguna.
