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

## Midtrans sandbox
1. Daftar/masuk https://dashboard.sandbox.midtrans.com, pilih environment **Sandbox**.
2. Settings > Access Keys: salin **Merchant ID**, **Client Key** (`SB-Mid-client-...`), **Server Key** (`SB-Mid-server-...`) ke `.env` (`MIDTRANS_*`). Contoh nama ada di `.env.example`.
3. `tools/terapkan_midtrans.sh` menguji kunci ke Midtrans lalu menulisnya ke site_config (tidak dicetak). `--matikan` kembali ke simulator.
4. Pembayaran: QRIS dan VA BNI/BRI/Permata lewat Core API; GoPay, ShopeePay, BSI, VA lain lewat Snap. Status lunas diambil dua jalur: webhook (butuh URL publik) dan polling saat halaman donasi dibuka (cukup untuk lokal).
5. Webhook (opsional di lokal): Settings > Payment > Notification URL = `https://<tunnel>/api/method/donasionline.api.payment.webhook` (mis. `cloudflared tunnel --url http://127.0.0.1:8082 --http-host-header donasi.localhost`).
6. Uji bayar: simulator sandbox https://simulator.sandbox.midtrans.com (QRIS/VA/GoPay).
Kode Midtrans diuji dengan respons tiruan (7 tes); BELUM dicoba ke sandbox nyata.

## Kanal OTP
Pengaturan Donasi > "Kanal OTP & pengingat": `Log saja` (bawaan; kode tidak terkirim), `WhatsApp` (POST JSON ke gateway generik: URL https, token di header, badan dari template dengan `{phone}`/`{message}`), `Email` (butuh Email Account keluar; email palsu `@donor.invalid` dilewati), atau `WhatsApp lalu Email`. Gagal kirim = galat generik ke donatur, kode tidak pernah masuk log. Teruji dengan gateway tiruan (5 tes); BELUM dicoba ke gateway WA/SMTP nyata. Produksi: matikan `donasionline_otp_dev_echo`.
Pengingat Rutin: `run_due` berjalan tiap jam, membuat donasi Pending saat jam jadwal tiba dan mengirim pengingat (WA lewat gateway yang sama, email) SEKALI per eksekusi, dengan tautan `/donasi/<id>`. Hasil dicatat di Log Pengingat Rutin (Terkirim/Gagal/Dilewati; Dilewati = gateway belum diatur atau donor tanpa kontak). Diuji dengan gateway tiruan. UI Rutin (mode terhubung): jadwal disimpan di server lewat `recurring.save_schedule` (divalidasi server), kejadian DIBAYAR dibaca dari server; UPCOMING/DUE/MISSED tetap dibangkitkan mesin `ui/src/rutin.js` di browser. Tombol Bayar membuat donasi per tanggal (`execute` dengan `targetDate`, jendela genapi 7 hari) lalu pembayaran. Mode demo (`VITE_REAL_API=0`) tetap localStorage. Batas: pembayaran masih lewat simulator, jadi 'lunas' dari UI baru terjadi setelah staf menjalankan `payment.simulate_paid`; streak server dan streak UI dihitung terpisah.

## Dua mode UI
- **Gabung (bawaan):** `cd ui && npm run build:gabung` membangun UI ke `apps/donasionline/donasionline/public/ui` (hasil build ikut di-commit, jadi server tidak butuh Node). Setelah `install-app`, UI langsung tampil di `/` dan rute SPA lain; `/desk`, `/api`, `/login` tetap milik Frappe. Matikan lewat Pengaturan Donasi > "Layani UI donasi dari Frappe". Rute SPA baru harus ditambah ke `SPA_ROOTS` di `donasionline/ui.py`.
- **Terpisah:** `VITE_API_BASE=https://api.contoh.org npm run build`, layani `ui/dist` dari hosting lain. Cookie sesi lintas domain butuh subdomain yang sama atau reverse proxy `/api` ke Frappe (lalu `VITE_API_BASE` kosong); bila memakai domain berbeda, isi `allow_cors` di site config (`bench --site X set-config allow_cors https://domain-ui`, lalu restart backend; tanpa tanda kutip ganda).
  Diuji 2026-11-23: CORS + preflight + alur donasi/OTP/profil lewat skrip Node lintas-origin OK. BELUM diuji di browser: cookie sesi Frappe bertanda `SameSite=Lax` (tidak bisa diubah lewat config), jadi login lintas-SITE (domain berbeda) kemungkinan gagal; subdomain domain yang sama (app.x.org + api.x.org) atau reverse proxy `/api` aman.

## Belum / perlu keputusan
Midtrans nyata (gateway masih simulator), kanal OTP/pengingat, halaman Rutin masih localStorage, hapus-akun & avatar di UI, tinjauan halaman legal, jawaban F1-F29.
