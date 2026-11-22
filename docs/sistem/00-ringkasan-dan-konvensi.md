# 00. Ringkasan dan Konvensi Rancangan Sistem donasi (Tahap 2 / W5)

Tanggal: 2026-11-22. Merek tampilan: **donasi** (nama teknis app: `donasionline`). Dokumen ini menggambarkan sistem seperti yang **sudah dibangun** di folder ini (W1-W6), bukan hanya rencana. Tiap klaim diberi tanda:

- **FAKTA** = diverifikasi dari kode/perintah di proyek ini, atau dari handover yang dibaca langsung.
- **USULAN** = rancangan yang diambil sebagai keputusan kerja; bisa diubah pemilik.
- **ASUMSI** = diisi sementara karena sumbernya tidak diketahui; harus dikonfirmasi.

Berkas: 00 ringkasan · 01 alur sistem · 02 alur data dan mesin status · 03 DFD · 04 ERD/DocType (otomatis) · 05 matriks keterlacakan (otomatis) · 06 keamanan, retensi, idempotensi · 07 integrasi keuangan PSAK · 08 celah, asumsi, risiko.

## 14 modul

| # | Modul | DocType utama | Method (modul api) | Status |
|---|---|---|---|---|
| 1 | Akun dan OTP | Donor, Permintaan OTP, User | `auth`, `donor` | Dibangun + tes. Pengiriman OTP nyata (WA/email) BELUM: kanal belum diputuskan |
| 2 | Kampanye | Kampanye Donasi (diperluas), Mitra | `campaign` | Dibangun + tes; 63 kampanye diimpor |
| 3 | Donasi dan pembayaran | Donation, Permintaan Pembayaran, Metode Pembayaran | `donation`, `payment`, `gateway` | Dibangun + tes dengan **simulator**; Midtrans nyata BELUM |
| 4 | Zakat dan wakaf | Kampanye Donasi (`is_system`), Harga Emas | `zakat` | Harga emas + kampanye sistem; wakaf diblokir di jurnal (F4) |
| 5 | Mitra dan atribusi | Mitra, Donation.ref/utm_* | `donation.create`, `content.mitra_*` | Dibangun + tes; kebijakan atribusi otomatis dari kampanye BELUM diputuskan |
| 6 | Doa dan Amin | Doa Amin (+ Donation.message) | `doa` | Dibangun + tes |
| 7 | Notifikasi | turunan Doa Amin | `notification` | Dibangun + tes (lonceng) |
| 8 | Survei | Survei Kepuasan, Jawaban Survei | `survey` | Dibangun + tes; 3 survei contoh, skala = ASUMSI |
| 9 | Gamifikasi | Level, Hadiah, Klaim Hadiah, Pengaturan | `gamification` | Dibangun + tes; rumus poin = ASUMSI; klaim mati bawaan |
| 10 | Jejak Kebaikan | (tampilan atas Gamifikasi + Donation) | `gamification.get`, `donor.donations` | Dibangun |
| 11 | Shadaqa Rutin | Jadwal Rutin, Eksekusi Rutin, Log Pengingat | `recurring` + scheduler harian | Dibangun + tes; pengingat belum terkirim (kanal) |
| 12 | Konten | Penyaluran, Artikel, Video, Laporan, Banner, Halaman Legal, Pengaturan Beranda, Wilayah | `content` | Dibangun + tes; sebagian snapshot parsial (24/193 penyaluran, 30/267 artikel) |
| 13 | Quran Jar dan referensi | Ayat Quran Jar, Wilayah | `content.quran_jar`, `content.wilayah` | Dibangun; label/warna mood tetap di UI |
| 14 | Qurban | — | — | **Batas sengaja**: ditunda; jenis dana `qurban` diblokir di jurnal; rute UI harus dinonaktifkan |

Ditambah modul keuangan (W3/W4): Dana, Pengaturan Donasi, bagan akun 86, mesin jurnal E2-E5 (lihat 07).

## Arsitektur ringkas (FAKTA)

Frappe 16 + ERPNext 16 di Docker (project `donasi-eco3`, port 8082). App `donasionline` memuat DocType, method whitelisted `/api/method/donasionline.api.<modul>.<fungsi>`, mesin jurnal, seed dan impor snapshot. UI Vue (`ui/`) di port 5174, saat ini mode demo (belum memanggil method ini; itu W7).
