# 05 - Rancangan Akun, Dimensi, dan Katalog Jurnal Otomatis (USULAN)

Tanggal: 2026-11-22. Disusun hanya dari berkas riset 01-04 di folder ini.

## 0. Cara membaca

- Semua keputusan desain di dokumen ini berstatus **USULAN** kecuali dikutip sebagai fakta riset dengan rujukan berkas (01, 02, 03, 04) dan bagian.
- Label keyakinan mengikuti riset: TERVERIFIKASI, DUGAAN, INTERPRETASI. Label konfirmasi: `[AKUNTAN]`, `[SYARIAH]`, `[PAJAK/HUKUM]`.
- Rujukan standar memakai nomor baru dengan nomor lama: PSAK 409 (dahulu PSAK 109), PSAK 401 (dahulu PSAK 101), PSAK 412 (dahulu PSAK 112), ISAK 335 (dahulu ISAK 35). Jangan menulis "PSAK 109" polos: nomor itu sejak 1 Jan 2024 adalah Instrumen Keuangan (01 bagian 1).
- Batas riset yang mempengaruhi semua isi di bawah: teks final PSAK 409 dan PSAK 401 (Lampiran C) tidak terbaca; dasarnya Draf Eksposur (DE) Revisi 2021 (01 bagian 0, 02 bagian 12). Nama pos dan nomor paragraf adalah dari DE.
- **Penomoran rujukan.** "01"-"04" di dokumen ini = berkas riset di folder ini (`docs/psak/01..04`), BUKAN berkas handover Frappe. Rujukan ke handover ditulis **HF-0x** = `donasi-eco3/docs/handover-frappe/0x-*.md` (HF-03 = Doctype dan field; HF-04 = alur kunci). Contoh: "04 bag. 5" = kapabilitas ERPNext; "HF-04" = alur kunci platform.
- Nama status DocType `Donation` di kolom "Pemicu" (Pending, Paid, Posted, Settled, dst.) adalah **nama USULAN internal**. Skema Donation platform ada di HF-03 bag. 3 (status huruf kecil: pending, paid, failed, expired, refunded). Pemetaan di bagian H.3; `Posted`/`Settled` bukan status Donation di HF-03 melainkan penanda baru (H.3).
- Yang TERVERIFIKASI dari image: ERPNext v16.56.0, tanpa modul Non Profit, tanpa app payments/Midtrans/Winpay (04 bagian 0, 5, 6). Rancangan jurnal lewat Journal Entry (JE) dari DocType `Donation` custom adalah USULAN. Hal yang **belum teruji** (hanya desain/DUGAAN, 04): perilaku akun clearing bertipe Bank, presisi mata uang 0 desimal, Accounting Dimension Filter pada JE multi-Dana, PCV dengan banyak nilai Dana. Hasil verifikasi ulang kode pada 2026-11-22 dicatat di bagian I.
- **Model peran platform (F1) dan data platform (HF-03) belum terpenuhi.** Seluruh katalog E2-E7 berlaku hanya untuk model A (platform = amil/penyelenggara PUB berizin) dan hanya bila prasyarat data di bagian H tersedia. Jangan mengaktifkan posting otomatis sebelum gerbang di H.1 lulus.

## A. Prinsip desain

| # | Prinsip (USULAN) | Dasar riset |
|---|---|---|
| A1 | **Dana terpisah dan tidak boleh tercampur**: Zakat, Infak/Sedekah Tidak Terikat, Infak/Sedekah Terikat (per program/campaign), Dana Amil, Dana Nonhalal. Wakaf hanya jika masuk ruang lingkup (A9). | Aset neto amil = dana zakat, dana infak dan sedekah, dana amil (01 bag. 3.3, 02 bag. 8). UU 23/2011 Pasal 28: infak/sedekah/DSKL dicatat dalam pembukuan tersendiri dan dipakai sesuai peruntukan ikrar (03 R1). Perbaznas 5/2018 Pasal 19: rekapitulasi terpisah per jenis dana (03 R5). |
| A2 | **Dana ZIS adalah aset neto, bukan liabilitas.** Dana yang sudah diterima tapi belum disalurkan tetap saldo dana, tanpa jurnal tambahan. | DK40-DK42 DE (01 bag. 3.3, 10.5a). |
| A3 | **Pengakuan penerimaan saat amil menerima aset**, nominal untuk kas. Donasi yang masih Pending (belum dibayar) tidak diakui. | DE para 08 dan 19 (01 bag. 3.1-3.2). Pending tanpa jurnal = INTERPRETASI. |
| A4 | **Penerimaan diakui bruto** (jumlah yang dibayar donatur). Biaya gateway = beban **Dana Amil**, tidak mengurangi penerimaan dana zakat/infak. Penerimaan neto setelah fee **tidak disarankan**. Konsekuensi: Dana Amil menanggung fee padahal kas awalnya milik dana sumber; lihat E4 (aturan saldo kas Dana Amil, tidak boleh negatif). | 01 bag. 9 butir 1, 2, 5 (INTERPRETASI; tidak ada ketentuan eksplisit). `[AKUNTAN]` `[SYARIAH]` |
| A5 | **Bagian amil adalah pasangan jurnal antar dana**: beban penyaluran ke amil di dana sumber, penghasilan bagian amil di Dana Amil. Persentase adalah parameter kebijakan, bukan rumus bawaan standar. **Sumber batas saling bertentangan antar berkas riset:** 03 R3 menyatakan 12,5% (zakat) dan 20% TERVERIFIKASI di Perbaznas 1/2016 Pasal 8 (pedoman RKAT BAZNAS; berlaku untuk LAZ swasta belum pasti), sedangkan 01 bag. 4.2 menyebut 12,5% bersumber Fatwa MUI 8/2011 (bukan UU) dan 20% hanya **DUGAAN, tidak ditemukan di regulasi yang dibaca 01**. Bobot: teks Perbaznas 1/2016 dibaca langsung di 03, tetapi berlakunya bagi LAZ swasta tidak pasti; konflik ini belum terselesaikan (F6). **20% bukan tarif hak amil infak**: menurut 03 R3 itu plafon biaya operasional subsider dari infak/sedekah/DSKL bila bagian amil zakat tidak cukup. | DE PSAK 101 C04 (01 bag. 4.1); 03 R3; 01 bag. 4.2. |
| A6 | **Penyaluran diakui beban saat diterima mustahik/penerima manfaat**, bukan saat transfer keluar. Penyaluran tidak langsung lewat pihak lain: piutang penyaluran dulu. | DE para 13-14, 25-26 (01 bag. 5, 10.4). |
| A7 | **Infak terikat (muqayyadah) tidak boleh dipakai di luar peruntukan**; kampanye/program wajib pada tiap penerimaan dan penyaluran infak terikat. Larangan hak amil atas zakat muqayyadah hanya **USULAN default blokir, menunggu F10** (01 bag. 4.2: DUGAAN dari artikel sekunder; sumber yang sama menyebut amil boleh meminta biaya operasional ke muzaki). | UU 23/2011 Pasal 28 (03 R1); 01 bag. 4.2 (DUGAAN). |
| A8 | **Pemisahan operator platform dan dana ZIS**: fee/jasa platform dan titipan pihak ketiga bukan penerimaan dana ZIS. | 01 bag. 9 butir 7; 03 bag. 3 model A/B/C dan S5. Model peran (A/B/C) belum diputuskan (F1); **katalog D mengasumsikan model A** (dana langsung jadi dana ZIS milik platform sebagai amil/penyelenggara PUB berizin). Di model B (agen kanal) semua penerimaan menjadi titipan/liabilitas dan fee = pendapatan platform (03 bag. 3); di entitas PUB non-amil berlaku ISAK 335, bukan PSAK 409 (01 bag. 2; 03 S2; 02 bag. 1.3), sehingga pos infak terikat/Dana Infak tidak otomatis berlaku. Gerbang: lihat H.1. |
| A9 | **Wakaf dalam ruang lingkup bersyarat**: bila dicakup, buku wakaf entitas pelaporan terpisah, tidak dikonsolidasi, wakaf uang temporer = liabilitas, imbalan nazhir berbasis hasil neto kas. Sampai diputuskan, wakaf hanya disiapkan sebagai nilai dimensi dan akun placeholder. | PSAK 412 DE 2018 (03 S3). |
| A10 | **Qurban = liabilitas titipan, bukan pendapatan, dan jurnal penutupnya ditunda** sampai akuntan/ahli syariah memutuskan. | 03 S6 dan F4 (DUGAAN; tidak ada standar). |
| A11 | **Tidak ada edit transaksi terposting.** Koreksi lewat jurnal pembalik atau pembatalan; periode dikunci dengan Accounting Period (hanya untuk jenis dokumen yang dicantumkan di `closed_documents`, lihat E16) dan/atau `accounts_frozen_till_date` per Company. `reversal_of` hanya untuk pembalikan penuh satu kali (D0). | 04 bag. 7-8; PP 14/2014 audit (03 R2). |
| A12 | **Jurnal langsung (Journal Entry) dari DocType Donation**, bukan Sales Invoice/Payment Entry; satu Company, IDR. Payment Entry diverifikasi mewajibkan Party Type untuk Receive/Pay biasa (`payment_entry.py` baris ~625), jadi tidak cocok untuk donasi tanpa invoice. Konsekuensi yang harus diterima: JE tidak memberi alokasi, Payment Ledger Entry, maupun tautan Payment Request; `Payment Request`/`Payment Gateway Account` tidak dipakai, dan seluruh integrasi gateway (webhook, token Snap, status, `payment_url`) adalah kode kustom penuh. Dimensi Dana mandatory memaksa SEMUA sumber GL membawa Dana (lihat C4). | 04 bag. 5, 7, 10. |
| A13 | **Aset neto dimodelkan di akun Equity; pemisahan dana lewat Accounting Dimension "Dana"** (opsi A di 04 bag. 3), bukan akun aset neto per dana. | 04 bag. 3, 10. |

## B. Usulan Chart of Accounts (CoA) bertingkat

Aturan ERPNext: root type hanya Asset, Liability, Equity, Income, Expense; tidak ada root "Aset Neto"/"Fund" (04 bag. 3). Mulai dari CoA kustom, bukan CoA Indonesia bawaan yang komersial (04 bag. 9). Beri `Account Category` supaya template laporan bisa memilih akun (04 bag. 4). Penomoran di bawah USULAN (format `X-YZZZ`, induk berakhiran 000).

Kolom "Tipe" = `account_type` ERPNext (daftar resmi; tidak ada tipe "receivable tanpa party"). **Jangan memakai Receivable/Payable** untuk akun tanpa party: `journal_entry.validate_party` (baris ~627-640) mewajibkan Party Type dan Party pada akun bertipe Receivable/Payable, dan flag `party_not_required` khusus Payroll. Akun piutang penyaluran memakai tipe kosong atau Current Asset (TERVERIFIKASI dari kode; uji sebelum dikunci).

Kolom "Pos PSAK" = pos di laporan posisi keuangan (C03) atau laporan aktivitas (C04) DE PSAK 101 Lampiran C (02 bag. 5, 11). `G` = grup (tidak diposting). Dimensi Dana yang berlaku diuraikan di bagian C.

### B1. Aset (Root: Asset, laporan Balance Sheet)

| No | Nama akun | Tipe | Root ERPNext | Pos PSAK |
|---|---|---|---|---|
| 1-0000 | ASET | G | Asset | Aset |
| 1-1000 | Aset Lancar | G | Asset | Aset Lancar |
| 1-1100 | Kas dan Setara Kas | G | Asset | Kas dan setara kas |
| 1-1101 | Bank Operasional (kas dana ZIS) | Bank | Asset | Kas dan setara kas |
| 1-1110 | Clearing Gateway - Midtrans (dana ZIS) | Bank | Asset | PROVISIONAL: Kas dan setara kas atau piutang kanal (F7; 01 bag. 9 butir 1 dan 04 bag. 5 berbeda, belum diputuskan) |
| 1-1120 | Clearing Gateway - Winpay (dana ZIS) | Bank | Asset | idem (F7) |
| 1-1130 | Clearing Kanal Lain (retail, kartu kredit; USULAN, bergantung H.2 dan F27) | Bank | Asset | idem (F7) |
| 1-1150 | Kas Pihak Ketiga (grup; dikecualikan dari kas dana ZIS, A8) | G | Asset | Tidak diatur DE; disajikan terpisah |
| 1-1102 | Bank Titipan (rekening/sub-akun terpisah untuk titipan donatur, qurban, wakaf) | Bank | Asset | Kas pihak ketiga, bukan kas dana ZIS |
| 1-1115 | Clearing Titipan (gateway) | Bank | Asset | Kas pihak ketiga |
| 1-1190 | Kas Valas (jika ada; bergantung F19) | Cash | Asset | Kas dan setara kas |
| 1-1200 | Piutang Penyaluran Zakat | (kosong atau Current Asset; bukan Receivable) | Asset | Piutang penyaluran zakat |
| 1-1210 | Piutang Penyaluran Infak dan Sedekah | idem | Asset | Piutang penyaluran infak dan sedekah |
| 1-1220 | Al-Qardh Al-Hasan | idem | Asset | Al-qardh al-hasan |
| 1-1400 | Piutang Antar-Dana (dimensi Dana = dana pemberi pinjaman; USULAN, F5/F28) | Current Asset | Asset | Eliminasi/pengungkapan; tidak disajikan sebagai aset neto dana lain |
| 1-1300 | Aset Zakat/Infak Nonkas (emas, saham, persediaan) | G | Asset | (rincian aset zakat/infak, CaLK) |
| 1-2000 | Aset Tidak Lancar | G | Asset | Aset Tidak Lancar |
| 1-2100 | Aset Tetap (milik amil) | G | Asset | Aset tetap |
| 1-2150 | Akumulasi Penyusutan Aset Tetap | Accumulated Depreciation | Asset | Aset tetap |
| 1-2200 | Aset Takberwujud | | Asset | Aset takberwujud |
| 1-2300 | Aset Kelolaan | G | Asset | Aset kelolaan |
| 1-2350 | Akumulasi Penyusutan Aset Kelolaan | Accumulated Depreciation | Asset | Aset kelolaan |

Catatan: jurnal untuk 1-1300, 1-2100/2150/2200, 1-2300/2350 ada di E17 (draf, ditunda; F18); akun tanpa jurnal bertanda "tahap 2" tidak boleh dipakai bebas. Akun clearing dan kas titipan: lihat A8, E5, dan F25. Catatan: aset kelolaan diukur model biaya, beban penyaluran hanya sebesar penyusutan bila dikendalikan amil (01 bag. 6). Model revaluasi tidak diizinkan.

### B2. Liabilitas (Root: Liability)

