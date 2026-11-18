# CHANGELOG

Format: setiap entri memuat tanggal, perubahan, dan file yang terdampak. Entri terbaru di atas.

## [0.1.1] - 2026-11-19

Keputusan atas pertanyaan terbuka dan pembaruan dokumen terkait.

### Diubah
- `SPEC.md`: bagian 11 berisi keputusan, bukan pertanyaan. Undangan ditandai ditunda di bagian 7.
- `RENDER.md`: undangan ditandai ditunda. Ditambahkan gerbang coverage (render dihentikan jika ada huruf dengan kurang dari 3 varian). Gaya cepat dicatat sebagai tidak dicakup.
- `DECISIONS.md`: ditambahkan D-011 (undangan ditunda), D-012 (coverage minimum 3, target 5), dan D-013 (satu gaya untuk tahap awal).

### Diketahui belum teruji
- Keputusan D-012 dan D-013 bergantung pada uji persepsi di `EVALUATION.md`, yang belum dilakukan.

## [0.1.0] - 2026-11-19

Tahap dokumentasi dan template awal. Belum ada engine render dan belum ada pengujian pada foto nyata.

### Ditambahkan
- `make_template.py`: membuat `template_tulisan_A4.pdf` tiga halaman dengan kotak, label, garis panduan, marker sudut, dan kode halaman.
- `template_tulisan_A4.pdf`: hasil dari `make_template.py`.
- `extract_glyphs.py`: deteksi marker, koreksi perspektif, pemotongan kotak, klasifikasi status, dan penyimpanan glyph bank dengan `manifest.json`.
- `SPEC.md`: spesifikasi produk versi 0.1.
- `TEMPLATE.md`: geometri dan tabel label template.
- `PIPELINE.md`: alur ekstraksi dari foto ke glyph bank.
- `RENDER.md`: spesifikasi engine render (belum diimplementasikan).
- `EVALUATION.md`: metrik, protokol uji, dan bagian riwayat hasil.
- `ETHICS.md`: batasan penggunaan, persetujuan pemilik, dan kebijakan output tidak resmi.
- `DECISIONS.md`: catatan keputusan D-001 sampai D-010.
- `README.md`: ringkasan project, struktur file, dan cara menjalankan.
- `CHANGELOG.md`: dokumen ini.

### Diketahui belum teruji
- Deteksi marker dan pemotongan kotak belum diuji pada foto tulisan tangan nyata.
- Parameter render (rasio tinggi baris, jitter, spasi) masih perkiraan.
- Jumlah varian per label (5 dan 3) belum divalidasi.

### Belum dikerjakan
- Engine render.
- Antarmuka pengguna.
- Uji ekstraksi dan persepsi (lihat `EVALUATION.md`).