# Generator Dokumen Tulisan Tangan

Sistem yang membuat dokumen (catatan, surat, undangan) dengan tulisan tangan dari pemilik sampelnya. Tahap awal memakai glyph bank per pengguna, tanpa machine learning.

> Dokumen ini tidak untuk memalsukan tanda tangan atau dokumen resmi. Baca `ETHICS.md` sebelum memakai atau mengembangkan sistem ini.

## Cara kerja singkat

1. Pengguna mencetak `template_tulisan_A4.pdf` (tiga halaman) dan menulis di setiap kotak.
2. Pengguna memfoto ketiga halaman, lalu sistem mengekstrak setiap kotak menjadi glyph bank pribadi.
3. Pengguna memasukkan teks dan memilih jenis dokumen.
4. Sistem merender teks menggunakan varian acak dari glyph bank, lalu menghasilkan PDF atau PNG dengan penanda tidak resmi.

## Struktur file

| File | Isi |
|---|---|
| `README.md` | Ringkasan dan cara menjalankan (dokumen ini) |
| `AGENTS.md` | Instruksi kerja untuk agent |
| `SPEC.md` | Spesifikasi produk |
| `TEMPLATE.md` | Geometri dan label template |
| `PIPELINE.md` | Alur ekstraksi dari foto ke glyph bank |
| `RENDER.md` | Engine render tulisan |
| `EVALUATION.md` | Cara mengukur kualitas dan hasil uji |
| `ETHICS.md` | Batasan penggunaan dan keamanan |
| `DECISIONS.md` | Catatan keputusan arsitektur |
| `CHANGELOG.md` | Riwayat perubahan |
| `make_template.py` | Membuat template A4 tiga halaman |
| `extract_glyphs.py` | Mengekstrak glyph dari foto template |

## Persiapan

```bash
pip install reportlab opencv-python numpy
```

Python 3.9 atau lebih baru.

## Menjalankan

### 1. Buat template

```bash
python make_template.py
```

Hasil: `template_tulisan_A4.pdf`. Cetak dengan ukuran 100%.

### 2. Ekstrak glyph

Setelah template diisi dan difoto (urutan TPL-01, TPL-02, TPL-03):

```bash
python extract_glyphs.py --user <id> --pages tpl01.jpg tpl02.jpg tpl03.jpg
```

Hasil ada di `glyph_bank/<id>/`. Periksa `debug_page*.png` sebelum memakai hasilnya.

### 3. Render dokumen

Tahap render belum diimplementasikan. Lihat `RENDER.md` untuk spesifikasinya.

## Yang belum ada

- Engine render (lihat `RENDER.md`).
- Antarmuka pengguna (lihat `SPEC.md` bagian 8).
- Pengujian foto HP dengan variasi cahaya dan perspektif. Ekstraksi pada scan tulisan nyata sudah diuji; coverage dan hasil tinjauan tercatat di `EVALUATION.md`.

## Catatan untuk kontributor

- Jangan mengunggah `glyph_bank/` ke repositori publik. Tambahkan ke `.gitignore`.
- Setiap perubahan geometri template harus diperbarui di `make_template.py`, `extract_glyphs.py`, dan `TEMPLATE.md` sekaligus.
- Catat keputusan baru di `DECISIONS.md` dan perubahan di `CHANGELOG.md`.
