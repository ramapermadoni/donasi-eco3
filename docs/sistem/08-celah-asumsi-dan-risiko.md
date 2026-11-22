# 08. Celah, Asumsi, dan Risiko (jujur)

## Belum dibangun / belum teruji
1. **Gateway Midtrans nyata**: hanya simulator. `midtrans_enabled` di site_config memicu error eksplisit. Tanda tangan webhook mengikuti rumus dokumentasi, belum dicocokkan dengan sandbox.
2. **Pengiriman OTP dan pengingat** (WA/email): kanal belum diputuskan; hanya log. Tanpa itu pengguna nyata tidak bisa masuk.
3. **UI belum tersambung** ke method ini (W7). UI masih mode demo.
4. **Unduh aset** ke File Frappe: ditunda (izin hak aset); URL hotlink sedekah.id dipertahankan.
5. **Rate limit** hanya diuji HTTP untuk satu endpoint; kunci berbasis IP perlu penerusan IP asli di nginx.
6. **Sanitasi HTML** tanpa tes payload berbahaya.
7. **Qurban, refund, penyaluran, titipan, nonhalal**: ditunda (lihat 07).
8. **Pengaturan Beranda/popup menu, Laporan Donasi**: DocType ada, tanpa data (tidak ada snapshot).
9. Kampanye sistem Zakat/Wakaf/Fidyah dibuat sebagai Kampanye Donasi; kalkulator zakat sisi server tidak ada (hanya harga emas; konstanta zakat tetap di UI).

## ASUMSI (harus dikonfirmasi pemilik)
- Rumus poin gamifikasi = total donasi Paid / `idr_per_point` (default 1); klaim hadiah mati bawaan.
- Label skala survei (5 butir) dan 3 judul survei (judul "Tentang donasi" menggantikan "Tentang sedekah.id").
- Sponsor pool dipasangkan ke misi menurut urutan snapshot; nama sponsor "Hamba Allah".
- OTP: 6 digit, 5 menit, 5 percobaan. Batas amin 10 per pelaku per doa (dari komentar UI).
- Kedaluwarsa donasi 24 jam.
- Halaman Legal diimpor dari snapshot dengan merek diganti "donasi"; isi hukum menyebut organisasi lain dan **wajib ditinjau pemilik/penasihat hukum**.

## Risiko dari handover yang masih berlaku
Hotlink aset (±400 URL), `v-html` dari konten scrape (disanitasi di keluaran API tapi UI masih memakai data statis), endpoint tulis tamu tanpa anti-bot, minimum donasi tiga sumber (kini satu: server Rp3.000 + min per metode), SPA tanpa SSR/meta.

## Pemeriksaan cakupan (otomatis)
`python3 tools/cek_cakupan.py`: 44 endpoint handover 02 dan 29 Doctype handover 03 semuanya punya padanan atau alasan ditunda (lihat 05). Pemeriksa ini adalah skrip, bukan peninjau manusia; ia tidak menilai kebenaran semantik.
