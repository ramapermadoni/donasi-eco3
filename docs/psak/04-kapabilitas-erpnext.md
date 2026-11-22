# Kapabilitas ERPNext/Frappe v16 untuk Akuntansi Dana ala PSAK 109/101

Tanggal riset: 2026-11-22. Metode: membaca kode sumber di image Docker lokal `frappe/erpnext:version-16` (perintah baca-saja lewat `docker run --rm --entrypoint bash`, tanpa menyentuh container/volume lain), ditambah sumber web. Tidak ada site hidup yang dijalankan, jadi semua klaim perilaku runtime adalah hasil membaca kode, bukan hasil uji.

Legenda keyakinan: **TERVERIFIKASI** = dibaca langsung dari kode/dokumen sumber. **DUGAAN** = inferensi, sumber sekunder, atau belum diuji.

Fakta image: `erpnext.__version__ = "16.56.0"` (`/home/frappe/frappe-bench/apps/erpnext/erpnext/__init__.py`). Folder `apps/` di image hanya berisi `erpnext` dan `frappe` (tidak ada app `payments` maupun `non_profit`). TERVERIFIKASI.

Semua path kode di bawah relatif terhadap `/home/frappe/frappe-bench/apps/erpnext/erpnext/` kecuali disebut lain.

---

## 0. Standar yang berlaku (wajib dicantumkan)

