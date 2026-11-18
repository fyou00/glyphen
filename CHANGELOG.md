# CHANGELOG

Format: setiap entri memuat tanggal, perubahan, dan file yang terdampak. Entri terbaru di atas.

## [Unreleased] - 2026-11-19

### Pelebaran kecil spasi antarkata (D-021)
- `render_document.py`: naikkan pengali token spasi dari 2,5 menjadi 3,0 (+20%); parameter antarhuruf dan jitter tetap.
- `RENDER.md`: selaraskan pengali aktif dan rujukan keputusan.
- `DECISIONS.md`: tambahkan D-021 berdasarkan umpan balik pemilik tentang spasi yang terlalu rapat.
- `EVALUATION.md`: catat perbandingan paragraf/seed yang sama dan hasil verifikasi.
- Verifikasi: 14 pengujian lulus; paragraf seed 42 tetap satu halaman dan 165 instance tanpa karakter hilang. Spasi pada bank ini bertambah sekitar 0,227 mm per token; pratinjau perbandingan diperiksa visual.
- Artefak lokal `outputs/spacing-03/`: PDF, PNG, laporan, dan gambar perbandingan dengan contoh sebelumnya; tetap diabaikan Git.
- `CHANGELOG.md`: catat seluruh perubahan penyesuaian ini; perubahan yang diverifikasi dibuatkan commit.

### Tahap 5: evaluasi teknis awal
- `scripts/evaluate_segmentation.py`: tambahkan enam lembar audit sumber/crop, template anotasi per kotak, hash bukti berkas, perhitungan ketepatan hanya atas anotasi eksplisit, dan metrik status/kotak kosong setiap label. Gunakan geometri dan inset dari ekstraktor.
- `scripts/evaluate_render.py`: tambahkan `--repeat` positif untuk beban padat; default tetap teks standar satu kali. Simpan jumlah pengulangan dalam ringkasan baru.
- `tests/test_evaluation.py`: tiga metode uji untuk anotasi kosong/parsial, manifest/sumber/glyph yang berubah, anotasi duplikat, dan pemeriksa yang belum diisi. Seluruh 14 pengujian audit serta renderer lulus.
- Artefak lokal `outputs/stage5/`: simpan enam lembar audit awal dan hasil evaluator, 323 anotasi visual agent, ringkasan segmentasi, 10 render standar, 10 render padat/multihalaman, render 73 karakter template, pratinjau, dan laporan gabungan. Seluruhnya tetap diabaikan Git.
- Bahan uji manusia lokal: siapkan inventaris 20 pasangan belum terisi, CSV 200 baris penilaian kosong, dan petunjuk persiapan. Tidak ada skor atau referensi independen buatan; protokol persepsi menunggu keputusan pemilik.
- `EVALUATION.md`: tambahkan Uji 4 dengan ketepatan visual agent 323/323 pada set scan ini, kecepatan 0,81120 dan 1,16362 detik/halaman, 0 kotak bertumpuk, variasi lebar, watermark seluruh 41 halaman, serta target slash dan uji persepsi/foto/cetak yang belum terpenuhi. Perjelas keterbatasan tes tebak jika watermark terlihat.
- `DECISIONS.md`: tambahkan D-020 untuk aturan anotasi, keterlacakan bukti, pengukuran beban padat, dan pemisahan audit agent dari persepsi manusia.
- `README.md`: dokumentasikan audit, anotasi, pengulangan teks untuk beban padat, definisi durasi per halaman, dan status evaluasi teknis.
- `RENDER.md`: tambahkan rujukan evaluasi Tahap 5. Tidak ada perubahan engine, geometri, atau parameter.
- `CHANGELOG.md`: catat seluruh perubahan dan batas kesimpulan evaluasi; kode dan dokumen yang diverifikasi dibuatkan commit.

