# SPEC: Generator Dokumen Tulisan Tangan (glyph bank tanpa ML)

Versi: 0.1 (draft awal)
Status: ekstraksi, coverage, dan engine render awal sudah diuji; persepsi, hasil cetak render, dan ketahanan foto HP belum diuji (lihat `EVALUATION.md`)

## 1. Ringkasan

Sistem menerima sampel tulisan tangan pengguna dari template berlabel, membangun glyph bank per pengguna, lalu merender teks menjadi dokumen (PDF untuk cetak, PNG untuk pratinjau) yang terlihat ditulis oleh pengguna tersebut.

## 2. Tujuan dan non-tujuan

### Tujuan
- Menghasilkan dokumen otomatis (surat, undangan, catatan, laporan singkat) dalam tulisan tangan pengguna.
- Render cepat dan bisa dijalankan dalam jumlah banyak di laptop biasa tanpa GPU.
- Setiap output tampak natural, dengan variasi antar-huruf yang terkendali.

### Non-tujuan
- Tidak membuat tulisan tangan yang dapat dipakai untuk memalsukan tanda tangan atau dokumen resmi.
- Tidak menangani tulisan bersambung (cursive) pada tahap awal.
- Tidak memakai model machine learning pada tahap awal.
- Tidak melakukan OCR tulisan tangan dari buku atau catatan bebas.

## 3. Pengguna dan alur utama

1. Pengguna mencetak template `template_tulisan_A4.pdf` (3 halaman).
2. Pengguna menulis di setiap kotak sesuai labelnya.
3. Pengguna memfoto ketiga halaman, lalu mengunggahnya.
4. Sistem mengekstrak glyph dan membangun glyph bank pengguna.
5. Pengguna memasukkan teks dan memilih jenis dokumen.
6. Sistem merender dokumen dan mengembalikan PDF atau PNG.

## 4. Template

- Ukuran kertas: A4 (210 × 297 mm), dicetak 100% tanpa penyesuaian.
- Terdiri dari tiga halaman:
  - **TPL-01**: huruf kecil a–z, 5 varian per huruf.
  - **TPL-02**: huruf kapital A–Z, 5 varian per huruf, dibagi dua kolom.
  - **TPL-03**: angka 0–9 (3 varian), tanda baca `. , ? ! : ; " ' - ( )` (3 varian), dan dua kotak kalimat contoh (satu kalimat per kotak; D-016).
- Setiap halaman memiliki empat marker kotak hitam pejal di sudut dan kode halaman di bagian bawah tengah.
- Geometri lengkap didefinisikan di `make_template.py`. Perubahan geometri harus diikuti pembaruan `TEMPLATE.md` dan `extract_glyphs.py`.

## 5. Ekstraksi glyph

- Input: foto ketiga halaman dengan urutan TPL-01, TPL-02, TPL-03.
- Deteksi keempat marker sudut, koreksi perspektif, dan normalisasi ke 10 px/mm.
- Setiap kotak dipotong dengan inset 1,2 mm.
- Status kotak:
  - `ok`: siap dipakai.
  - `empty`: rasio tinta di bawah 0,3%, tidak disimpan.
  - `touches_edge`: tinta menyentuh tepi kotak, disimpan dan ditandai untuk ditinjau.
- Output per pengguna:
  - `glyph_bank/<user>/glyphs/<label>/<label>_NN.png`
  - `glyph_bank/<user>/manifest.json`
  - `glyph_bank/<user>/debug_page1.png` sampai `debug_page3.png`

### Target coverage
- Minimal 3 varian untuk setiap huruf a–z dan A–Z.
- Target ideal 5 varian untuk huruf dan 3 varian untuk angka serta tanda baca.
- Coverage dicatat di `coverage.json`.
- Render dihentikan jika ada huruf a–z atau A–Z dengan kurang dari 3 varian. Laporkan label yang belum lengkap dan minta pengguna mengulang halaman terkait; jangan menyalin varian untuk menutupi kekurangan (D-014).

## 6. Engine render

### Input
- Teks (string, dengan baris baru).
- ID pengguna.
- Jenis dokumen: catatan atau surat; undangan ditunda sesuai D-011.

