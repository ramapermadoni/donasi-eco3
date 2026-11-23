# Mengganti konten contoh dengan konten Anda

Instalasi baru membawa **konten contoh**: kampanye, mitra, banner, video, penyaluran, dan artikel salinan dari situs asal. Isinya cerita nyata lembaga lain (DT Peduli dan mitranya), jadi **wajib diganti sebelum dibuka ke publik**.

## Cara kerjanya
- Setiap konten contoh bertanda `is_sample = 1` (kotak "Konten contoh" di Desk). Yang Anda buat sendiri bertanda 0 dan tidak pernah disentuh.
- Kampanye inti (`sedekah`, `zakat-*`, `wakaf-umum`, `fidyah`) dipakai sistem dan **tidak pernah dianggap contoh**.
- Sebelum dibersihkan, UI memakai berkas statis bawaan (tampilan tidak berubah). Setelah dibersihkan, UI membaca kampanye, banner, mitra, dan video dari server lewat `GET /api/content/bundle`.

## Langkah
1. **Isi konten Anda dulu** di Desk: Kampanye Donasi, Mitra, Banner, Video Donasi, Penyaluran, Artikel. Biarkan "Konten contoh" tak dicentang.
2. **Lihat ringkasannya:**
   ```
   docker compose exec backend bench --site <site> execute donasionline.setup.konten_contoh.ringkasan
   ```
3. **Simulasi** (tidak mengubah apa pun), periksa daftar yang akan dihapus:
   ```
   docker compose exec backend bench --site <site> execute donasionline.setup.konten_contoh.bersihkan
   ```
4. **Bersihkan sungguhan** (cadangkan database dulu; tidak bisa dibatalkan):
   ```
   docker compose exec backend bench --site <site> execute donasionline.setup.konten_contoh.bersihkan --kwargs "{'dry_run': 0}"
   ```
   Hasilnya: konten contoh dihapus; kampanye contoh yang **sudah punya donasi atau jadwal rutin tidak dihapus** (catatan keuangan), hanya dinonaktifkan (tidak tampil, tidak bisa dibayar); mitra contoh yang masih dirujuk dipertahankan dan dilaporkan; sakelar "konten contoh sudah dibersihkan" menyala sehingga impor snapshot tidak membuatnya ulang.
5. Muat ulang situs dan periksa Beranda, Kampanye, Mitra, dan Video.

## Yang BELUM ikut berpindah ke server
Halaman berikut masih membaca berkas statis di dalam bundel UI dan belum membaca dari server. Isinya tetap konten contoh sampai disambungkan:
- **Detail Penyaluran** dan **Detail Artikel** (daftarnya sudah dari server, detailnya belum).
- **Kabar terbaru** di tiap kampanye (`data/kabar.json`).
- **Doa**, gamifikasi, misi Jalan Kebaikan, dan teks kampanye berbahasa Inggris.
- Nominal "terkumpul" di Detail Kampanye masih tabel bawaan (`RAISED`).
Setelah dibersihkan, halaman-halaman ini bisa menampilkan cerita yang tidak cocok dengan data server. Sambungkan sebelum rilis, atau sembunyikan menunya.

## Bila perlu mengulang
Hapus centang "Konten contoh sudah dibersihkan" di Pengaturan Donasi, lalu jalankan `bench execute donasionline.setup.import_snapshot.run`. Itu membuat ulang konten contoh yang hilang.
