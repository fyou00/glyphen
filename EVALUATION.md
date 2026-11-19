# EVALUATION: Pengukuran Kualitas

Dokumen ini menjelaskan cara mengukur sistem dan mencatat hasilnya. Target yang belum diuji ditandai sebagai perkiraan. Jangan menyatakan sebuah target tercapai sebelum ada data yang mendukungnya.

## 1. Tujuan evaluasi

Ada tiga pertanyaan yang harus dijawab:
1. Apakah ekstraksi glyph akurat dan cukup lengkap?
2. Apakah hasil render terlihat seperti tulisan tangan pemiliknya?
3. Apakah render cukup cepat untuk dipakai dalam jumlah banyak?

## 2. Metrik

### 2.1 Ekstraksi (tahap PIPELINE)

| Metrik | Cara hitung | Target awal |
|---|---|---|
| Kotak `ok` | jumlah kotak status `ok` / total kotak | ≥ 90% |
| Kotak `empty` | jumlah kotak status `empty` / total kotak | ≤ 5% |
| Kotak `touches_edge` | jumlah kotak status `touches_edge` / total kotak | ≤ 5% |
| Coverage per label | jumlah varian `ok` atau `touches_edge` per label | ≥ 3 untuk semua huruf a–z dan A–Z |
| Ketepatan pemotongan | kotak yang terpotong benar dari total kotak yang diperiksa visual | ≥ 98% pada sampel periksa |

Ketepatan pemotongan dihitung dengan memeriksa `debug_page*.png` secara manual. Pemeriksa menandai kotak yang salah potong (garis ikut terpotong, bagian kotak tidak masuk, atau dua kotak tergabung).

### 2.2 Render (tahap RENDER)

| Metrik | Cara hitung | Target awal |
|---|---|---|
| Waktu render per halaman A4 | rata-rata dari 10 kali render | < 2 detik |
| Karakter tidak tersedia | jumlah karakter yang tidak punya glyph / total karakter | 0 untuk teks uji standar |
| Variasi antar-instance | simpangan baku lebar glyph untuk label yang sama | > 0 (glyph tidak identik) |
| Tumpang tindih karakter | jumlah pasangan karakter yang bertumpuk | 0 |

### 2.3 Persepsi (uji manusia)

Metrik ini paling penting untuk tujuan produk, tetapi juga paling sulit diukur.

Protokol:
1. Siapkan 20 pasangan gambar. Setiap pasangan berisi satu halaman tulisan asli pemilik dan satu halaman hasil render dengan teks yang sama.
2. Tampilkan pasangan secara acak kepada minimal 10 penilai yang tidak mengetahui mana yang asli.
3. Penilai menjawab: "Mana yang ditulis tangan?" dan memberi skor 1 sampai 5 untuk kemiripan dengan tulisan pemilik.
4. Hitung persentase jawaban benar dan rata-rata skor kemiripan.

Target awal: penilai menebak dengan benar pada 50% sampai 65% kasus. Angka di bawah 50% berarti hasil tidak bisa dibedakan dari tulisan asli, sedangkan angka di atas 80% berarti render masih mudah dikenali.

Catatan: target ini bisa berbeda untuk tujuan lain. Untuk dokumen yang tampak ditulis tangan, ini tetap tujuan utama.

Kewajiban watermark tetap berlaku selama evaluasi. Watermark yang terlihat dapat membocorkan panel hasil render, sehingga uji tebak tidak boleh dilaporkan sebagai uji buta dalam kondisi itu. Protokol persepsi perlu ditetapkan sebelum mengambil skor; usulan penilaian terbuka kemiripan/keterbacaan 1–5 menunggu keputusan pemilik project. Persentase tebakan di bawah 50% saja juga bukan bukti bahwa tulisan tidak dapat dibedakan; jumlah sampel dan bias penilaian harus diperhitungkan.

## 3. Protokol uji