| No | Nama akun | Root | Pos PSAK |
|---|---|---|---|
| 2-0000 | LIABILITAS | Liability | Liabilitas |
| 2-1000 | Liabilitas Jangka Pendek | Liability | Liabilitas Jangka Pendek |
| 2-1100 | Liabilitas Penyaluran Zakat | Liability | Liabilitas penyaluran zakat |
| 2-1200 | Liabilitas Penyaluran Infak dan Sedekah | Liability | Liabilitas penyaluran infak dan sedekah |
| 2-1300 | Titipan Zakat Penghasilan di Muka (belum terklasifikasi) | Liability | Tidak diatur DE (DK13-DK17 menegaskan liabilitas; 01 bag. 10.5c); pos tambahan ("tidak terbatas pada"). Hanya untuk E8; fee TIDAK memakai akun ini. |
| 2-1340 | Titipan Biaya Kanal Ditanggung Donatur | Liability | idem; INTERPRETASI (E4) |
| 2-1360 | Titipan Sponsor Pool Jalan Kebaikan (USULAN; E18, F22) | Liability | idem; INTERPRETASI |
| 2-1350 | Selisih Bayar Donatur (kurang/lebih bayar, kode unik) | Liability | idem; INTERPRETASI (E19) |
| 2-1500 | Utang Antar-Dana (dimensi Dana = dana peminjam; USULAN, F5/F28) | Liability | Eliminasi/pengungkapan |
| 2-1310 | Titipan Qurban | Liability | idem; INTERPRETASI |
| 2-1320 | Utang Refund Donatur | Liability | idem |
| 2-1330 | Titipan Wakaf Uang (belum diteruskan ke nazhir/LKS-PWU) | Liability | idem; bersyarat A9 |
| 2-1400 | Utang Pajak dan Utang Lain (kode pajak, lihat F11) | Liability | idem |
| 2-2000 | Liabilitas Jangka Panjang | Liability | Liabilitas Jangka Panjang |
| 2-2100 | Liabilitas Imbalan Kerja | Liability | Liabilitas imbalan kerja |

### B3. Aset Neto (Root: Equity)

Hanya dibedakan lewat dimensi Dana (A13). Akun penutup Period Closing Voucher harus bertipe Equity atau Liability (04 bag. 1, 3).

| No | Nama akun | Root | Pos PSAK |
|---|---|---|---|
| 3-0000 | ASET NETO | Equity | Aset neto |
| 3-1000 | Saldo Dana (akun penutup periode; dimensi Dana membedakan) | Equity | Dana zakat; Dana infak dan sedekah; Dana amil (agregasi per Dana) |
| 3-2000 | Saldo Awal / Penyesuaian Dana (migrasi, koreksi tahun lalu) | Equity | idem |

Dana Nonhalal dan Wakaf tidak muncul di daftar pos aset neto C03 DE (hanya tiga dana); **tidak ikut total aset neto L1**, disajikan sebagai pos terpisah/pengungkapan sampai ada keputusan (F2, F4; lihat L1).

**Klasifikasi pembatasan aset neto (01 bag. 3.3, DK39):** dalam kerangka nirlaba, dana zakat dan dana infak/sedekah = aset neto DENGAN pembatasan; hanya dana amil = tanpa pembatasan. Pembedaan terikat/tidak terikat (INFAK-T / INFAK-TT) hanya pada **penghasilan dan beban** di laporan aktivitas (C04(e)(f)), bukan klasifikasi aset neto; 02 bag. 8 menegaskan struktur amil adalah tiga dana, bukan terikat/tidak terikat ala ISAK 335. Akun 3-1000/3-2000 tidak membedakan ini; label "Tidak Terikat" pada INFAK-TT berarti "penghasilan tanpa pembatasan (mutlaqah)", BUKAN aset neto tanpa pembatasan.

### B4. Penghasilan (Root: Income, laporan Profit and Loss)

| No | Nama akun | Dana yang diperbolehkan | Pos laporan aktivitas |
|---|---|---|---|
| 4-0000 | PENGHASILAN | G | |
| 4-1000 | Penerimaan Zakat | G | Dana Zakat: Penghasilan |
| 4-1100 | Penerimaan Zakat - Muzaki Pribadi | ZAKAT | Penerimaan zakat dari muzaki pribadi |
| 4-1200 | Penerimaan Zakat - Muzaki Perusahaan | ZAKAT | Penerimaan zakat dari muzaki perusahaan |
| 4-1900 | Dampak Pengukuran Ulang Aset Zakat | ZAKAT | Dampak pengukuran ulang aset zakat |
| 4-2000 | Penerimaan Infak dan Sedekah | G | Dana Infak dan Sedekah: Penghasilan |
| 4-2100 | Infak dan Sedekah Tanpa Pembatasan (mutlaqah) | INFAK-TT | Infak dan sedekah tanpa pembatasan |
| 4-2200 | Infak dan Sedekah Dengan Pembatasan (muqayyadah) | INFAK-T | Infak dan sedekah dengan pembatasan |
| 4-2900 | Hasil Pengelolaan Aset Infak dan Sedekah | INFAK-TT / INFAK-T | Hasil pengelolaan aset infak dan sedekah |
| 4-2950 | Dampak Pengukuran Ulang Aset Infak dan Sedekah | INFAK-TT / INFAK-T | Dampak pengukuran ulang aset infak dan sedekah |
| 4-3000 | Penghasilan Dana Amil | G | Dana Amil: Penghasilan |
| 4-3100 | Bagian Amil dari Penerimaan Zakat | AMIL | Bagian amil dari penerimaan zakat |
| 4-3200 | Bagian Amil dari Penerimaan Infak dan Sedekah | AMIL | Bagian amil dari penerimaan infak dan sedekah |
| 4-3900 | Penghasilan Lain Dana Amil (termasuk sedekah jasa/diskon konsesi untuk amil, ujrah) | AMIL | Penghasilan lain |
| 4-4000 | Penerimaan Dana Nonhalal (jasa giro, dll) | NONHALAL | tidak ada di DE; pengungkapan (para 18(b), 33(c)); USULAN |
| 4-5000 | Penerimaan Wakaf (placeholder; bersyarat A9) | WAKAF | PSAK 412 |

Akun yang diizinkan untuk dua Dana (4-2900, 4-2950, 5-2300, 5-2400, 5-2900) wajib didaftarkan ke Accounting Dimension Filter mode Allow dengan kedua nilai (C1 butir 5). Akun fee jasa platform (pendapatan operator) tidak dimuat di sini; bila platform adalah entitas terpisah, fee dicatat di pembukuan entitas itu (A8, F1).

### B5. Beban (Root: Expense)

| No | Nama akun | Dana | Pos laporan aktivitas |
|---|---|---|---|
| 5-0000 | BEBAN | G | |
| 5-1000 | Penyaluran Zakat | G | Dana Zakat: Beban |
| 5-1100 | Penyaluran Zakat - Amil | ZAKAT | Amil |
| 5-1110 | Penyaluran Zakat - Fakir | ZAKAT | Fakir |
| 5-1120 | Penyaluran Zakat - Miskin | ZAKAT | Miskin |
| 5-1130 | Penyaluran Zakat - Riqab | ZAKAT | Riqab |
| 5-1140 | Penyaluran Zakat - Gharim | ZAKAT | Gharim |
| 5-1150 | Penyaluran Zakat - Muallaf | ZAKAT | Muallaf |
| 5-1160 | Penyaluran Zakat - Sabilillah | ZAKAT | Sabilillah |
| 5-1170 | Penyaluran Zakat - Ibnu Sabil | ZAKAT | Ibnu sabil |
| 5-1190 | Selisih Realisasi/Kerugian Aset Zakat (bukan lalai) | ZAKAT | beban dana zakat (para 11-12) |
| 5-2000 | Penyaluran Infak dan Sedekah | G | Dana Infak dan Sedekah: Beban |
| 5-2100 | Penyaluran Infak TT - Kepada Amil | INFAK-TT | Tanpa pembatasan: kepada amil |
| 5-2110 | Penyaluran Infak TT - Kepada Penerima Manfaat | INFAK-TT | Tanpa pembatasan: penerima manfaat |
| 5-2200 | Penyaluran Infak T - Kepada Amil | INFAK-T | Dengan pembatasan: kepada amil |
| 5-2210 | Penyaluran Infak T - Kepada Penerima Manfaat | INFAK-T | Dengan pembatasan: penerima manfaat |
| 5-2300 | Beban Penyusutan Aset Kelolaan (penyaluran) | per dana sumber | beban penyaluran (para 15, 27) |
| 5-2400 | Penghapusan Al-Qardh Al-Hasan (saat hapus tagih) | INFAK-TT / INFAK-T | beban (para 16, 28) |
| 5-2900 | Selisih Realisasi/Kerugian Aset Infak | INFAK | para 23-24 |
| 5-3000 | Beban Dana Amil | G | Dana Amil: Beban |
| 5-3100 | Beban Pegawai | AMIL | Beban pegawai |
| 5-3200 | Beban Biaya Kanal Pembayaran (MDR/fee gateway) | AMIL | Beban lain |
| 5-3300 | Beban Pemasaran/Iklan Penghimpunan (wajar) | AMIL | Beban lain |
| 5-3400 | Beban Penyusutan Aset Tetap Amil | AMIL | Beban lain |
| 5-3500 | Beban Operasional Lain | AMIL | Beban lain |
| 5-3600 | Beban Administrasi Bank dan Biaya Transfer Keluar (USULAN; E17) | AMIL | Beban lain |
| 5-3900 | Kerugian Aset karena Kelalaian Amil | AMIL | para 11, 23 |
| 5-4000 | Penyaluran Dana Nonhalal | NONHALAL | tidak ada di DE; USULAN |
| 5-5000 | Penyaluran/Beban Wakaf (placeholder; bersyarat A9) | WAKAF | PSAK 412 |

Catatan: ERPNext mewajibkan Cost Center pada akun P&L (04 bag. 2); lihat C2. Belum ada akun untuk gaji amil vs bagian amil, hadiah ke muzaki, maupun operasional dari bagian fi sabilillah (03 F1 butir 7-9; 01 bag. 4.2): lihat kontrol di E3 dan F26. 5-3100 (pegawai) dan 5-3300 (pemasaran "wajar") hanya boleh dibiayai dari Dana Amil; pemasaran dari dana zakat diblokir default (E3).

## C. Pola Accounting Dimension

### C1. Dimensi "Dana" (wajib)

- Dibuat sebagai DocType `Dana` + satu Accounting Dimension; `mandatory_for_bs` dan `mandatory_for_pl` dicentang sehingga JE tanpa Dana ditolak (04 bag. 1).
- Nilai (USULAN): `ZAKAT`, `INFAK-TT` (Infak/Sedekah **tanpa pembatasan penghasilan**/mutlaqah), `INFAK-T` (Infak/Sedekah **dengan pembatasan penghasilan**/muqayyadah), `AMIL`, `NONHALAL`, `WAKAF` (bersyarat A9), `TITIPAN` (nilai teknis untuk liabilitas/aset pihak ketiga yang bukan dana ZIS; diperlukan karena mandatory BS berlaku untuk semua akun neraca).
- Label TT/T hanya membedakan **penghasilan/beban** (C04(e)(f)); aset neto dana infak seluruhnya "dengan pembatasan" dan dana amil "tanpa pembatasan" (DK39; lihat B3). Tidak ada nilai/atribut "zakat muqayyadah": bila larangan hak amil atas zakat terikat ingin ditegakkan (F10), tambahkan atribut `restriction` pada Donation (H.2) atau nilai Dana khusus; tanpa itu aturan tidak dapat ditegakkan.
- Alasan:
  1. Pemisahan tiga dana adalah struktur laporan resmi (01 bag. 3.3; 02 bag. 8). Cost Center tidak menjangkau akun neraca, jadi tidak cukup (04 bag. 2).
  2. `group_by_dimension` pada Balance Sheet, Profit and Loss, dan Cash Flow **standar** memberi kolom per Dana, tetapi layout tetap per root type (tanpa pos PSAK, tanpa agregasi INFAK-TT + INFAK-T). **Pada Financial Report Template / Custom Financial Statement `group_by_dimension` TIDAK didukung** (TERVERIFIKASI: `financial_report_engine.py` baris ~273-278 memunculkan "Dimension-based grouping is currently unsupported in Custom Financial Report"; `financial_statements.py` `build_period_list` melewati `get_dimension_period_list` bila `report_template` terisi). Lihat opsi laporan di bagian E.
  3. Period Closing Voucher menutup surplus/defisit per kombinasi dimensi sehingga tiap dana mewarisi saldonya sendiri (04 bag. 1).
  4. Infak terikat/tidak terikat: DE memperlakukan keduanya satu dana dengan dua sub-kategori (04 bag. 0; 02 bag. 8). Dimodelkan sebagai dua nilai dimensi demi keterlacakan, dengan agregasi untuk laporan resmi (laporan "Dana Infak dan Sedekah" = INFAK-TT + INFAK-T; 04 bag. 10 butir 6).
  5. Accounting Dimension Filter dipakai agar akun tertentu hanya boleh dengan Dana tertentu (mis. 4-1100 hanya ZAKAT). Perilaku TERVERIFIKASI dari `general_ledger.validate_allowed_dimensions`: mode **Allow** menolak bila nilai dimensi terisi dan tidak ada di daftar; mode **Restrict** menolak bila nilai ada di daftar; filter hanya berlaku pada akun yang terdaftar di Applicable On Account (satu akun hanya boleh di satu filter per dimensi); dimensi tidak dipaksa terisi kecuali `is_mandatory` pada baris akun (mandatory BS/PL tetap dari C1). Konsekuensi: daftarkan SETIAP akun P&L dan penyaluran ke satu filter Allow; akun lintas dua Dana (4-2900, 4-2950, 5-2300, 5-2400, 5-2900) dimasukkan ke filter yang sama dengan kedua nilai; akun yang tidak terdaftar tidak dibatasi sama sekali. Uji tetap diperlukan pada JE multi-Dana (belum dijalankan).
- Dimensi tidak berlaku retroaktif pada transaksi lama (04 bag. 1); pasang sebelum posting pertama.
- Kontrol: jangan campur nilai dimensi dalam satu baris ke akun yang tidak diizinkan. **ERPNext TIDAK menegakkan keseimbangan per Dana** (D0); validasi sendiri wajib dibuat di kode.

### C2. Program dan Kampanye

