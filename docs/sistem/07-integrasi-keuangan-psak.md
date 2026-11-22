# 07. Integrasi Platform dengan Keuangan (PSAK 409/401)

Semua aturan akuntansi berstatus **USULAN/PROVISIONAL** sampai akuntan/ahli syariah menjawab F1-F29 (`docs/psak/`). Posting otomatis mati bawaan (`Pengaturan Donasi.posting_enabled = 0`).

## Pemetaan data platform -> jurnal (FAKTA di kode)
| Platform | Efek keuangan |
|---|---|
| Donation Pending | tidak ada jurnal (E1) |
| Donation Paid | E2: Dr Clearing[gateway] / Cr 4-1100|4-1200 (zakat), 4-2100 (infak bebas), 4-2200 (infak terikat) — dimensi Dana, Program (Cost Center), Kampanye |
| setelah E2 | E3: hak amil (`h_zakat` 12,5% provisional, `h_infak` 0): pasangan beban penyaluran/penghasilan bagian amil + pindah clearing antar-Dana |
| fee gateway | E4: beban Dana Amil, ditahan bila saldo clearing AMIL kurang |
| settlement | E5: per Dana Dr Bank / Cr Clearing |
| Doa, Amin, survei, misi, gamifikasi, rutin (jadwal) | tidak ada jurnal |
| Jalan Kebaikan klaim voucher | **tidak ada Donation dan tidak ada jurnal** (E18 diblokir sampai F22) |
| Rutin | Donation per eksekusi mengikuti aturan donasi biasa |

## Gerbang H.1 (di `journals.check_gate`)
`posting_enabled`, model A (F1), jenis dana bukan wakaf/fidyah/qurban (F4), program wajib, kampanye wajib untuk infak terikat, jumlah > 0. Pelanggaran -> `PostingBlocked`; Donation tetap tercatat dan dapat diposting ulang setelah gerbang dibuka.

## Titik yang belum dihubungkan
- Pemicu E4 (fee) dan E5 (settlement) dari data gateway/rekening koran: fungsi ada (`post_fee`, `settle`), belum ada penjadwal/impor yang memanggilnya.
- Jenis dana kampanye hasil impor = `infak_bebas` (PROVISIONAL); pengelola harus menetapkan `infak_terikat` per kampanye yang memang terikat.
- Refund (E10), penyaluran (E6), titipan (E8) belum.
