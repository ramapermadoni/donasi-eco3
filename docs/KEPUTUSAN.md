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

## Lingkup produk: ZISWAF (arahan pemilik 2026-11-23)
Zakat, infak, sedekah, dan wakaf adalah lingkup inti. Fidyah dan qurban tetap dapat menerima donasi (tidak digerbang). Semua donasi Paid, termasuk wakaf/fidyah/qurban, WAJIB tercatat di Donation. Bila jurnalnya diblokir (aturan akuntansi belum diputuskan), donasi muncul di laporan Desk **Donasi Belum Dijurnal** beserta alasannya, untuk diposting susulan. Hanya wakaf yang punya gerbang (lihat F4 di bawah), karena menerima wakaf tanpa nazhir sah bermasalah secara hukum.

## F4 Wakaf: dua mode, per kampanye (arahan pemilik 2026-11-23)
Lembaga ingin dapat menjadi nazhir DAN perantara, keduanya bersamaan. **Untuk saat ini: perantara dulu** (Titipan). Mode "Dikelola lembaga" disiapkan di kode tetapi baru dipakai nanti.

Mode ada di tiap kampanye wakaf (field "Mode wakaf", bawaan Titipan):

| Mode kampanye | Syarat agar menerima donasi |
|---|---|
| Titipan ke nazhir mitra (bawaan) | kampanye terikat ke Mitra yang field "No. registrasi nazhir BWI"-nya terisi |
| Dikelola lembaga | Pengaturan Donasi: "Lembaga terdaftar sebagai nazhir" dicentang DAN nomor BWI lembaga terisi |

- Gerbang di `donation.create`. Sebelumnya wakaf bisa dibayar tanpa syarat; yang terblokir hanya jurnal.
- Wakaf yang sudah ada otomatis diset Titipan (patch `wakaf_titipan`). Selama belum ada Mitra bernomor nazhir yang terikat, wakaf tidak menerima donasi.
- **Jurnal wakaf tetap diblokir** (`journals.BLOCKED_FUND_TYPES`); donasinya tercatat di Donation dan laporan "Donasi Belum Dijurnal".
- Titipan: liabilitas 2-1330 (bukan penghasilan lembaga). Dikelola lembaga: dana wakaf terpisah; PSAK 412 meminta entitas pelaporan terpisah (Company kedua). BELUM diputuskan.
- BELUM ADA: pencatatan penerusan dana ke nazhir (tanggal, jumlah, bukti transfer). Perlu dibangun agar titipan dapat dipertanggungjawabkan.
- Syarat hukum di luar sistem: nazhir badan hukum terdaftar di BWI; wakaf uang lazimnya lewat LKS-PWU. Sistem hanya memeriksa nomor terisi, bukan keabsahannya.

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