### 3.1 Uji ekstraksi
1. Cetak `template_tulisan_A4.pdf`.
2. Isi satu halaman sesuai `TEMPLATE.md`.
3. Foto dengan HP, kondisi cahaya normal, dan jarak sekitar 30 cm.
4. Jalankan `extract_glyphs.py` dan catat hasilnya.
5. Periksa `debug_page*.png` dan hitung ketepatan pemotongan.
6. Ulangi dengan cahaya lebih redup dan foto sedikit miring untuk melihat ketahanan.

### 3.2 Uji render
1. Gunakan teks uji standar (lihat bagian 5).
2. Render minimal 10 kali dengan `seed` berbeda.
3. Catat waktu render, jumlah karakter tidak tersedia, dan tumpang tindih.
4. Periksa hasil secara visual untuk tiga kasus: huruf kecil, kapital, dan angka.

### 3.3 Uji persepsi
Ikuti bagian 2.3.

## 4. Riwayat hasil

Isi bagian ini setiap kali ada uji. Jangan menghapus entri lama.

### Uji 0: belum dilakukan
- Status: menunggu template dicetak dan diisi.
- Catatan: tidak ada data nyata saat dokumen ini dibuat.

### Pemeriksaan teknis template: 2026-11-19
- Skrip awal gagal dengan `SyntaxError` karena bagian akhirnya terpotong.
- Setelah pemulihan, `.venv/bin/python make_template.py` berhasil membuat PDF dengan tiga objek halaman A4.
- Stream konten setiap halaman didekompresi dan dibandingkan dengan PDF awal: ketiganya identik, termasuk geometri kotak dan marker.
- Pemeriksaan ini bukan uji ekstraksi atau uji cetak. Belum ada foto nyata, `debug_page*.png`, statistik status kotak, atau coverage pengguna.
- Tindak lanjut: pengguna mencetak template pada ukuran 100%, mengisi TPL-01, lalu menyediakan foto dengan empat marker terlihat beserta ID pemilik dan persetujuan pemrosesan.
- Keputusan terkait: D-015.

### Pemeriksaan dua kotak kalimat contoh: 2026-11-19
- PDF dibuat ulang dengan `.venv/bin/python make_template.py` dan tetap memiliki tiga halaman A4.
- Stream konten TPL-01 dan TPL-02 identik dengan versi sebelum pengurangan kotak.
- Pemeriksaan persegi panjang pada stream TPL-03 memastikan tepat dua kotak contoh 180 × 12 mm, pada posisi dua kotak pertama versi sebelumnya. Seluruh persegi panjang kotak glyph dan marker tetap identik.
- Sintaks `make_template.py` dan `extract_glyphs.py` valid. Belum dilakukan uji cetak atau ekstraksi foto nyata.
- Keputusan terkait: D-016.

### Uji 1: ekstraksi tiga scan nyata, 2026-11-19
- Sampel: tiga scan template lama enam kotak; area kalimat contoh tidak diekstrak. Identitas dan persetujuan pemilik disimpan lokal di JSON, terpisah dari gambar.
- Praproses: TPL-01 diputar 180°; TPL-02 dan TPL-03 tetap. Gambar asli dipertahankan di `scan_demo/originals/`; PNG kerja tanpa metadata EXIF disimpan di `scan_demo/`.
- Percobaan awal: TPL-01 gagal dengan 0 marker. Perbaikan parsial masih gagal pada TPL-02 dengan 3 marker. Setelah D-017, empat marker terdeteksi pada setiap halaman.

| Halaman | Total | ok | empty | touches_edge |
|---|---:|---:|---:|---:|
| TPL-01 | 130 | 60 | 0 | 70 |
| TPL-02 | 130 | 130 | 0 | 0 |
| TPL-03 | 63 | 59 | 0 | 4 |
| Total | 323 | 249 | 0 | 74 |