### Tahap 4: engine render dan verifikasi awal
- `render_document.py`: tambahkan API/CLI render catatan dan surat, validasi persetujuan/tinjauan/coverage/file, isolasi glyph pengguna, mask tinta dan metrik baseline, pemilihan varian dengan seed, jitter, word wrap termasuk kata panjang, baris kosong, dan pagination.
- `render_document.py`: tambahkan PDF A4, PNG 300 DPI, watermark wajib setiap halaman, placeholder karakter hilang, garis panduan opsional, laporan JSON tanpa isi teks, format tunggal, dan penolakan folder keluaran lama. Undangan tetap ditunda.
- `.gitignore`: abaikan `outputs/` untuk melindungi dokumen dan input pribadi.
- `requirements.txt`: catat empat library stack yang sudah disetujui, termasuk Pillow untuk komposisi PNG; tidak menambah library di luar stack.
- `tests/test_render.py`: 11 metode uji dengan glyph buatan sementara untuk aturan layout, keamanan bank, determinisme, penanganan karakter hilang, format, dan watermark multipage, tanpa sampel pengguna di repositori.
- `scripts/evaluate_render.py`: evaluasi 10 seed memakai teks standar, ukur durasi, tumpang tindih kotak, dan variasi lebar; simpan artefak serta statistik tanpa isi teks di folder keluaran lokal.
- `README.md`: dokumentasikan dependensi, API melalui CLI, syarat bank, folder hasil, laporan, dan perintah pengujian; perbarui status implementasi.
- `SPEC.md`: perbarui status engine, selaraskan undangan yang ditunda dan watermark terlihat setiap halaman dengan keputusan/kebijakan yang sudah berlaku.
- `RENDER.md`: dokumentasikan implementasi, mask tinta, pemeriksaan bank, baseline/envelope layout, API/CLI, metadata, dan perlindungan hasil lama; perbaiki aturan spasi saat mencegah tumpang tindih.
- `DECISIONS.md`: tambahkan D-018 dan D-019 untuk implementasi dan batas layout tanpa mengubah entri lama.
- `EVALUATION.md`: catat Uji 3, 11 pengujian lulus, pemeriksaan visual PNG/PDF, serta 10 render dengan rata-rata 0,81819 detik/halaman dan 0 kotak bertumpuk. Slash belum tersedia dan dilaporkan sebagai placeholder; uji persepsi/cetak belum dilakukan.
- Artefak lokal `outputs/`: contoh diary dan laporan, 10 pasangan PDF/PNG evaluasi beserta ringkasan, pratinjau PNG/PDF untuk tinjauan, dan hasil uji CLI bergaris panduan. Sampel dan keluaran pribadi tidak di-commit.
- `CHANGELOG.md`: catat seluruh perubahan tahap ini dan batas hasil pengujian. Perubahan kode/dokumentasi yang diverifikasi dibuatkan commit sesuai instruksi project.

### Aturan commit
- `AGENTS.md`: sesuai instruksi pemilik project, setiap perubahan yang selesai dan diverifikasi wajib di-commit; data pribadi tetap diabaikan Git.

### Ekstraksi ulang dan validasi coverage: Uji 2
- Input pribadi lokal: pindahkan `Scan.jpeg` baru (TPL-01) dan `Scan 1.jpeg` baru (TPL-03) ke `scan_demo/attempt02/originals/`, simpan PNG kerja tanpa rotasi tambahan, dan gunakan kembali TPL-02 sebelumnya.
- Metadata lokal: arsipkan pemetaan percobaan pertama dalam `metadata_attempt01.json`; perbarui `metadata.json` aktif serta salin ke percobaan kedua dan `consent.json` glyph bank. Persetujuan pemilik sebelumnya tetap dipakai.
- Arsip lokal: pindahkan glyph bank pertama ke `glyph_bank/history/` sebelum ekstraksi ulang agar hasil lama tidak tertimpa atau bercampur dengan varian baru.
- Hasil lokal: buat ulang manifest, 323 glyph, tiga debug, laporan ekstraksi per label, serta `coverage.json`. Tambahkan pratinjau input, debug kecil, lembar tinjauan glyph, dan pembandingan empat potongan bertanda dengan kotak penuh di `scan_demo/`.
- Hasil verifikasi: 319 ok, 0 empty, 4 touches_edge; empat tanda tepi ditinjau dan tinta tampak utuh. 52/52 huruf punya 5 varian dan 21 label angka/tanda baca punya 3 varian; tidak ada label di bawah target. Seluruh file tersedia, dan TPL-02 identik hasil pertama.
- `EVALUATION.md`: tambahkan Uji 2, perbandingan hasil, kelulusan tinjauan, coverage, dan batas pengukuran yang belum dilakukan.
- `README.md`, `SPEC.md`, `PIPELINE.md`: perbarui status pengujian scan nyata; uji foto HP dalam variasi cahaya dan render tetap belum selesai.
- `CHANGELOG.md`: catat seluruh perubahan percobaan ini. Tidak ada perubahan algoritme, geometri, parameter crop, atau aturan render; tidak ada keputusan arsitektur baru.