| Butir | Temuan | Sumber | Keyakinan |
|---|---|---|---|
| Penomoran baru | IAI/DSAK mengesahkan perubahan penomoran PSAK pada 12 Desember 2022, berlaku efektif **1 Januari 2024**. Standar syariah diberi awalan 4xx. **PSAK 109 -> PSAK 409** (Akuntansi Zakat dan Infak/Sedekah), **PSAK 101 -> PSAK 401** (Penyajian Laporan Keuangan Syariah). Substansi tidak diganti oleh standar lain, hanya dinomori ulang. | https://web.iaiglobal.or.id/assets/files/file_publikasi/Perubahan_Penomoran_PSAK_ISAK_dalam_SAK_Indonesia.pdf ; daftar pasangan lama-baru: https://web.iaiglobal.or.id/assets/files/file_publikasi/Komparasi%20Perubahan%20Penomoran%20PSAK%20ISAK%20SAK%20Indonesia_FINAL.pdf | TERVERIFIKASI (PDF dibaca) |
| Revisi isi | Draf Eksposur PSAK 109 dan PSAK 101 (Revisi 2021) diterbitkan DSAS IAI, tanggapan paling lambat 31 Maret 2022. Dalam DE itu tanggal efektif yang diusulkan 1 Januari 2023, tanpa penerapan dini. | https://web.iaiglobal.or.id/assets/files/file_berita/DE%20PSAK%20101%20dan%20DE%20PSAK%20109%20Revisi%202021.pdf | TERVERIFIKASI (DE dibaca) |
| Pengesahan final | Revisi disahkan akhir Mei 2022 (sumber sekunder menyebut 31 Mei 2022), berlaku efektif 1 Januari 2024 dengan opsi penerapan dini. | https://www.jurnal.id/id/blog/psak-109-dalam-laporan-keuangan/ ; ringkasan pencarian atas buletin IAI "DSAS Terkini" | DUGAAN (sumber sekunder; teks final tidak berhasil saya baca) |
| Konflik sumber | Satu artikel jurnal menyebut pembaruan menjadi PSAK 409 berlaku 1 Januari 2025 (https://jamak.fe.ung.ac.id/index.php/jamak/article/download/494/201/), bertentangan dengan dokumen IAI (1 Januari 2024). Saya menganggap dokumen IAI yang benar. | lihat atas | Konflik, belum terselesaikan sepenuhnya |
| Amandemen lain | Ada "Penyesuaian Tahunan 2023" atas PSAK 109 yang disebut hanya perubahan redaksi. Hanya dari hasil pencarian, PDF buletin tidak terbaca. | https://web.iaiglobal.or.id/assets/files/file_publikasi/DSAS%20Terkini%20XIII-XIV%202023.pdf | DUGAAN |
| Pengganti | Tidak ditemukan standar yang menggantikan/mencabut PSAK 409 per 2026-11-22. Tidak ditemukan pula sumber tentang nasib ISAK 35 (yang menurut DE mengatur penyajian entitas nirlaba, termasuk amil, sebelum PSAK 101 revisi). | pencarian web | TIDAK DITEMUKAN |
| Rujukan BAZNAS/OJK | Tidak dicari mendalam; belum ada teks BAZNAS/OJK yang dibaca. Regulasi (UU Zakat, peraturan BAZNAS) belum diverifikasi di dokumen ini. | - | TIDAK DIVERIFIKASI |

Isi DE PSAK 101/109 Revisi 2021 yang relevan untuk desain (dibaca dari PDF; teks DE, bukan standar final, nomor paragraf sengaja tidak dikutip):

- Komponen laporan keuangan entitas amil di DE: laporan posisi keuangan, **laporan aktivitas**, laporan arus kas, catatan atas laporan keuangan. Istilah "laporan perubahan dana" (PSAK 109 versi 2010) diganti "laporan aktivitas". Laporan perubahan aset kelolaan dihapus dari komponen. TERVERIFIKASI (DE).
- Aset neto di laporan posisi keuangan disubklasifikasi menjadi **dana zakat, dana infak/sedekah, dan dana amil**. Bila memakai kerangka nirlaba, dana zakat dan infak/sedekah = aset neto dengan pembatasan, dana amil = tanpa pembatasan. Dasar kesimpulan DE (DK40-DK42) menjelaskan DSAS memutuskan dana ZIS diperlakukan sebagai aset neto, bukan liabilitas, walau sebagian pihak berpendapat liabilitas. TERVERIFIKASI (DE).
- Liabilitas penyaluran zakat dan penyaluran infak/sedekah tetap ada sebagai pos liabilitas (ilustrasi laporan posisi keuangan di DE). TERVERIFIKASI (DE).
- Laporan aktivitas memuat penerimaan infak/sedekah **dengan pembatasan (muqayyadah)** dan **tanpa pembatasan (mutlaqah)**, hasil pengelolaan aset, bagian amil dari penerimaan zakat dan dari infak/sedekah, serta beban. Pengungkapan wajib mencakup persentase/jumlah bagian amil dan rincian saldo infak terikat/tidak terikat. TERVERIFIKASI (DE).
- **Dana nonhalal**: teks PSAK 109 versi lama (ED 2008/2010, salinan di https://idr.uin-antasari.ac.id/11349/10/LAMPIRAN.pdf) menyebut penerimaan nonhalal (mis. jasa giro bank konvensional) diakui sebagai dana nonhalal, terpisah dari dana zakat, infak/sedekah, dan amil, dan disalurkan sesuai syariah (TERVERIFIKASI untuk versi lama). Pada teks DE Revisi 2021 hasil ekstraksi saya tidak ada kata "halal" sama sekali. Entah dana nonhalal dipertahankan, dipindah, atau DE hanya memuat paragraf yang berubah. **Status dana nonhalal di PSAK 409 final: TIDAK TERVERIFIKASI.** Rekomendasi: tetap pisahkan sebagai dana tersendiri (paling aman), lalu konfirmasi dengan auditor/DSAS.
- Catatan terminologi: permintaan Anda menyebut "Infak Terikat" dan "Infak Tidak Terikat" sebagai dua dana. Di DE keduanya adalah **satu dana infak/sedekah** dengan dua sub-kategori (terikat/tidak terikat) yang dilaporkan di laporan aktivitas/CALK. Memodelkannya sebagai dua nilai dimensi tetap berguna (lihat bagian 9), asal ada agregasi untuk pelaporan resmi.

---

## 1. Accounting Dimension dan Dimension-wise Filter

**Bisakah dipakai untuk "Dana"? Ya.** TERVERIFIKASI.

- DocType `Accounting Dimension` (`accounts/doctype/accounting_dimension/`) punya field `label`, `fieldname`, `document_type` (DocType apa pun sebagai sumber nilai), `disabled`, tabel `dimension_defaults`. Saat disimpan, `make_dimension_in_accounting_doctypes` (accounting_dimension.py baris ~138) membuat Custom Field di DocType transaksi (GL Entry, Journal Entry Account, Payment Entry, Payment Request, dll.). Jadi dimensi "Dana" = DocType custom `Dana` (mis. 5 record) + satu Accounting Dimension yang menunjuk ke sana.
- Tabel anak `Accounting Dimension Detail` (`accounts/doctype/accounting_dimension_detail/`) per **Company** punya: `default_dimension`, **`mandatory_for_bs`**, **`mandatory_for_pl`**, `automatically_post_balancing_accounting_entry`, `offsetting_account`.

**Wajib per akun?** Tidak per akun individual, melainkan per **jenis laporan** (Balance Sheet / Profit and Loss) per company. Pemeriksaan ada di `accounts/doctype/gl_entry/gl_entry.py` (`validate_dimensions_for_pl_and_bs`, baris ~185-215: melempar error "Accounting Dimension X is required for 'Profit and Loss' account Y" bila field dimensi kosong) dan `accounts/general_ledger.py` baris ~682. Untuk kasus kita, mencentang kedua kotak memaksa setiap baris jurnal punya "Dana". TERVERIFIKASI. Dokumentasi resmi membenarkan: https://docs.frappe.io/erpnext/user/manual/en/accounting-dimensions (kutipan: P&L "Requires a dimension for postings to Income and Expense accounts", Balance Sheet "... Asset, Liability, and Equity accounts"; dimensi tidak menandai transaksi lama secara retroaktif). TERVERIFIKASI.

**Pembatasan akun per nilai dimensi:** DocType `Accounting Dimension Filter` (`accounts/doctype/accounting_dimension_filter/`): field `accounting_dimension`, `allow_or_restrict` (Allow/Restrict), tabel `accounts` (Applicable On Account), tabel `dimensions` (Allowed Dimension: `accounting_dimension`, `dimension_value`), `apply_restriction_on_values`, `company`, `disabled`. Ini dapat dipakai agar mis. akun "Pendapatan Zakat" hanya boleh bersama Dana=Zakat. Validasi di `accounting_dimension_filter.py` (`validate_applicable_accounts` mencegah satu akun terdaftar di dua filter dimensi yang sama). Penegakan saat posting TERVERIFIKASI (koreksi 2026-11-22) di `accounts/general_ledger.py` `validate_allowed_dimensions` (baris ~908-950): mode **Allow** menolak bila nilai dimensi terisi dan tidak ada di daftar; mode **Restrict** menolak bila nilai ada di daftar; hanya berlaku pada akun yang terdaftar (Applicable On Account); dimensi tidak dipaksa terisi kecuali `is_mandatory` pada baris akun. Uji pada JE multi-dimensi tetap belum dilakukan.

**Auto-offsetting antar dimensi:** `accounts/general_ledger.py` fungsi `make_acc_dimensions_offsetting_entry` (baris 73-106) semula saya gambarkan sebagai baris penyeimbang otomatis per nilai dimensi memakai `offsetting_account` (gambaran itu keliru, lihat koreksi di bawah). **KOREKSI 2026-11-22 (TERVERIFIKASI dari kode):** ini BUKAN baris penyeimbang per nilai dimensi. `make_acc_dimensions_offsetting_entry` menyalin SETIAP GL Entry dan menambah baris lawan ke `offsetting_account` (jumlah dibagi jumlah dimensi), sehingga melipatgandakan GL bila dinyalakan. ERPNext tidak menegakkan keseimbangan per nilai dimensi sama sekali: `gl_entry.validate_dimensions_for_pl_and_bs` hanya memeriksa dimensi tidak kosong dan `journal_entry.set_total_debit_credit` hanya membandingkan total debit dan kredit. Karena itu tulis baris pindah kas antar Dana secara eksplisit, buat validasi per Dana sendiri di kode, dan biarkan `automatically_post_balancing_accounting_entry` nonaktif.

**Laporan dapat difilter/dikelompokkan per dimensi:** TERVERIFIKASI.

- `accounts/report/balance_sheet/balance_sheet.js`, `profit_and_loss_statement/profit_and_loss_statement.js`, `cash_flow/cash_flow.js` memanggil `erpnext.utils.add_dimensions(...)` (filter per dimensi) dan memiliki filter **`group_by_dimension`** (opsi dari `erpnext.financial_statements.get_accounting_dimension_options()`). Logikanya di `accounts/report/financial_statements.py` (`get_dimension_values`, `get_dimension_period_list`: kolom = hasil kali nilai dimensi x periode).
- Arus kas: `cash_flow.py` baris ~148-156 menolak "Opening and Closing balance" untuk laporan arus kas yang dikelompokkan dimensi ("not supported for dimension grouped cash flow statement"). Jadi arus kas per dana bisa, tetapi tanpa saldo awal/akhir kas per dana. TERVERIFIKASI.
- Ada pula laporan khusus `Dimension-wise Accounts Balance Report` (`accounts/report/dimension_wise_accounts_balance_report/`). TERVERIFIKASI keberadaan.
- Catatan di `financial_statements.py`: "Disabled dimensions values are not filtered out". DUGAAN dampak: nilai dimensi yang dinonaktifkan tetap muncul sebagai kolom.

**Penutupan buku per dimensi:** `Period Closing Voucher` menghitung saldo P&L **per kombinasi dimensi** (`get_account_balances_based_on_dimensions`, `update_default_dimensions`, period_closing_voucher.py baris ~412-491) dan menaruh selisih ke akun penutup bertipe Liability/Equity (baris ~159). Artinya surplus/defisit tiap dana dipindahkan ke aset neto dana yang sama, tanpa tercampur. TERVERIFIKASI.

---

## 2. Cost Center, Project, Company: pisah atau satu Company?

- `Cost Center` (`accounts/doctype/cost_center/`): `company`, `parent_cost_center`, `is_group`, `disabled`. Pohon per company. `Project` (`projects/doctype/project/`): `company`, `cost_center`, `status`, `project_type`. TERVERIFIKASI.
- Cost center **wajib untuk akun Profit and Loss** (`gl_entry.py` melempar "Missing Cost Center"), bukan untuk akun neraca. Kalau "Dana" dijadikan Cost Center, akun neraca (kas, aset neto, liabilitas penyaluran) tidak ikut terpisah per dana. Karena itu **dimensi custom "Dana" yang mandatory BS+PL lebih tepat** daripada cost center. DUGAAN-kuat (inferensi dari kode di atas).
- Pembagian yang masuk akal: Dana = Accounting Dimension (sumber dana, dimensi pelaporan resmi); Cost Center atau Project = program/kampanye (mis. "Program Pendidikan", "Palestina"), opsional. `Payment Request` memiliki field `cost_center` dan `project` (+ dimensi lain di section accounting dimensions), jadi donasi online bisa membawa label dana dan program. TERVERIFIKASI.
- **Satu Company vs banyak Company**: sedekah.id hanya perlu satu entitas hukum; satu Company cukup. Banyak Company hanya bila ada entitas hukum terpisah (LAZ + yayasan, atau cabang berbadan hukum). Biaya banyak Company: setiap company punya CoA, mata uang, fiscal-year-link, akun clearing, dan penutupan sendiri; transfer antar dana jadi transaksi inter-company yang rumit. Ada laporan `consolidated_financial_statement` tapi tidak diperlukan. TERVERIFIKASI keberadaan laporan; rekomendasi satu Company adalah penilaian saya.

---

## 3. Chart of Accounts: root type dan pemodelan "Dana"

- `Account.root_type` hanya: **Asset, Liability, Income, Expense, Equity** (`accounts/doctype/account/account.json`, baris ~90). `report_type`: Balance Sheet / Profit and Loss. `account_type` memiliki daftar tetap (Bank, Cash, Payable, Receivable, Equity, Liability, Temporary, dst.). Tidak ada root type "Fund"/"Net Assets". TERVERIFIKASI.
- Akun dana dapat dimodelkan sebagai **Equity** ("Aset Neto") dan **Liability** ("Liabilitas Penyaluran Zakat/Infak"): Period Closing Voucher menerima akun penutup Liability atau Equity (`period_closing_voucher.py` baris ~159), jadi keduanya valid. TERVERIFIKASI.
- Ada juga `Account Category` (link dari Account, account.json baris ~206) yang dipakai template laporan baru untuk mengelompokkan akun (bagian 4). TERVERIFIKASI.
- Dua cara memodelkan pemisahan dana:
  - **(A) Dimensi saja** (satu akun "Aset Neto" + dimensi Dana). CoA ringkas, laporan per dana lewat `group_by_dimension`. Risiko: dimensi bisa salah diisi, jadi andalkan mandatory + Dimension Filter.
  - **(B) Akun terpisah per dana** (Aset Neto Zakat, Aset Neto Infak, ...) tanpa dimensi. Risiko: kombinatorial akun besar, laporan resmi mudah tetapi tidak fleksibel.
  - Rekomendasi: A, ditambah (opsional) beberapa akun aset neto terpisah hanya bila auditor meminta.

---

## 4. Financial Report Template / Custom Financial Statement di v16

**Ada.** TERVERIFIKASI.

- DocType `Financial Report Template` (`accounts/doctype/financial_report_template/`): `template_name`, `report_type` (Profit and Loss Statement / Balance Sheet / Cash Flow / **Custom Financial Statement**), `module`, tabel `rows` (`Financial Report Row`), `disabled`.
- `Financial Report Row` (`accounts/doctype/financial_report_row/`): `reference_code`, `display_name`, `indentation_level`, **`data_source`** (Account Data / Calculated Amount / Custom API / Blank Line / Column Break / Section Break), `balance_type` (Opening Balance / Closing Balance / Period Movement), `calculation_formula` (mis. `REV100 + COGS100`), `hide_when_empty`, `reverse_sign`, `fieldtype`, `advanced_filtering`, dll.
- Mesin: `accounts/doctype/financial_report_template/financial_report_engine.py`. Ia memakai filter standar termasuk **dimensi akuntansi** (`_apply_standard_filters`, baris ~776-781, memakai `get_accounting_dimensions`), dan **pada baris ~273-278 justru memunculkan peringatan "Dimension-based grouping is currently unsupported in Custom Financial Report"** bila `group_by_dimension` diisi (koreksi 2026-11-22: sebelumnya salah dibaca sebagai validasi; TERVERIFIKASI). Baris `Account Data` diseleksi lewat aturan akun / `account_category` (contoh: `{"and":[["account_category","=","Revenue from Operations"]]}` di `accounts/financial_report_template/standard_profit_and_loss_(ifrs)/`).
- Template bawaan: Standard P&L (IFRS), Balance Sheet (IFRS), Cash Flow (IFRS), horizontal P&L/BS (kolom), Financial Ratios Analysis. Laporan `Custom Financial Statement` (`accounts/report/custom_financial_statement/`) merender template yang dipilih dan menambah filter dimensi (`erpnext.utils.add_dimensions`: filter satu nilai, bukan pengelompokan); `financial_statements.py` `build_period_list` melewati `get_dimension_period_list` bila `report_template` terisi.
- **Kesimpulan**: "Laporan Aktivitas" amil dapat dibuat sebagai Financial Report Template tipe Custom Financial Statement, dengan baris per kategori akun (penerimaan zakat, penerimaan infak terikat, bagian amil, beban ...) dan formula hitung (surplus). **Pemisahan per dana datang dari filter/pengelompokan dimensi laporan, bukan dari filter dimensi di tingkat baris**: dalam skema baris yang saya baca, baris hanya memfilter akun (`Account Data`) atau formula; saya tidak menemukan filter dimensi per baris. **KOREKSI 2026-11-22 (TERVERIFIKASI): `group_by_dimension` TIDAK didukung pada template/Custom Financial Statement**, jadi kolom per Dana dalam satu laporan tidak bisa dihasilkan dari template. Opsi: (a) jalankan template satu kali per nilai Dana memakai filter dimensi lalu gabungkan di Script Report/cetak; (b) Script Report kustom yang membaca GL Entry atau Account Closing Balance per Dana; (c) Balance Sheet/P&L standar dengan `group_by_dimension` untuk tampilan internal (layout per root type, tanpa pos PSAK dan tanpa agregasi Infak Terikat + Tidak Terikat).
- Template mengikuti struktur "Account Category", sehingga CoA Indonesia perlu diberi kategori akun agar laporan terbaca benar. DUGAAN.

---

## 5. Payment Gateway / Payment Request / Payment Entry (Midtrans, Winpay)

- `Payment Gateway Account` (`accounts/doctype/payment_gateway_account/`): `payment_gateway` (Link ke DocType `Payment Gateway`), `payment_account` (Link Account), `currency`, `company`, `payment_channel`, `is_default`, template pesan. **DocType `Payment Gateway` sendiri tidak ada di image**, karena berada di app terpisah `frappe/payments` (README repo: modul "Payments" dan "Payment Gateways"; https://github.com/frappe/payments). Image v16 hanya berisi `frappe` dan `erpnext`. TERVERIFIKASI untuk isi image; hubungan dengan app payments TERVERIFIKASI dari repo (hasil pencarian), tetapi apakah app payments v16 dipasang default di instalasi Docker kita DUGAAN.
- `Payment Request` (`accounts/doctype/payment_request/`): `payment_gateway_account`, `payment_url`, `status`, `grand_total`, `party_type/party`, `reference_doctype/name`, `cost_center`, `project`, `payment_account`; metode `on_payment_authorized` (payment_request.py baris 450) memicu pembuatan Payment Entry. TERVERIFIKASI. Alur ini dirancang untuk invoice (Sales Invoice/Sales Order dst.), `reference_doctype` Journal Entry tidak otomatis cocok. DUGAAN.
- **Midtrans/Winpay**: tidak ditemukan app Frappe/ERPNext resmi untuk keduanya (pencarian web; hasil hanya plugin Magento/WooCommerce/Odoo dll.). Midtrans menyediakan Snap API (token di server memakai server key, sandbox `app.sandbox.midtrans.com/snap/v1/transactions`; https://docs.midtrans.com/en/snap/integration-guide ; https://snap-docs.midtrans.com). TIDAK DITEMUKAN app siap pakai; jalur realistis adalah integrasi custom (endpoint `@frappe.whitelist(allow_guest=True)` untuk webhook, verifikasi signature, lalu buat jurnal).
- **Akun clearing**: `Payment Gateway Account.payment_account` menunjuk satu akun (tipe Bank/Cash). Pola aman: akun aset "Kas di Midtrans (Clearing)" bertipe Bank. Donasi sukses = Dr Clearing, Cr Pendapatan/Dana (dengan dimensi Dana). Settlement = Dr Bank, Cr Clearing (Journal Entry atau Payment Entry tipe Internal Transfer); biaya gateway = Dr Beban, Cr Clearing. DUGAAN (desain, bukan fitur tertentu).
- `Payment Entry` memerlukan pihak (party) untuk tipe Receive/Pay biasa: TERVERIFIKASI (`payment_entry.py` baris ~625 "Party Type is mandatory"; koreksi 2026-11-22). Untuk donasi tanpa piutang, **Journal Entry langsung lebih sederhana**. Konsekuensi yang harus dicatat: JE tidak memberi alokasi, Payment Ledger Entry, maupun tautan ke Payment Request, sehingga `payment_url`/status Payment Request tidak dapat dipakai; semua integrasi gateway adalah kode kustom penuh.

---

## 6. Modul Non Profit / Donation / Donor di v16

- **Tidak ada di ERPNext v16.** Patch `patches/v13_0/non_profit_deprecation_warning.py` mencetak peringatan bahwa Non Profit Domain pindah ke app terpisah `https://github.com/frappe/non_profit` dan akan dihapus di v14. Patch `patches/v14_0/delete_non_profit_doctypes.py` menghapus Module Def "Non Profit", workspace, print format (80G), report, dashboard, dan semua DocType modul tersebut (termasuk "Tax Exemption 80G Certificate"). `hooks.py` tidak memuat referensi non_profit/donation. Di image hanya sisa fixture grup customer bernama "Non Profit" (`setup/setup_wizard/operations/install_fixtures.py` baris 187). TERVERIFIKASI.
- App terpisah `frappe/non_profit`: repositori **diarsipkan pemiliknya pada 31 Juli 2025 (read-only)**, dokumentasi menautkan v14. Tidak ada klaim kompatibilitas v16. TERVERIFIKASI untuk status arsip (halaman GitHub dibaca); isi DocType Donation/Donor tidak saya baca di repo. Kesimpulan: jangan bergantung padanya; fitur 80G-nya khusus India dan tidak berkaitan dengan PSAK 109. Bangun DocType `Donation` custom sendiri. DUGAAN untuk alasan "tidak berkaitan", fakta pengarsipan terverifikasi.

---

## 7. Journal Entry otomatis dari DocType Donation custom dan idempotensi

- `Journal Entry` (`accounts/doctype/journal_entry/journal_entry.json`): penamaan `naming_series` (`ACC-JV-.YYYY.-`), field `voucher_type`, `posting_date`, `user_remark`, `cheque_no`, `bill_no`, `is_opening`, `reversal_of`, `multi_currency`, `title`; baris `Journal Entry Account`: `account`, `cost_center`, `project`, `party_type`, `debit_in_account_currency`, `credit_in_account_currency`, `reference_type` (opsi termasuk Journal Entry, Payment Entry; **tidak** ada DocType custom), plus kolom dimensi dinamis. TERVERIFIKASI.
- **Tidak ada constraint unik bawaan** pada JE (tidak ada `"unique": 1` di JSON; `bill_no`/`cheque_no` hanya Data biasa). Artinya panggilan ganda (webhook Midtrans yang dikirim ulang, retry job) akan membuat jurnal ganda kecuali kita menjaga idempotensi sendiri. TERVERIFIKASI (tidak ada unique), konsekuensinya DUGAAN-kuat.
- Pola idempotensi yang disarankan (desain):
  1. Tambah Custom Field `donation_ref` (Data, **unique**, read-only) di `Journal Entry` -> indeks unik di DB; isi dengan ID donasi + jenis peristiwa (mis. `DON-2026-0001:RECEIPT`, `...:SETTLEMENT`, `...:FEE`).
  2. Kunci unik pada Donation: `gateway_order_id` / `transaction_id` Midtrans, dan status mesin (Pending -> Paid -> Posted) yang hanya bisa maju.
  3. Di kode: ambil lock baris Donation (`frappe.db.get_value(..., for_update=True)`), cek `frappe.db.exists("Journal Entry", {"donation_ref": key})`, baru `insert()` + `submit()`; tangkap `frappe.UniqueValidationError` sebagai tanda sudah diproses (aman diabaikan).
  4. Pembatalan/refund lewat JE pembalik (field `reversal_of` ada) atau cancel JE asli, bukan edit.
- Mekanisme pemicu: hook `doc_events` di custom app (`on_submit`/webhook handler) atau Server Script bawaan Frappe. Untuk logika transaksi keuangan, **custom app + Python + test** lebih aman daripada Server Script (kemampuan Server Script di v16 dan apakah aktif secara default tidak saya verifikasi). DUGAAN.
- Dimensi harus diisi eksplisit pada setiap baris JE (nama field dimensi mengikuti `fieldname` Accounting Dimension, mis. `dana`). Bila mandatory aktif, JE tanpa dimensi ditolak (bagian 1), jadi kegagalan akan terlihat, bukan diam-diam salah.

---

## 8. Fiscal year, periode, dan penutupan

- `Fiscal Year` (`accounts/doctype/fiscal_year/`): `year` (nama), `year_start_date`, `year_end_date`, `disabled`; validasi tanggal dan **tumpang tindih** (`validate_dates`, `validate_overlap` di fiscal_year.py). Tabel `Fiscal Year Company` membatasi per company. Tahun buku tidak harus kalender (bebas). TERVERIFIKASI.
- `Accounting Period` + `Closed Document` (`accounts/doctype/accounting_period/`): `period_name`, `start_date`, `end_date`, `company`, `closed_documents` (jenis dokumen yang ditutup), `exempted_role`. `general_ledger.py` (baris ~161-185) menolak posting/cancel di periode tertutup: "You cannot create or cancel any accounting entries with in the closed Accounting Period". Ini mekanisme kunci bulanan. TERVERIFIKASI.
- `Period Closing Voucher` (dan `Process Period Closing Voucher` baru di v16): menutup laba rugi ke akun Liability/Equity, **memperhitungkan dimensi** (bagian 1). Koreksi 2026-11-22: pengaturan "frozen up to" tidak ada di `Accounts Settings` karena di v16 sudah dipindah ke **Company** (`accounts_frozen_till_date`, `role_allowed_for_frozen_entries`; dicek di `general_ledger.py` baris ~852; patch `v16_0/migrate_account_freezing_settings_to_company`). TERVERIFIKASI keberadaan. Catatan penting: `Accounting Period` hanya mengunci jenis dokumen yang tercantum di tabel `closed_documents` (`accounting_period.py`), bukan semua posting GL; masukkan `Journal Entry` (dan `Period Closing Voucher`) lalu uji penolakan posting.
- Implikasi PSAK: laporan aktivitas per periode berjalan dari `Period Movement` GL; penutupan tahunan memindahkan surplus tiap dana ke aset neto dana itu sendiri berkat per-dimensi PCV. Hal yang tidak dijamin: akun penutup tunggal dipakai untuk semua dana, perbedaan dana hanya lewat dimensi, jadi laporan neraca per dana harus dibaca dengan `group_by_dimension`.

---

## 9. Lokalisasi Indonesia

- **CoA Indonesia bawaan ada:** `accounts/doctype/account/chart_of_accounts/verified/id_chart_of_accounts.json` ("Indonesia - Chart of Accounts", country_code `id`). Struktur akar: Aktiva (Asset: Aktiva Lancar, Aktiva Tetap), Beban (Expense: Beban Lain-lain, Beban Langsung, Beban Tidak Langsung, Biaya Amortisasi, Biaya Penyusutan), Modal (Equity: Laba, Modal), Passiva (Liability: Pasiva Lancar, Passiva Tetap), Penjualan (Income: Harga Pokok Pembelian, Pendapatan Lain-lain, Pendapatan Service/Jasa, Penjualan Barang Dagangan). TERVERIFIKASI. Ini CoA **komersial**, bukan akun zakat/PSAK 109; perlu dibuat CoA kustom (atau "Existing Company"/CoA mulai kosong lalu impor). Mekanisme CoA kustom: file di `chart_of_accounts/` dimuat oleh `chart_of_accounts.py`; juga bisa impor lewat Data Import atau dibuat dengan script saat membuat Company. DUGAAN untuk detail cara.
- **Bahasa**: terjemahan Indonesia ada, `erpnext/erpnext/locale/id.po` (11.590 baris berisi `msgid`) dan `frappe/frappe/locale/id.po`. Cakupan/kualitas terjemahan tidak diperiksa. TERVERIFIKASI keberadaan.
- **Mata uang**: `frappe/frappe/geo/country_info.json` entri Indonesia: kode `id`, mata uang **IDR**, nama "Rupiah", simbol "Rp", fraksi "Sen" (100), `number_format` `#.###,##`, zona waktu Asia/Jakarta, Makassar, Jayapura, Pontianak. TERVERIFIKASI. Rekomendasi (DUGAAN): atur presisi mata uang 0 desimal agar sen tidak muncul di laporan.
- Folder `erpnext/regional/` hanya berisi australia, italy, south_africa, turkey, united_arab_emirates, united_states. **Tidak ada regional Indonesia** (tidak ada pajak/faktur/laporan lokal Indonesia di image). TERVERIFIKASI.

---

## 10. Rekomendasi: pola paling sederhana yang aman

1. **Satu Company** (IDR). Tahun buku Jan-Des (atau sesuai kebijakan), kunci bulanan dengan Accounting Period.
2. **Satu Accounting Dimension "Dana"** (DocType `Dana`: Zakat, Infak Terikat, Infak Tidak Terikat, Amil, Nonhalal), `mandatory_for_bs` dan `mandatory_for_pl` **dicentang**. Pakai Accounting Dimension Filter untuk membatasi akun pendapatan tertentu ke dana tertentu. Setelah dimensi dibuat, setiap JE tanpa "Dana" ditolak.
3. **CoA kustom ringkas** berbasis kategori PSAK: Aset (Kas/Bank, Clearing Gateway, Piutang Penyaluran), Liabilitas (Liabilitas Penyaluran Zakat, Penyaluran Infak/Sedekah), Aset Neto (Equity, satu akun penutup per jenis), Pendapatan (penerimaan zakat, infak/sedekah terikat/tidak terikat, hasil pengelolaan, nonhalal), Beban (penyaluran, bagian amil, operasional). Beri `Account Category` supaya Financial Report Template bisa memakainya.
4. **Pencatatan lewat Journal Entry langsung** (bukan Sales Invoice/Payment Entry), dibuat otomatis dari DocType `Donation` custom, dengan custom field `donation_ref` unik (bagian 7). Bagian amil (mis. persentase dari zakat) dicatat sebagai JE terpisah dengan dua baris dimensi yang berbeda (Dana=Zakat keluar, Dana=Amil masuk), seimbang dan eksplisit.
5. **Akun clearing gateway** satu per gateway (Midtrans, Winpay): donasi sukses -> Clearing; settlement -> bank; biaya -> beban. Webhook = endpoint custom, tanda tangan diverifikasi, idempoten.
6. **Laporan**: Balance Sheet / Profit and Loss / Cash Flow standar dengan `group_by_dimension = Dana` hanya untuk tampilan internal. Laporan aktivitas/posisi keuangan resmi: Financial Report Template dijalankan per nilai Dana (filter dimensi) lalu digabung, atau Script Report kustom (koreksi 2026-11-22: template tidak mendukung `group_by_dimension`). Agregasi Infak (Terikat + Tidak Terikat) di lapisan penggabung.
7. **Tutup tahun** dengan Period Closing Voucher (per-dimensi), akun penutup bertipe Equity.
8. **Jangan** memakai app Non Profit (diarsipkan, v14), **jangan** memakai Company terpisah per dana, **jangan** memakai Cost Center sebagai pengganti Dana.

### Hal yang wajib diuji sebelum dipakai (belum diuji)
- Accounting Dimension Filter pada JE multi-dimensi (perilaku Allow/Restrict sudah terbaca dari kode; uji end-to-end belum).
- `automatically_post_balancing_accounting_entry`: sudah terjawab dari kode, **dinonaktifkan** (menyalin setiap GL Entry; bukan penyeimbang per Dana).
- ~~`group_by_dimension` pada template kustom~~ sudah terjawab: TIDAK didukung (engine baris ~273-278).
- Accounting Period dengan `closed_documents` Journal Entry dan `accounts_frozen_till_date` pada Company; Asset depreciation, Payroll, dan jurnal opening dengan dimensi Dana mandatory.
- Hasil Period Closing Voucher dengan lima nilai dimensi.
- Keberadaan/versi app `payments` di instalasi target dan apakah diperlukan.
- Konfirmasi final dengan auditor: dana nonhalal, penyajian infak terikat/tidak terikat, dan tanggal efektif PSAK 409/401.

---

## Daftar sumber

- IAI, Perubahan Penomoran PSAK dan ISAK: https://web.iaiglobal.or.id/assets/files/file_publikasi/Perubahan_Penomoran_PSAK_ISAK_dalam_SAK_Indonesia.pdf
- IAI, Komparasi Penomoran: https://web.iaiglobal.or.id/assets/files/file_publikasi/Komparasi%20Perubahan%20Penomoran%20PSAK%20ISAK%20SAK%20Indonesia_FINAL.pdf
- IAI, DE PSAK 101 dan PSAK 109 Revisi 2021: https://web.iaiglobal.or.id/assets/files/file_berita/DE%20PSAK%20101%20dan%20DE%20PSAK%20109%20Revisi%202021.pdf
- Jurnal.id, PSAK 109 dalam Laporan Keuangan (sekunder): https://www.jurnal.id/id/blog/psak-109-dalam-laporan-keuangan/
- Salinan ED PSAK 109 versi lama (2008): https://idr.uin-antasari.ac.id/11349/10/LAMPIRAN.pdf
- Jamak UNG (konflik tanggal 2025): https://jamak.fe.ung.ac.id/index.php/jamak/article/download/494/201/
- Frappe docs, Accounting Dimensions: https://docs.frappe.io/erpnext/user/manual/en/accounting-dimensions
- Frappe non_profit (arsip): https://github.com/frappe/non_profit
- Frappe payments: https://github.com/frappe/payments
- Midtrans Snap: https://docs.midtrans.com/en/snap/integration-guide ; https://snap-docs.midtrans.com
- Kode sumber: image `frappe/erpnext:version-16` (erpnext 16.56.0), path `/home/frappe/frappe-bench/apps/erpnext/erpnext/...` seperti dirinci di tiap bagian.