- Rasio status: ok 77,09%; empty 0%; touches_edge 22,91%. Target ok ≥90% dan touches_edge ≤5% belum tercapai.
- Jumlah kotak kosong setiap label: 0. Rincian per label tersimpan lokal dalam `extraction_report.json` bersama manifest dan glyph.
- `debug_page1.png`, `debug_page2.png`, dan `debug_page3.png`, serta lembar tinjauan seluruh potongan glyph, sudah diperiksa visual. Posisi kotak tampak sejajar, tetapi inset memotong sebagian tinta di bawah pada sejumlah glyph TPL-01, antara lain b, d, dan p varian pertama. Status `touches_edge` disimpan untuk ditinjau dan bukan jaminan glyph utuh.
- Hasil tinjauan: gagal; tidak melanjutkan ke validasi coverage atau render. `coverage.json` belum dibuat. Ketepatan pemotongan belum diberi angka karena tiap potongan belum diberi penilaian lulus/gagal satu per satu.
- Tindak lanjut: tinjau strategi pemotongan dengan foto asli sebelum menentukan perlu penyesuaian inset atau pengisian ulang. Parameter pemotongan belum diubah.
- Verifikasi teknis: uji marker pejal diterima dan kotak garis ditolak; 323 file glyph ada. Tidak ada pengukuran waktu render atau uji persepsi.
- Keputusan terkait: D-017.

### Uji 2: scan pengganti TPL-01 dan TPL-03, 2026-11-19
- Gunakan `Scan.jpeg` baru untuk TPL-01 dan `Scan 1.jpeg` baru untuk TPL-03. Keduanya sudah tegak sehingga tidak diputar. TPL-02 memakai scan sebelumnya. Persetujuan pemilik tetap berlaku; identitas dan pemetaan sumber disimpan dalam JSON lokal.
- Input baru disimpan di `scan_demo/attempt02/`; hasil pertama diarsipkan di `glyph_bank/history/`. Hasil baru berada di glyph bank aktif. Tidak ada perubahan algoritme, threshold, atau inset.

| Halaman | Total | ok | empty | touches_edge |
|---|---:|---:|---:|---:|
| TPL-01 | 130 | 126 | 0 | 4 |
| TPL-02 | 130 | 130 | 0 | 0 |
| TPL-03 | 63 | 63 | 0 | 0 |
| Total | 323 | 319 | 0 | 4 |

- Rasio ok 98,76%, empty 0%, touches_edge 1,24%; ketiganya memenuhi target status awal pada sampel ini. Jumlah touches_edge turun dari 74 menjadi 4.
- Ketiga debug diperiksa: kotak sejajar. Potongan TPL-01 dan TPL-03 ditinjau ulang; TPL-02 identik hasil sebelumnya. Empat potongan bertanda (`lower_d` varian 4, `lower_g` varian 1 dan 5, `lower_p` varian 1) dibandingkan dengan kotak penuh: tinta tampak utuh, hanya dekat batas crop. Status tetap dipertahankan untuk keterlacakan; tinjauan lulus.
- Coverage dicatat dalam `coverage.json`: 52/52 huruf punya 5 varian; 21 label angka/tanda baca punya 3 varian. Tidak ada label di bawah minimum atau target ideal; jumlah kosong setiap label 0. Penghitungan mengikuti aturan ok + touches_edge, dengan empat tanda tepi telah ditinjau.
- Verifikasi: 323 file glyph tersedia dan manifest TPL-02 identik percobaan pertama. `extraction_report.json` menyimpan rincian label dan hasil tinjauan. Tidak ada varian yang disalin untuk menambah coverage.
- Batas: belum menghitung ketepatan pemotongan sebagai persentase dari anotasi per kotak; belum mengukur variasi antar-instance, performa render, atau persepsi. Engine render belum dikerjakan pada percobaan ini.