- **Cost Center = Program** (pohon Program, mis. Pendidikan, Kesehatan, Palestina). Alasan: ERPNext sudah mewajibkan Cost Center di akun P&L sehingga tidak perlu dimensi baru, dan Payment Request/JE membawanya (04 bag. 2).
- **Dimensi custom "Kampanye"** (DocType `Kampanye Donasi` platform) untuk tingkat kampanye/penggalangan spesifik, wajib untuk INFAK-T. **Nama `Campaign` DILARANG**: ERPNext v16 sudah punya DocType standar `Campaign` (`crm/doctype/campaign`, field `campaign_name`, dst.); Accounting Dimension untuk DocType yang sama ditolak ("Document Type already used as a dimension"), dan fieldname `campaign` bentrok dengan field CRM/pricing rule (TERVERIFIKASI). Pakai DocType `Kampanye Donasi` dengan label dimensi `Kampanye` (fieldname `kampanye`), atau secara sadar pakai Campaign CRM dengan custom field. Catatan: HF-03 juga mengusulkan DocType platform bernama `Campaign`; nama itu sama dengan DocType CRM bawaan dan harus diganti di handover (H.2). Pastikan juga nama `Dana` bebas (Non Profit sudah dihapus patch v14; `Donation` aman) (dikontrol di kode, bukan mandatory ERPNext, karena mandatory ERPNext berlaku per laporan BS/PL untuk semua baris). Alternatif: Project (04 bag. 2). Pilihan Cost Center + dimensi Kampanye vs Project ada di F9. Sumber nilai Program dan Kampanye adalah DocType platform (HF-03 bag. 2): Campaign saat ini hanya punya `category`; peta `catOf` baru mencakup 29 dari 56 campaign, sehingga Program wajib (Cost Center di akun P&L) tidak bisa diturunkan untuk 27 campaign. Prasyarat: `Campaign.program` wajib (H.2); publish tanpa program ditolak.
- Alasan: UU 23/2011 Pasal 28 mewajibkan peruntukan ikrar ditaati dan dicatat tersendiri (03 R1); PUB berbasis kampanye perlu laporan per kampanye (03 P1, P2). Saldo infak terikat per Kampanye = `Balance Sheet` difilter Dana=INFAK-T, group by Campaign.

### C3. Atribut yang bukan dimensi akuntansi (disimpan di Donation dan di JE sebagai referensi)

Kanal pembayaran (langsung/tidak langsung, QRIS/GoPay/ShopeePay/VA), jenis donor (pribadi/perusahaan), asnaf, pihak berelasi, NIK/NPWP donor, nomor izin (zakat/PUB/wakaf) (02 bag. 8; 01 bag. 8; 03 bag. 5 butir 2). Alasan: dibutuhkan untuk pengungkapan dan SiMBA; mempertahankan dimensi sedikit agar tidak salah isi. Asnaf dimodelkan sebagai akun penyaluran terpisah (B5) karena laporan aktivitas menyajikannya per baris. USULAN. **Catatan: HF-03 saat ini TIDAK memuat atribut ini** (Donor tidak punya jenis donor/NIK/NPWP; Donation tidak punya jenis dana/restriction); lihat H.2.

### C4. Dimensi mandatory dan sumber GL non-Donation

`gl_entry.validate_dimensions_for_pl_and_bs` (TERVERIFIKASI, baris ~188-215) memaksa dimensi Dana pada SETIAP GL Entry akun BS/PL di Company ini, dari modul apa pun: Depreciation/Asset, Payroll, Period Closing Voucher, jurnal opening (3-2000). Tanpa default dimension, posting otomatis dari modul itu gagal ("Accounting Dimension Dana is required"). Rancangan (USULAN): (a) `default_dimension` per Company (Accounting Dimension Detail) hanya bila ditetapkan per jalur: penyusutan aset tetap dan beban pegawai ke AMIL; (b) jurnal opening dibuat per Dana lewat E20; (c) catat bahwa default dimension dapat menyembunyikan salah isi, jadi jangan dipakai untuk jalur donasi. Uji Asset depreciation, Payroll (bila dipakai) dan opening entry dengan dimensi mandatory sebelum CoA dikunci.

## D. Katalog jurnal otomatis

### D0. Konvensi

- Semua jurnal dibuat oleh kode custom app (webhook/handler), bukan Server Script (04 bag. 7). `voucher_type`: **`Bank Entry`** untuk JE yang menyentuh akun bertipe Bank (settlement, penyaluran, refund, bunga, pindah kas), dengan `cheque_no` (referensi settlement/bukti transfer) dan `cheque_date` terisi (`validate_cheque_info` mewajibkan keduanya untuk Bank Entry; TERVERIFIKASI); `Journal Entry` untuk jurnal tanpa akun Bank. Uji bahwa `donation_ref`, Bank Reconciliation Tool dan Bank Account (`is_company_account`) bekerja untuk akun Clearing bertipe Bank (belum teruji).
- **Idempotensi**: Custom Field `donation_ref` pada Journal Entry, tipe Data, **unique**, `read_only`, **`no_copy = 1`**, tidak pernah diisi string kosong (hanya NULL atau nilai). Nilai `{ID-entitas}:{PERISTIWA}[:{urut}]`. Kode: lock baris Donation (`for_update`), cek `exists`, `insert` + `submit`, tangkap `UniqueValidationError` (04 bag. 7). Webhook gateway dapat dikirim ulang; JE tidak punya unique bawaan. Perilaku Frappe yang harus diperhitungkan (TERVERIFIKASI dari `journal_entry.py` dan `model/mapper.py`):
  1. `map_reverse_journal_entry` memakai `get_mapped_doc`, yang menyalin field bernama sama kecuali `no_copy`; tanpa `no_copy` JE pembalik menyalin `donation_ref` asal dan langsung kena unique index.
  2. Pembalik bawaan menolak pembalikan kedua ("A Reverse Journal Entry ... already exists", cek docstatus=1) dan menolak membalik JE yang sendiri punya `reversal_of`. Jadi `reversal_of` hanya untuk **pembalikan penuh satu kali**. Refund parsial dan koreksi berulang = JE baru dengan baris pembalik ditulis manual, kunci `{DON-id}:REFUND:{n}` / `:CORR:{n}`, tanpa `reversal_of`.
  3. JE yang dibatalkan tetap menyimpan `donation_ref`; posting ulang/amend dengan kunci sama ditolak unique. Aturan: setelah cancel, kunci pengganti memakai akhiran `:CORR:{n}` (E14); tambahkan tes.
  4. Isi `posting_date` pembalik/koreksi secara eksplisit (tanggal peristiwa); jangan bergantung pada default (perilaku default tidak diuji).
  5. Unique pada Data aman untuk JE lama/manual bila baris NULL dibolehkan oleh pemeriksaan unik (ifnull(...,'')): DUGAAN, belum diuji; yang pasti, field jangan pernah diisi ''.
- **Keseimbangan per Dana**: ERPNext **tidak menegakkan** keseimbangan per nilai dimensi. `gl_entry.validate_dimensions_for_pl_and_bs` hanya memeriksa dimensi tidak kosong; `journal_entry.set_total_debit_credit` hanya membandingkan total debit dan total kredit (TERVERIFIKASI). JE yang tidak seimbang per Dana lolos dan diam-diam merusak saldo per dana. Karena itu aturan "setiap JE wajib seimbang per nilai Dana" adalah **kontrol buatan sendiri**: helper pembuat JE dan hook `before_submit` menjumlahkan debit minus kredit per nilai Dana dan menolak bila ada yang tidak nol; tes wajib untuk E3, E4, E5, E8, E10, E13 (dan properti acak untuk G, h, F). Setiap jurnal lintas Dana WAJIB menulis baris pindah kas eksplisit (Dr/Cr Clearing atau Bank pada kedua Dana). `automatically_post_balancing_accounting_entry` **dibiarkan nonaktif di semua dimensi**: `make_acc_dimensions_offsetting_entry` menyalin SETIAP GL Entry dan menambah baris lawan ke `offsetting_account` (jumlah dibagi jumlah dimensi), jadi bukan penyeimbang per Dana dan melipatgandakan GL bila dinyalakan (TERVERIFIKASI, `general_ledger.py` baris ~73-106).
- Notasi dimensi: `[Dana | Program(CC) | Kampanye]`. Jumlah: `G` = jumlah pokok donasi (`Donation.amount`; bila donatur menanggung fee, G tetap pokok, lihat E4), `F` = fee gateway, `h` = persentase hak amil (parameter kebijakan), `A` = round(G x h).
- **Pembulatan** (USULAN): mata uang IDR dengan presisi 0 desimal ADALAH REKOMENDASI yang belum teruji (04 bag. 9: DUGAAN; default ERPNext IDR memakai fraksi 100). `A` dibulatkan half-up ke rupiah utuh; sisa `G - A` ke dana sumber. Semua baris JE dihitung dari angka yang sudah dibulatkan sehingga per Dana tetap nol; jangan bergantung pada Round Off (akan membuat akun/Dana tak terduga). Refund parsial: `A_R = round(R x h)`, refund terakhir menyesuaikan agar jumlah `A_R` = `A`. Tes properti untuk G acak.
- Nomor akun mengacu bagian B.
- Tanggal posting (`posting_date`) = tanggal peristiwa nyata (pembayaran/settlement), bukan tanggal job berjalan; berlaku Accounting Period (04 bag. 8).

### E1. Donasi dibuat (Pending)

| Item | Isi |
|---|---|
| Debit/Kredit | **Tidak ada jurnal** (USULAN). Belum ada aset yang diterima; DE para 08/19 mengaitkan pengakuan dengan penerimaan aset (01 bag. 3). Tetap tercatat di DocType Donation dan laporan operasional (donasi menunggu). |
| Dimensi | Tidak ada. Atribut (jenis dana, campaign, restriction) disimpan di Donation dan dikunci sejak dibuat. |
| Pemicu | Donation dibuat, status `Pending`. |
| Idempotensi | Kunci unik pada Donation: `gateway_order_id` (04 bag. 7). Tidak ada kunci JE. |
| Catatan | Bila tampil di laporan, tidak boleh dicampur ke saldo dana. |

### E2. Donasi lunas (QRIS/GoPay/ShopeePay/Virtual Account)

| Item | Isi |
|---|---|
| Gerbang | Hanya model A dan hanya bila H.1 lulus (jenis dana, program, kampanye, tidak ada upsell tak terputus, kanal terpetakan). Campaign `wakaf` dan donasi dengan `upsell_amount` > 0 DITOLAK sebelum diputuskan (E7, E19). |
| Jurnal (kasus infak tidak terikat) | Dr 1-1110 Clearing Midtrans (atau 1-1120 Winpay) `[INFAK-TT | Program | Kampanye]` G ; Cr 4-2100 Infak dan Sedekah Tanpa Pembatasan `[INFAK-TT | Program | Kampanye]` G |
| Zakat | Cr 4-1100 (pribadi) atau 4-1200 (perusahaan) `[ZAKAT | Program]`; Dr Clearing `[ZAKAT | ...]` |
| Infak terikat | Cr 4-2200 `[INFAK-T | Program | Kampanye wajib]`; Dr Clearing `[INFAK-T | ...]` |
| Nonhalal (bila jenis donasi itu ada) | tidak dipakai untuk donasi biasa; lihat E15 |
| Pemicu | Donation `Pending` -> `Paid` (konfirmasi gateway tervalidasi tanda tangannya). Nama status notifikasi gateway (mis. `settlement`/`capture` Midtrans) = USULAN/dugaan tanpa sumber di riset; samakan dengan dokumentasi gateway saat implementasi. |
| Idempotensi | `donation_ref` = `{DON-id}:RECEIPT`. Status mesin hanya boleh maju: Pending -> Paid -> Posted. Kunci unik `gateway_order_id`/`transaction_id` (04 bag. 7). |
| Fee | **Tidak diakui di jurnal ini.** Fee diakui di E4 saat nilainya pasti. Alasan: fee sering baru diketahui saat settlement (INTERPRETASI). Data fee per transaksi belum tersimpan di HF-03 (H.2). |
| Catatan | Pembulatan dan keseimbangan per Dana: D0. Zakat fitrah tidak ada di platform (HF-03 bag. 9: zakat penghasilan, maal, emas, investasi, perniagaan). Bila jenis dana adalah zakat penghasilan di muka (belum memenuhi syarat), gunakan E8. Kanal (QRIS/GoPay/dst.) disimpan sebagai atribut, bukan dimensi (C3); DE mengharuskan pengungkapan penerimaan langsung/tidak langsung (para 18(d), 33(e); 01 bag. 8-9). |

### E3. Pembagian hak amil

| Item | Isi |
|---|---|
| Jurnal (zakat) | Dr 5-1100 Penyaluran Zakat - Amil `[ZAKAT | Program]` A ; Cr 4-3100 Bagian Amil dari Penerimaan Zakat `[AMIL | Program]` A ; sekaligus pindah kas antar dana: Dr 1-1110 Clearing `[AMIL]` A ; Cr 1-1110 Clearing `[ZAKAT]` A |
| Jurnal (infak tidak terikat) | Dr 5-2100 `[INFAK-TT]` A ; Cr 4-3200 `[AMIL]` A ; Dr Clearing `[AMIL]` A ; Cr Clearing `[INFAK-TT]` A |
| Infak terikat | Hanya bila pemberi mengizinkan (pos 5-2200 tersedia di DE C04(f)(i)); selain itu tidak ada hak amil. Zakat muqayyadah: **USULAN default blokir, menunggu F10** (01 bag. 4.2 DUGAAN); belum bisa ditegakkan tanpa atribut `restriction` (C1, H.2). |
| Kontrol lain (USULAN) | Blokir pemberian hadiah/promo ke muzaki yang dibiayai dana zakat dan penerimaan hadiah oleh amil (Fatwa MUI 8/2011 butir 7-9; 03 F1). Amil bergaji tidak mengambil bagian amil: pertanyaan F26. |
| Pemicu | Donation `Paid` (diposting setelah E2 dalam satu transaksi database; JE terpisah). Parameter kebijakan berversi dan bertanggal efektif: `h_zakat` (batas atas 12,5%: Perbaznas 1/2016 Pasal 8 menurut 03 R3; sumber lain Fatwa MUI 8/2011, 01 bag. 4.2) dan `h_infak` (tarif hak amil dari infak = **parameter kebijakan lembaga, TIDAK ada tarif regulasi terverifikasi**). Angka **20% BUKAN `h_infak`**: menurut 03 R3 itu plafon biaya operasional subsider dari infak/sedekah/DSKL bila bagian amil zakat tidak cukup; 01 bag. 4.2 menyebutnya DUGAAN tidak terverifikasi (konflik 01 vs 03, F6). Kontrol plafon 20% dipasang di L9 (total beban Dana Amil yang dibiayai infak dibanding penerimaan infak/DSKL), bukan pada perhitungan A per donasi. |
| Idempotensi | `{DON-id}:AMIL` |
| Catatan | Pola jurnal sesuai C04 DE (beban penyaluran ke amil + penghasilan bagian amil; 01 bag. 4.1, 10.2). Nama akun mengikuti DE. Waktu pengambilan hak amil (saat terima atau saat tutup periode) = F5. |

### E4. Biaya gateway (fee/MDR)

