# WORK ORDER: Project donasi-eco3 (Frappe 16 + ERPNext + app `donasionline`)

Dibuat: 2026-11-22. Untuk sesi Claude Code baru. Bahasa kerja: Indonesia. Baca seluruh berkas ini dulu, lalu kerjakan per fase (W0..W8).
Pengguna adalah pemilik proyek; gaya kerjanya: jelaskan rencana dulu, lalu eksekusi bertahap, laporkan jujur (apa yang teruji vs tidak).

## 0. Tujuan
Membangun versi Frappe dari platform donasi sedekah.id dengan SEMUA keuangan masuk ke modul Finance ERPNext memakai pola
PSAK 409 (dahulu 109, Akuntansi ZIS) dan PSAK 401 (dahulu 101, Penyajian Laporan Keuangan Syariah). Semua kode kustom ada di
satu app Frappe bernama **`donasionline`**, di project Docker bernama **donasi-eco3** (folder ini).

## 1. Aturan keras (jangan dilanggar)
1. Folder kerja: `/Users/ramapermadoni/Project/docker/donasi-eco3/`. Jangan menyentuh stack Docker lain (tautin, docker-hrdt, smisdev, mppdev, biosocket, dll.), tidak menghapus
   container/volume/jaringan yang bukan milik project `donasi-eco3`. Jangan restart Docker Desktop tanpa izin.
2. `/Users/ramapermadoni/Project/donasi-eco3/sedekah-vue` (tiruan UI) TIDAK diubah. UI yang dibutuhkan DISALIN ke `ui/` di folder ini.
3. Dilarang POST/tulis ke https://sedekah.id (donasi/pembayaran nyata). Hanya GET bila perlu.
4. lpm.siapguna.org: HANYA BACA (GET). Kunci API sudah terekspos di sesi lama: minta pengguna membuat kunci baru. Jangan simpan kunci di berkas/memori.
5. Rahasia (token GitHub, kunci WA, kata sandi): jangan ditulis ke berkas, git, atau memori; token dari pengguna dipakai sekali di perintah push. Kata sandi stack hanya di `.env` (mode 600, di .gitignore).
6. Semua aturan akuntansi berstatus USULAN/PROVISIONAL sampai akuntan/ahli syariah menjawab F1-F29. Posting jurnal otomatis dimatikan bawaan (`posting_enabled=0`).
7. Jangan klaim "terverifikasi/selesai" tanpa bukti perintah yang dijalankan. Laporkan celah apa adanya.
8. `docs/lpm/` sudah ada di `.gitignore` (jangan dihapus dari sana). Repo GitHub `ramapermadoni/donasi-eco3` PUBLIK; `ramapermadoni/sedekah-id-replica` privat. Jangan push `docs/lpm/` (angka keuangan lembaga) ke repo publik. Sebelum push: pindai rahasia.
9. Standing instruction pengguna: setelah pekerjaan selesai, kirim ringkasan ke WhatsApp 6285173321453 (minta pengguna kunci API WA yang berlaku; jangan menebak) DAN ringkas di chat.

## 2. Bahan yang sudah ada
| Apa | Lokasi |
|---|---|
| Riset PSAK + rancangan akun/jurnal (USULAN) | `docs/psak/01..05-*.md` (salinan; asli di `/Users/ramapermadoni/Project/sedekah-erp/docs/psak/`) |
| 29 pertanyaan keputusan (F1-F29), PDF isian | `docs/psak/keputusan-akuntan-syariah.pdf` |
| Draf app (kerangka, DocType, bagan akun 86 akun) | `_draft/sedekah_finance/` (nama LAMA; ganti jadi `donasionline`) |
| Draf Dockerfile/compose yang SUDAH TERUJI jalan | `_draft/Dockerfile.referensi`, `_draft/compose.yaml.referensi` |
| Analisis keuangan LPM (hanya baca) | `docs/lpm/analisis-keuangan-lpm.md` (jangan di-push publik) |
| Paket serah terima UI -> Frappe (peta halaman, 80+ endpoint, Doctype usulan, alur kunci, risiko) | `/Users/ramapermadoni/Project/donasi-eco3/docs/handover-frappe/` (mulai `RINGKAS.md`), `docs/HANDOVER.md`, `docs/PANDUAN-UJI.md` |
| Rancangan Shadaqa Rutin (spec, plan, engine UI) | `/Users/ramapermadoni/Project/donasi-eco3/docs/superpowers/specs|plans/2026-11-21-shadaqa-rutin-flow*.md`, `docs/reference/shadaqa-rutin-flow.md`, `sedekah-vue/src/rutin.js` |
| UI Vue (tiruan sedekah.id) | `/Users/ramapermadoni/Project/donasi-eco3/sedekah-vue` (repo GitHub `sedekah-id-replica`, privat) |
| Stack percobaan lama `sedekah-erp` | SUDAH DIGABUNG ke folder ini (2026-11-22): `compose.yaml`, `compose.override.yaml`, `Dockerfile`, `.env`, `.git`, `apps/sedekah_finance/` kini ada di root folder ini. Folder `/Users/ramapermadoni/Project/sedekah-erp` sudah dihapus. Container lama dimatikan (`compose down`, tanpa `-v`); volume lama `sedekah-erp_*` (kosong, tanpa data penting) masih ada: hapus hanya atas izin pengguna |