### Uji 3: engine render awal dan 10 seed, 2026-11-19
- Engine `render_document.py` memakai glyph bank hasil Uji 2 yang sudah memenuhi coverage dan tinjauan visual. Contoh diary netral menghasilkan satu PDF A4 dan PNG 2480 × 3508 piksel pada 300 DPI, dengan 165 instance glyph dan tanpa karakter hilang.
- Contoh diary ditinjau pada PNG dan hasil rasterisasi PDF melalui PDFKit macOS. Tulisan dan watermark tampak; PDFKit mengonfirmasi ukuran A4 dan watermark sebagai teks halaman. Ini belum merupakan uji persepsi kemiripan atau uji cetak.
- Sebelas pengujian otomatis dengan bank buatan sementara lulus: normalisasi, persetujuan/identitas/tinjauan, isolasi path pengguna, file hilang/duplikat, coverage nyata, penerimaan varian tepi, seed berulang/berbeda, penghindaran varian berurutan, word wrap/pagination/margin, placeholder, watermark multipage, format tunggal, teks kosong, serta penolakan folder hasil lama. Kasus terkait digabung dalam metode uji.
- Evaluasi terulang melalui `.venv/bin/python scripts/evaluate_render.py --user <id> --out outputs/evaluasi-baru`, memakai teks standar bagian 5 tanpa perubahan.
- Lingkungan: Python 3.13.18, macOS/Darwin x86_64; Pillow/ReportLab/OpenCV/NumPy lokal, tanpa GPU atau model ML. Waktu mencakup pemuatan bank, layout, ekspor PDF, dan PNG, dilaporkan oleh engine sebelum penulisan JSON laporan.

| Metrik | Hasil |
|---|---|
| Jumlah render / halaman | 10 seed berbeda / 10 halaman |
| Waktu rata-rata per halaman | 0,81819 detik |
| Waktu minimum–maksimum per halaman | 0,6558–1,3246 detik |
| Pasangan kotak glyph bertumpuk | 0 pada semua halaman/seed |
| Label yang muncul dengan simpangan baku lebar instance > 0 | 33/33 label; rentang 1,044–7,593 piksel sumber |
| Label bank dengan simpangan baku lebar tinta varian > 0 | 73/73 label; rentang 0,471–12,862 piksel sumber |
| Karakter tidak tersedia pada teks standar | `/` (dua kemunculan per render), tampil sebagai placeholder |

- Target waktu <2 detik/halaman dan variasi lebar >0 tercapai pada sampel serta mesin ini. Pemeriksaan kotak gambar menunjukkan 0 tumpang tindih; tidak ada pengukuran persepsi manusia.
- Target 0 karakter hilang pada teks standar belum tercapai: slash tidak ada pada template. Tidak membuat glyph baru atau menyalin glyph lain; placeholder terlihat pada pratinjau dan slash tercatat dalam laporan.
- Tinggi baris contoh diary 7,358 mm mengikuti batas envelope D-019. Nilai dasar rotasi ±3°, offset ±0,4 mm, baseline ±0,3 mm, skala ±5%, pengali tinggi 2,4, jarak 0,15, dan spasi kata 2,5 tetap dipertahankan; belum dikalibrasi melalui uji persepsi.
- Hasil pribadi dan statistik rinci tetap lokal di `outputs/` yang diabaikan Git, termasuk `demo/`, `cli-check/`, dan `evaluation/summary.json`. CLI dengan file UTF-8 juga diuji untuk catatan dengan garis panduan.
- Keputusan terkait: D-018 dan D-019. Tahap engine render awal selesai; uji persepsi, hasil cetak, ketahanan bank lain, dan karakter di luar template masih memerlukan evaluasi lanjutan.

