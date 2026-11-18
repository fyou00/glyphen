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