| Item | Isi |
|---|---|
| Jurnal | Dr 5-3200 Beban Biaya Kanal Pembayaran `[AMIL | Program Operasional]` F ; Cr 1-1110 Clearing `[AMIL]` F. Per Dana AMIL nol. |
| Syarat saldo (WAJIB) | Saldo Clearing `[AMIL]` tidak boleh negatif. ERPNext tidak menolak saldo negatif per dimensi, jadi kode memeriksa: saldo Clearing `[AMIL]` pada gateway tersebut (hasil E3 yang belum dipakai) >= F. Bila tidak cukup (mis. infak terikat/zakat muqayyadah dengan A = 0, atau A < F): **E4 ditahan (antrean, tidak diposting)** sampai F5 dijawab. Dana Amil tidak boleh diam-diam meminjam kas dari dana zakat/infak. |
| Bila F5(c) dipilih | Jurnal pinjaman antar-dana eksplisit (hanya untuk kekurangan S = F - saldo): Dr 1-1400 Piutang Antar-Dana `[INFAK-TT]` S ; Cr Clearing `[INFAK-TT]` S ; Dr Clearing `[AMIL]` S ; Cr 2-1500 Utang Antar-Dana `[AMIL]` S. Pelunasan: kebalikannya, kunci `{SETTLEMENT-id}:LOAN` / `:LOANPAY`. Pemberi pinjaman hanya INFAK-TT dengan persetujuan DPS (F5(d), 01 bag. 9 butir 3); ZAKAT dan INFAK-T tidak boleh meminjamkan. Seimbang per Dana pada kedua sisi. |
| Pemicu | Laporan/notifikasi settlement gateway yang memuat fee per transaksi; atau job rekonsiliasi harian. Data fee per transaksi belum ada di HF-03 (H.2). |
| Idempotensi | `{SETTLEMENT-id}:FEE` (fee agregat per settlement) atau `{DON-id}:FEE` (per transaksi); pilih satu (F7). |
| Fee ditanggung donatur | Definisi: `Donation.amount` = G = pokok donasi; `total_paid` = G + F. **Saat dibayar:** Dr 1-1110 Clearing `[INFAK-TT/dana sumber]` G ; Cr penerimaan 4-xxxx G (E2) ; Dr 1-1115 Clearing Titipan `[TITIPAN]` F ; Cr 2-1340 Titipan Biaya Kanal `[TITIPAN]` F. **Saat gateway memotong fee dari settlement:** Dr 2-1340 `[TITIPAN]` F ; Cr 1-1115 Clearing Titipan `[TITIPAN]` F. Seimbang per Dana (Dana sumber G/G; TITIPAN F/F). Fee bukan penerimaan ZIS, tidak masuk 4-xxxx, tidak memicu E3, dan tidak dibebankan ke Dana Amil (01 bag. 9 butir 4). Akun 2-1340 terpisah dari 2-1300 (titipan zakat). Selisih bayar kurang/lebih: E19. |
| Fee transaksi titipan (non-ZIS) | Fee atas transaksi E8/E12/E13 **tidak otomatis ke Dana Amil** (bukan penerimaan ZIS): ditahan manual sampai F25 dijawab. |
| Catatan | Beban di Dana Amil, tidak mengurangi dana zakat/infak (01 bag. 9 butir 2; INTERPRETASI). Bila gateway memberi diskon/cashback dengan konfirmasi tertulis: penghasilan 4-3900 (dana amil) atau dana infak bila manfaat ke pihak lain (PwC via 01 bag. 9 butir 6). Pajak atas fee (PPN/PPh): kosongkan, lihat F11. |

### E5. Settlement gateway ke bank

| Item | Isi |
|---|---|
| Jurnal | Per Dana X yang punya saldo clearing atas donasi dalam batch: Dr 1-1101 Bank Operasional `[Dana X]` S_X ; Cr 1-1110 Clearing `[Dana X]` S_X, dengan **S_X = saldo clearing Dana X atas donasi batch itu** setelah E3 dan E4: dana sumber = sum(G - A); AMIL = sum(A) - sum(F). Total semua S_X = sum(G) - sum(F) = uang yang diterima di bank. Contoh: 1 donasi infak TT G=100.000, A=12.500 (12,5%), F=4.000: S_INFAK-TT=87.500, S_AMIL=8.500, total 96.000. **Fee tidak mengurangi dana sumber** (A4). |
| Pemicu | Notifikasi/laporan settlement gateway atau rekonsiliasi rekening koran (batch `Settled`). Donation pada batch itu ditandai `Settled` (penanda baru, H.3). Voucher `Bank Entry` dengan `cheque_no` = settlement_id (D0). |
| Idempotensi | `{SETTLEMENT-id}:SETTLE`; kunci unik pada tabel settlement (`gateway`, `settlement_id`). Tabel settlement belum ada di HF-03 (H.2). |
| Kontrol (WAJIB) | (1) Per Dana, setelah batch lengkap, saldo clearing atas donasi batch = 0 (tes). (2) L8: saldo clearing per gateway = jumlah per Dana (sum(G-A) untuk dana sumber ditambah sum(A)-sum(F) untuk AMIL) atas donasi `Paid` belum `Settled`, yaitu **sum(G) - sum(F)**; kontrol lama "Paid belum Settled - fee" ambigu per Dana dan mengabaikan A. (3) Tolak posting bila E4 untuk batch itu masih ditahan (E4 syarat saldo). |
| Catatan | Selisih waktu antara E2 dan E5 tampil sebagai saldo clearing (04 bag. 5, 10 butir 5). **01 dan 04 BERBEDA**: 01 bag. 9 butir 1 menyebut piutang kanal pembayaran sebagai **aset di luar kas** (contoh 10.1 memakai akun piutang kanal), sedangkan 04 dan B1 mengklasifikasikan clearing sebagai Bank/Kas dan setara kas. Klaim "tak berbeda secara substansi" dihapus; ini keputusan F7 `[AKUNTAN]` dan klasifikasi B1 PROVISIONAL (menggeser neraca antara kas dan piutang). Kas pihak ketiga (titipan) memakai akun terpisah 1-1115/1-1102 dan tidak dicampur (A8; 01 bag. 9 butir 7). |

### E6. Penyaluran dana (campaign/penyaluran)

Pemicu bertahap sesuai DE para 13-14 dan 25-26 (03 bag. 5 butir 3: status dihimpun, dialokasikan, dikirim, diterima).

**Gerbang data (H.1):** semua skenario di bawah bergantung pada DocType `Disbursement` yang **belum ada**: `Penyaluran` di HF-03 bag. 6 hanya artikel berita (slug, title, subtitle, date, category, image, location, program, description) tanpa nominal, asnaf, penerima, status, rekening, atau Dana. Doctype `Qardh` dan `Aset Kelolaan` juga tidak ada di HF-03. Sampai didefinisikan (H.2), E6 berstatus **DITUNDA** dan baris qardh/aset kelolaan di bawah tidak boleh dikodekan. Kontrol "infak terikat hanya ke Campaign yang sama dan tidak melebihi saldo" tidak dapat ditegakkan tanpa itu. Kontrol tambahan: dana zakat/infak tidak boleh membiayai reward Jejak Kebaikan (F28; Accounting Dimension Filter).

| Skenario | Jurnal | Pemicu | Idempotensi |
|---|---|---|---|
| Penyaluran langsung zakat (diterima mustahik) | Dr 5-11xx Penyaluran Zakat - {asnaf} `[ZAKAT | Program]` ; Cr 1-1101 Bank `[ZAKAT]` | Penyaluran status `Diterima` (bukti terima ada) | `{DIS-id}:DISBURSE` |
| Penyaluran langsung infak | Dr 5-2110 (TT) atau 5-2210 (T) `[INFAK-TT/INFAK-T | Program | Kampanye]` ; Cr Bank `[sama]` | Penyaluran `Diterima` | `{DIS-id}:DISBURSE` |
| Penyaluran tidak langsung (via mitra) - saat dikirim | Dr 1-1200 (zakat) atau 1-1210 (infak) `[Dana]` ; Cr Bank `[Dana]` | Penyaluran `Dikirim` | `{DIS-id}:SEND` |
| idem - saat dikonfirmasi diterima mustahik | Dr 5-11xx/5-2x10 ; Cr 1-1200/1-1210 | Penyaluran `Diterima` | `{DIS-id}:CONFIRM` |
| Al-qardh al-hasan (infak/sedekah saja; zakat tidak diatur) | Salur: Dr 1-1220 / Cr Bank. Kembali: Dr Bank / Cr 1-1220. Hapus tagih: Dr 5-2400 / Cr 1-1220 | Status qardh terkait | `{QRD-id}:OUT|BACK|WRITEOFF` |
| Penyaluran berupa aset kelolaan (DITUNDA, E17) | Perolehan dan penyusutan: lihat E17. Beban seluruhnya bila dikelola entitas lain yang tidak dikendalikan | Penyaluran jenis aset kelolaan | `{ASET-id}:DISBURSE` / `:DEP-{periode}` |
| Penyaluran dana nonhalal | Dr 5-4000 `[NONHALAL]` / Cr Bank `[NONHALAL]` | Penyaluran dari dana nonhalal | `{DIS-id}:DISBURSE` |

Kontrol sistem (USULAN): (1) infak terikat hanya boleh disalurkan ke Campaign yang sama dan tidak melebihi saldo Dana x Campaign (UU 23/2011 Pasal 28; 03 R1); (2) tidak boleh melebihi saldo bank pada Dana tersebut; (3) zakat hanya ke asnaf; (4) pos "liabilitas penyaluran" (2-1100/2-1200) tidak dipakai default karena DE para 13 mengaitkan beban dengan penerimaan oleh mustahik; konflik ini perlu konfirmasi auditor (01 bag. 10.5b). Pelaporan PUB: sisa dana wajib disalurkan paling lambat 1 bulan setelah jangka waktu (Permensos 8/2021 Pasal 14-15; 03 P2): alert, bukan jurnal.

### E7. Penerimaan zakat vs infak (penentuan akun dan dimensi)

Bukan jurnal terpisah; aturan pemetaan di E2. **Sumber pemetaan: atribut `Campaign.fund_type` (H.2), bukan tebakan dari kategori.** HF-03 saat ini hanya punya `Campaign.category` (Kesehatan dst.) dan `is_system/system_kind`; Donation dan Donor belum punya jenis dana, restriction, donor_type, NIK/NPWP (H.2). Tanpa `fund_type`, posting E2 ditolak.

| `fund_type` Campaign (H.2) / jenis | Akun penghasilan | Dana | Syarat |
|---|---|---|---|
| zakat: penghasilan, maal, emas & perak, investasi, perniagaan (5 campaign sistem HF-03 bag. 9; fitrah TIDAK ada di platform) | 4-1100 (pribadi) / 4-1200 (perusahaan) menurut `donor_type` | ZAKAT | Hanya jika entitas penerima adalah amil berizin (A8, F1); `donor_type` wajib (H.2) |
| infak_bebas | 4-2100 | INFAK-TT | model A + izin PUB/amil (F1/F17) |
| infak_terikat (campaign) | 4-2200 | INFAK-T | Kampanye wajib; model A + izin (F1/F17) |
| **wakaf** (`wakafcamp-umum-000000001`, halaman `/wakaf`; donasi nyata yang sudah bisa dibayar) | **tidak ada akun penghasilan** | TITIPAN | **Diblokir**: Campaign `fund_type=wakaf` tidak menerima pembayaran sampai flag kebijakan F4 aktif. Perlakuan sementara bila dibuka: titipan 2-1330 tanpa pengakuan penghasilan (E12). Tes: E2 menolak campaign wakaf. |
| **fidyah** (`zakatcamp-fidyah-0000001`; ada di server asli, tidak tampil di `/zakat`) | belum diputuskan | belum diputuskan | **Diblokir** sampai F23 (fidyah bukan zakat; klasifikasi: infak terikat, titipan, atau DSKL; jangan masuk 4-1100). |
| Qurban (campaign kategori Qurban) | tidak ada akun penghasilan | TITIPAN | E13; DITUNDA, F13/F25 |
| Penerimaan tak sah menurut syariah/bunga | 4-4000 | NONHALAL | lihat E15 |

Alasan: pembedaan zakat, infak tak terikat dan terikat ada di laporan aktivitas (C04; 02 bag. 8, 11.2). Kunci idempotensi sama dengan E2.

### E8. Titipan zakat penghasilan/belum terklasifikasi

Kas titipan memakai akun terpisah 1-1115 Clearing Titipan dan 1-1102 Bank Titipan (B1; A8). Setiap jurnal lintas Dana menulis baris pindah kas eksplisit (D0).

| Item | Isi |
|---|---|
| Saat diterima | Dr 1-1115 Clearing Titipan `[TITIPAN]` G ; Cr 2-1300 Titipan Zakat Penghasilan di Muka `[TITIPAN]` G |
| Saat dikonfirmasi sebagai zakat | Dr 2-1300 `[TITIPAN]` G ; Cr 4-1100 `[ZAKAT]` G ; Dr 1-1101 Bank (atau 1-1110 Clearing) `[ZAKAT]` G ; Cr 1-1102 Bank Titipan (atau 1-1115) `[TITIPAN]` G. Seimbang: ZAKAT Dr G / Cr G; TITIPAN Dr G / Cr G. Lalu E3 untuk hak amil. |
| Bila syarat tidak terpenuhi | Reklasifikasi ke penghasilan infak/sedekah (DK13-DK17 DE; 03 S1a): Dr 2-1300 `[TITIPAN]` G ; Cr 4-2100 `[INFAK-TT]` G ; Dr 1-1101 Bank `[INFAK-TT]` G ; Cr 1-1102 Bank Titipan `[TITIPAN]` G. Seimbang per Dana. |
| Pemicu | Donation jenis `Titipan Zakat`; evaluasi akhir tahun. |
| Idempotensi | `{DON-id}:HOLD`, `{DON-id}:CONFIRM`, `{DON-id}:RECLASS` |
| Catatan | **Perhatikan perbedaan sumber:** A2 menyatakan dana ZIS yang sudah diakui bukan liabilitas; titipan ini liabilitas karena BELUM menjadi dana ZIS (sah menurut 03 S1a), tetapi 01 bag. 10.5c dan DK13-DK17 menandainya **tidak diatur DE batang tubuh**. `[AKUNTAN]` `[SYARIAH]`; jika fitur tidak ditawarkan (F12 default), E8 tidak dibuat. |

### E9. Donasi gagal atau kedaluwarsa

| Item | Isi |
|---|---|
| Jurnal | **Tidak ada** (tidak pernah ada aset yang diterima) |
| Pemicu | Donation `Pending` -> `Failed`/`Expired` (batas waktu pembayaran gateway). |
| Idempotensi | Transisi status satu arah; tidak ada kunci JE. Bila notifikasi lunas tiba setelah `Expired`: tetap diproses lewat E2 hanya jika gateway mengonfirmasi dana benar-benar masuk (kasus tepi; F8). |
| Catatan | Pastikan tidak ada JE `:RECEIPT` untuk donasi ini sebelum menutup sebagai `Failed`. Jika ada JE, perlakuannya refund (E10). |

### E10. Refund (donasi yang sudah lunas dikembalikan)

Contoh angka: infak TT, G=100.000, h=12,5% (A=12.500). Semua jurnal seimbang per Dana (D0).

