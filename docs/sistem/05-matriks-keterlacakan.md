# 05. Matriks Keterlacakan (HASIL OTOMATIS)

Dihasilkan oleh `tools/gen_sistem_docs.py`. Sumber endpoint: handover `02-katalog-endpoint.md` (FAKTA, dibaca dari berkas); method dan tes: `apps/donasionline/donasionline/api/catalog.py` (FAKTA, ada di kode). Cakupan diperiksa oleh `tools/cek_cakupan.py`.

## A. Endpoint -> Method -> Tes

| HTTP | Path lama (sedekah.id) | Method Frappe `donasionline.api.…` | Tamu | Tes | Catatan |
|---|---|---|---|---|---|
| GET | `/api/auth/me` | `auth.me` | ya | `test_auth_alur_register_otp_login_me_logout` |  |
| POST | `/api/auth/otp/request` | `auth.request_otp` | ya | `test_auth_alur_register_otp_login_me_logout` | batas laju 5/10 menit |
| POST | `/api/auth/otp/verify` | `auth.verify_otp` | ya | `test_otp_salah_dan_percobaan_dibatasi` | 5 percobaan, kedaluwarsa 5 menit (ASUMSI) |
| POST | `/api/auth/register` | `auth.register_donor` | ya | `test_auth_alur_register_otp_login_me_logout` |  |
| POST | `/api/auth/logout` | `auth.logout` | tidak | `test_auth_alur_register_otp_login_me_logout` |  |
| POST | `/api/auth/delete-account` | `auth.delete_account` | tidak | `test_hapus_akun_anonimkan` | konfirmasi 'HAPUS' |
| GET | `/api/auth/google/status` | `auth.google_status` | ya | `test_konten_publik` | selalu enabled=false |
| GET | `/api/donor/stats` | `donor.stats` | tidak | `test_donasi_pembayaran_webhook_paid` |  |
| GET | `/api/donor/donations` | `donor.donations` | tidak | `test_donasi_pembayaran_webhook_paid` |  |
| GET | `/api/donor/doa` | `donor.my_doa` | tidak | `test_doa_amin_notifikasi` |  |
| PATCH | `/api/donor/profile` | `donor.update_profile` | tidak | `test_profil_dan_donor` |  |
| GET | `/api/donor/gamification` | `gamification.get` | tidak | `test_gamifikasi_klaim` | rumus poin = ASUMSI |
| POST | `/api/donor/gamification/claim` | `gamification.claim_reward` | tidak | `test_gamifikasi_klaim` | klaim mati bawaan |
| GET | `/api/campaigns/feed` | `campaign.list_campaigns` | ya | `test_kampanye` |  |
| GET | `/api/campaigns/:slug` | `campaign.detail` | ya | `test_kampanye` |  |
| POST | `/api/donations` | `donation.create` | ya | `test_donasi_validasi_dan_atribusi` | min Rp3.000; id publik acak |
| POST | `/api/payment/create` | `payment.create` | ya | `test_donasi_pembayaran_webhook_paid` | SIMULATOR; Midtrans nyata belum |
| GET | `/api/donasi/:id` | `donation.status` | ya | `test_donasi_pembayaran_webhook_paid` |  |
| GET | `/api/donasi/:id/qr` | `payment.qr_png` | ya | `test_donasi_pembayaran_webhook_paid` |  |
| GET | `/api/payment/methods` | `payment.methods` | ya | `test_konten_publik` |  |
| GET | `/api/payment/snap-config` | `payment.snap_config` | ya | `test_konten_publik` | hanya clientKey |
| GET | `/api/gold-price` | `zakat.gold_price` | ya | `test_konten_publik` | fallback 2.300.000 |
| GET | `/api/campaigns/:slug/donors` | `campaign.donors` | ya | `test_kampanye` |  |
| GET | `/api/penyaluran` | `content.penyaluran_list` | ya | `test_konten_publik` |  |
| GET | `/api/penyaluran/meta` | `content.penyaluran_meta` | ya | `test_konten_publik` |  |
| GET | `/api/laporan` | `content.laporan_list` | ya | `test_konten_publik` |  |
| GET | `/api/doa` | `doa.list_doa` | ya | `test_doa_amin_notifikasi` |  |
| GET | `/api/doa/untuk-diaminkan` | `doa.for_amin` | ya | `test_doa_amin_notifikasi` |  |
| POST | `/api/doa/:id/amin` | `doa.amin` | ya | `test_doa_amin_notifikasi` | maks 10 per pelaku per doa |
| GET | `/api/video/latest` | `content.video_latest` | ya | `test_konten_publik` |  |
| GET | `/api/home/popup-menu` | `content.popup_menu` | ya | `test_konten_publik` |  |
| GET | `/api/notifications` | `notification.list_notifications` | ya | `test_doa_amin_notifikasi` |  |
| POST | `/api/notifications` | `notification.mark_read` | tidak | `test_doa_amin_notifikasi` |  |
| GET | `/api/satisfaction-survey` | `survey.get` | ya | `test_survei` |  |
| POST | `/api/satisfaction-survey` | `survey.submit` | ya | `test_survei` |  |
| POST | `/api/baik/start` | `baik.start` | tidak | `test_baik_start_claim_release` | klaim TIDAK membuat Donation/jurnal (E18 diblokir F22) |
| POST | `/api/baik/claim` | `baik.claim` | tidak | `test_baik_start_claim_release` |  |
| POST | `/api/baik/release` | `baik.release` | tidak | `test_baik_start_claim_release` |  |
| GET | `/api/recurring/schedules/me` | `recurring.me` | tidak | `test_rutin_jadwal_eksekusi_streak` |  |
| POST | `/api/recurring/schedules` | `recurring.create` | tidak | `test_rutin_jadwal_eksekusi_streak` | min Rp5.000 |
| GET | `/api/recurring/streak` | `recurring.streak` | tidak | `test_rutin_jadwal_eksekusi_streak` |  |
| POST | `/api/recurring/schedules/:id/execute` | `recurring.execute` | tidak | `test_rutin_jadwal_eksekusi_streak` |  |
| POST | `/api/recurring/schedules/:id/execute/makeup` | `recurring.execute_makeup` | tidak | `test_rutin_jadwal_eksekusi_streak` |  |
| PATCH | `/api/recurring/schedules/:id` | `recurring.update` | tidak | `test_rutin_jadwal_eksekusi_streak` |  |
| POST | `/api/recurring/schedules/:id/<aksi>` | `recurring.set_state` | tidak | `test_rutin_jadwal_eksekusi_streak` | pause/resume/cancel (juga pengganti DELETE) |
| GET | `/api/artikel` | `content.artikel_list` | ya | `test_konten_publik` | tidak dipanggil tiruan; dibangun dari snapshot |
| GET | `/api/artikel/:slug` | `content.artikel_detail` | ya | `test_konten_publik` |  |
| GET | `/api/wilayah` | `content.wilayah` | ya | `test_konten_publik` |  |
| GET | `/api/campaigns/:slug/updates` | `campaign.updates` | ya | `test_kampanye` |  |
| GET | `(baru) mitra` | `content.mitra_list` | ya | `test_konten_publik` | daftar mitra |
| GET | `(baru) mitra/:slug` | `content.mitra_detail` | ya | `test_konten_publik` |  |
| GET | `(baru) legal` | `content.legal` | ya | `test_konten_publik` | 3 halaman x 2 bahasa |
| GET | `(baru) banners` | `content.banners` | ya | `test_konten_publik` |  |
| GET | `(baru) quran-jar` | `content.quran_jar` | ya | `test_konten_publik` |  |
| GET | `(baru) misi` | `baik.missions` | ya | `test_baik_start_claim_release` |  |
| GET | `(baru) payment/instruksi` | `payment.instructions` | ya | `test_konten_publik` |  |
| GET | `(baru) video` | `content.video_list` | ya | `test_konten_publik` |  |
| POST | `(baru) webhook gateway` | `payment.webhook` | ya | `test_donasi_pembayaran_webhook_paid` | tanda tangan SHA-512 wajib; tanpa kunci = ditolak |
| POST | `(baru) simulate_paid` | `payment.simulate_paid` | tidak | `test_donasi_pembayaran_webhook_paid` | hanya Petugas/System Manager |

