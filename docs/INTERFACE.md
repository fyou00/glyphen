# Antarmuka lokal Glyphen

Jenis: aplikasi software lokal untuk pemilik glyph bank. Tujuan utama: mengubah teks menjadi dokumen tulisan tangan, memeriksa setiap halaman, lalu mengunduh PDF atau PNG.

Satu ruang kerja, bukan halaman promosi: editor di kiri dan kertas A4 di kanan, ditumpuk pada layar sempit. Warna kertas putih, latar abu-abu kehijauan, tinta gelap, dan tombol hijau membedakan tindakan dari dokumen. Judul dan wordmark memakai Georgia lokal; isi dan kontrol memakai font sistem. Tidak memakai foto, logo pihak lain, font jaringan, shader, atau panel statistik dekoratif. Gerak terbatas pada kemunculan awal, respons tombol, dan indikator proses; reduced motion dihormati.

Copy menggunakan Bahasa Indonesia langsung: label menyebut isi, tombol menyebut tindakan, pesan kesalahan menyebut langkah berikutnya. Fakta yang ditampilkan berasal dari aplikasi: profil aktif, margin, ukuran A4, jumlah halaman, durasi, dan karakter yang hilang. Teks awal hanya contoh catatan netral yang dapat diedit.

## Menjalankan

```bash
python -m pip install -r requirements.txt
python app.py --user <id> --port 8010
```

Buka `http://127.0.0.1:8010/`. Untuk pengujian, pasang `requirements-dev.txt`, lalu jalankan `python -m unittest discover -s tests -v`.

## Perilaku

- Profil dipilih melalui `--user` saat server dimulai. Tidak ada pemilihan bank orang lain atau upload sampel melalui UI ini.
- Profil harus memiliki persetujuan, coverage, dan tinjauan glyph yang valid. Jika belum siap, tombol render dinonaktifkan.
- Halaman awal berisi teks netral dan membuat pratinjau lokal melalui API render. Pengguna dapat mengosongkan teks atau menggantinya. Batas isi 12.000 karakter.
- Pilihan catatan/surat mengikuti margin engine. Opsi seed dapat dikosongkan untuk variasi acak; garis panduan hanya aktif untuk catatan.
- Tombol render atau Cmd/Ctrl+Enter membuat PDF dan PNG. Indikator proses tampil selama render. Teks dapat diedit saat proses berjalan; hasil lama ditandai perlu diperbarui dan unduhannya dinonaktifkan.
- Pratinjau mendukung halaman sebelumnya/berikutnya serta pembesaran. Unduh PNG mengikuti halaman yang sedang dilihat; unduh PDF mencakup seluruh dokumen.
- Karakter yang tidak tersedia ditampilkan dalam peringatan; placeholder engine tetap berada pada posisinya. Watermark tidak dapat dinonaktifkan.
- Tidak ada autosave atau localStorage teks. Request body tidak dicatat ke log. Setiap hasil berada di `outputs/ui/<id-acak>/`, tidak menimpa dokumen lain dan diabaikan Git. Tidak ada layanan pihak ketiga yang dipanggil oleh halaman.

## API

| Metode / rute | Fungsi |
|---|---|
| `GET /` | Editor lokal |
| `GET /api/profile` | Kesiapan profil tanpa mengirim pernyataan persetujuan atau path pribadi |
| `POST /api/render` | Body JSON `text`, `doc_type`, `seed`, `guidelines`; hasil berupa tautan PDF/PNG serta statistik |
| `GET /api/renders/{id}/{filename}` | Berkas hasil yang terdaftar; `?download=true` untuk lampiran |

Server hanya mendengarkan loopback. Host lokal dan Origin diperiksa; tidak membuka CORS untuk situs lain. Header CSP membatasi sumber ke aplikasi sendiri, dan respons pribadi memakai `Cache-Control: no-store`. Nama/path bebas dan akses manifest/consent melalui rute unduhan ditolak. Ini aplikasi lokal satu pemilik, tanpa autentikasi multi-pengguna atau deployment publik.

## Verifikasi