| Item | Isi |
|---|---|
| Tahap 1: sebelum settlement | Pembalik E2: Dr 4-xxxx (akun penerimaan asal) `[Dana | Program | Kampanye sama]` G ; Cr 1-1110 Clearing `[Dana]` G. Pembalik E3 (bagian amil): Dr 4-3100/4-3200 `[AMIL]` A ; Cr 5-1100/5-2x00 `[Dana sumber]` A ; Dr Clearing `[Dana sumber]` A ; Cr Clearing `[AMIL]` A. Hasil akhir clearing: dana sumber Cr (G - A) = 87.500, AMIL Cr A = 12.500, total G keluar ke donatur. Bila Clearing `[AMIL]` sudah dipakai E4 (fee) sehingga tidak cukup untuk membalik A: aturan saldo negatif E4 berlaku (tahan atau pinjaman antar-dana F5(c)); refund tidak boleh membuat Clearing `[AMIL]` negatif diam-diam. |
| Tahap 2: setelah settlement (kas sudah di Bank) | JE lengkap, **pemindahan kas WAJIB** (bukan "bila perlu"): <br>INFAK-TT: Dr 4-2100 G (100.000) ; Cr 5-2100 A (12.500) ; Cr 1-1101 Bank `[INFAK-TT]` (G - A) 87.500. <br>AMIL: Dr 4-3200 A (12.500) ; Cr 1-1101 Bank `[AMIL]` A (12.500). <br>TITIPAN: Dr 1-1102 Bank Titipan `[TITIPAN]` G (100.000) ; Cr 2-1320 Utang Refund Donatur `[TITIPAN]` G (100.000). <br>Saat dana keluar ke donatur: Dr 2-1320 `[TITIPAN]` G ; Cr 1-1102 Bank Titipan `[TITIPAN]` G. Bank `[AMIL]` tidak boleh negatif (aturan E4). |
| Fee yang tidak dikembalikan gateway | Tetap beban 5-3200 `[AMIL]` (tidak dibalik) (USULAN; F8). Bila gateway mengembalikan fee: Dr Clearing/Bank `[AMIL]` ; Cr 5-3200 `[AMIL]` (F8(b)). |
| Pemicu | Donation `Paid`/`Settled` -> `Refunded` (notifikasi refund gateway atau persetujuan manual berwenang). Chargeback kartu: E19. |
| Idempotensi | Refund penuh satu kali: JE pembalik penuh dengan `reversal_of` (tahap 1) atau JE manual `{DON-id}:REFUND` (tahap 2). **Refund parsial/ulang: JE baru dengan baris pembalik manual** (`A_R = round(R x h)`, D0), kunci `{DON-id}:REFUND:{n}`, jumlah kumulatif tidak melebihi G; `reversal_of` tidak dipakai karena pembalik bawaan hanya sekali dan penuh (D0). Set `posting_date` eksplisit = tanggal refund. Simpan `refund_id` gateway. |
| Catatan | Dana yang sudah disalurkan (E6) atau periode yang sudah ditutup: butuh kebijakan (F8). Tidak ada rujukan standar untuk refund donasi di riset; seluruhnya INTERPRETASI. Tes: E10 tahap 1 dan 2, penuh dan parsial, per-Dana nol. |

### E11. Donasi Shadaqa Rutin (berulang)

| Item | Isi |
|---|---|
| Jurnal | Setiap penagihan berhasil = satu Donation `Paid` -> E2 (+ E3 bila ada hak amil). Jadwal/langganan itu sendiri tidak berjurnal. |
| Pemicu | Job penagihan periodik membuat Donation baru dengan atribut jadwal; lunas -> `Paid`. |
| Idempotensi | Donation unik pada (`schedule_id`, `target_date`) (HF-03 bag. 8: Recurring Execution punya `target_date` dan `is_makeup`); donasi susulan (`is_makeup`) mengisi `target_date` siklus lama **satu kali saja** dan tidak menabrak donasi siklus normal; JE `{DON-id}:RECEIPT`. Pengiriman ulang job tidak boleh membuat Donation kedua untuk (schedule, target_date) yang sama. Tes: susulan, kirim ulang job, siklus normal+susulan. |
| Catatan | Bila donor mengisi "sedekah rutin" tanpa kampanye, dana = INFAK-TT. Metode tagih otomatis (e-wallet autodebit, token) belum diketahui dari HF-03; bila dipakai, kebijakan data pembayaran di luar lingkup dokumen ini. Tidak ada ketentuan standar khusus rutin di riset (INTERPRETASI). |

### E12. Wakaf (bersyarat A9)

Status: **tidak boleh diaktifkan** sebelum F4 dijawab. Karena campaign `wakafcamp-umum-000000001` sudah menerima pembayaran di platform (HF-03 bag. 9), gerbangnya WAJIB di kode: Campaign `fund_type=wakaf` tidak dapat dibayar sampai flag kebijakan F4 aktif, dan E2 menolak posting campaign wakaf (E7). Draf (kas titipan memakai 1-1115/1-1102, B1):

| Skenario | Jurnal (USULAN, draf) | Catatan |
|---|---|---|
| Wakaf uang diterima platform (platform bukan nazhir/LKS-PWU) | Dr 1-1115 Clearing Titipan `[TITIPAN]` ; Cr 2-1330 Titipan Wakaf Uang `[TITIPAN]` | Platform wakaf uang bukan LKS-PWU kecuali ditetapkan; jalur ke LKS-PWU diperlukan (03 R6). |
| Diteruskan ke LKS-PWU/nazhir | Dr 2-1330 `[TITIPAN]` ; Cr 1-1102 Bank Titipan `[TITIPAN]` | Bukti: nomor AIW/sertifikat wakaf uang. |
| Entitas adalah nazhir (aset wakaf dalam kendali) | Dr Bank/Aset wakaf `[WAKAF]` ; Cr 4-5000 `[WAKAF]` (permanen); wakaf temporer: Cr liabilitas (PSAK 412 DE par. 26) | Pembukuan **terpisah dan tidak dikonsolidasi** (03 S3; 03 bag. 5 butir 1: minimal tiga lapisan entitas). A12 mengunci satu Company, sehingga Dana WAKAF/NONHALAL di Company ini **dikeluarkan dari total aset neto L1** dan disajikan terpisah; atau hapus akun 4-5000/5-5000 dan nilai WAKAF sampai F4 diputuskan. |
| Hasil pengelolaan | Bagi tiga: mauquf alaih, reinvestasi, imbalan nazhir (maks 10% hasil neto, basis kas; 03 S3, R6) | Parameter `max_imbalan_nazhir`. |

Idempotensi: `{DON-id}:WAQF-HOLD`, `:WAQF-FWD`, `:WAQF-RECEIPT`.

### E13. Qurban (titipan; penutupan ditunda)

Status keseluruhan: **DRAF; dikunci sampai F13 dan F25 dijawab** (sesuai G butir 5 dan A10). Baris pertama (HOLD) boleh dikodekan lebih dulu tetapi tidak diaktifkan di produksi sebelum F13 dijawab. Rujukan internal "E-QRB-1" sebelumnya tidak ada di dokumen mana pun dan dihapus. Kas titipan memakai 1-1115/1-1102 (B1).

| Tahap | Jurnal (USULAN) | Status |
|---|---|---|
| Qurban dibayar | Dr 1-1115 Clearing Titipan `[TITIPAN]` G ; Cr 2-1310 Titipan Qurban `[TITIPAN]` G | Draf (HOLD), tunggu F13 |
| Pembelian hewan/biaya | Dr 2-1310 `[TITIPAN]` ; Cr Bank Titipan/utang pemasok `[TITIPAN]` | **DITUNDA** |
| Penyembelihan dan distribusi (porsi shohibul qurban) | Dr 2-1310 `[TITIPAN]` ; Cr Bank Titipan/utang (pengiriman) `[TITIPAN]` | **DITUNDA** |
| Ujrah/biaya operasional qurban | Dr 2-1310 `[TITIPAN]` U ; Cr 4-3900 `[AMIL]` U ; **pindah kas:** Dr 1-1101 Bank `[AMIL]` U ; Cr 1-1102 Bank Titipan `[TITIPAN]` U. Seimbang per Dana (TITIPAN Dr U/Cr U; AMIL Cr U/Dr U). | **DITUNDA**, pajak (F11) |
| Daging dibagikan kepada fakir miskin | Penyaluran dari dana titipan; tidak masuk 5-1xxx/5-2xxx bila bukan dana ZIS | **DITUNDA** |
| Sisa dana/qurban tak terlaksana | Dr 2-1310 ; Cr 2-1320 (kembalikan) atau Cr Dana sesuai keputusan (dengan pindah kas eksplisit) | **DITUNDA** |

Idempotensi: `{QRB-id}:HOLD`; lainnya `{QRB-id}:{TAHAP}` setelah diputuskan. Dasar: Perbaznas 1/2023 Pasal 3(2) menyebut kurban dan harta amanah/titipan sebagai DSKL, tetapi DE tidak menyebut qurban dan tidak ada aturan/fatwa akuntansi qurban oleh amil yang ditemukan (03 S6, F4: DUGAAN, TIDAK DITEMUKAN). Fee gateway transaksi qurban: F25 (bukan otomatis E4).

### E14. Koreksi

| Item | Isi |
|---|---|
| Kesalahan akun/dimensi (belum ditutup periode) | JE pembalik penuh (`reversal_of`, hanya satu kali per JE asal; D0) lalu JE benar; kunci `{DON-id}:CORR:{n}:REV` dan `:CORR:{n}:NEW` (`donation_ref` `no_copy`; `posting_date` eksplisit). Koreksi kedua atas JE yang sama: JE manual, bukan `reversal_of`. JE yang dibatalkan tetap memegang kuncinya, jadi pengganti memakai akhiran `:CORR:{n}`. |
| Salah Dana (mis. zakat tercatat INFAK-TT) | Pindah: Dr/Cr akun penerimaan lama dan baru per Dana, serta pindah kas antar dana; wajib persetujuan role keuangan. |
| Periode sudah ditutup | Dilarang sistem kecuali role `exempted_role` Accounting Period; koreksi diposting di periode berjalan dengan pengungkapan, atau buka periode secara terkontrol. Keputusan = F8. |
| Pemicu | Aksi manual berotorisasi (bukan job otomatis), tercatat pelaku, alasan. |
| Idempotensi | `{ref-asal}:CORR:{n}` n bertambah monoton. |
| Catatan | Pencatatan audit trail dan snapshot periode mendukung audit semester dan tahunan (03 R2, R4). |

### E15. Penerimaan nonhalal (jasa giro/bunga)

| Item | Isi |
|---|---|
| Jurnal | Dr 1-1101 Bank `[NONHALAL]` ; Cr 4-4000 Penerimaan Dana Nonhalal `[NONHALAL]` |
| Pemicu | Entri dari rekonsiliasi bank (bukan Donation). |
| Idempotensi | `{BANKTX-id}:NONHALAL` |
| Catatan | DE 2021 tidak memuat dana nonhalal sebagai bab, hanya pengungkapan (para 18(b), 33(c)); versi 2008/2010 memuatnya (01 bag. 3.4). Usulan tetap pisah (INTERPRETASI). Bunga pada rekening penampung PUB diperlakukan sebagai tambahan dana kampanye menurut Permensos 8/2021 (03 P2): berbenturan dengan perlakuan nonhalal; F2. **Default E15 ditahan untuk rekening penampung PUB** sampai F2 dijawab (hanya rekening non-PUB yang diposting ke 4-4000). Voucher `Bank Entry` dengan `cheque_no` = referensi mutasi bank (D0). Pajak atas jasa giro: E17. |

### E16. Tutup periode dan tahun

Bukan peristiwa donasi, tetapi wajib: Period Closing Voucher menutup P&L ke akun 3-1000 per kombinasi dimensi (Dana, Cost Center, Kampanye) sehingga saldo tiap dana tidak tercampur (04 bag. 1, 8). **Accounting Period hanya mengunci jenis dokumen yang tercantum di `closed_documents`** (`accounting_period.py`; TERVERIFIKASI), bukan semua posting GL: buat Accounting Period bulanan dengan `closed_documents` mencakup `Journal Entry` (dan `Period Closing Voucher` bila perlu) dan uji penolakan posting. Mekanisme alternatif yang TERVERIFIKASI ada: v16 menyimpan `accounts_frozen_till_date` dan `role_allowed_for_frozen_entries` pada **Company** (diperiksa di `general_ledger.py` baris ~852; patch `migrate_account_freezing_settings_to_company`); koreksi klaim 04 yang mengira tidak ada "frozen up to". Pakai keduanya dan uji. Pengujian PCV dengan lima/enam nilai Dana belum dilakukan (04 akhir).

### E17. Operasional, aset, dan akun tahap 2 (DRAF; DITUNDA kecuali dinyatakan lain)

Aturan: **akun di CoA yang belum punya jurnal tertulis di katalog ini dinonaktifkan (disabled) sampai jurnalnya ditulis** (1-1300, 1-2200, 2-1400, 2-2100, 4-1900, 4-2900, 4-2950, 5-1190, 5-2900, 5-3900 dst.); tidak diklaim lengkap. Draf di bawah USULAN, setiap baris seimbang per Dana, dan memakai `Bank Entry` bila menyentuh Bank (D0).

