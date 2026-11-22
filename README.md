# donasi-eco3: Frappe 16 + ERPNext (lokal)

Stack Docker terpisah untuk keuangan platform donasi (pola PSAK 109 / PSAK 101).

- Web: http://127.0.0.1:8082 (hanya localhost). Site: `donasi.localhost`. User: `Administrator`.
- Kata sandi ada di `.env` (tidak masuk git, mode 600).
- Image: `frappe/erpnext:version-16` (rolling), digest saat dibuat 2026-11-22:
  `sha256:15a1270f7d8d674de5facd16c3390665a12bd632f5abb846bdd67b61d7461d84`
  (frappe 16.56.0, erpnext 16.55.0). Untuk pin, ganti ERPNEXT_IMAGE di `.env` dengan `frappe/erpnext@sha256:...`.
- Database dan Redis tidak dibuka ke host. Nama project Compose: `donasi-eco3`.

## Perintah
    docker compose up -d          # nyalakan
    docker compose down           # matikan (data tetap di volume)
    docker compose exec backend bench --site donasi.localhost console
    docker compose exec backend bench --site donasi.localhost backup --with-files

Catatan: `down -v` MENGHAPUS data. Kalau backend 502 setelah restart, jalankan `docker compose restart frontend`.
## Status (2026-11-22, akhir W8)
- Stack jalan; site `donasi.localhost` (wizard selesai) dan `uji.localhost` (untuk tes). Image lokal `donasi-eco3:local` (Dockerfile, base di-pin digest).
- App `apps/donasionline`: bagan akun 86 akun, 7 Dana, dimensi Dana/Kampanye, mesin jurnal E2-E5, 35 DocType, 63 method API. Tes: `docker compose exec backend bench --site uji.localhost run-tests --app donasionline` (33 tes).
- Posting jurnal MATI bawaan (`Pengaturan Donasi.posting_enabled=0`). Semua aturan akuntansi PROVISIONAL sampai F1-F29 dijawab (`docs/psak/keputusan-akuntan-syariah.pdf`).
- Dokumen sistem: `docs/sistem/00-08`; keputusan: `docs/KEPUTUSAN.md`.
- UI Vue: `ui/` (`cd ui && npm i && npm run dev`, http://127.0.0.1:5174, proxy ke Frappe). `VITE_REAL_API=1` memakai `ui/src/apiShim.js`; `0` = mode demo.
- Dev: kode OTP tampil di layar karena `donasionline_otp_dev_echo` (matikan di produksi).

## Dua mode UI
- **Gabung (bawaan):** `cd ui && npm run build:gabung` membangun UI ke `apps/donasionline/donasionline/public/ui` (hasil build ikut di-commit, jadi server tidak butuh Node). Setelah `install-app`, UI langsung tampil di `/` dan rute SPA lain; `/desk`, `/api`, `/login` tetap milik Frappe. Matikan lewat Pengaturan Donasi > "Layani UI donasi dari Frappe". Rute SPA baru harus ditambah ke `SPA_ROOTS` di `donasionline/ui.py`.
- **Terpisah:** `VITE_API_BASE=https://api.contoh.org npm run build`, layani `ui/dist` dari hosting lain. Cookie sesi lintas domain butuh subdomain yang sama atau reverse proxy `/api` ke Frappe (lalu `VITE_API_BASE` kosong); bila memakai domain berbeda, isi `allow_cors` di site config (BELUM diuji).

## Belum / perlu keputusan
Midtrans nyata (gateway masih simulator), kanal OTP/pengingat, halaman Rutin masih localStorage, hapus-akun & avatar di UI, tinjauan halaman legal, jawaban F1-F29.
