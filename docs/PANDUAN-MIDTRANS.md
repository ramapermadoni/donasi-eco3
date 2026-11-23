# Panduan Midtrans: API key, webhook, dan pengaturannya

Berlaku untuk donasi-eco3 (app `donasionline`). Bagian 1-5 sudah dicoba langsung di sandbox pada 2026-11-23 (VA BNI lunas lewat polling, uji notifikasi webhook berhasil). Hal yang BELUM dicoba ditandai **[belum diuji]**. Nama menu dashboard Midtrans bisa berubah; bila beda, cari kata kuncinya.

## 0. Gambaran singkat
```
Donatur -> UI -> Frappe (payment.create) -> Midtrans (buat VA/QRIS/Snap)
Donatur bayar -> Midtrans -> (a) webhook ke Frappe  dan/atau  (b) Frappe bertanya status (polling)
Frappe -> Donation = Paid -> (jurnal bila posting_enabled=1)
```
- **Webhook** = Midtrans memanggil alamat kita saat status berubah. Butuh alamat publik HTTPS.
- **Polling** = saat halaman donasi dibuka, Frappe menanyakan status ke Midtrans (maks 1x/10 detik). Cukup untuk lokal, tetapi jangan jadi satu-satunya jalur di produksi.
- Dua jalur aman dijalankan bersamaan: status hanya bisa maju dan jumlah selalu dicocokkan.

## 1. Mendapatkan API key
Ada DUA lingkungan terpisah, masing-masing punya akun dashboard, kunci, dan Notification URL sendiri.

| | Sandbox (uji, uang palsu) | Produksi (uang asli) |
|---|---|---|
| Dashboard | https://dashboard.sandbox.midtrans.com | https://dashboard.midtrans.com |
| Prefiks kunci | `SB-Mid-server-...` / `SB-Mid-client-...` | `Mid-server-...` / `Mid-client-...` |
| Syarat | daftar gratis | verifikasi bisnis/KYC dan aktivasi channel pembayaran |

Langkah (sandbox; produksi sama, tetapi pastikan environment **Production**):
1. Masuk dashboard, pastikan pilihan environment di pojok kiri atas sesuai (Sandbox/Production).
2. Buka **Settings -> Access Keys**.
3. Catat tiga hal:
   - **Merchant ID**: diawali `G` + angka (juga terlihat pada nama kunci di tabel).
   - **Client Key**: boleh publik, dipakai Snap di browser.
   - **Server Key**: RAHASIA. Jangan masuk chat, git, tangkapan layar, atau kode UI. Di dashboard baru, server key bisa tampil dengan label "Signature Secret Key"; nilainya yang berawalan `...-server-`.
4. Bila kunci pernah bocor: klik **Regenerate** di halaman yang sama, lalu isi ulang `.env` dan jalankan lagi skrip di bagian 2.

## 2. Menaruh kunci di proyek
1. Salin `.env.example` menjadi `.env` bila belum ada (`.env` tidak ikut git, mode 600).
2. Isi:
   ```
   MIDTRANS_MERCHANT_ID=G...
   MIDTRANS_CLIENT_KEY=SB-Mid-client-...
   MIDTRANS_SERVER_KEY=SB-Mid-server-...
   MIDTRANS_IS_PRODUCTION=0      # 1 hanya untuk kunci produksi
   ```
3. Jalankan dari root repo:
   ```
   tools/terapkan_midtrans.sh            # pasang
   tools/terapkan_midtrans.sh --matikan  # kembali ke simulator
   ```
   Skrip: menolak kunci yang tidak cocok dengan mode (sandbox harus `SB-Mid-...`), menguji kunci ke Midtrans, menulisnya ke `site_config` Frappe (`midtrans_server_key`, `midtrans_client_key`, `midtrans_production`, `midtrans_enabled`), memulai ulang backend, dan TIDAK mencetak kunci.
4. Bila lebih dari satu site: `SITE=nama.site tools/terapkan_midtrans.sh`.
5. Perubahan `site_config` baru terbaca setelah backend dimulai ulang (skrip sudah melakukannya).