| Peristiwa | Jurnal (draf) | Status / keputusan |
|---|---|---|
| Pembayaran beban operasional/gaji dari Dana Amil | Dr 5-3100/5-3300/5-3500 `[AMIL | Program Operasional]` ; Cr 1-1101 Bank `[AMIL]` | Aktif bersama E3; Bank `[AMIL]` tidak boleh negatif. Gaji amil vs bagian amil: F26 |
| Biaya administrasi bank dan biaya transfer keluar (termasuk transfer penyaluran) | Dr 5-3600 `[AMIL]` ; Cr 1-1101 Bank `[AMIL]` | Dana Amil menanggung (PUB: biaya penyaluran dibebankan ke penyelenggara, Permensos 8/2021 Pasal 18 ayat 1; 03 P2) |
| Perolehan aset tetap amil | Dr 1-2100 `[AMIL]` ; Cr 1-1101 Bank `[AMIL]` | Tahap 2; modul Asset dengan default dimensi AMIL (C4) |
| Penyusutan aset tetap amil (bulanan) | Dr 5-3400 `[AMIL]` ; Cr 1-2150 Akumulasi Penyusutan `[AMIL]` | Tahap 2 |
| Perolehan aset kelolaan dari dana ZIS | Dr 1-2300 `[Dana sumber]` ; Cr 1-1101 Bank `[Dana sumber]` | DITUNDA; bergantung `Aset Kelolaan` (H.2) dan F18 |
| Penyusutan aset kelolaan (dikendalikan amil; model biaya, 01 bag. 6) | Dr 5-2300 `[Dana sumber]` ; Cr 1-2350 `[Dana sumber]`, kunci `{ASET-id}:DEP-{periode}` | DITUNDA |
| Terima aset nonkas (emas, saham) | Dr 1-1300 `[ZAKAT/INFAK]` nilai wajar ; Cr 4-1100/4-2100 (zakat/infak) sama | DITUNDA (F18 default: hanya kas) |
| Hasil pengelolaan aset infak | Dr Bank `[INFAK-TT/T]` ; Cr 4-2900 `[INFAK-TT/T]` | DITUNDA |
| Pengukuran ulang aset zakat/infak (01 bag. 10.6-10.7) | Naik: Dr 1-1300 ; Cr 4-1900 (zakat) / 4-2950 (infak). Turun/rugi bukan lalai: Dr 5-1190 / 5-2900 ; Cr 1-1300 | DITUNDA (F18) |
| Penjualan aset nonkas | Dr Bank `[Dana]` harga ; Cr 1-1300 `[Dana]` nilai tercatat ; selisih ke 4-1900/5-1190 (zakat) atau 4-2950/5-2900 (infak) | DITUNDA |
| Kerugian aset karena kelalaian amil | AMIL: Dr 5-3900 L ; Cr 1-1101 Bank `[AMIL]` L. Dana sumber: Dr 1-1101 Bank `[ZAKAT/INFAK]` L ; Cr 1-1300 `[ZAKAT/INFAK]` L (dana sumber tidak menanggung) | DITUNDA (01 bag. 3, 6) |
| PPh final jasa giro dan pajak bunga rekening (nonhalal/PUB) | Dr 1-1101 Bank `[NONHALAL]` (bunga - pajak) ; Dr 5-4000 `[NONHALAL]` pajak (sementara) ; Cr 4-4000 `[NONHALAL]` bunga bruto | DITUNDA (F11) |
| Utang pajak 2-1400, liabilitas imbalan kerja 2-2100, aset takberwujud 1-2200 | belum ada jurnal | DITUNDA (F11, F17) |

### E18. Jalan Kebaikan: pool sponsor dan voucher (DRAF; DIBLOKIR sampai F22)

HF-03 bag. 8: Baik Sponsor Pool (`poolAvailable`), misi selesai -> voucher menjadi Donation yang dibiayai pool (`baik_funding_source`, `baik_replaces_pool_id`), reservasi pool (`reservedUntil`) dan penggantian pool. Donasi bersumber voucher **tidak lewat gateway**: E2 (Dr Clearing) akan membuat clearing negatif dan L8 selisih. Gerbang: Donation dengan `baik_funding_source` selain gateway tidak diposting lewat E2 dan dikeluarkan dari L8.

| Peristiwa | Jurnal (draf, tergantung F22) | Kunci |
|---|---|---|
| E-BAIK-1: setoran sponsor ke pool | Opsi titipan: Dr 1-1102 Bank Titipan `[TITIPAN]` S ; Cr 2-1360 Titipan Sponsor Pool `[TITIPAN]` S. Opsi infak terikat ke kampanye sponsor: Dr 1-1101 Bank `[INFAK-T | Program | Kampanye]` S ; Cr 4-2200 `[INFAK-T | Program | Kampanye]` S. Opsi pendapatan jasa promosi: di pembukuan operator, bukan dana ZIS | `{POOL-id}:FUND` |
| E-BAIK-2: voucher menjadi donasi (pool membiayai) | Opsi titipan: Dr 2-1360 `[TITIPAN]` V ; Cr 4-2200 `[INFAK-T | Program | Kampanye]` V ; pindah kas: Dr 1-1101 Bank `[INFAK-T]` V ; Cr 1-1102 Bank Titipan `[TITIPAN]` V (lalu E3 bila ada hak amil). Opsi infak terikat sudah diakui: tanpa jurnal bila kampanye sama | `{POOL-id}:VOUCHER:{DON-id}` |
| E-BAIK-3: pool kedaluwarsa/diganti (`baik_replaces_pool_id`) | Opsi titipan: Dr 2-1360 `[TITIPAN]` ; Cr 1-1102 Bank Titipan `[TITIPAN]` (dikembalikan) atau Cr 2-1360 pool pengganti; opsi infak terikat: tidak ada jurnal (dana tetap INFAK-T kampanye sponsor) | `{POOL-id}:EXPIRE` / `:REPLACE` |

### E19. Kanal lain, selisih bayar, upsell, valas (DRAF; sebagian DIBLOKIR)

| Peristiwa | Perlakuan |
|---|---|
| Transfer manual dikonfirmasi (`manual_transfer`, tanpa gateway) | Dr 1-1101 Bank `[Dana]` G ; Cr 4-xxxx `[Dana]` G (tanpa clearing); konfirmasi manual berwenang (`Bank Entry`, cheque_no = bukti transfer); hak amil E3 dengan pindah kas lewat Bank: Dr Bank `[AMIL]` A ; Cr Bank `[Dana]` A. Kunci `{DON-id}:RECEIPT` |
| Retail (Indomaret/Alfamart) dan kartu kredit | Clearing 1-1130 atau satu clearing per gateway dengan atribut kanal (F27); alur E2-E5 sama |
| Chargeback kartu kredit | Seperti E10 tahap 1/2 tanpa persetujuan manual; status `chargeback` baru di Donation (H.2); fee chargeback beban 5-3200 `[AMIL]` (F27) |
| Bayar kurang/lebih (kode unik, 3 digit akhir `Total Pembayaran`) | `Donation.amount` (G) vs `total_paid` didefinisikan di H.2. Selisih lebih: Dr 1-1115 Clearing Titipan `[TITIPAN]` d ; Cr 2-1350 `[TITIPAN]` d (dikembalikan atau dialihkan ke donasi oleh keputusan F24). Kurang bayar: pengakuan sebesar kas diterima (DE para 08), Donation disesuaikan |
| Upsell (`upsell_amount`, `upsell_label`, `upsell_breakdown`) | E2 memisahkan `main_amount` dan `upsell_amount` per akun/dimensi/kampanye tujuan. **Posting diblokir bila `upsell_amount` > 0** sampai tujuan diputuskan (F24); tes yang menolak posting |
| Donasi valas (`intl_qris`, `idr_equivalent`) | Default F19 = IDR saja: gerbang menolak `currency` bukan IDR dan metode `intl_qris` sampai F19 dijawab. Bila dibuka: akun 1-1190 dan selisih kurs |

### E20. Saldo awal dan migrasi (E-OPEN; DRAF)

HF-03 bag. 2 dan 11: snapshot impor membawa `raised_amount` (RAISED) 56 campaign dari sistem asli sementara GL mulai nol; bila `Campaign.raised_amount` dihitung dari Donation `paid`, laporan campaign/L7 tidak akan sama dengan GL. Rancangan: JE saldo awal per Dana dan Kampanye: Dr Bank/aset `[Dana | Program | Kampanye]` ; Cr 3-2000 Saldo Awal `[Dana]` (kunci `{KAMPANYE-id}:OPEN`; seimbang per Dana); Donation sintetis tipe `historis` ditandai `jurnal_dikecualikan` (tidak dijurnal ulang); rekonsiliasi `raised_amount` snapshot terhadap GL (L7) sebelum go-live. Akun 3-2000 tidak boleh dipakai di luar E20 dan E14.

## E. Laporan PSAK yang harus bisa dihasilkan dan sumber data

Basis format: DE PSAK 101 Revisi 2021 Lampiran C (02 bag. 11); versi final belum terbaca. Format Perbaznas 5/2018 Pasal 23(3) masih meminta laporan perubahan dana dan perubahan aset kelolaan (03 R5; 01 bag. 7). Usulan: ERP menyediakan kedua versi.

**Koreksi mekanisme (TERVERIFIKASI dari image v16.56.0):** Financial Report Template / Custom Financial Statement **tidak mendukung `group_by_dimension`** (`financial_report_engine.py` baris ~273-278 memunculkan peringatan "unsupported"; `custom_financial_statement.js` hanya memanggil `add_dimensions`, yakni filter dimensi satu nilai; `financial_statements.py` `build_period_list` melewati `get_dimension_period_list` bila `report_template` terisi). Dokumen 04 keliru membaca baris ~273 sebagai validasi. Balance Sheet/P&L standar memang punya `group_by_dimension`, tetapi layoutnya per root type (tanpa pos PSAK dan tanpa agregasi INFAK-TT + INFAK-T). Opsi (USULAN, pilih satu sebelum G dikunci): **(a)** jalankan template satu kali per nilai Dana dengan filter dimensi `dana` (didukung `add_dimensions`) lalu gabungkan kolom di Script Report kustom/cetak; **(b)** Script Report kustom yang membaca GL Entry atau Account Closing Balance per Dana (rekomendasi untuk L1/L2/L6/L7); **(c)** Balance Sheet/P&L standar dengan `group_by_dimension` untuk tampilan internal saja. Kolom tabel di bawah ditulis menurut opsi (a)/(b); "group_by_dimension pada template kustom" tidak lagi diuji karena sudah terjawab: tidak didukung.

| # | Laporan | Sumber data ERPNext | Cara (USULAN) | Catatan |
|---|---|---|---|---|
| L1 | Laporan Posisi Keuangan (C03; aset lancar/tidak lancar, liabilitas, aset neto per dana) | GL Entry; template `Balance Sheet` dijalankan per nilai Dana (filter dimensi) atau Script Report kustom per Dana (opsi a/b di atas) | Template memakai `Account Category` dari B. Kolom ZAKAT + INFAK-TT + INFAK-T + AMIL dijumlah untuk total aset neto; **WAKAF dan NONHALAL (dan TITIPAN/kas pihak ketiga) dikeluarkan dari total** dan disajikan sebagai pos terpisah/pengungkapan (C03 DE hanya tiga dana; A9, F4). Piutang/utang antar-dana dieliminasi. Klasifikasi kas vs piutang kanal PROVISIONAL (F7). | Kontrol: Jumlah Aset = Liabilitas + Aset Neto (02 bag. 11.1). Aset neto per dana = akun 3-xxx + surplus berjalan per Dana. |
| L2 | Laporan Aktivitas (C04: Dana Zakat, Dana Infak dan Sedekah, Dana Amil; saldo awal/akhir per dana) | GL Entry (`Period Movement`); template Custom Financial Statement dijalankan per nilai Dana (filter dimensi) lalu digabung, atau Script Report kustom (opsi a/b); BUKAN `group_by_dimension` | Baris per akun penghasilan/beban (B4, B5); Dana Infak = INFAK-TT + INFAK-T dijumlah di lapisan penggabung (agregasi tidak tersedia di template). | Kontrol: saldo akhir ketiga dana = jumlah aset neto L1 (02 bag. 11.2). Eliminasi/pencocokan beban penyaluran ke amil vs bagian amil (E3) harus diuji. Pemisahan per Dana datang dari satu eksekusi per Dana (filter dimensi) atau pembacaan GL per Dana; tidak ada filter dimensi per baris dan tidak ada `group_by_dimension` pada template (TERVERIFIKASI). |
| L3 | Laporan Arus Kas (C05; PSAK 207, dahulu PSAK 2) | Cash Flow report; `group_by_dimension` tanpa saldo awal/akhir per dana (04 bag. 1) | Pakai Cash Flow bawaan atau template; arus kas per dana tanpa opening/closing. | Klasifikasi operasi/investasi/pendanaan untuk dana ZIS tidak ditentukan sumber (02 bag. 11.3). `[AKUNTAN]` |
| L4 | Catatan atas Laporan Keuangan (C06; para 18, 33 DE) | Gabungan: GL, DocType Donation/Penyaluran/Aset Kelolaan, parameter kebijakan | Laporan/script kustom: bagian amil (jumlah, persentase, peruntukan, perubahan), infak terikat/tidak terikat dan rincian saldo, aset yang tidak diakui sebagai penghasilan (bunga bank), penerimaan langsung/tidak langsung, muzaki pribadi/perusahaan, kas/nonkas, penyaluran per asnaf, pihak berelasi, aset kelolaan, al-qardh (01 bag. 8) | Butuh atribut transaksi di C3. |
| L5 | Rekonsiliasi/Perubahan Aset Kelolaan | Register aset kelolaan, GL akun 1-23xx, 5-2300 | Laporan kustom (penambahan, penyusutan, penurunan nilai, penghentian pengakuan per dana sumber; para 18(m), 33(m)) | Dipindah ke CaLK di PSAK 401 Revisi 2022; tetap dibutuhkan Perbaznas 5/2018 (01 bag. 7). |
| L6 | Laporan Perubahan Dana (format Perbaznas 5/2018 / PSAK 109 versi 2010) | GL via Script Report per Dana (opsi a/b) | Re-pakai data L2 dalam format lama | Opsional per kebutuhan pelaporan ke BAZNAS (03 R5). |
| L7 | Saldo dana per Program dan Kampanye (terutama INFAK-T) | GL Entry / Dimension-wise Accounts Balance Report (belum diuji) atau Balance Sheet standar dengan filter dan `group_by_dimension`=Kampanye (laporan standar, bukan template) | Filter Dana=INFAK-T, group by Kampanye/Cost Center; rekonsiliasi dengan `raised_amount` snapshot (E20) | Mendukung ketaatan peruntukan (A7) dan PUB (03 P1, P2). |
| L8 | Rekonsiliasi gateway (clearing vs settlement vs bank) | Saldo akun 1-1110/1-1120/1-1130, tabel Donation (Paid/Settled), tabel settlement, rekening koran | Laporan kustom dengan selisih per gateway DAN per Dana | Kontrol E5: saldo clearing = sum(G) - sum(F) atas donasi `Paid` belum `Settled`, dan clearing tiap Dana nol setelah batch lengkap. Donasi bersumber voucher/manual dikeluarkan (E18, E19). |
| L9 | Pengungkapan bagian amil dan batas | GL 4-3100/4-3200, parameter persentase berversi | Laporan kustom: persentase aktual `h_zakat` vs batas 12,5% (Perbaznas 1/2016 menurut 03 R3; berlaku bagi LAZ swasta belum pasti) dan plafon biaya operasional subsider dari infak/DSKL 20% (**DUGAAN/belum terkonfirmasi**: 03 R3 terverifikasi, 01 bag. 4.2 tidak; F6). 20% = plafon beban operasional, bukan tarif hak amil infak | Pengungkapan wajib (para 18(a), 33(a); 01 bag. 4.1). |
| L10 | Laporan SiMBA/BAZNAS (kinerja + keuangan; semester dan tahunan; tenggat LAZ ke BAZNAS 10 Juli, 15 Agustus, 10 Jan, 15 Feb, 15 Agustus berikutnya; **LAZ ke pemda 1 September, Pasal 12 ayat 2**) | Donation, Penyaluran, data muzaki/mustahik, L1-L4 | Ekspor sesuai skema SiMBA (skema tidak ada di riset) | Perbaznas 1/2023 (03 R4); tenggat dari 03 saja. |
| L11 | Laporan PUB per kampanye (hasil, penggunaan, audit akuntan publik bila > Rp500 juta) | L7 + data izin PUB per Campaign | Laporan kustom | Permensos 8/2021 Pasal 25 (03 P2); ketaatan izin tidak pasti (03 P3). |
| L12 | Bukti penerimaan donasi (NIK/NPWP donor, jumlah, validasi) dan laporan DJP triwulan/tahunan | Donation (atribut donor), JE terkait | Dokumen cetak dan ekspor | PMK 114/2025 Pasal 17-19 (03 X1); status lembaga bukan bentukan pemerintah `[PAJAK/HUKUM]`. |
| L13 | Mutasi dana nonhalal, titipan (donatur, qurban, wakaf, sponsor), kas pihak ketiga | GL per akun 2-13xx, 1-1102/1-1115, Dana NONHALAL/TITIPAN | Laporan kustom | Untuk pengendalian internal; kas pihak ketiga dikecualikan dari kas dana ZIS (A8). |
| L14 | Laporan wakaf (bersyarat A9) | Pembukuan Dana WAKAF/Company wakaf | Format PSAK 412 (tidak dibaca final) | `[AKUNTAN]` |

