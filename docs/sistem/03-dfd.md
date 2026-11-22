# 03. Diagram Alur Data (DFD)

Notasi: persegi = entitas luar, lingkaran/bulat = proses, silinder = penyimpanan. Status: USULAN struktur; setiap proses sudah memiliki padanan kode (lihat 05).

## Level 0
```mermaid
flowchart LR
  DON([Donatur / Tamu]) -->|donasi, doa, amin, survei, misi, jadwal rutin| SYS((Sistem donasi))
  SYS -->|status, konten, riwayat, notifikasi| DON
  GW([Gateway pembayaran]) <-->|charge, webhook bertanda tangan| SYS
  MITRA([Mitra / pembagi tautan]) -->|tautan ref + utm| DON
  PET([Petugas Donasi]) -->|kelola konten, klaim hadiah, settlement| SYS
  AKT([Akuntan Donasi]) <-->|laporan per Dana, jurnal| SYS
  WA([WA/email gateway]) <-.OTP, pengingat (belum terhubung).-> SYS
```

## Level 1
```mermaid
flowchart TB
  UI([UI Vue / donatur]) --> P1((1 Akun & OTP))
  UI --> P2((2 Kampanye & konten))
  UI --> P3((3 Donasi & pembayaran))
  UI --> P4((4 Doa, Amin, notifikasi))
  UI --> P5((5 Survei, misi, gamifikasi))
  UI --> P6((6 Shadaqa Rutin))
  P1 --- D1[(Donor, User, OTP)]
  P2 --- D2[(Kampanye, Mitra, Penyaluran, Artikel, Video, Banner, Legal)]
  P3 --- D3[(Donation, Permintaan Pembayaran, Metode)]
  P4 --- D4[(Doa Amin)]
  P5 --- D5[(Survei, Misi, Pool, Sesi, Hadiah, Klaim)]
  P6 --- D6[(Jadwal Rutin, Eksekusi, Log)]
  GW([Gateway]) --> P3
  P3 --> P7((7 Mesin jurnal PSAK))
  P7 --- D7[(Journal Entry, GL, Dana, Kampanye)]
  P6 --> P3
  P4 --> D3
```

## Level 2 — proses kritis: webhook sampai jurnal (proses 3 + 7)
```mermaid
flowchart TB
  W([Gateway]) -->|order_id, status, gross, signature| V{3.1 Verifikasi tanda tangan SHA-512}
  V -->|tidak valid / kunci tak ada| X[tolak 403]
  V -->|valid| M{3.2 Order ada & jumlah cocok?}
  M -->|tidak| X2[tolak]
  M -->|ya| S{3.3 Status Permintaan sudah paid?}
  S -->|ya| N[noop - idempoten]
  S -->|tidak| P[3.4 Donation Pending->Paid]
  P --> G{7.1 Gerbang H.1: posting_enabled, model A, bukan wakaf/fidyah/qurban, program, kampanye utk infak terikat}
  G -->|tertutup| H[tetap Paid tanpa jurnal]
  G -->|lulus| E2[7.2 E2 penerimaan per Dana]
  E2 --> E3[7.3 E3 hak amil - Decimal half-up]
  E3 --> K[(donation_ref unik: DON-x:RECEIPT / :AMIL)]
```

## Level 2 — proses Shadaqa Rutin harian (proses 6)
```mermaid
flowchart LR
  C([Scheduler harian]) --> Q[6.1 Pilih jadwal Aktif dengan next_run <= hari ini]
  Q --> I{6.2 Eksekusi tanggal itu sudah ada?}
  I -->|ya| R[pakai Donation yang ada]
  I -->|tidak| T[6.3 Buat Donation Pending + baris Eksekusi]
  T --> L[6.4 Catat Log Pengingat per kanal aktif]
```
