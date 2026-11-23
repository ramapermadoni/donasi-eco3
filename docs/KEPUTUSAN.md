# Keputusan Proyek donasi-eco3

Dicatat: 2026-11-22 (W0). Tanpa rahasia. Semua aturan akuntansi berstatus USULAN/PROVISIONAL sampai akuntan/ahli syariah menjawab F1-F29.

## Dijawab pengguna
| Topik | Keputusan |
|---|---|
| Nama merek | Merek tampilan "sedekah.id" diganti menjadi **"donasi"** (UI, teks, judul, i18n id/en). Nama teknis app tetap `donasionline`. |
| Warna utama | **#005399** menjadi warna primer palet. Variabel CSS "lime" di UI diganti turunan #005399 (lihat catatan W7). |

## Dipilih pemilik (2026-11-23), tetap menunggu penegasan akuntan/ahli syariah
| Kode | Pilihan pemilik | Catatan |
|---|---|---|
| F1 | (a) Model A: platform = amil/PUB berizin | Ini FAKTA izin lembaga, bukan sekadar desain: wajib dibuktikan (izin LAZ/BAZNAS/PUB) sebelum zakat/infak dibuka. |
| F7 | (a) Clearing = Kas/Bank; bruto; fee per settlement | Provisional; akuntan dapat menggesernya ke piutang kanal. |
| F25 | Fee non-ZIS ditahan (belum diputuskan) | Tidak otomatis dibebankan ke Dana Amil. |

## Usulan menunggu persetujuan pemilik
| Kode | Usulan |
|---|---|
| F4 | Wakaf DIBUKA hanya sebagai penerusan ke nazhir mitra terdaftar BWI (opsi b): dana dicatat titipan (2-1330), bukan penghasilan lembaga, lalu diteruskan ke rekening nazhir/LKS-PWU. Gerbang di sistem: kampanye wakaf hanya dapat dibayar bila Mitra penerima bertanda "nazhir terverifikasi" (nomor registrasi BWI terisi). Sampai ada mitra yang memenuhi, wakaf tetap diblokir. Bila lembaga sendiri kelak terdaftar sebagai nazhir, beralih ke opsi (c)/(d). |

## Default (belum dikonfirmasi pengguna; PROVISIONAL)
| Kode | Keputusan |
|---|---|
| Peran Frappe | "Petugas Donasi", "Akuntan Donasi" (usul) |
| Retensi | Occurrence & Reminder Log 24 bulan; OTP & log atribusi 90 hari (usul) |
| Kanal pengingat | Belum diputuskan (tidak menghalangi W0-W4) |
| Port host | 8082 (dicek bebas 2026-11-22) |

## Catatan W7 (UI)
- Tema warna: primer #005399; turunan (hover/gelap/terang/latar) dihitung dari warna itu dan harus lolos kontras WCAG AA untuk teks.
- Penggantian "sedekah.id" -> "donasi" hanya di salinan `ui/`, bukan di `sedekah-vue` asli. Tautan/URL nyata ke sedekah.id tidak diubah menjadi domain baru tanpa keputusan pengguna.
