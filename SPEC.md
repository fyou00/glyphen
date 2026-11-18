# SPEC: Generator Dokumen Tulisan Tangan (glyph bank tanpa ML)

Versi: 0.1 (draft awal)
Status: belum diuji pada foto tulisan tangan asli

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
  - **TPL-03**: angka 0–9 (3 varian), tanda baca `. , ? ! : ; " ' - ( )` (3 varian), dan area kalimat contoh.
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

## 6. Engine render

### Input
- Teks (string, dengan baris baru).
- ID pengguna.
- Jenis dokumen (misalnya surat, undangan, catatan).

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
- Setiap output memuat penanda "tidak resmi" (watermark atau metadata).

### Performa
- Target: kurang dari 2 detik per halaman A4 pada laptop biasa tanpa GPU.

## 7. Jenis dokumen awal

| Jenis | Margin | Catatan |
|---|---|---|
| Catatan | 20 mm | Garis panduan opsional |
| Surat | 25 mm | Kop surat berupa teks biasa |
| Undangan | 30 mm | Teks di tengah halaman |

## 8. Antarmuka (tahap berikutnya)

- Form sederhana (Streamlit atau FastAPI) untuk mengisi teks dan memilih jenis dokumen.
- Unduh PDF atau PNG.
- Tidak termasuk dalam tahap awal.

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

- Apakah jenis dokumen awal cukup tiga, atau perlu ditambah?
- Berapa target minimal coverage sebelum glyph bank dianggap layak dipakai?
- Apakah pengguna perlu memilih antara gaya rapi dan gaya cepat, atau cukup satu gaya?