### Ekstraksi scan nyata pertama (D-017)
- `.gitignore`: abaikan `scan_demo/` untuk melindungi sampel dan metadata pribadi.
- File pribadi lokal: pindahkan tiga JPEG ke `scan_demo/originals/`; simpan PNG kerja dengan TPL-01 diputar 180°, urutan halaman tetap, serta persetujuan dan hash sumber di `metadata.json`. Buat pratinjau masukan, salinan debug berukuran kecil, dan lembar tinjauan glyph di folder yang sama.
- Lingkungan `.venv`: pasang OpenCV dan NumPy yang sudah termasuk stack project.
- `extract_glyphs.py`: ganti threshold marker adaptif dengan Otsu, kontur luar, dan pemeriksaan isi tinta minimal 90%; koordinat dan parameter crop tetap.
- `PIPELINE.md`: selaraskan dokumentasi deteksi marker dengan implementasi.
- `glyph_bank/` (diabaikan Git): hasilkan 323 glyph, manifest, tiga debug PNG, salinan persetujuan dalam `consent.json`, dan `extraction_report.json` berisi statistik tiap label serta hasil tinjauan visual.
- `DECISIONS.md`: tambahkan D-017 beserta alasan perubahan deteksi dan batas pengujiannya.
- `EVALUATION.md`: catat percobaan gagal, hasil ekstraksi, dan temuan tinta terpotong pada TPL-01. Coverage serta render ditahan; tahap ekstraksi belum lulus tinjauan.
- `CHANGELOG.md`: catat seluruh perubahan pemrosesan ini. Verifikasi: marker pejal diterima, kotak garis ditolak, empat marker terdeteksi per scan, dan seluruh file glyph tercatat tersedia.

### Penyesuaian kotak kalimat contoh (D-016)
- `make_template.py`: kurangi enam kotak kalimat contoh menjadi dua dan perjelas instruksi satu kalimat per kotak besar.
- `template_tulisan_A4.pdf`: dibuat ulang dengan dua kotak contoh di TPL-03.
- `TEMPLATE.md`: dokumentasikan dua kotak, koordinatnya, dan fungsi garis putus-putus.
- `SPEC.md`: selaraskan jumlah kotak kalimat contoh di bagian 4.
- `extract_glyphs.py`: perbarui komentar agar sesuai dengan dua kotak contoh yang tidak diekstrak; koordinat ekstraksi tetap.
- `DECISIONS.md`: tambahkan D-016; entri keputusan lama tetap dipertahankan.
- `AGENTS.md`: wajibkan pencatatan setiap perubahan, sekecil apa pun, di changelog.
- `EVALUATION.md`: tambahkan hasil pemeriksaan PDF dua kotak tanpa mengubah riwayat pemeriksaan sebelumnya.
- `CHANGELOG.md`: catat seluruh perubahan dan verifikasi penyesuaian ini.
- Verifikasi penyesuaian: PDF tetap tiga halaman; TPL-01/TPL-02 identik; TPL-03 tepat dua kotak contoh dengan geometri glyph dan marker tetap; sintaks kedua skrip valid. Uji cetak dan ekstraksi nyata belum dilakukan.

### Diperbaiki
- `make_template.py`: melengkapi bagian akhir yang terpotong dan fungsi utama untuk membuat PDF tiga halaman.
- `template_tulisan_A4.pdf`: dibuat ulang; stream konten ketiga halaman identik dengan PDF awal, tanpa perubahan geometri.
- `SPEC.md`: render wajib dihentikan jika ada huruf a–z atau A–Z dengan kurang dari 3 varian.
- `DECISIONS.md`: keputusan D-014 tentang gerbang coverage dan D-015 tentang pemulihan skrip.

### Verifikasi
- Pembuatan PDF berhasil dengan `.venv/bin/python make_template.py`; tiga objek halaman dan seluruh stream konten dibandingkan dengan PDF awal.
- Pencetakan, pengisian, dan ekstraksi foto nyata masih menunggu pengguna; tahap template fisik dan ekstraksi belum dinyatakan selesai.

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