### Uji 4: evaluasi teknis Tahap 5, 2026-11-19
- Bank yang diuji: hasil scan pada Uji 2, dengan persetujuan pemilik yang sama; satu pemilik dan satu set scan. Algoritme segmentasi, geometri, jitter, dan aturan render tidak diubah.
- Audit enam lembar kotak sumber versus crop mencakup seluruh 323 kotak, termasuk semua varian bertanda tepi. Anotasi eksplisit per label/varian dibuat setelah pemeriksaan visual oleh agent (`codex_visual_agent`), bukan oleh penilai manusia independen. Hash manifest, tiga scan sumber, dan setiap glyph disimpan bersama anotasi agar hasil tidak dipakai untuk data yang berbeda.
- Pemeriksaan visual: 323/323 benar pada set ini, ketepatan pemotongan 100%; tidak tampak tinta terpotong, garis kotak hitam ikut masuk, atau dua kotak tergabung. Empat varian tepi tetap utuh dan statusnya tidak dihapus. Angka ini terbatas pada tinjauan visual agent terhadap scan ini; belum merupakan ukuran ketahanan pada populasi pengguna/foto lain.
- Status tetap 319 ok (98,76%), 0 empty (0%), 4 touches_edge (1,24%). Jumlah kosong setiap label 0. Coverage tetap 52/52 huruf dengan 5 varian dan 21 label angka/tanda baca dengan 3 varian.
- Uji render tambahan seluruh karakter template: 73 instance (a–z, A–Z, angka, dan 11 tanda baca), tanpa karakter hilang. Pratinjau ditinjau visual, termasuk kapital, angka, dan tanda baca.

| Metrik | Standar: 10 seed | Padat: 10 seed, teks diulang 8 kali |
|---|---:|---:|
| Jumlah halaman | 10 | 30 |
| Rata-rata detik/halaman | 0,81120 | 1,16362 |
| Rentang detik/halaman antar-run | 0,5815–1,0615 | 1,06077–1,26057 |
| Pasangan kotak glyph bertumpuk | 0 | 0 |
| Label terpakai dengan simpangan baku lebar instance >0 | 33/33 | 33/33 |
| Rentang simpangan baku lebar instance (piksel sumber) | 1,044–7,593 | 1,183–8,254 |
| Label bank dengan simpangan baku lebar varian >0 | 73/73 | 73/73 |
| Karakter hilang | `/` | `/` |

- Waktu adalah durasi penuh satu pemanggilan render (muat bank, layout, PDF, PNG) dibagi jumlah halaman, sebelum penulisan JSON laporan. Rentang di atas adalah rentang rata-rata per halaman antar-run, bukan waktu terpisah tiap halaman. Lingkungan tetap Python 3.13.18/macOS x86_64, tanpa GPU. Hasil 30 halaman mencakup halaman terakhir yang tidak penuh.
- Target rata-rata <2 detik/halaman tercapai pada kedua beban ini. Target variasi lebar dan 0 tumpang tindih kotak juga tercapai pada data ini. Ini bukan klaim bahwa seluruh target kualitas tulisan sudah tercapai.
- Target karakter hilang 0 pada teks standar tetap belum tercapai: slash tidak ada dalam template. Semua kemunculannya tetap placeholder dan dilaporkan; tidak membuat atau menggandakan glyph untuk menutup kekurangan.
- Pemeriksaan berkas: 21 PDF / 41 halaman A4 dan 41 PNG RGB 300 DPI; watermark teks diverifikasi pada setiap halaman PDF dengan PDFKit dan keberadaan tinta footer pada setiap PNG. Pratinjau tiga halaman beban padat seed 0 ditinjau visual; watermark tetap terlihat pada halaman lanjutan.
- Pengujian otomatis: 14 metode lulus (11 renderer, 3 metrik audit). Metrik tanpa anotasi tetap null; anotasi parsial tidak dianggap lengkap; manifest/sumber/glyph berbeda, anotasi duplikat, dan pemeriksa kosong ditolak.
- Artefak lokal: `outputs/stage5/summary.json`, `segmentation_final/` beserta anotasi dan enam lembar audit, `standard/`, `dense/`, serta `all_characters/`. Seluruh artefak pribadi diabaikan Git.
- Uji manusia belum dijalankan: 0 penilai, 0 skor, dan belum ada 20 pasangan referensi halaman independen. Dua baris satu pangram pada TPL-03 tidak digandakan agar seolah-olah menjadi 20 sampel. `human-study/` hanya berisi inventaris 20 pasangan yang belum terisi, CSV 200 baris kosong untuk 10 ID penilai anonim, dan petunjuk persiapan; protokol watermark/persepsi masih menunggu keputusan.
- Batas lain: belum diuji dengan foto HP cahaya redup/miring, pengguna lain, atau hasil cetak. Tidak ada hasil persepsi atau ketahanan fisik yang direkayasa. Evaluasi teknis awal selesai dan tercatat; evaluasi persepsi serta seluruh target produk belum selesai.
- Keputusan terkait: D-020.

