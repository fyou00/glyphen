# Antarmuka lokal Glyphen

Jenis: aplikasi software lokal untuk pemilik glyph bank. Tujuan utama: mengubah teks menjadi dokumen tulisan tangan, memeriksa setiap halaman, lalu mengunduh PDF atau PNG.

Satu ruang kerja, bukan halaman promosi: editor di kiri dan kertas A4 di kanan, ditumpuk pada layar sempit. Warna kertas putih, latar abu-abu kehijauan, tinta gelap, dan tombol hijau membedakan tindakan dari dokumen. Judul dan wordmark memakai Georgia lokal; isi dan kontrol memakai font sistem. Tidak memakai foto, logo pihak lain, font jaringan, shader, atau panel statistik dekoratif. Gerak terbatas pada kemunculan awal, respons tombol, dan indikator proses; reduced motion dihormati.

Copy menggunakan Bahasa Indonesia langsung: label menyebut isi, tombol menyebut tindakan, pesan kesalahan menyebut langkah berikutnya. Fakta yang ditampilkan berasal dari aplikasi: profil aktif, margin, ukuran A4, jumlah halaman, durasi, dan karakter yang hilang. Teks awal hanya contoh catatan netral yang dapat diedit.

## Menjalankan

```bash
python -m pip install -r requirements.txt
python app.py --port 8010
```

Buka `http://127.0.0.1:8010/`. Untuk pengujian, pasang `requirements-dev.txt`, lalu jalankan `python -m unittest discover -s tests -v`.

## Perilaku

- Profil dipilih dari dropdown. `--user <id>` tetap tersedia sebagai pilihan profil awal opsional; tanpa profil, tombol Tambah profil tetap dapat digunakan. Bank lama dikenali tanpa memindahkan glyph.
- Tambah profil menyimpan nama/alias dan persetujuan tulisan sendiri di JSON sebelum menerima tiga JPEG/PNG TPL-01/02/03. Setiap gambar maksimal 10 MiB/20 megapiksel, dapat diputar 0/90/180/270° searah jarum jam. Orientasi EXIF dinormalisasi dan metadata gambar dibuang; sumber disimpan sebagai PNG RGB dalam folder profil.
- Rotasi sampel memakai dua tombol panah: kiri untuk berlawanan arah jarum jam dan kanan untuk searah jarum jam, masing-masing 90° per klik. Sudut saat ini ditampilkan dan pratinjau langsung mengikuti; tombol aktif setelah gambar dipilih dan dinonaktifkan selama pemrosesan.
- Setelah ekstraksi, pemilik wajib memeriksa tiga debug dan menerima setiap potongan touches_edge. Tinjauan salah menghentikan proses; coverage baru dihitung setelah tinjauan lolos. Jika huruf kurang dari 3 varian, label/halaman dilaporkan dan tiga gambar dapat diupload ulang. Halaman lain boleh menggunakan scan sebelumnya; tidak ada penggandaan varian untuk mengisi kekurangan.
- Ikon pensil mengedit nama tampilan, sementara ID dan identitas persetujuan awal tetap. Ikon keranjang sampah meminta konfirmasi sebelum menghapus profil beserta sumber, percobaan, glyph, arsip, dan hasil lokal yang terkait. Pemilik lain tidak dihapus. Unduhan di luar penyimpanan proyek perlu dihapus sendiri.
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
| `GET /api/profile?user_id=…` | Kesiapan profil pilihan atau profil awal, tanpa mengirim pernyataan persetujuan atau path pribadi |
| `GET/POST /api/profiles` | Daftar profil dan pilihan awal / buat profil dengan `display_name`, `consent: true` |
| `GET/PATCH/DELETE /api/profiles/{id}` | Detail / ubah `display_name` / hapus dengan `confirm: true` |
| `POST /api/profiles/{id}/samples` | Multipart `tpl01`, `tpl02`, `tpl03`, `rotation1/2/3`, dan `owner_confirmation=true` pada setiap upload untuk profil yang belum siap |
| `POST /api/profiles/{id}/review` | `crops_correct`, tiga `pages_checked`, dan `accepted_edges` per label/varian; aktifkan hanya setelah coverage valid |
| `GET /api/profiles/{id}/debug/{page}` | Gambar debug halaman 1/2/3 untuk tinjauan |
| `GET /api/profiles/{id}/glyph/{label}/{variant}` | Potongan glyph terdaftar untuk tinjauan tepi |
| `POST /api/render` | Body JSON `user_id`, `text`, `doc_type`, `seed`, `guidelines`; hasil berupa tautan PDF/PNG serta statistik. ID eksplisit dari UI, fallback profil awal untuk klien lama. |
| `GET /api/renders/{id}/{filename}` | Berkas hasil yang terdaftar; `?download=true` untuk lampiran |

Server hanya mendengarkan loopback. Host lokal dan Origin diperiksa; tidak membuka CORS untuk situs lain. Header CSP membatasi sumber ke aplikasi sendiri, dengan `blob:` hanya untuk pratinjau file lokal sebelum upload; respons pribadi memakai `Cache-Control: no-store`. Nama/path bebas dan akses manifest/consent melalui rute unduhan ditolak. Ini aplikasi lokal yang dapat mengelola beberapa profil/alias tulisan sendiri, tanpa autentikasi akun atau deployment publik.

Sumber percobaan berada dalam `glyph_bank/<id>/sources/`. Penghapusan juga mengenali `glyph_bank/history/<id>/`, `render_report.json` milik profil, serta direktori sumber/artefak yang memiliki metadata pemilik (`owner.json` atau metadata terkait). Direktori campuran tidak menghapus dokumen pemilik lain; berkas milik pemilik yang dihapus dibersihkan sesuai marker. Salinan lama yang tidak memiliki metadata kepemilikan perlu diidentifikasi terlebih dahulu; tidak menebak berdasarkan kemiripan gambar. Artefak sesi awal yang diketahui milik profil lama diberi marker lokal, tanpa mengubah gambar atau menghapus data saat pemasangan fitur.

## Verifikasi

Pengujian API memakai bank buatan sementara, termasuk bank lama, render/unduhan, validasi input/Origin/Host, profil baru, persetujuan, rotasi, pembuangan EXIF, gambar invalid/besar/duplikat, tinjauan yang belum lengkap, coverage kurang, upload ulang, rename tanpa perubahan ID, serta penghapusan sumber/arsip/turunan dengan isolasi pemilik lain. Pengujian renderer dan audit sebelumnya tetap dijalankan. Uji browser memakai halaman buatan untuk alur tambah–tinjau–aktifkan–rename–render–hapus; bukan sampel orang lain atau penilaian persepsi. Bukti pemeriksaan serta pratinjau disimpan lokal dalam `outputs/ui-checks/`; hasilnya dicatat di `EVALUATION.md`.

### Riwayat pemeriksa desain antarmuka awal (D-023)

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
