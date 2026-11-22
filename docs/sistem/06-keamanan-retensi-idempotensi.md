# 06. Keamanan, Retensi, Idempotensi

Kolom Status: **TERUJI** (ada tes yang lulus), **KODE** (ada di kode, belum diuji otomatis), **BELUM**.

## Keamanan
| Kontrol | Penerapan | Status |
|---|---|---|
| Tulis publik dibatasi laju | `@rate_limit` pada create donasi (20/mnt), payment.create (20/mnt), request_otp (5/10 mnt), verify_otp (10/10 mnt), register (5/10 mnt), amin (60/mnt), survei (10/mnt), klaim hadiah (10/mnt), start misi (30/mnt) | request_otp diuji lewat HTTP: panggilan ke-6 = 429. Lainnya KODE. **Catatan:** kunci laju berbasis IP; di belakang proxy semua klien bisa tampak satu IP bila header IP asli tak diteruskan (cek konfigurasi nginx saat produksi) |
| Validasi masukan | nominal minimal Rp3.000, mata uang IDR saja, telepon 9-15 digit, panjang UTM 100, nama/pesan dipotong, metode dan kampanye harus ada | TERUJI |
| Id donasi tak tertebak | id publik = `gateway_order_id` acak 20 karakter; nama internal `DON-xxxxx` tidak pernah dikembalikan API | TERUJI |
| OTP | kode 6 digit acak, disimpan sebagai hash bergaram, kedaluwarsa 5 menit, maks 5 percobaan, tidak dikembalikan ke klien kecuali konfigurasi uji `donasionline_otp_dev_echo` | TERUJI |
| Webhook | tanda tangan SHA-512 (`order_id+status_code+gross_amount+server_key`); tanpa `midtrans_server_key` semua ditolak; jumlah harus cocok; hanya maju | TERUJI. Rumus tanda tangan mengikuti dokumentasi Midtrans dari ingatan: **belum dicocokkan dengan sandbox nyata** |
| Rahasia | kunci server hanya di site_config; `snap_config` hanya clientKey | TERUJI (bentuk respons) |
| Izin | method baca publik `allow_guest`; method pribadi memerlukan login dan memeriksa kepemilikan (jadwal, sesi, klaim); `simulate_paid` hanya System Manager/Petugas Donasi | TERUJI |
| HTML dari konten | disanitasi dengan `clean_html` Frappe pada keluaran (deskripsi kampanye, penyaluran, artikel, legal) | KODE; belum ada tes dengan payload `<script>` |
| Penghapusan akun | anonimkan Donor, putus tautan donasi, nonaktifkan User; catatan keuangan tetap (kewajiban pembukuan) | TERUJI. Kebijakan hukum retensi data keuangan perlu dikonfirmasi |
| Anti-bot | belum ada CAPTCHA pada endpoint tulis tamu | BELUM |

## Idempotensi
| Operasi | Kunci | Status |
|---|---|---|
| Jurnal E2/E3/E4/E5 | `donation_ref` unik pada Journal Entry (`{DON}:RECEIPT`, `:AMIL`, `:FEE`, `{STL}:SETTLE`) | TERUJI (W4) |
| Webhook berulang | status Permintaan Pembayaran `paid` final | TERUJI |
| payment.create berulang | donasi+metode+pending -> permintaan yang sama | TERUJI |
| Eksekusi Rutin | satu baris per (jadwal, tanggal) | TERUJI |
| Impor snapshot | lewati yang sudah ada | TERUJI |
| Seed keuangan | cek keberadaan | TERUJI (W3) |

## Retensi (USULAN dari W0; belum dikonfirmasi pengguna)
| Data | Retensi | Mekanisme |
|---|---|---|
| Log Pengingat Rutin | 24 bulan | `recurring.purge_logs` (scheduler harian) — KODE |
| Permintaan OTP | 90 hari | idem — KODE |
| Log atribusi | 90 hari | belum ada log atribusi terpisah (atribusi disimpan di Donation, mengikuti retensi donasi) |
| Donation, Journal Entry | permanen (catatan keuangan) | — |
| Doa Amin | mengikuti Donation | — |