## 3. Pelajaran teknis (sudah terbukti; hemat waktu)
- Image: `frappe/erpnext:version-16` (rolling; saat dibuat frappe 16.56.0, erpnext 16.55.0, Python 3.14, venv di `env/`, `uv` tersedia).
  Tag stabil juga ada (v16.9.x, Maret 2026). Pin digest di README setelah build.
- Backend: `gunicorn` TIDAK ada di PATH. Perintah wajib: `/home/frappe/frappe-bench/env/bin/gunicorn --chdir=/home/frappe/frappe-bench/sites -b 0.0.0.0:8000 --threads=4 --workers=2 --worker-class=gthread --worker-tmp-dir=/dev/shm --timeout=120 --preload frappe.app:application` (tanpa `--chdir` muncul "site does not exist").
- Setelah backend (re)start nginx bisa 502: `docker compose restart frontend`.
- Entrypoint image: `entrypoint.sh` menautkan assets; `start.sh` bawaan.
- Compose referensi: db `mariadb:11.8` (flag utf8mb4), redis x2, configurator, create-site, backend, frontend (nginx-entrypoint.sh, env `FRAPPE_SITE_NAME_HEADER`), websocket (`node .../socketio.js`), scheduler, queue-short, queue-long. DB & Redis tidak dibuka ke host. Web bind `127.0.0.1:<port>`.
- Aktifkan scheduler per site: `bench --site <site> enable-scheduler`.
- Port host terpakai: 80, 3306-3308, 5000, 5181, 7000, 8011, 8025, 8080, 8081 (stack lama), 9011, 9110-9111, 6379, 5173. Pakai **8082** untuk project ini (cek ulang dulu).
- Docker Desktop ~8 GB RAM; stack `tautin-*` juga menyala. Daemon pernah macet: cek dengan `curl --unix-socket ~/.docker/run/docker.sock http://localhost/_ping`.
- Pembuatan akun: `create_charts(company, custom_chart=<dict>)` dengan `frappe.local.flags.ignore_chart_of_accounts=True` saat membuat Company lalu isi akun sendiri.
- Accounting Dimension: `on_update` mengantre `make_dimension_in_accounting_doctypes` (queue long); panggil fungsi itu langsung dalam seed. Nama `Campaign` DILARANG (bentrok CRM): pakai `Kampanye Donasi`.
- ERPNext TIDAK menegakkan keseimbangan per nilai dimensi: wajib hook `before_submit` Journal Entry (per Dana). `automatically_post_balancing_accounting_entry` harus NONAKTIF.
- Journal Entry bertipe Bank Entry mewajibkan `cheque_no` dan `cheque_date`. Akun Receivable/Payable wajib Party: jangan dipakai untuk akun tanpa party.
- Idempotensi jurnal: Custom Field `donation_ref` (Data, unique, no_copy, read_only), nilai `{ID}:{PERISTIWA}[:n]`, tak pernah ''.
- `Financial Report Template` v16 tidak mendukung `group_by_dimension`: laporan per Dana memakai Balance Sheet/P&L/Cash Flow standar (kolom per Dana) + Script Report kustom untuk format PSAK.
- Python `urllib` ke lpm.siapguna.org ditolak 403 tanpa `User-Agent` mirip curl.
- Image build: `docker build -t donasi-eco3:local .`; mode dev: bind mount folder app (tanpa rebuild); editable install `uv pip install --python env/bin/python -e apps/donasionline`.

## 4. Fase kerja

### W0. Keputusan & prasyarat (tanya pengguna, satu pesan)
Jawaban F1, F4, F7, F25 (prioritas, lihat PDF). Bila belum, pakai default: F1=model A (platform = amil/PUB berizin), F4=wakaf diblokir, F7=clearing=Kas (provisional), F25=fee non-ZIS ditahan. Tanyakan juga: nama peran Frappe, kanal pengingat (WA gateway/email), retensi data (usul: Occurrence & Reminder Log 24 bulan, OTP & log atribusi 90 hari). Tanyakan token GitHub baru dan kunci WA bila akan push/kirim.
Selesai bila: keputusan tercatat di `docs/KEPUTUSAN.md` (tanpa rahasia).