### Sengaja ditunda

| HTTP | Path | Alasan |
|---|---|---|
| GET | `/api/media/...` | Aset: unduh ke File Frappe butuh izin hak aset (risiko 06); URL hotlink dipertahankan |
| POST | `/api/donations/au-transfer` | Tidak dipanggil tiruan, bentuk tak terdokumentasi |
| * | `/api/payment/* (PayPal)` | Intl/PayPal tidak ditiru |

## B. Doctype handover 03 -> DocType dibangun

| Doctype usulan (handover 03) | Dibangun sebagai |
|---|---|
| Campaign | Kampanye Donasi |
| Campaign Update | Penyaluran (Link kampanye) |
| Donation | Donation |
| Payment Request | Permintaan Pembayaran |
| Payment Method | Metode Pembayaran |
| Donor | Donor |
| Mitra | Mitra |
| Doa Amin | Doa Amin |
| Penyaluran | Penyaluran |
| Artikel | Artikel |
| Video | Video Donasi |
| Laporan | Laporan Donasi |
| Satisfaction Survey | Survei Kepuasan |
| Survey Scale Item | Butir Skala Survei |
| Survey Response | Jawaban Survei |
| Gold Price | Harga Emas |
| Recurring Schedule | Jadwal Rutin |
| Recurring Execution | Eksekusi Rutin |
| Baik Mission | Misi Kebaikan |
| Baik Sponsor Pool | Pool Sponsor Kebaikan |
| Baik Session | Sesi Kebaikan |
| Gamification Level | Level Gamifikasi |
| Gamification Reward | Hadiah Gamifikasi |
| Reward Claim | Klaim Hadiah |
| Home Popup Menu | Pengaturan Beranda + Item Menu Popup Beranda |
| Banner | Banner |
| Quran Jar Mood / Verse | Ayat Quran Jar (mood = Select; label/warna mood tetap di UI) |
| Region (Wilayah) | Wilayah |
| Legal Page | Halaman Legal |

