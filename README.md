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
| `render_document.py` | Merender teks menjadi PDF/PNG tidak resmi |
| `scripts/evaluate_render.py` | Mengukur 10 render teks standar |
| `scripts/evaluate_segmentation.py` | Audit sumber/crop, anotasi per kotak, dan metrik segmentasi |
| `requirements.txt` | Dependensi Python |
| `app.py`, `web/` | Antarmuka editor dan pratinjau lokal |
| `profiles.py` | Profil, upload TPL, tinjauan, coverage, dan penghapusan turunan |
| `docs/INTERFACE.md` | Perilaku dan verifikasi antarmuka |

## Persiapan

```bash
python -m pip install -r requirements.txt
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

Siapkan file teks UTF-8 di `outputs/teks.txt` (folder `outputs/` diabaikan Git), lalu jalankan:

```bash
python render_document.py --user <id> --text-file outputs/teks.txt --doc-type catatan --out outputs/catatan-01 --seed 42
```

Hasil: `document.pdf`, `page_001.png` (dan halaman lanjutan), serta `render_report.json`. Gunakan folder keluaran baru pada setiap render agar hasil tidak tercampur. Pilih `--doc-type surat` untuk margin 25 mm, `--format pdf` atau `--format png` untuk satu format, dan `--guidelines` untuk garis panduan catatan. Undangan masih ditunda.

Engine memeriksa `consent.json`, `coverage.json`, dan kelulusan tinjauan dalam `extraction_report.json`. Setiap huruf wajib punya minimal 3 file varian unik; glyph `touches_edge` wajib memiliki persetujuan tinjauan per varian. Tidak ada fallback ke bank pengguna lain.

Karakter yang belum tersedia menjadi placeholder dan tercatat dalam laporan. Seluruh halaman memiliki watermark wajib. Isi teks tidak ditulis ke log atau JSON laporan; ID dan statistik disimpan terpisah dari PNG.

### 4. Buka antarmuka lokal

```bash
python app.py --port 8010
```

Buka `http://127.0.0.1:8010/`. Tulis atau tempel teks, pilih catatan/surat, lalu klik **Buat tulisan tangan** (Cmd/Ctrl+Enter). Periksa pratinjau per halaman, perbesar bila perlu, lalu unduh PDF seluruh dokumen atau PNG halaman aktif. Seed dan garis panduan tersedia pada pengaturan tulisan.

Klik **Tambah profil**, isi nama/alias pemilik dan persetujuan, lalu pilih tiga gambar TPL-01/02/03. Gunakan rotasi jika gambar terbalik. Setelah ekstraksi, periksa ketiga debug dan setiap potongan bertanda tepi. Coverage diperiksa setelah tinjauan lolos; profil belum bisa dirender jika ada huruf dengan kurang dari 3 varian. Halaman dan label yang perlu diulang akan dilaporkan, dan upload ulang tersedia.

Pilih profil melalui dropdown. Tombol **pensil** mengubah nama tampilan tanpa mengganti ID atau glyph; tombol **keranjang sampah** menghapus profil dan data lokal terkait setelah konfirmasi. Berkas yang sudah diunduh ke luar penyimpanan proyek perlu dihapus sendiri. Parameter opsional `--user <id>` tetap dapat memilih profil awal; bank lama langsung dikenali.

Antarmuka memuat contoh catatan netral dan membuat pratinjau lokal jika profil awal sudah siap. Teks yang diubah belum disimpan atau dirender sampai tombol ditekan lagi; hasil lama ditandai perlu diperbarui. Hasil berada di `outputs/ui/` yang diabaikan Git, dan sampel profil baru berada di dalam `glyph_bank/<id>/sources/`. Identitas/persetujuan disimpan di JSON, metadata gambar dibuang, serta tidak ada unggahan ke layanan lain atau autosave teks di browser. Lihat `docs/INTERFACE.md`. Setelah memperbarui kode backend, restart server sebelum memuat ulang halaman.

### Pengujian

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/evaluate_render.py --user <id> --out outputs/evaluasi-01
```

Pengujian otomatis memakai bank buatan sementara. Evaluasi memakai bank pengguna yang telah ditinjau dan menghasilkan 10 pasangan PDF/PNG serta `summary.json` lokal. Lihat `EVALUATION.md` untuk hasil dan batas pengujian.

Untuk mengaudit pemotongan dan menguji dokumen yang lebih padat:

```bash
python scripts/evaluate_segmentation.py --user <id> --out outputs/audit-01
python scripts/evaluate_render.py --user <id> --out outputs/evaluasi-padat-01 --repeat 8
```

Audit menghasilkan enam lembar perbandingan kotak sumber dengan crop dan `review_template.json`. Periksa setiap kotak, isi `correct` dengan `true`/`false`, catat `reviewer` dan alasan, lalu simpan anotasi terpisah. Hitung metrik dengan `--review outputs/anotasi.json --out outputs/audit-02`. Anotasi kosong tidak dinilai lulus; perubahan hash manifest, scan, atau glyph membatalkan anotasi lama. Audit ini menggunakan pemetaan sumber dalam `consent.json` dan folder `scan_demo/` secara default.

`--repeat 8` mengulang teks standar delapan kali; default tetap satu teks standar asli. Waktu per halaman merupakan durasi render satu dokumen dibagi jumlah halamannya, bukan pengukuran terpisah setiap halaman. Tahap 5 sudah memiliki evaluasi teknis awal; uji persepsi manusia dan kondisi foto lain masih belum selesai.

## Yang belum ada

- Uji persepsi kemiripan tulisan dan uji cetak hasil render.
- Autentikasi akun dan hosting publik; aplikasi saat ini dikelola lokal di satu perangkat.
- Pengujian foto HP dengan variasi cahaya dan perspektif. Ekstraksi pada scan tulisan nyata sudah diuji; coverage dan hasil tinjauan tercatat di `EVALUATION.md`.

## Catatan untuk kontributor

- Jangan mengunggah `glyph_bank/` ke repositori publik. Tambahkan ke `.gitignore`.
- Setiap perubahan geometri template harus diperbarui di `make_template.py`, `extract_glyphs.py`, dan `TEMPLATE.md` sekaligus.
- Catat keputusan baru di `DECISIONS.md` dan perubahan di `CHANGELOG.md`.