## F. Hal yang HARUS diputuskan akuntan dan ahli syariah (pertanyaan terbuka)

Format: pertanyaan, opsi, rekomendasi sementara bila ada (USULAN).

| # | Pertanyaan | Opsi | Rekomendasi sementara |
|---|---|---|---|
| F1 | **Siapa pemegang dana dan model peran platform?** (zakat hanya boleh dikumpulkan BAZNAS/LAZ berizin; PUB oleh ormas berbadan hukum; 03 bag. 3) `[SYARIAH]` `[PAJAK/HUKUM]` `[AKUNTAN]` | (a) Platform = amil/penyelenggara PUB berizin: dana langsung dana ZIS di pembukuannya. (b) Platform = agen kanal bagi lembaga mitra: dana ditahan sebagai titipan, fee = pendapatan platform (PSAK wakalah belum terbit per 2022). (c) Platform di bawah yayasan terpisah. | Rancang jurnal untuk (a) **dengan gerbang "model A saja" pada E2-E7 (H.1)**; sediakan alternatif jurnal (b) (semua E2 menjadi titipan/liabilitas, fee = pendapatan platform; dimensi `Lembaga Mitra`) sebelum jurnal dikunci. Jangan aktifkan zakat, infak, maupun campaign sebelum jelas (E7 hanya menjaga izin amil untuk zakat; izin PUB/amil untuk infak juga perlu, F17). |
| F2 | **Dana nonhalal: pertahankan sebagai dana terpisah?** DE 2021 tak memuatnya; versi 2008/2010 ya (01 bag. 3.4); bunga rekening PUB menurut Permensos masuk tambahan dana kampanye (03 P2). `[AKUNTAN]` `[SYARIAH]` `[PAJAK/HUKUM]` | (a) Dana tersendiri NONHALAL (B3/B4/B5). (b) Hanya pengungkapan di CaLK, tanpa dana. (c) Ikuti Permensos untuk rekening PUB, nonhalal hanya untuk zakat/infak. | (a). Bila konflik PUB: pisahkan rekening. |
| F3 | **Infak terikat/tidak terikat sebagai dua dimensi vs satu dana dengan sub-kategori.** DE: satu dana, dua sub-kategori (04 bag. 0). `[AKUNTAN]` | (a) Dua nilai Dana + agregasi laporan (usulan). (b) Satu nilai Dana INFAK + dimensi/atribut `restriction`. | (a); uji agregasi L2 (04 bag. 4). |
| F4 | **Apakah wakaf dalam ruang lingkup, dan bagaimana pemisahannya?** Wakaf sudah bisa dibayar di platform (campaign `wakafcamp-umum-000000001`, HF-03 bag. 9), jadi gerbang pemblokiran wajib (E7, E12). (PSAK 412: tidak dikonsolidasi; wakaf uang lewat LKS-PWU; 03 S3, R6) `[SYARIAH]` `[AKUNTAN]` | (a) Di luar lingkup tahap 1. (b) Wakaf sebagai titipan ke LKS-PWU/nazhir mitra (E12). (c) Company terpisah untuk nazhir. (d) Dana WAKAF dalam Company yang sama. | (a)/(b). Rekomendasi (04) satu Company; PSAK 412 meminta entitas pelaporan terpisah: konflik, putuskan. |
| F5 | **Kapan dan berapa hak amil diambil, dan bagaimana menutup fee gateway bila saldo kas Dana Amil belum cukup?** (E4 menahan fee, tidak membiarkan saldo kas AMIL negatif) Batas 12,5% hanya batas (03 R3); 20% adalah plafon operasional subsider, bukan tarif; sumber operasional lain boleh (01 bag. 4.2). `[SYARIAH]` `[AKUNTAN]` | (a) Alokasikan hak amil saat setiap donasi lunas (E3). (b) Alokasikan periodik (mis. bulanan). (c) Fee di Dana Amil dengan pinjaman antar dana sementara. (d) Fee sebagian dibebankan ke infak tidak terikat dengan persetujuan DPS (01 bag. 9 butir 3). | (a); bila saldo kas AMIL kurang, E4 ditahan; (c) hanya dengan jurnal pinjaman antar-dana eksplisit (akun 1-1400/2-1500, E4) dan pemberi pinjaman hanya INFAK-TT; batas sebagai parameter berversi. |
| F6 | **Apakah batas 12,5% (zakat) dan plafon operasional 20% (infak/DSKL) mengikat LAZ swasta, dan apa sumbernya?** KONFLIK ANTAR BERKAS: 03 R3 = 12,5% dan 20% terverifikasi di Perbaznas 1/2016 Pasal 8 (untuk BAZNAS); 01 bag. 4.2 = 12,5% dari Fatwa MUI 8/2011 dan 20% DUGAAN tidak ditemukan di regulasi yang dibaca. KMA 606/2020 tak terbaca. `[PAJAK/HUKUM]` `[SYARIAH]` | (a) Terapkan sebagai batas keras. (b) Peringatan saja. (c) Kebijakan internal lain, diungkapkan. | (b) peringatan saja; angka 20% diberi label DUGAAN/belum dikonfirmasi di parameter dan L9; dimodelkan sebagai plafon beban operasional subsider. |
| F7 | **Perlakuan clearing gateway dan fee.** (a) Clearing = kas dan setara kas atau piutang kanal? **01 dan 04 berbeda** (01 bag. 9 butir 1: piutang kanal = aset di luar kas; 04/B1: Bank/kas) dan keputusan ini ada di akuntan; klasifikasi B1 PROVISIONAL. (b) Fee dicatat per transaksi atau agregat per settlement? (c) Penerimaan bruto atau neto? (01 bag. 9; tak ada ketentuan eksplisit) `[AKUNTAN]` | (a) Kas/Bank (04). (b) Piutang kanal pembayaran (01). Fee: per transaksi atau per settlement. Penerimaan: bruto (usulan) atau neto (tak disarankan). | Bruto; klasifikasi clearing sebagai kas dan setara kas hanya sementara (provisional); fee per settlement (kecuali auditor meminta lain). |
| F8 | **Refund, chargeback, kedaluwarsa tapi dana masuk, dan koreksi setelah periode ditutup.** Refund setelah dana disalurkan? Fee tak dikembalikan? (Chargeback: E19, F27.) | (a) Pembalik penuh dan fee tetap beban Dana Amil. (b) Fee dibalik bila gateway mengembalikan. (c) Refund setelah disalurkan: piutang pada penerima atau beban dana amil. (d) Koreksi pasca tutup: buka periode vs jurnal di periode berjalan dengan pengungkapan. | (a), (d) periode berjalan. Tak ada rujukan standar. |
| F9 | **Program/Kampanye: Cost Center, Project, atau dimensi custom?** (04 bag. 2; nama `Campaign` bentrok dengan DocType CRM, C2) | (a) Cost Center = Program + dimensi `Kampanye` (DocType `Kampanye Donasi`) (usulan). (b) Cost Center = Campaign. (c) Project untuk campaign. | (a); uji pelaporan lintas dimensi. |
| F10 | **Zakat muqayyadah dan infak terikat: boleh hak amil dan biaya operasional?** (A7/E3 hanya USULAN default blokir sampai ini dijawab) Fatwa MUI 15/2011 via Hukumonline (sekunder, 01 bag. 4.2); DE menyediakan pos "penyaluran infak dengan pembatasan kepada amil" (01 bag. 10.3). `[SYARIAH]` | (a) Dilarang untuk zakat muqayyadah, boleh infak terikat bila pemberi mengizinkan (usulan). (b) Dilarang untuk keduanya; operasional hanya dari dana amil/infak tidak terikat. (c) Boleh meminta biaya operasional langsung ke donor di luar jumlah ikrar. | (a), blokir default untuk keduanya sampai ada pernyataan donor. |
| F11 | **Pajak atas fee dan jasa platform: PPN/PPh, status PKP, tarif; PPN/PPh atas ujrah qurban.** Tidak ditemukan aturan tegas (03 X4, X5). `[PAJAK/HUKUM]` | (a) Fee platform kena PPN bila PKP. (b) Di luar PPN. (c) Per jenis jasa. | Jangan isi default; kolom kode pajak kosong (03 X4). |
| F12 | **Titipan zakat penghasilan dan titipan lain: ditawarkan atau tidak? Dan kapan reklasifikasi?** DE tak mengaturnya (batang tubuh); DK13-DK17 menegaskan liabilitas (03 S1a). `[SYARIAH]` `[AKUNTAN]` | (a) Tidak ditawarkan. (b) Ditawarkan dengan E8. (c) Dicatat langsung sebagai infak bila syarat belum ada. | (a) tahap 1. |
| F13 | **Qurban: liabilitas titipan di neraca atau di luar neraca? Akad (wakalah) dan ujrah? Sisa dana? Bagian daging untuk fakir miskin?** Tidak ada standar/fatwa yang ditemukan (03 S6, F4). `[SYARIAH]` `[AKUNTAN]` | (a) Liabilitas titipan 2-1310 (usulan). (b) Di luar laporan posisi keuangan (catatan). (c) Penghasilan dana amil untuk ujrah, sisa ke infak. | (a) dengan jurnal penutupan ditunda (E13). |
| F14 | **Hak amil atas zakat bila muzaki menunjuk mustahik via amil (imbalan/ujrah).** DE 2021 tidak mengatur lagi (DK05-06); versi 2008/2010 mengatur (01 bag. 4.1). `[SYARIAH]` `[AKUNTAN]` | (a) Seluruh zakat tetap dana zakat; ujrah tambah dana amil. (b) Tidak ditawarkan. | (b) bila belum perlu. |
| F15 | **Penyaluran: apakah memakai "liabilitas penyaluran" atau hanya beban saat diterima?** Konflik antara pos C03 dan para 13 (01 bag. 10.5b). `[AKUNTAN]` | (a) Beban saat mustahik menerima; piutang penyaluran bila lewat mitra (usulan). (b) Liabilitas bila kewajiban mengikat. | (a). |
| F16 | **Standar pelaporan yang menjadi acuan: laporan aktivitas (PSAK 401 Rev. 2022 Lampiran C) saja, atau juga laporan perubahan dana/perubahan aset kelolaan (Perbaznas 5/2018)?** Perubahan PSAK 401 efektif 1 Jan 2027 (amil dipindah ke PSAK 409; belum terverifikasi; 02 bag. 0, 9) `[AKUNTAN]` | (a) Hanya PSAK. (b) Kedua format (usulan). (c) Bergantung audit BAZNAS. | (b). |
| F17 | **Pilar SAK entitas (SAK umum, SAK EP, SAK EMKM) dan ISAK 335 bagi entitas non-amil (yayasan PUB).** Tidak terjawab dalam riset (02 bag. 1.3, 12). `[AKUNTAN]` | (a) SAK umum + Lampiran C. (b) SAK EP/EMKM + ISAK 403. (c) ISAK 335 untuk PUB. | Jangan kunci laporan sebelum dijawab. |
| F18 | **Pengukuran aset nonkas (emas, saham, tanah) dan kebijakan nilai wajar, penurunan nilai, kerugian lalai.** (01 bag. 3, 6) `[AKUNTAN]` | (a) Terima hanya kas tahap 1. (b) Terima nonkas dengan kebijakan nilai wajar dan akun 1-1300. | (a). |
| F19 | **Mata uang asing dan selisih kurs untuk donasi valas.** HF-03 punya `intl_qris` dan `idr_equivalent`, jadi valas bisa masuk; gerbang H.1 menolak non-IDR sampai dijawab. (01 bag. 10.6; rujukan PSAK 210 tidak diverifikasi) `[AKUNTAN]` | (a) Hanya IDR. (b) Terima valas dengan akun 1-1190 dan perubahan nilai di dana zakat/infak. | (a), dengan penolakan eksplisit di kode. |
| F20 | **Tanggal efektif PSAK 409 (2024 vs 2025), amendemen setelahnya, dan teks final.** (01 bag. 1, 11) `[AKUNTAN]` | (a) Pakai 2024 (sumber IAI). (b) Tunda sampai teks final dibaca. | (a) + review teks final sebelum kunci CoA. |
| F21 | **Pembiayaan operasional PUB maksimum 10% dan biaya penyaluran, sumber dana operasional.** (03 P1, P2) `[PAJAK/HUKUM]` | (a) Parameter per kampanye PUB. (b) Fee 5% model Kitabisa (klaim pihak itu, 03 bag. 3). | (a), dan putuskan dasar izin. |
| F22 | **Jalan Kebaikan: sponsor = donatur (infak terikat/titipan) atau pembayar jasa promosi (pendapatan)?** Reservasi dan penggantian pool, pool kedaluwarsa (HF-03 bag. 8). `[AKUNTAN]` `[SYARIAH]` | (a) Titipan sponsor 2-1360 sampai voucher dipakai. (b) Infak terikat ke kampanye sponsor saat setor. (c) Pendapatan operator. | Belum ada; blokir E18 sampai dijawab. |
| F23 | **Fidyah: klasifikasi dan asnaf penyaluran.** Campaign `zakatcamp-fidyah-0000001` ada di server asli; fidyah bukan zakat (03 bag. 4.2 R4: DSKL mencantumkan fidyah). `[SYARIAH]` `[AKUNTAN]` | (a) Infak terikat/DSKL tersendiri. (b) Titipan. (c) Tidak ditawarkan. | Blokir sampai dijawab; jangan masuk 4-1100. |
| F24 | **Upsell, `amount` vs `total_paid`, dan selisih bayar.** Tujuan `upsell_amount` (kampanye lain, biaya platform, infak tambahan?), arti `Donation.amount` terhadap total bayar (donasi + fee/kode unik). `[AKUNTAN]` | (a) Upsell = infak ke kampanye tujuan. (b) Upsell = biaya platform (pendapatan operator, bukan dana ZIS). (c) Tidak ditawarkan. Selisih bayar ke 2-1350. | Blokir posting bila upsell > 0. |
| F25 | **Siapa menanggung fee gateway atas transaksi non-ZIS (titipan zakat penghasilan, qurban, wakaf, sponsor)?** `[AKUNTAN]` `[SYARIAH]` | (a) Dipotong dari titipan. (b) Dana Amil/operator. (c) Donatur (2-1340). | Tahan (E4), tidak otomatis ke Dana Amil. |
| F26 | **Kontrol gaji amil vs bagian amil, hadiah ke muzaki, dan operasional dari bagian fi sabilillah.** Fatwa MUI 8/2011 butir 7-9 (03 F1); 01 bag. 4.2. `[SYARIAH]` | (a) Blokir hadiah dari dana zakat dan amil bergaji tidak mengambil bagian amil. (b) Operasional boleh dari fi sabilillah dalam batas wajar (butuh akun/dimensi). | (a); (b) menunggu keputusan. |
| F27 | **Kanal retail, transfer manual, kartu kredit (chargeback).** Akun clearing per kanal atau per gateway + atribut kanal; fee chargeback; blokir `intl_qris` (F19). `[AKUNTAN]` | (a) Clearing per kanal (1-1130). (b) Satu clearing per gateway + atribut kanal. | (b); status `chargeback` ditambah (H.2). |
| F28 | **Pinjaman antar-dana dan pembiayaan reward Jejak Kebaikan.** Akun 1-1400/2-1500; siapa membiayai hadiah fisik (`Reward Claim`: Dana Amil, sponsor, operator); dana ZIS tidak boleh membiayai reward. `[AKUNTAN]` `[SYARIAH]` | (a) Dana Amil. (b) Sponsor/operator. | Larang dana ZIS lewat Accounting Dimension Filter. |
| F29 | **Saldo awal/migrasi dan rekonsiliasi `raised_amount` snapshot.** (E20) `[AKUNTAN]` | (a) JE opening per Dana/Kampanye + Donation `historis`. (b) Mulai dari nol, snapshot sebagai pengungkapan. | (a). |

