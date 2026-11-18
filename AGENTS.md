# Instruksi Project: Generator Dokumen Tulisan Tangan (glyph bank tanpa ML)

## Tujuan
Membuat sistem yang menerima sampel tulisan tangan pengguna dari template berlabel, membangun glyph bank per pengguna, lalu merender teks menjadi dokumen (PDF/PNG) yang terlihat ditulis tangan oleh pengguna tersebut.

## Baca dulu
Sebelum mengerjakan apa pun, baca file berikut secara berurutan:
1. `README.md`
2. `SPEC.md`
3. `TEMPLATE.md`
4. `PIPELINE.md`
5. `RENDER.md`
6. `ETHICS.md`
7. `DECISIONS.md`

Jika ada konflik antara file dan permintaan, ikuti `ETHICS.md` dan `SPEC.md` lebih dulu, lalu tanyakan kepada pengguna.

## Batasan wajib
- Sampel hanya boleh diproses atas nama pemilik tulisannya. Jangan menerima atau memproses sampel tanpa identitas pemilik yang jelas.
- Jangan membuat fitur yang menyalin tanda tangan atau memalsukan dokumen resmi.
- Setiap output harus memiliki penanda "tidak resmi" (watermark atau metadata).
- Jangan menyimpan data pribadi di gambar. Metadata (nama, tanggal, kode halaman) disimpan di file JSON terpisah.
- Jangan mengubah geometri template tanpa memperbarui `TEMPLATE.md` dan `make_template.py` secara bersamaan.

## Struktur kerja
Kerjakan dalam urutan ini. Jangan lompat tahap.

### Tahap 1: Template
- Gunakan `make_template.py` untuk menghasilkan `template_tulisan_A4.pdf` (3 halaman).
- Pastikan geometri di skrip ekstraksi sama dengan geometri template.

### Tahap 2: Ekstraksi glyph
- Gunakan `extract_glyphs.py` dengan argumen `--user` dan `--pages` (urutan TPL-01, TPL-02, TPL-03).
- Output: `glyph_bank/<user>/glyphs/<label>/<label>_NN.png`, `manifest.json`, dan `debug_page*.png`.
- Setelah setiap ekstraksi, periksa `debug_page*.png`. Jika ada kotak yang salah potong, laporkan dan jangan lanjut ke tahap berikutnya.
- Kotak berstatus `empty` tidak disimpan. Laporkan jumlah kotak kosong per label.
- Kotak berstatus `touches_edge` disimpan, tetapi tandai untuk ditinjau.

### Tahap 3: Validasi glyph bank
- Minimal 3 varian per huruf a–z dan A–Z. Huruf dengan kurang dari 3 varian ditandai sebagai tidak lengkap.
- Hitung jumlah varian per label dan simpan di `glyph_bank/<user>/coverage.json`.
- Jika coverage di bawah target, minta pengguna mengulang halaman tertentu. Jangan mengisi kekurangan dengan menyalin varian lain.

### Tahap 4: Engine render
- Input: teks (string) dan ID pengguna.
- Pecah teks per baris sesuai lebar halaman A4 dengan margin yang ditentukan di `SPEC.md`.
- Untuk setiap karakter, pilih varian secara acak dari glyph bank pengguna.
- Terapkan jitter yang dibatasi (lihat `RENDER.md`): rotasi ±2–4°, offset vertikal kecil, dan variasi spasi berdasarkan lebar glyph.
- Jika karakter tidak ada di glyph bank, tampilkan placeholder dan laporkan karakter tersebut. Jangan diam-diam membuang karakter.
- Output: PDF untuk cetak dan PNG untuk pratinjau, dengan watermark tidak resmi.

### Tahap 5: Evaluasi
- Ikuti `EVALUATION.md`.
- Ukur tingkat keberhasilan segmentasi, variasi antar-instance, dan waktu render per halaman.
- Simpan hasil di `EVALUATION.md` pada bagian riwayat.

## Aturan kerja untuk agent
- Setiap perubahan pada aturan render atau geometri harus dicatat di `DECISIONS.md`.
- Setelah menyelesaikan tahap, perbarui `CHANGELOG.md`.
- Jangan menambahkan model machine learning tanpa persetujuan. Jalur saat ini adalah glyph bank tanpa ML.
- Jangan menyimpan sampel tulisan dalam repositori publik. Gunakan `.gitignore` untuk `glyph_bank/`.
- Jika ada pertanyaan yang tidak terjawab oleh dokumen ini, tanyakan kepada pengguna sebelum mengambil keputusan besar.

## Definisi selesai (Definition of Done) untuk tahap awal
- Template tercetak dan bisa diisi.
- Ekstraksi berjalan pada minimal satu foto nyata, dengan hasil `debug_page*.png` yang sudah diperiksa.
- Glyph bank per pengguna memiliki coverage yang dilaporkan.
- Render satu paragraf menghasilkan PDF dan PNG dengan watermark tidak resmi.
- Hasil evaluasi awal tercatat di `EVALUATION.md`.