## C. DocType -> method yang menyentuhnya

| DocType | Method (terbaca dari kode) |
|---|---|
| Mitra | campaign.detail, content.mitra_detail, content.mitra_list, donation.create |
| Banner | content.banners |
| Wilayah | content.wilayah |
| Halaman Legal | content.legal |
| Ayat Quran Jar | content.quran_jar |
| Penyaluran | campaign.updates, content.penyaluran_list, content.penyaluran_meta |
| Artikel | content.artikel_detail, content.artikel_list |
| Video Donasi | content.video_latest, content.video_list |
| Laporan Donasi | content.laporan_list |
| Harga Emas | zakat.gold_price |
| Item Menu Popup Beranda | — (diisi impor/admin atau mesin jurnal) |
| Pengaturan Beranda | content.popup_menu |
| Instruksi Pembayaran | — (diisi impor/admin atau mesin jurnal) |
| Metode Pembayaran | payment.create, payment.instructions, payment.methods, recurring.create |
| Permintaan Pembayaran | donation.status, payment._apply_status, payment.create, payment.qr_png, payment.simulate_paid, payment.webhook |
| Donor | _util.current_donor, auth.register_donor, auth.verify_otp, donation.create, gamification.claim_reward, recurring._spawn |
| Permintaan OTP | auth._send_otp, auth.verify_otp, recurring.purge_logs |
| Doa Amin | doa.amin, donor.my_doa |
| Butir Skala Survei | — (diisi impor/admin atau mesin jurnal) |
| Survei Kepuasan | survey.get, survey.submit |
| Jawaban Survei | survey.submit |
| Eksekusi Rutin | — (diisi impor/admin atau mesin jurnal) |
| Jadwal Rutin | recurring._mine, recurring.create, recurring.me, recurring.on_donation_paid, recurring.run_due, recurring.streak |
| Log Pengingat Rutin | recurring.purge_logs, recurring.run_due |
| Pool Sponsor Kebaikan | baik.claim, baik.missions |
| Misi Kebaikan | baik.claim, baik.missions, baik.start |
| Sesi Kebaikan | baik._own, baik.claim, baik.release, baik.start |
| Level Gamifikasi | gamification._levels |
| Hadiah Gamifikasi | gamification.claim_reward, gamification.get |
| Klaim Hadiah | gamification.claim_reward |
| Pengaturan Gamifikasi | gamification.claim_reward, gamification.get, gamification.points |
| Kampanye Donasi | _util.campaign_by_key, baik.claim, campaign.detail, campaign.list_campaigns, content.video_list, donation.create, donation.status, recurring._spawn, recurring.create |
| Donation | campaign.donors, doa.for_amin, doa.list_doa, donation.by_public_id, donation.create, donation.status, donor.donations, donor.my_doa, payment._apply_status, payment.create, recurring._spawn, recurring.execute, recurring.execute_makeup, survey.submit |
| Dana | — (diisi impor/admin atau mesin jurnal) |
| Pengaturan Donasi | — (diisi impor/admin atau mesin jurnal) |