### W1. Stack Docker project donasi-eco3
KONDISI AWAL (sudah disiapkan; BELUM dinyalakan): berkas stack sudah ada di root folder ini (compose.yaml, compose.override.yaml, Dockerfile, README.md, .env mode 600 dengan `COMPOSE_PROJECT_NAME=donasi-eco3`, `SITE_NAME=donasi.localhost`, `HTTP_PORT=8082`, `ERPNEXT_IMAGE=sedekah-erp:local` yang masih memuat app lama), serta repo git (commit `40c5d86` sudah ada di GitHub `donasi-eco3`, remote belum dikonfigurasi).
1. Ganti `ERPNEXT_IMAGE` menjadi `donasi-eco3:local`; setelah W2 (rename app) rebuild image. Cek ulang port 8082 bebas dan `docker compose config -q`.
2. Build image (FROM frappe/erpnext:version-16 + app `donasionline`), `docker compose up -d`, `restart frontend`. Karena nama project baru, volume baru dan site `donasi.localhost` dibuat otomatis oleh service `create-site`.
Selesai bila (bukti): `curl 127.0.0.1:8082/api/method/ping` = pong; login Administrator via API OK; `bench version` menampilkan frappe 16.x & erpnext 16.x; `bench doctor` worker online; scheduler enabled.
Stack lama `sedekah-erp` sudah mati; volume lamanya jangan dihapus tanpa izin pengguna.

### W2. App `donasionline`
Buat dari `_draft/sedekah_finance` dengan penamaan baru: paket `donasionline`, modul "Donasi Online", `hooks.py` (`required_apps=["erpnext"]`, `after_install`, `doc_events`). Hapus sisa nama `sedekah_finance`. Install ke site (`bench --site donasi.localhost install-app donasionline`).
Selesai bila: `bench --site ... list-apps` memuat donasionline; DocType Dana, Kampanye Donasi, Donation, pengaturan tampil; tidak ada import error.

### W3. Fondasi keuangan (PSAK 409/401) — di site UJI dulu (`uji.localhost`), lalu site utama
Implementasi sesuai `docs/psak/05` bagian A-C:
- `setup/seed.py` idempoten: Company (IDR), Fiscal Year, bagan akun (`setup/chart.py`, 86 akun), nilai Dana (ZAKAT, INFAK-TT, INFAK-T, AMIL, NONHALAL, WAKAF, TITIPAN), Accounting Dimension `Dana` (mandatory BS & PL) dan `Kampanye`, Accounting Dimension Filter per Dana (aturan di `chart.py` FILTERS), Cost Center Program + Operasional Amil, Custom Field `donation_ref`, default akun Company.
- `guards.py`: `validate_dana_balance` (before_submit JE): jumlah debit-kredit per nilai Dana harus nol; flag `skip_dana_balance` untuk pengecualian eksplisit.
- Setup wizard: jalankan `setup_complete` TANPA company, lalu seed membuat Company (uji di site uji; jika gagal, buat Company dengan flag ignore_chart_of_accounts).
Selesai bila (bukti): tes `bench --site uji.localhost run-tests --app donasionline` lulus; JE tak seimbang per Dana DITOLAK, JE seimbang DITERIMA; akun di luar filter Dana DITOLAK; Balance Sheet/P&L `group_by_dimension=Dana` menampilkan kolom per Dana; seed dijalankan dua kali tanpa duplikasi.

### W4. DocType Donation + mesin jurnal E2-E5
`donation_logic.py`/`journals.py` sesuai `docs/psak/05` D0, E1-E5: E2 penerimaan (zakat->4-1100/4-1200 ZAKAT; infak_bebas->4-2100 INFAK-TT; infak_terikat->4-2200 INFAK-T + kampanye wajib; wakaf/fidyah/qurban DIBLOKIR), E3 hak amil (Decimal half-up, h_zakat=12,5 provisional, h_infak=0), E4 fee (ditahan bila saldo clearing AMIL kurang, tidak pernah negatif), E5 settlement per Dana (S_X). Idempotensi `donation_ref`; Bank Entry dengan cheque_no/date; posting_date = tanggal peristiwa; gerbang `posting_enabled` & peran model A.
Selesai bila: tes termasuk properti acak G (per-Dana nol, total saldo konsisten), kirim ulang peristiwa tidak menggandakan jurnal, fee ditahan, settlement menutup clearing per Dana (contoh G=100.000, h=12,5%, F=4.000 -> S_INFAK-TT=87.500, S_AMIL=8.500).
Ditunda dengan sengaja (draf di 05): E6 penyaluran (butuh DocType Disbursement), E8, E10 refund, E12-E20.