## G. Ringkasan teknis untuk implementasi (USULAN)

1. Buat CoA kustom (B) dengan `Account Category` dan `account_type` yang benar (B; bukan Receivable untuk akun tanpa party); centang mandatory BS dan PL pada dimensi Dana; rancang `default_dimension` per jalur non-Donation (C4); daftarkan setiap akun P&L/penyaluran ke satu Accounting Dimension Filter mode Allow (C1 butir 5).
2. Tambah Custom Field `donation_ref` pada Journal Entry (unique, read-only, **no_copy**, tidak pernah ''); kunci unik pada Donation dan settlement; `voucher_type` Bank Entry + cheque_no/cheque_date untuk JE yang menyentuh Bank (D0).
3. Implementasi di custom app (Python): validator **keseimbangan per Dana** (`before_submit`/helper; ERPNext tidak menegakkannya), aturan pembulatan, aturan saldo kas AMIL tidak negatif (E4), gerbang H.1; tes untuk tiap kolom "Idempotensi" di D, tes per-Dana nol untuk E3, E4, E5, E8, E10, E13, tes properti untuk G acak, dan tes yang menolak posting campaign wakaf/fidyah/upsell > 0. Integrasi gateway adalah kode kustom penuh (A12).
4. Uji sebelum dipakai (belum dijalankan): Accounting Dimension Filter pada JE multi-Dana, `automatically_post_balancing_accounting_entry` (**dibiarkan nonaktif di semua dimensi**; D0), PCV dengan banyak nilai Dana, Accounting Period dengan `closed_documents` dan `accounts_frozen_till_date`, Asset depreciation/Payroll/opening dengan dimensi mandatory, Bank Reconciliation untuk akun clearing, ketersediaan app `payments`. **Sudah terjawab, tidak diuji lagi:** `group_by_dimension` pada template kustom TIDAK didukung (bagian E; L1/L2/L6/L7 memakai opsi a/b).
5. Kunci CoA dan jurnal E8, E12, E13, E17-E19 hanya setelah F-nya dijawab; E6 setelah DocType `Disbursement` ada; E2-E7 hanya setelah F1 (model A) dan H.1 lulus.

## H. Ketergantungan pada data platform (HF-03) dan pemetaan status

Dokumen ini dibuat dari riset 01-04 dan belum direkonsiliasi dengan skema platform di `donasi-eco3/docs/handover-frappe/03-doctype-dan-field.md` (HF-03). Hasil pembacaan HF-03 menunjukkan jurnal D bergantung pada data yang BELUM ada di sana.

### H.1 Gerbang posting (kode harus menolak posting bila tidak terpenuhi)

1. Model peran = A (F1) dan izin sesuai jenis (zakat: amil berizin; infak/campaign: F17).
2. Campaign punya `fund_type`, `program` (Link Cost Center, wajib), dan bila terikat `Kampanye` yang valid.
3. Donation punya `total_paid`, `amount`, kanal terpetakan, `upsell_amount` = 0, `currency` = IDR (E19).
4. `fund_type` bukan `wakaf`/`fidyah` (E7), dan Donation tidak bersumber voucher/pool (E18).
5. Fee, settlement dan clearing tersedia bila E4/E5 diaktifkan.
6. Dimensi dan filter Dana aktif dan validator per Dana lulus.

### H.2 Data yang harus ditambahkan ke HF-03 (usulan untuk handover; berkas HF-03 TIDAK diubah di sini)

| Doctype / field | Alasan |
|---|---|
| `Campaign.fund_type` (zakat, infak_bebas, infak_terikat, wakaf, qurban, fidyah, nonhalal), `Campaign.program` (wajib), `Campaign.amil_percent` berversi, `Campaign.end_date`, nomor izin PUB; tolak publish tanpa program | E7, C2; `catOf` hanya 29 dari 56 campaign |
| `Donor.donor_type` (pribadi/perusahaan), `Donor.nik`, `Donor.npwp`; `Donation.restriction`, `Donation.fund_type` turunan | E7 (4-1100 vs 4-1200), C3, bukti penerimaan (X1) |
| `Donation.total_paid`, `Donation.amount` (definisi G), `settlement_status`, status `chargeback` | E4, E5, E19 |
| `Payment Request.fee_amount`, `fee_borne_by`, `gross_amount`, `net_amount`, `settlement` (Link) | E4/E5. `Payment Method` sudah punya `fee_flat`/`fee_percent` (konfigurasi per metode), tetapi fee aktual per transaksi belum tersimpan |
| Doctype `Gateway Settlement` (gateway, settlement_id, tanggal, total, fee, daftar donasi) | E5, L8 |
| Doctype `Disbursement` (campaign, dana, nominal, asnaf, penerima, kanal, status, bukti, tanggal diterima) terpisah dari `Penyaluran` (berita); Doctype `Qardh`, `Aset Kelolaan` | E6, E17 |
| Pemisahan `main_amount`/`upsell_amount` per tujuan | E19 |
| `Recurring Execution` (target_date, is_makeup) dipakai sebagai kunci | E11 |
| Baik Sponsor Pool dengan perjanjian sponsor, `Reward Claim` dengan sumber biaya | E18, F28 |

### H.3 Pemetaan status 05 ke HF-03 bag. 3

| Nama di 05 | Status HF-03 / keterangan |
|---|---|
| Pending | `pending` |
| Paid | `paid` |
| Failed, Expired | `failed`, `expired` |
| Refunded | `refunded` |
| Posted | BUKAN status HF-03; penanda baru (mis. `jurnal_status` = posted) pada Donation |
| Settled | BUKAN status HF-03; penanda baru `settlement_status` pada Donation (H.2) |
| (tidak ada) chargeback | status baru yang diusulkan (E19) |

## I. Catatan review (verifikasi ulang temuan, 2026-11-22)

Tiap temuan diperiksa terhadap berkas 01, 03, 04, 05, HF-03 dan kode image `frappe/erpnext:version-16` (16.56.0; perintah baca-saja). "Diterima" = klaim terbukti dan diperbaiki di bagian yang disebut. Hal yang tidak terbukti ditandai.

**Hasil verifikasi kode (TERVERIFIKASI):**
- `financial_report_engine.py` baris 273-278: `group_by_dimension` pada Custom Financial Report memunculkan "currently unsupported"; `custom_financial_statement.js` hanya `add_dimensions`; `financial_statements.py` `build_period_list` melewati `get_dimension_period_list` bila `report_template` terisi. Dokumen 04 salah membaca (dikoreksi di 04 dan bagian E/C1/G).
- `gl_entry.validate_dimensions_for_pl_and_bs` hanya memeriksa dimensi tidak kosong; `journal_entry.set_total_debit_credit` hanya total debit = total kredit; tidak ada keseimbangan per dimensi (D0). `make_acc_dimensions_offsetting_entry` menyalin setiap GL Entry per dimensi dengan jumlah dibagi jumlah dimensi, bukan penyeimbang per Dana.
- `map_reverse_journal_entry` menolak pembalikan kedua dan pembalikan JE yang sendiri `reversal_of`; `get_mapped_doc` menyalin field bernama sama kecuali `no_copy` (D0).
- DocType `Campaign` CRM ada (field `campaign_name`, dst.); `accounting_dimension.py` menolak DocType yang sama dua kali (C2).
- `journal_entry.validate_party` mewajibkan party untuk Receivable/Payable (B); `validate_cheque_info` mewajibkan `cheque_no`/`cheque_date` untuk Bank Entry (D0); `payment_entry.py` baris ~625 mewajibkan Party Type (A12; di 04 diubah dari DUGAAN menjadi TERVERIFIKASI).
- `accounting_period.py` hanya mengunci jenis dokumen di `closed_documents` (E16). `general_ledger.validate_allowed_dimensions`: perilaku Allow/Restrict/is_mandatory persis seperti di temuan (C1 butir 5).

**Koreksi atas temuan:**
- Temuan "04 menyebut tidak ada 'frozen up to' dan grep `accounts_settings.json` kosong; mekanisme tidak terverifikasi" **hanya sebagian benar**: di v16 pengaturan ini sudah dipindah ke Company (`accounts_frozen_till_date`, `role_allowed_for_frozen_entries`; `general_ledger.py` baris ~852; patch `migrate_account_freezing_settings_to_company`). Jadi mekanisme alternatif ada dan terverifikasi (E16).
- Temuan "Payment Entry: kemungkinan tidak, belum diperiksa": sudah diperiksa, Party Type wajib; keputusan JE langsung terkonfirmasi (A12).
- Temuan "Mitra.total '37.606'": angka itu adalah total daftar Teman Sedekah (`data/teman.json`, HF-03 bag. 3), bukan total Mitra; inti temuan (snapshot raised/total tidak sama dengan GL) tetap berlaku (E20).
- Temuan "Payment Request tanpa fee": `Payment Method` punya `fee_flat`/`fee_percent` (konfigurasi per metode); yang belum ada adalah fee aktual per transaksi (H.2).
- Temuan "A2 vs E8": bukan kontradiksi murni; titipan zakat penghasilan liabilitas karena belum menjadi dana ZIS. Dibenarkan sebagian: labelnya diperjelas (E8) dan status "tidak diatur DE" dicantumkan.
- Temuan "posting_date pembalik default hari ini" dan "unique ifnull memperbolehkan NULL" **tidak dapat dikonfirmasi** dari bacaan terbatas; keduanya ditulis sebagai DUGAAN/perlu uji dengan tindakan aman (set posting_date eksplisit; jangan isi '') di D0.
- Temuan yang merujuk "03 bag.X" untuk data platform (Baik, Campaign, Donation, Penyaluran, Donor, Payment) sebenarnya merujuk HF-03 (handover), bukan `psak/03-standar-terkait.md`; rujukan dibedakan di bagian 0. Temuan itu terbukti benar (HF-03 tidak memuat field/doctype yang dibutuhkan), tetapi perbaikannya berupa usulan untuk handover (H.2), dan berkas HF-03 tidak diubah.

**Disposisi per temuan (ringkas):**

| Temuan | Disposisi | Bagian |
|---|---|---|
| E8/E10 tahap 2/E13 ujrah jurnal tidak seimbang per Dana | Diterima | E8, E10, E13, D0 |
| E4/E5 fee vs clearing AMIL; akun antar-dana | Diterima | E4, E5, B1, B2, F5, F28 |
| Fee ditanggung donatur tanpa jurnal lengkap | Diterima | E4, B2 (2-1340), E19 |
| 05 menyamakan piutang kanal dengan clearing | Diterima | E5, B1, F7 |
| Konflik 12,5%/20% 01 vs 03; 20% bukan tarif | Diterima | A5, E3, F6, L9 |
| Titipan/wakaf/qurban mencampur kas | Diterima | B1, E8, E12, E13, A8, L1 |
| Wakaf/Nonhalal dalam total aset neto L1 | Diterima | B3, L1, E12 |
| Model A/B/C belum diputuskan tetapi dipakai | Diterima | A8, F1, H.1 |
| Zakat muqayyadah sebagai aturan sistem | Diterima (diturunkan jadi USULAN) | A7, E3, F10, C1 |
| T/TT vs aset neto dengan/tanpa pembatasan | Diterima | B3, C1 |
| Akun tanpa jurnal | Diterima | E17, B1 |
| Rujukan tanpa sumber (settlement/capture, E-QRB-1); status E13 | Diterima | E2, E13 |
| 0 desimal dan clearing "sudah ketat" | Diterima | Bagian 0, D0 |
| Gaji amil, hadiah, fi sabilillah | Diterima | E3, B5, F26 |
| Bunga PUB vs nonhalal; tenggat 1 September | Diterima | E15, L10 |
| Template laporan tidak mendukung `group_by_dimension` | Diterima (terverifikasi) | Bagian E, C1, G, 04 |
| Alasan D0 keliru; auto-offsetting | Diterima (terverifikasi) | D0, 04 |
| Idempotensi vs perilaku Frappe | Diterima; dua butir DUGAAN | D0, E10, E14 |
| DocType `Campaign` bentrok | Diterima (terverifikasi) | C2 |
| Tipe akun Receivable-like | Diterima (terverifikasi) | B |
| voucher_type Bank Entry | Diterima (terverifikasi) | D0 |
| Mandatory dimension untuk modul lain | Diterima | C4 |
| Accounting Period dan pembekuan | Diterima dengan koreksi (Company) | E16 |
| Dimension Filter terbaca dari kode | Diterima | C1 |
| Pembulatan hak amil | Diterima | D0 |
| Saldo negatif Clearing AMIL | Diterima | E4 |
| Payment Entry bukan Payment Request | Diterima (terverifikasi) | A12 |
| Baik sponsor pool, Campaign fund_type/program, wakaf/fidyah campaign, Penyaluran, status Donation, payment types, upsell, Recurring makeup, saldo awal, reward | Diterima terhadap HF-03; perbaikan = gerbang + draf E17-E20 + usulan H.2 | E6, E7, E11, E18-E20, H |
| Status 05 vs HF-03; penomoran rujukan | Diterima | Bagian 0, H.3 |