## 3. Metode pembayaran yang didukung
| Kode | Jalur | Catatan |
|---|---|---|
| `qris` | Core API | QR berlaku 24 jam (disamakan dengan donasi) |
| `bni_va`, `bri_va`, `permata_va` | Core API | nomor VA tampil di halaman donasi |
| `gopay`, `shopeepay`, `bsi_va`, `other_va` | Snap | donatur dibawa ke halaman/popup Midtrans |
Metode yang kanal-nya belum aktif di akun Midtrans akan ditolak Midtrans; donatur melihat pesan generik. Aktifkan kanal yang dibutuhkan di dashboard (Settings -> channel/payment; nama menu dapat berbeda).

## 4. Webhook (Notification URL)
### 4.1 Alamat endpoint
```
https://<DOMAIN-ANDA>/api/method/donasionline.api.payment.webhook
```
- Ikut ada otomatis di setiap site yang memasang app `donasionline`; tidak ada yang perlu didaftarkan di server.
- Yang perlu Anda atur adalah ALAMAT ini di dashboard Midtrans (disimpan di sisi Midtrans, bukan di kode kita).

### 4.2 Mengisi di dashboard
1. **Settings -> Payment** (atau Configuration) -> bagian **Notification URL**.
2. Isi **Payment Notification URL** dengan alamat di 4.1. Kolom lain (Recurring, Pay Account, dan sejenisnya) kosongkan.
3. Klik **Test notification URL**, harus **sukses**, lalu **Save**.
4. **View notification history** menunjukkan setiap kiriman dan jawaban kita; berguna untuk melacak masalah.

### 4.3 Bagaimana kita memverifikasi
- Setiap notifikasi membawa `signature_key = SHA512(order_id + status_code + gross_amount + ServerKey)`. Tanpa tanda tangan sah, permintaan ditolak (403).
- Jumlah (`gross_amount`) harus sama dengan donasi; status hanya bisa maju (pending -> paid/failed/expired), paid final; pengulangan notifikasi tidak melunasi dua kali (idempoten).
- Order yang tidak dikenal tetapi bertanda tangan sah (mis. tombol "Test notification URL") dijawab **200** dan diabaikan, supaya Midtrans tidak mengulang terus.
- Midtrans menganggap berhasil hanya bila kita menjawab HTTP 200.

### 4.4 Untuk uji LOKAL: butuh tunnel (hanya di lokal)
Laptop Anda tidak punya alamat publik, jadi Midtrans perlu tunnel. Di server produksi dengan domain + HTTPS, tunnel TIDAK dipakai.

Pilihan tunnel:
| Alat | Alamat tetap? | Catatan |
|---|---|---|
| Pinggy via ssh (dicoba, bekerja) | tetap selama sesi, maks 60 menit | `ssh -p 443 -R0:127.0.0.1:8082 free.pinggy.io` lalu pakai URL `https://...free.pinggy.net` yang tercetak. Tanpa instal. |
| localhost.run via ssh | TIDAK: alamat berganti tiap beberapa menit dan tunnel putus bila sepi | jangan dipakai untuk webhook |
| Cloudflare Tunnel (**[belum diuji]**) | tetap bila memakai domain di Cloudflare | `brew install cloudflared`, `cloudflared tunnel login`, `cloudflared tunnel create donasi`, `cloudflared tunnel route dns donasi webhook.domain-anda.com`, `cloudflared tunnel run --url http://127.0.0.1:8082 donasi` |
| `cloudflared tunnel --url http://127.0.0.1:8082` (**[belum diuji]**) | alamat `trycloudflare.com` tetap selama proses jalan, berubah saat dijalankan ulang | tanpa domain |

Catatan lokal: backend sudah menerima host apa pun (`FRAPPE_SITE_NAME_HEADER`), jadi tidak ada pengaturan host tambahan. Selama tunnel hidup, situs lokal (termasuk halaman login Desk) bisa dibuka dari internet; matikan tunnel dan kosongkan Notification URL setelah selesai.