### Proses
1. Pecah teks menjadi baris sesuai lebar area tulis A4 dan margin dari jenis dokumen.
2. Untuk setiap karakter, pilih varian secara acak dari glyph bank pengguna.
3. Terapkan jitter yang dibatasi:
   - Rotasi ±2 sampai ±4°.
   - Offset vertikal kecil.
   - Spasi antarhuruf berdasarkan lebar glyph.
4. Jika karakter tidak ada di glyph bank, tampilkan placeholder dan laporkan karakter tersebut. Karakter tidak boleh dibuang diam-diam.

### Output
- PDF untuk cetak.
- PNG untuk pratinjau.
- Setiap halaman output memuat watermark terlihat "TIDAK RESMI - HASIL GENERASI" sebagai konten halaman, sesuai `ETHICS.md`.

### Performa
- Target: kurang dari 2 detik per halaman A4 pada laptop biasa tanpa GPU.

## 7. Jenis dokumen awal

| Jenis | Margin | Catatan |
|---|---|---|
| Catatan | 20 mm | Garis panduan opsional |
| Surat | 25 mm | Kop surat berupa teks biasa |
| Undangan | 30 mm | Ditunda (D-011); rancangan teks di tengah halaman |

## 8. Antarmuka lokal

- FastAPI dengan editor HTML/CSS/JavaScript lokal, setelah engine render selesai (D-023).
- Teks maksimal 12.000 karakter, jenis catatan/surat, opsi seed dan garis panduan.
- Pratinjau A4 per halaman dengan pembesaran; unduh PDF seluruh dokumen atau PNG halaman aktif.
- ID pemilik dipilih saat menjalankan server; hanya glyph bank yang telah memiliki persetujuan, coverage, serta tinjauan valid yang boleh dipakai.
- Teks tidak disimpan otomatis di browser atau dicatat ke log; hasil disimpan lokal di folder yang diabaikan Git. Tidak ada upload sampel melalui UI ini atau deployment publik.

## 9. Batasan dan keamanan

- Sampel hanya boleh diproses atas nama pemilik tulisannya.
- Dilarang membuat fitur penyalinan tanda tangan atau pemalsuan dokumen resmi.
- Output wajib memiliki penanda tidak resmi.
- Data pribadi (nama, tanggal, kode halaman) disimpan dalam JSON terpisah, bukan dalam gambar.
- Folder `glyph_bank/` tidak boleh masuk repositori publik (gunakan `.gitignore`).

## 10. Kriteria keberhasilan tahap awal

- Template tercetak dan bisa diisi.
- Ekstraksi berjalan pada minimal satu foto nyata, dengan `debug_page*.png` sudah diperiksa.
- Coverage glyph bank pengguna tercatat.
- Render satu paragraf menghasilkan PDF dan PNG dengan penanda tidak resmi.
- Kecepatan render memenuhi target di bagian 6.
- Hasil evaluasi awal tercatat di `EVALUATION.md`.

## 11. Pertanyaan terbuka

- Apakah jenis dokumen awal cukup tiga, atau perlu ditambah? Jawaban: Mulai dengan catatan dan surat. Undangan ditunda ke tahap berikutnya, karena teks yang dipusatkan butuh logika layout tambahan dan uji tersendiri.
- Berapa target minimal coverage sebelum glyph bank dianggap layak dipakai? Jawaban: Minimal 3 varian untuk setiap huruf a–z dan A–Z sebelum render boleh dilakukan; 5 varian adalah target ideal. Jika ada huruf dengan kurang dari 3 varian, hentikan render, laporkan label yang belum lengkap, dan minta pengguna mengulang halaman terkait. Jangan menyalin varian lain untuk menutupi kekurangan (D-014).
- Apakah pengguna perlu memilih antara gaya rapi dan gaya cepat, atau cukup satu gaya? Jawaban: Pakai satu gaya dulu. Gaya cepat butuh halaman template kedua dan beban tambahan bagi pengguna, dan belum ada bukti bahwa satu gaya tidak cukup. Uji dulu dengan satu gaya, lalu putuskan berdasarkan hasil uji persepsi di EVALUATION.md.
