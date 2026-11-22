# sedekah-erp: Frappe 16 + ERPNext (lokal)

Stack Docker terpisah untuk keuangan platform donasi (pola PSAK 109 / PSAK 101).

- Web: http://127.0.0.1:8081 (hanya localhost). Site: `sedekah.localhost`. User: `Administrator`.
- Kata sandi ada di `.env` (tidak masuk git, mode 600).
- Image: `frappe/erpnext:version-16` (rolling), digest saat dibuat 2026-11-22:
  `sha256:15a1270f7d8d674de5facd16c3390665a12bd632f5abb846bdd67b61d7461d84`
  (frappe 16.56.0, erpnext 16.55.0). Untuk pin, ganti ERPNEXT_IMAGE di `.env` dengan `frappe/erpnext@sha256:...`.
- Database dan Redis tidak dibuka ke host. Nama project Compose: `sedekah-erp`.

## Perintah
    docker compose up -d          # nyalakan
    docker compose down           # matikan (data tetap di volume)
    docker compose exec backend bench --site sedekah.localhost console
    docker compose exec backend bench --site sedekah.localhost backup --with-files

Catatan: `down -v` MENGHAPUS data. Kalau backend 502 setelah restart, jalankan `docker compose restart frontend`.
Setup wizard (perusahaan, CoA) belum dijalankan: menunggu rancangan akun di `docs/psak/`.
