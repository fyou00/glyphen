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