### Penyesuaian spasi antarkata: 2026-11-19
- Berdasarkan umpan balik pemilik bahwa spasi terlalu rapat, pengali token spasi dinaikkan dari 2,5 menjadi 3,0 (+20%) sesuai D-021. Pada bank ini: 1,137 menjadi 1,365 mm, bertambah sekitar 0,227 mm per spasi. Jarak antarhuruf dan parameter lain tetap.
- Bandingkan contoh diary Uji 3 dengan teks dan seed 42 yang sama. Varian tulisan tetap sama; posisi kata dan pemecahan baris mengikuti spasi baru. Perbandingan PNG sudah diperiksa visual.
- Hasil baru satu halaman PDF/PNG, 165 instance, tanpa karakter hilang; waktu satu render 0,9747 detik. Ini pemeriksaan satu contoh, bukan pengulangan benchmark 10 seed atau uji persepsi manusia.
- Seluruh 14 pengujian otomatis lulus, termasuk margin, pagination, tumpang tindih, determinisme seed, dan watermark multipage.
- Hasil lokal disimpan di `outputs/spacing-03/`, termasuk gambar perbandingan berwatermark. Riwayat evaluasi parameter lama tetap dipertahankan.

### Uji 5: antarmuka lokal, 2026-11-19
- Implementasikan editor/pratinjau FastAPI setelah engine selesai, sesuai D-023. Tidak ada perubahan aturan render, bank, atau geometri template.
- Seluruh 19 metode unittest lulus: 11 engine, 3 audit, 5 API. Bank uji API dibuat sementara; uji mencakup kesiapan profil, bank tanpa persetujuan, input kosong/terlalu panjang/jenis atau seed tidak valid, Origin/Host asing, penolakan akses laporan/berkas bebas, render multipage, unduhan PDF/PNG, isolasi hasil, dan tidak menyimpan isi teks dalam laporan.
- Pemeriksaan sintaks Python/JavaScript dan `pip check` lulus. Starlette versi lingkungan ini memberi peringatan deprecation tentang httpx pada TestClient; pengujian HTTP tetap lulus. httpx hanya dipakai saat pengujian.
- Uji browser headless Chrome lokal dengan engine dan profil yang sebenarnya: pratinjau awal, ubah teks, pilihan surat, seed, render 3 halaman, peringatan @/#, navigasi maju/mundur, pembesaran, unduh PDF/PNG, kosongkan teks, penonaktifan unduhan hasil usang, simulasi kegagalan HTTP dan pemulihan, serta Ctrl+Enter semuanya berhasil.
- Pratinjau diperiksa pada lebar 1440, 1024, 820, 768, 390, dan 320 piksel, tanpa overflow horizontal terdeteksi. Dua panel bertumpuk di ponsel. Tombol utama pada viewport 390 × 844 berada sampai y=830 setelah perbaikan containing block animasi; animasi kini hanya pada judul. Pada layar desktop pendek, sebagian editor dapat memerlukan scroll.
- Pemeriksaan performa browser: 0 FAIL, 5 WARN; transfer sekitar 353 KiB desktop/346 KiB ponsel, tidak ada request rusak, layout shift 0. FCP relatif pada mesin uji sekitar 456 ms desktop dan 384 ms ponsel; ini waktu cat pertama, bukan waktu selesai render dokumen. Warning terkait atribut dimensi gambar, gambar belum lazy di ponsel, dan PNG 300 DPI yang lebih besar dari ukuran tampil.
- Gate desain: `GATE: OPEN 15 (rounds used up)` dengan lima waiver dan 12 warning, bukan PASS. Temuan terbuka terutama aturan hero satu layar, container/heading tepi luar, serta unduhan di fold pertama yang dirancang untuk landing page. Editor dua panel dan unduhan setelah pratinjau pada ponsel tetap dipertahankan. Daftar aturan, waiver, warning, dan alasannya ada di `docs/INTERFACE.md`.
- Berkas, log, dan screenshot QA berada lokal di `outputs/ui-checks/`; hasil dokumen di `outputs/ui/`. Keduanya diabaikan Git. Tidak ada sampel atau teks yang diunggah ke layanan lain, tidak ada publikasi situs, dan belum dilakukan pengujian perangkat ponsel fisik atau penilaian manusia.
- Batas aplikasi: satu pemilik pada loopback, belum memiliki upload/onboarding sampel, autentikasi multi-pengguna, atau penyimpanan draft. Ini tidak menyelesaikan uji persepsi yang tertunda pada tahap sebelumnya.