### W5. Rancangan sistem (Tahap 2; BELUM pernah dikerjakan)
`docs/sistem/00..08` untuk SELURUH sistem (14 modul: akun/OTP, kampanye, donasi+pembayaran, zakat/wakaf, mitra/atribusi, doa+amin, notifikasi, survei, gamifikasi, Jejak Kebaikan, Shadaqa Rutin, konten, Quran Jar/referensi, Qurban sebagai batas): alur sistem (Mermaid sequence), alur data & mesin status, DFD L0/L1 (+L2 proses kritis), ERD & Doctype lengkap (termasuk tambahan H.2 di 05: Campaign.fund_type/program, Disbursement, Settlement, Reward Claim, Recurring Schedule/Occurrence/Reminder Log, atribut Donor), matriks keterlacakan (semua endpoint di `02-katalog-endpoint.md` dan semua Doctype di `03` dipetakan), keamanan/retensi/idempotensi. Gunakan Workflow multi-agen (agen per modul + sintesis + 3 reviewer adversarial: cakupan, konsistensi, kelayakan Frappe) bila pengguna mengaktifkan ultracode/izinkan.
Selesai bila: reviewer cakupan tak menemukan endpoint/Doctype yatim; setiap klaim ditandai FAKTA/USULAN/ASUMSI.

### W6. DocType platform + API whitelisted
Bangun Doctype dari W5 (Campaign->`Kampanye Donasi`, Donor, Payment Method, Mitra, Doa Amin, Penyaluran, Artikel, Video, Survei, Misi Baik, Reward/Klaim, Recurring, Notifikasi, dll.), impor snapshot dari `sedekah-vue/src/data/*` (bukan `doa.json`/`teman.json`: berisi teks pengguna nyata), method whitelisted sesuai katalog endpoint, webhook gateway (verifikasi tanda tangan, idempotensi) yang memanggil mesin jurnal W4. Integrasi gateway nyata hanya di sandbox.
Selesai bila: tiap endpoint di katalog punya method + tes; tidak ada akses tulis publik tanpa batas laju/validasi.

### W7. UI
Salin `sedekah-vue` ke `ui/` (salinan; jangan ubah aslinya). Ganti `src/donate.js` & `src/auth.js` (titik "Frappe hook") agar memanggil method `donasionline`. Pertahankan aturan di `handover-frappe/05` bagian 4 (urutan rute, penanda mitra, i18n dari URL, variabel CSS lime, konstanta zakat). Shadaqa Rutin: engine di `src/rutin.js` jadi acuan; jadwal/occurrence pindah ke Doctype + scheduler harian.
Selesai bila: alat uji di `docs/tools/` (helpers-test 400, feedlist-test 30, rutin-test 107, penanda-test, regress-shots) lulus terhadap backend Frappe; dua bahasa (id, /en).

### W8. Penutupan
Dokumen serah terima diperbarui, `README`, pin digest image, pindai rahasia, commit; push hanya bila pengguna memberi token & tujuan; laporan WA + chat; tawarkan penghapusan volume lama `sedekah-erp_*` (perlu persetujuan).

## 5. Status rancangan (jawaban "sudah selesai atau masih ada yang dikerjakan?")
| Bagian | Status |
|---|---|
| Riset PSAK 409/109, 401/101, standar terkait, kapabilitas ERPNext 16 | Selesai (teks final PSAK tidak terbuka; dasar: Draf Eksposur 2021, ditandai) |
| Rancangan akun, dimensi, katalog jurnal E1-E20 (`05`) | Draf lengkap, sudah direview 3 reviewer + 1 putaran perbaikan; BELUM divalidasi akuntan; E6, E8, E10, E12-E20 baru draf/ditunda |
| Keputusan F1-F29 | BELUM dijawab (PDF tersedia) |
| Rancangan sistem Tahap 2 (alur sistem, data flow, DFD, Doctype seluruh sistem, matriks) | BELUM dikerjakan (W5) |
| Doctype platform & API Frappe | Hanya usulan di handover; belum dibangun (W6) |
| Kode app (kerangka, DocType, bagan akun) | ~30%: guards, journals, seed, install, tes belum ada |
| UI Vue | Selesai sebagai tiruan; belum tersambung ke Frappe (W7) |
| Qurban | Ditunda sengaja |
Jadi rancangan keuangan sudah cukup untuk mulai membangun (W1-W4), tetapi rancangan sistem lengkap (W5-W6) masih harus dikerjakan.

## 6. Cara sesi baru memulai
1. `cd /Users/ramapermadoni/Project/docker/donasi-eco3` lalu baca berkas ini, `docs/psak/05-*.md`, `docs/psak/keputusan-akuntan-syariah.pdf`, `docs/lpm/analisis-keuangan-lpm.md`, dan `RINGKAS.md` di handover-frappe.
2. Konfirmasi ke pengguna: urutan fase, jawaban W0, dan bahwa W1 memakai port 8082.
3. Kerjakan per fase; setiap fase diakhiri bukti verifikasi + laporan singkat; jangan lanjut bila kriteria selesai belum terpenuhi.