Lima metode uji API memakai bank buatan sementara: halaman/profil, render serta berkas unduhan, validasi input/Origin/Host, bank yang belum siap, dan dokumen multipage dengan hasil terisolasi. Pengujian renderer dan audit sebelumnya tetap dijalankan. Bukti pemeriksaan browser serta pratinjau disimpan lokal dalam `outputs/ui-checks/`; hasil pemeriksaan akhir dicatat di `EVALUATION.md`.

### Laporan pemeriksa desain

`GATE: OPEN 15 (rounds used up)` — gate desain belum lulus. Pemeriksa ini ditujukan untuk landing page satu section per layar; aplikasi ini merupakan editor dua panel yang dapat digulir. Tidak menyatakan seluruh pemeriksaan visual lulus.

Temuan terbuka: `hero-screen`, `section-height`, `screen-short`, dan `hero-fold` menuntut ukuran hero/section tepat satu layar; `container-edges` dan `edge-left` menuntut heading serta teks panel berada di tepi container luar; `fold-action` mengharuskan unduhan PDF tampil pada layar ponsel pertama. Sebanyak 15 temuan mencakup pengulangan target aturan tersebut. Panel editor/pratinjau memiliki padding serta heading sendiri, dan unduhan berada setelah pratinjau pada ponsel. Layout ini dipertahankan untuk alur aplikasi, bukan dipaksakan menjadi halaman promosi.

Lima waiver dicatat secara eksplisit:

- `no-visual`: area editor berisi kontrol yang berfungsi dan pratinjau dokumen nyata; tidak membutuhkan rasio gambar hero promosi.
- `copy-actions`: aplikasi memerlukan render serta dua format unduhan, bukan batas dua CTA pemasaran.
- `hero-enter`: judul memiliki animasi masuk sendiri dan reduced motion; tidak memakai bootstrap `m-enter` kit.
- `moment-none`: tidak menambahkan section efek dekoratif pada ruang kerja editor.
- `one-heading`: heading Catatanmu dan Pratinjau diperlukan untuk membagi panel dan navigasi pembaca layar.

Temuan fungsi/akses yang sempat terdeteksi—kontras footer, radio tidak terlihat, tiga gaya tombol, tepi ponsel, dan posisi tombol tetap yang terikat animasi—sudah diperbaiki. Tombol utama pada viewport 390 × 844 diverifikasi berada sampai y=830, tetap di dalam layar, tanpa overflow horizontal. Pada viewport desktop yang pendek, pengguna dapat menggulir editor. Tidak ada foto stok, angka hasil uji palsu, kontak contoh, atau slot media klien yang belum diisi; seluruh visual utama adalah hasil engine lokal.

Dua belas warning tetap dicatat: `copy-headings`/`copy-buttons` tidak mengenali istilah Indonesia Pratinjau/Unduh; `stranded-action` menilai unduhan yang ditempatkan di sisi kanan toolbar; `copy-length` menghitung teks/kontrol editor sebagai copy promosi; `skip-link` tidak mengenali tautan pertama yang menuju form editor; `share-meta` karena aplikasi lokal tidak memakai metadata berbagi sosial; `tap-size` pada wordmark setinggi 32 piksel; `no-visual` untuk rasio kertas di ponsel; `off-grid` untuk inset footer 3 piksel; `proximity` untuk toolbar yang berdekatan dengan dokumen; `photo-weight` karena pratinjau memakai PNG 300 DPI yang sama dengan unduhan; dan `fold-action` untuk unduhan PNG yang berada setelah pratinjau. Tidak ada warning yang disembunyikan dari checker.

Uji browser fungsi berhasil, termasuk render tiga halaman, peringatan karakter hilang, unduhan kedua format, navigasi, zoom, hasil usang, pemulihan error, dan shortcut keyboard. Pemeriksaan performa terpisah menghasilkan 0 FAIL/5 WARN: cat pertama sekitar 456 ms desktop dan 384 ms ponsel pada mesin uji, dengan layout shift 0 dan tidak ada request rusak. Warning gambar berdimensi ekspor besar, belum memiliki atribut width/height, dan tidak lazy pada ponsel dicatat sebagai batas optimasi; pratinjau lokal tetap tampil dan ruang kertas sudah dicadangkan oleh aspect ratio.