### Uji 6: pengelolaan profil lokal, 2026-11-19
- Implementasikan D-024: tambah profil dari nama/alias dan tiga gambar, ubah nama melalui pensil, serta hapus melalui keranjang sampah. Tidak mengubah geometri atau parameter render.
- Seluruh 26 metode unittest lulus, termasuk profil lama, consent wajib sebelum upload dan pada upload ulang, rotasi/metadata gambar, halaman duplikat/tidak valid, gerbang tinjauan debug, penerimaan potongan touches_edge, coverage kurang dan pengulangan halaman, render setelah siap, serta penghapusan hasil sendiri dengan mempertahankan hasil profil lain.
- Uji browser headless memakai tiga halaman sintetis bertanda marker dan isian buatan; TPL-01 sengaja diputar 180°. Alur tambah → koreksi rotasi → ekstraksi → konfirmasi tiga debug → coverage/aktif → ubah nama dengan ID tetap → render/unduh PDF → hapus berhasil. Akses profil dan unduhan yang telah dihapus mengembalikan 404 sesuai harapan. Profil nyata k1ndtomato tetap ada; profil QA dibersihkan.
- Dialog tambah diperiksa pada desktop 1440 × 1000 dan ponsel 390 × 844; tidak ada overflow horizontal pada pemeriksaan ponsel. File input terkunci sampai identitas dan persetujuan diisi; ikon pensil dan keranjang sampah tersedia. Artefak QA tersimpan lokal di `outputs/ui-checks/` dan diabaikan Git.
- Ini uji fungsional dengan data sintetis, bukan pengukuran baru ketepatan segmentasi foto nyata, benchmark render, atau penilaian persepsi manusia. Gate desain Uji 5 tetap sebagai riwayat; tidak diklaim lulus kembali. Server lokal lama perlu dimulai ulang untuk memuat API profil baru.

<!--
Template entri:

### Uji N: <tanggal>
- Pengguna / ID: 
- Kondisi foto: 
- Kotak ok / empty / touches_edge: 
- Ketepatan pemotongan: 
- Coverage (label yang belum ≥ 3): 
- Waktu render rata-rata: 
- Hasil uji persepsi (jika ada): 
- Kesimpulan dan tindak lanjut: 
- Entri DECISIONS.md terkait: 
-->

## 5. Teks uji standar

Gunakan teks ini untuk membandingkan antar-versi:

```
Yth. Bapak/Ibu Dosen,
Dengan hormat, kami mengundang Bapak/Ibu untuk hadir pada kegiatan
praktikum pada tanggal 25 November 2026 pukul 09.00 WIB.
Terima kasih atas perhatiannya.
```

Teks ini mengandung huruf kecil, kapital, angka, dan tanda baca yang umum. Tambahkan teks lain untuk uji huruf jarang (q, x, z, j, k) bila diperlukan.

## 6. Kapan evaluasi dianggap cukup

Evaluasi tahap awal dianggap cukup jika:
- Uji ekstraksi sudah dilakukan minimal sekali pada foto nyata.
- Uji render sudah dilakukan dengan teks uji standar.
- Hasil dicatat di bagian 4 dengan entri yang lengkap.
- Parameter yang diubah sudah dicatat di `DECISIONS.md`.
