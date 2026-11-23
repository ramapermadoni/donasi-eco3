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

## Halaman yang membaca dari server setelah dibersihkan
Beranda, Kampanye, Mitra, dan Video (lewat `/api/content/bundle`), serta **Detail Penyaluran** (`/api/penyaluran/:slug`), **Detail Artikel** (`/api/artikel/:slug`, termasuk artikel terkait), **nominal terkumpul dan persentase** di Detail Kampanye (angka persis dari donasi berstatus Paid, diambil setiap halaman dibuka lewat `/api/campaigns/:slug`), dan **Kabar terbaru** tiap kampanye (`/api/campaigns/:slug/updates`, yaitu Penyaluran yang diikat ke kampanye). Kabar kampanye muncul dengan mengisi field Kampanye pada dokumen Penyaluran.

## Doa: selalu dari server
Halaman Doa dan bagian Doa di Beranda **selalu** membaca dari server (donasi berstatus Paid yang berisi ucapan doa), tanpa menunggu konten contoh dibersihkan. Alasannya: `doa.json` berisi doa dan nama pengguna situs lain, bukan konten contoh biasa. Berkas itu hanya dipakai di mode demo (`VITE_REAL_API=0`). Tombol "Aminkan" tersimpan di server (maksimal 10 per orang per doa), dan nama donatur di API publik selalu disamarkan ("T*** D***"). Sebelum ada donasi berisi doa, halaman menampilkan "Belum ada doa."

**Moderasi:** Petugas Donasi dan System Manager membuka laporan Desk **Moderasi Doa**, lalu menekan **Sembunyikan** pada doa yang tidak pantas (alasan wajib, tercatat siapa dan kapan) atau **Tampilkan** untuk membatalkan. Doa tersembunyi hilang dari halaman Doa, Beranda, dan tidak bisa diaminkan; data donasinya tetap utuh. Doa tidak disaring otomatis, jadi tinjau laporan ini secara berkala.

## Yang BELUM ikut berpindah ke server
Halaman berikut masih membaca berkas statis di dalam bundel UI. Isinya tetap konten contoh sampai disambungkan:
- Gamifikasi, misi Jalan Kebaikan, dan teks kampanye berbahasa Inggris.
- Halaman Qurban (`data/qurban.js`).
Setelah dibersihkan, halaman-halaman itu bisa menampilkan isi yang tidak cocok dengan data server. Sambungkan sebelum rilis, atau sembunyikan menunya.

## Bila perlu mengulang
Hapus centang "Konten contoh sudah dibersihkan" di Pengaturan Donasi, lalu jalankan `bench execute donasionline.setup.import_snapshot.run`. Itu membuat ulang konten contoh yang hilang.
