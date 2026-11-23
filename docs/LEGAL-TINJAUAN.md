# Tinjauan halaman legal (untuk penasihat hukum / ahli syariah)

Status: **DRAF**. Isi bawaan (Syarat & Ketentuan, Kebijakan Privasi, Hapus Akun; ID dan EN) disalin dari situs organisasi lain, lalu hanya diganti merek menjadi "donasi" dan nama/email organisasi lain menjadi penanda `{{org_*}}`. Tidak ada isi hukum yang saya tulis atau nilai benar/salahnya. Selama belum disetujui, UI menampilkan banner **DRAF** di halaman legal.

## Cara mengisi dan menyetujui
1. Desk > **Pengaturan Donasi** > bagian "Identitas penyelenggara & halaman legal": isi nama lembaga, email kontak, alamat, nomor izin.
2. Isi halaman legal ada di Desk > **Halaman Legal** (per slug dan bahasa; sunting `body_html`). Penanda yang tersedia: `{{org_name}}`, `{{org_email}}`, `{{org_address}}`, `{{org_license}}`. Penanda yang belum diisi tampil sebagai `[... belum diisi]` berlatar kuning.
3. Setelah ditinjau, centang **Halaman legal sudah ditinjau & disetujui**; banner DRAF hilang. Jangan dicentang sebelum ada persetujuan tertulis.

## Hal yang HARUS diperiksa (klaim dari dokumen asli)
| # | Klaim / bagian | Mengapa perlu ditinjau |
|---|---|---|
| 1 | Pihak yang disebut penyelenggara ("kami", "{{org_name}}") | Harus badan hukum/lembaga amil yang benar-benar menjalankan platform ini; dokumen asli merujuk lembaga lain |
| 2 | "Mitra ... {{org_name}}" (S&K bag. 1) | Definisi Mitra mengikuti struktur organisasi asal |
| 3 | Dasar hukum: UU No. 23/2011 (Pengelolaan Zakat), KMA No. 606/2020, Fatwa DSN-MUI No. 8/2011 (S&K bag. 5) | Dikutip dari dokumen asli; pastikan masih berlaku dan relevan untuk model penyelenggara Anda |
| 4 | Batas ujrah amil: zakat (angka di S&K bag. 5) dan "maksimal 20% infaq/sedekah" | Harus sama dengan kebijakan yang berlaku. Sistem saat ini memakai usulan 12,5% zakat dan 0% infak (PROVISIONAL, lihat `docs/KEPUTUSAN.md` dan pertanyaan F1-F29) |
| 5 | Donasi tidak dapat dikembalikan kecuali dengan persetujuan penyelenggara | Kebijakan pengembalian dana; sistem belum punya fitur refund |
| 6 | Donasi internasional (USD via PayPal) | PayPal tidak diimplementasi di platform ini; hapus atau sesuaikan |
| 7 | Daftar integrasi pihak ketiga (Kebijakan Privasi) | Sudah disesuaikan otomatis menjadi "Midtrans"; periksa vendor lain yang benar-benar dipakai (OTP WA/email, hosting, analitik) |
| 8 | UU No. 27/2022 (Pelindungan Data Pribadi): hak akses/koreksi/hapus/cabut persetujuan | Pastikan prosedur nyata mendukung janji ini (lihat bawah) |
| 9 | Penyimpanan data dan retensi | Janji harus sama dengan praktik sistem (lihat bawah) |
| 10 | Kebijakan cookie (jenis, masa simpan maks. 1 tahun) | Harus sama dengan cookie yang benar-benar dipasang UI |
| 11 | Pernyataan persetujuan donatur (S&K bag. 7), termasuk dana halal dan haul | Redaksi persetujuan; sesuaikan dengan alur pendaftaran nyata |
| 12 | Hak mengubah S&K sepihak dan cara pengumuman | Periksa kecukupan pemberitahuan |
| 13 | Penghapusan akun: permintaan via email dan/atau WhatsApp terdaftar | Prosedur nyata harus ada dan diawasi |
| 14 | Yurisdiksi/penyelesaian sengketa | Tidak ada di dokumen asli; tambahkan bila diperlukan |

## Fakta sistem untuk mencocokkan janji
(dari `docs/sistem/06-*.md`; per 2026-11-23)
- Data donatur: nama, nomor WhatsApp, email (opsional), tanggal lahir/kota/pekerjaan/tujuan (opsional saat daftar), riwayat donasi, doa. Kartu pembayaran TIDAK disimpan; pembayaran diproses Midtrans.
- Kode OTP disimpan sebagai hash bergaram, kedaluwarsa 5 menit; data OTP dihapus setelah 90 hari. Log pengingat 24 bulan (USULAN, belum disetujui).
- Hapus akun: data donatur dianonimkan (konfirmasi "HAPUS"); catatan donasi/keuangan tetap ada karena kewajiban pembukuan. Sesuaikan kalimat "data dihapus" dengan kenyataan ini.
- Data pelacak mitra/UTM disimpan 90 hari (USULAN).
- Kuki: cookie penanda mitra/UTM (`dtp_*`, 30 hari sampai 68 jam), sesi Frappe. Nama kuki `dtp_` masih berasal dari situs asal.
- Webhook dan kunci gateway tidak pernah terlihat oleh klien.

## Yang tidak saya lakukan
- Tidak menulis klausul baru, tidak memberi saran hukum, tidak menyatakan dokumen ini sah.
- Tidak mengubah tautan/URL eksternal di dalam isi.