## 5. Menguji pembayaran di sandbox
Simulator resmi (semua alamat berawalan https://simulator.sandbox.midtrans.com):
| Metode | Alamat | Cara |
|---|---|---|
| VA BNI | `/bni/va/index` | isi nomor VA, **Inquire**, **Pay** (berhasil dicoba) |
| VA lain (BSI, Mandiri, dst.) | `/openapi/va/index?bank=...` | sama |
| VA BCA | `/bca/va/index` | sama |
| QRIS / GoPay / ShopeePay (Core) | `/qris/index` (atau `/v2/qris/index` untuk akun lama) | tempel URL gambar QR |
| Snap (GoPay, ShopeePay, BSI) | tidak perlu simulator terpisah | buka tautan Snap, gunakan tombol simulasi di halamannya **[belum diuji lewat browser]** |

Hasil uji kami: QRIS berhasil DIBUAT di sandbox tetapi simulator QRIS menjawab `merchant not found` / `Transaction is unsuccessful` untuk merchant ini (kemungkinan sisi simulator/akun sandbox). Pelunasan QRIS **[belum terbukti]**; jalurnya sama dengan VA sehingga risikonya rendah, tetapi uji ulang di produksi/akun lain sebelum rilis.

Cara membuktikan webhook (bukan polling):
1. Notification URL tersimpan (bagian 4.2).
2. Buat donasi VA lalu bayar di simulator, JANGAN membuka halaman donasi (itu memicu polling).
3. Periksa: `docker compose logs frontend | grep webhook` harus ada `POST ...payment.webhook ... 200` dari `okhttp`, dan status Donation = Paid.

## 6. Checklist produksi
- [ ] Kunci produksi (`Mid-server-...`) hanya di `.env` server, `MIDTRANS_IS_PRODUCTION=1`, jalankan `tools/terapkan_midtrans.sh`.
- [ ] Domain + HTTPS valid (sertifikat sah); jangan memakai tunnel.
- [ ] Notification URL di dashboard PRODUKSI = `https://domain-anda/api/method/donasionline.api.payment.webhook`, tes sukses, tersimpan.
- [ ] Kanal pembayaran yang dipakai aktif di akun produksi.
- [ ] `donasionline_otp_dev_echo` dimatikan; kanal OTP diatur (lihat README).
- [ ] nginx meneruskan IP asli klien (batas laju berbasis IP) dan header host.
- [ ] `posting_enabled` tetap 0 sampai aturan akuntansi F1-F29 dijawab akuntan/ahli syariah.
- [ ] Uji satu donasi kecil nyata per metode utama, lalu cek webhook history di dashboard.
- [ ] Rotasi kunci bila pernah tertulis di chat/tiket/log.
- [ ] Pantau Error Log Frappe dan "View notification history" Midtrans secara berkala.

## 7. Masalah yang pernah ditemui dan solusinya
| Gejala | Penyebab | Solusi |
|---|---|---|
| Skrip: "Midtrans menolak kunci" | kunci salah / bukan lingkungan yang sama | salin ulang dari Access Keys; sandbox `SB-Mid-...` |
| `Test notification URL` gagal, tidak ada jejak di log | tunnel mati/berganti alamat (localhost.run) | pakai tunnel yang stabil (Pinggy/Cloudflare) |
| Test notifikasi gagal tetapi ada jejak `okhttp` 404 | order dummy dijawab 404 | sudah diperbaiki (dijawab 200) |
| Simulator QRIS: "Transaction is unsuccessful" | QR kedaluwarsa (QRIS bawaan 15 menit) atau akun/simulator | sekarang QR 24 jam; bila tetap gagal, hubungi support Midtrans (sertakan Merchant ID, "sandbox", galat) |
| Kunci baru tidak terbaca | `site_config` di-cache proses lama | mulai ulang backend |
| Donasi lunas di Midtrans tetapi tetap Pending | webhook tidak sampai dan halaman donasi belum dibuka | periksa Notification URL dan history; membuka halaman donasi memicu polling |
| Status "kedaluwarsa" kembali ke Pending | (sudah diperbaiki) GET tidak commit | pastikan versi terbaru |
