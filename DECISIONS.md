# DECISIONS: Catatan Keputusan Arsitektur

Dokumen ini mencatat keputusan penting beserta alasannya. Setiap perubahan pada aturan render, geometri template, atau kebijakan harus ditambahkan di sini sebagai entri baru. Jangan mengubah atau menghapus entri lama. Jika sebuah keputusan dibatalkan, tambahkan entri baru yang merujuk ke entri lama.

Format entri:
- **ID**: D-NNN
- **Tanggal**
- **Status**: aktif, diganti oleh D-NNN, atau dibatalkan
- **Keputusan**
- **Alasan**
- **Konsekuensi**

---

## D-001: Glyph bank tanpa machine learning sebagai tahap awal

- **Tanggal**: 2026-11-19
- **Status**: aktif

**Keputusan**
Tahap awal memakai glyph bank per pengguna (segmentasi, penyimpanan varian, pemilihan acak dengan jitter). Model generatif tidak dipakai.

**Alasan**
- Render massal harus cepat dan bisa berjalan di laptop tanpa GPU.
- Glyph bank bisa diuji dan dijelaskan dengan mudah, sehingga kualitasnya bisa diukur pada tiap tahap.
- Model generatif butuh data jauh lebih banyak dan waktu latih yang lama, sedangkan sampel per pengguna hanya beberapa halaman.

**Konsekuensi**
- Tulisan bersambung (cursive) tidak didukung pada tahap awal.
- Kualitas sambungan antarhuruf terbatas oleh sifat glyph yang terpisah.
- Model generatif bisa dipertimbangkan kembali sebagai tahap lanjutan, dengan keputusan baru.

---

## D-002: Sampel dikumpulkan dari template terstruktur, bukan catatan bebas

- **Tanggal**: 2026-11-19
- **Status**: aktif

**Keputusan**
Pengguna menulis di template A4 tiga halaman berlabel (`TEMPLATE.md`). Catatan dari buku atau tulisan bebas tidak dipakai untuk membangun glyph bank.

**Alasan**
- Label setiap kotak sudah pasti, sehingga tidak perlu OCR tulisan tangan yang tidak akurat.
- Kotak dengan posisi tetap memudahkan deteksi marker dan pemotongan otomatis.

**Konsekuensi**
- Pengguna harus menulis satu kali template sebelum bisa memakai sistem.
- Tulisan bebas hanya bisa dipakai untuk evaluasi gaya, bukan pembuatan glyph.

---

## D-003: Marker dibedakan oleh posisi, bukan bentuk

- **Tanggal**: 2026-11-19
- **Status**: aktif

**Keputusan**
Keempat marker sudut berbentuk kotak hitam dengan ukuran sama. Urutan ditentukan dari kedekatan ke sudut foto.

**Alasan**
- Desain sederhana lebih mudah dicetak dan dideteksi.
- Selama keempat marker terlihat dalam foto, urutan pasti benar.

**Konsekuensi**
- Foto yang memotong salah satu marker akan ditolak.
- Foto yang terbalik 180° belum tertangani. Jika terjadi di lapangan, pertimbangkan membedakan satu marker (misalnya lebih besar).

---

## D-004: Halaman template dibagi tiga

- **Tanggal**: 2026-11-19
- **Status**: aktif

**Keputusan**
Template terdiri dari TPL-01 (huruf kecil), TPL-02 (huruf kapital), dan TPL-03 (angka, tanda baca, kalimat contoh).

**Alasan**
- Jumlah kotak dalam satu halaman akan terlalu padat jika semua karakter digabung.
- Pemisahan per halaman memudahkan pengguna mengisi bertahap.

**Konsekuensi**
- Pengguna harus memfoto tiga halaman, dan urutannya wajib dijaga.

---

## D-005: Kunci tanda baca memakai nama, bukan simbol

- **Tanggal**: 2026-11-19
- **Status**: aktif

**Keputusan**
Tanda baca diberi label nama (`punct_question`, `punct_dquote`, dan seterusnya), bukan simbol (`?`, `"`).

**Alasan**
- Beberapa simbol bermasalah sebagai nama folder (`/`, `"`, `?` di Windows).
- Nama yang konsisten memudahkan pemetaan di render.

**Konsekuensi**
- Tabel pemetaan di `TEMPLATE.md` harus dijaga tetap sinkron dengan `extract_glyphs.py`.

---

## D-006: Jumlah varian per label

- **Tanggal**: 2026-11-19
- **Status**: aktif (angka masih perkiraan)

**Keputusan**
Target 5 varian untuk huruf kecil dan kapital, 3 varian untuk angka dan tanda baca. Minimal 3 varian untuk dianggap lengkap.

**Alasan**
- Di bawah 3 varian, hasil render terlihat berulang.
- Angka dan tanda baca lebih jarang dipakai.

**Konsekuensi**
- Angka 3 dan 5 belum diuji. Perubahan wajib dicatat sebagai entri baru.

---

## D-007: Watermark tidak resmi wajib di setiap output

- **Tanggal**: 2026-11-19
- **Status**: aktif

**Keputusan**
Setiap halaman output memuat "TIDAK RESMI - HASIL GENERASI" sebagai bagian dari konten halaman.

**Alasan**
- Mencegah dokumen hasil render dipakai sebagai dokumen resmi.
- Metadata saja mudah dihapus, jadi penanda dibuat sebagai bagian gambar.

**Konsekuensi**
- Fitur untuk menonaktifkan penanda tidak boleh dibuat (lihat `ETHICS.md` bagian 7).

---

## D-008: Tidak ada fitur penyalinan tanda tangan

- **Tanggal**: 2026-11-19
- **Status**: aktif

**Keputusan**
Sistem tidak mengekstrak, menyimpan, atau merender tanda tangan sebagai fitur khusus.

**Alasan**
- Tanda tangan adalah bentuk identitas yang paling mudah disalahgunakan.
- Menjaga batasan ini sejak awal lebih murah daripada memperbaikinya nanti.

**Konsekuensi**
- Jika glyph bank dipakai untuk menulis nama pengguna, pengguna tetap perlu menyadari risikonya. Pembahasan ini perlu dicatat di `ETHICS.md` jika fitur tanda tangan diminta di masa depan.

---

## D-009: Parameter render masih perkiraan

- **Tanggal**: 2026-11-19
- **Status**: aktif (perlu diuji)

**Keputusan**
Nilai rasio tinggi baris (2,4), batas jitter, jarak dasar antarhuruf (0,15), dan pengali spasi antarkata (2,5) ditetapkan sebagai nilai awal.

**Alasan**
- Belum ada data glyph nyata untuk dikalibrasi.

**Konsekuensi**
- Setiap perubahan nilai setelah uji pertama wajib dicatat sebagai entri baru.

---

## D-010: Pengujian dimulai dari satu foto nyata

- **Tanggal**: 2026-11-19
- **Status**: aktif

**Keputusan**
Sebelum tahap render dikembangkan lebih jauh, template dicetak, diisi, difoto, dan diekstrak minimal satu kali.

**Alasan**
- Desain template dan skrip ekstraksi belum pernah diuji pada foto tulisan tangan sungguhan.
- Masalah pencahayaan, perspektif, dan ukuran tulisan hanya terlihat dari data nyata.

**Konsekuensi**
- Hasil uji pertama harus dicatat di `EVALUATION.md` dan bisa memicu entri baru di dokumen ini.

---

## D-011: Undangan ditunda, tahap awal hanya catatan dan surat

- **Tanggal**: 2026-11-19
- **Status**: aktif

**Keputusan**
Jenis dokumen tahap awal adalah catatan dan surat. Undangan ditunda ke tahap berikutnya.

**Alasan**
- Teks yang dipusatkan membutuhkan logika layout tambahan dan uji tersendiri.
- Catatan dan surat sudah cukup untuk membuktikan pipeline dari ekstraksi sampai render.

**Konsekuensi**
- Bagian undangan di `SPEC.md` (bagian 7) dan `RENDER.md` ditandai ditunda.
- Margin 30 mm untuk undangan tetap dicatat sebagai rancangan, belum diimplementasikan.

---

## D-012: Coverage minimum 3 varian, target ideal 5

- **Tanggal**: 2026-11-19
- **Status**: aktif

**Keputusan**
Render boleh dilakukan jika setiap huruf punya minimal 3 varian. Target ideal adalah 5 varian. Huruf yang kurang dari 3 ditandai tidak tersedia, tidak diisi dengan varian dari huruf lain.

**Alasan**
- Di bawah 3 varian, hasil render terlihat berulang.
- Menyalin varian lain untuk menutup kekurangan membuat hasil tidak mewakili tulisan pemilik.

**Konsekuensi**
- Engine render harus memeriksa `coverage.json` sebelum merender.
- Target 3 dan 5 tetap perkiraan dan harus diuji dengan `EVALUATION.md`.

---

## D-013: Satu gaya tulisan untuk tahap awal

- **Tanggal**: 2026-11-19
- **Status**: aktif

**Keputusan**
Tahap awal hanya memakai satu gaya, yaitu gaya rapi dari template. Gaya cepat tidak dikerjakan.

**Alasan**
- Gaya cepat membutuhkan halaman template tambahan dan beban tambahan bagi pengguna.
- Belum ada bukti bahwa satu gaya tidak cukup.

**Konsekuensi**
- Keputusan ini ditinjau ulang setelah hasil uji persepsi di `EVALUATION.md`.
- Jika gaya cepat diminta nanti, perlu entri baru dan perubahan `TEMPLATE.md`.

---

## D-014: Render dihentikan jika coverage huruf belum memenuhi minimum

- **Tanggal**: 2026-11-19
- **Status**: aktif; memperjelas D-006 dan D-012

**Keputusan**
Sesuai instruksi terbaru pemilik project, setiap huruf a–z dan A–Z wajib memiliki minimal 3 varian sebelum render. Jika ada huruf di bawah minimum, hentikan render dan minta pengulangan halaman terkait. Target ideal tetap 5 varian. Kekurangan tidak boleh diisi dengan menyalin varian.

**Alasan**
- Menghilangkan opsi render dengan peringatan pada `SPEC.md` yang bertentangan dengan gerbang coverage di `RENDER.md` dan instruksi terbaru.

**Konsekuensi**
- `SPEC.md` bagian 5 dan 11 diperbarui; implementasi engine kelak wajib menerapkan gerbang ini.
- Angka minimum dan target tetap perlu dievaluasi pada sampel nyata.

---

## D-015: Pemulihan skrip template dari geometri terdokumentasi

- **Tanggal**: 2026-11-19
- **Status**: aktif

**Keputusan**
Lengkapi bagian akhir `make_template.py` yang terpotong: teks referensi, enam baris contoh, marker halaman ketiga, dan fungsi utama untuk menyimpan tiga halaman A4. Posisi baris contoh dipulihkan dari PDF awal (x = 15 mm, y bawah = 97 − 14 × indeks mm, ukuran 180 × 12 mm), sesuai `TEMPLATE.md`. Geometri ekstraksi tidak berubah.

**Alasan**
- Skrip awal menghasilkan `SyntaxError` dan tidak dapat membuat ulang template.
- Konten ketiga halaman hasil pemulihan diverifikasi identik dengan stream konten PDF awal.

**Konsekuensi**
- Tidak diperlukan perubahan geometri pada `extract_glyphs.py` atau `TEMPLATE.md`.
- Lingkungan lokal `.venv` memakai Python 3.13 dan ReportLab; dependensi transitif yang terpasang adalah Pillow dan charset-normalizer. Tidak ada dependensi baru yang dipakai langsung oleh kode project.

---

## D-016: Dua kotak kalimat contoh untuk dua pengulangan

- **Tanggal**: 2026-11-19
- **Status**: aktif; menggantikan jumlah enam kotak contoh pada D-015

**Keputusan**
Sesuai permintaan pemilik project, area kalimat contoh TPL-03 berisi dua kotak, satu kalimat per kotak. Pertahankan dua kotak pertama pada (15, 97) dan (15, 83) mm dari kiri-bawah halaman, masing-masing 180 × 12 mm; hapus empat kotak sisanya. Dua garis putus-putus di dalam setiap kotak tetap menjadi panduan tulisan.

**Alasan**
- Jumlah kotak harus sesuai dengan instruksi untuk menulis kalimat dua kali.

**Konsekuensi**
- Perbarui `make_template.py`, `TEMPLATE.md`, `SPEC.md`, dan PDF template. Sinkronkan komentar `page_layout()` di `extract_glyphs.py`: dua kotak contoh tetap dikecualikan dari ekstraksi.
- Geometri glyph dan marker tetap; foto template lama tetap memiliki posisi kotak glyph yang sama.
- Semua perubahan, sekecil apa pun, wajib dicatat di `CHANGELOG.md`; aturan ini juga ditambahkan ke `AGENTS.md` sesuai permintaan pemilik project.

---

## D-017: Deteksi marker scan menggunakan Otsu dan pemeriksaan isi

- **Tanggal**: 2026-11-19
- **Status**: aktif; menggantikan tahap threshold dan penyaringan lubang pada pipeline awal

**Keputusan**
Deteksi marker menggunakan threshold Otsu setelah blur Gaussian 5 × 5, kontur luar `RETR_EXTERNAL`, dan syarat minimal 90% piksel tinta di kotak pembatas. Batas luas, rasio sisi, kepejalan kontur minimal 0,9, kedekatan sudut, dan keunikan marker tetap dipakai. Geometri template, inset 1,2 mm, dan parameter klasifikasi glyph tidak berubah.

**Alasan**
- Pada scan nyata pertama, threshold adaptif membentuk lubang dan memecah area marker; algoritme awal menolak seluruh marker TPL-01. Melonggarkan pemeriksaan lubang saja masih gagal pada satu marker TPL-02.
- Pemeriksaan isi tinta membedakan marker pejal dari kotak garis tanpa menolak tekstur scan.

**Konsekuensi**
- Ketiga scan dapat diekstrak dengan empat marker per halaman. Uji buatan marker abu-abu pejal diterima dan kotak garis ditolak.
- Perubahan baru diuji pada tiga scan ini dan uji buatan sederhana; ketahanan pada foto berbayang atau cahaya tidak merata belum terbukti.
- Tinjauan visual menemukan tinta terpotong pada sejumlah glyph kecil. Validasi coverage dan render ditahan; tidak ada perubahan inset otomatis.
- Scan pribadi disimpan lokal dalam `scan_demo/` yang diabaikan Git; persetujuan dan pemetaan halaman disimpan dalam JSON terpisah. Glyph bank tetap diabaikan Git.

---

## D-018: Engine render lokal dengan pemeriksaan bank dan mask tinta

- **Tanggal**: 2026-11-19
- **Status**: aktif

**Keputusan**
Implementasikan API Python dan CLI `render_document.py` untuk catatan/surat, memakai Pillow, NumPy, OpenCV, dan ReportLab yang sudah disetujui. Wajib memverifikasi identitas, persetujuan pemilik dalam `consent.json`, kelulusan tinjauan ekstraksi beserta setiap varian tepi, jumlah file terhadap coverage, dan minimum 3 varian tiap huruf. Larang path keluar bank pengguna serta entri file/varian duplikat. Tidak ada fallback antar-pengguna.

Glyph dimuat sekali per render. Mask tinta memakai ambang 128 dan penyaringan komponen dengan luas minimal maksimum 2 piksel atau 1% komponen terbesar; komponen kecil yang tidak memenuhi batas dibuang. Glyph dipangkas ke batas tinta, baseline dihitung dari geometri garis panduan, kertas dibuat transparan, lalu varian, skala 0,95–1,05, rotasi ±3°, dan offset ±0,4 mm diterapkan dengan seed. Bank asli tetap utuh. Nilai penyaringan ini parameter awal dan belum divalidasi lintas sampel.

**Alasan**
- Kertas/garis panduan dan lebar kotak template tidak boleh ikut menjadi bentuk huruf dan jarak antarhuruf pada dokumen hasil.
- Coverage harus cocok dengan berkas yang dapat dibaca, dan persetujuan/tinjauan harus dapat ditelusuri sebelum render.

**Konsekuensi**
- Tambahkan `requirements.txt` dengan library stack yang sudah disetujui; tidak ada library baru di luar stack.
- Gambar glyph yang sangat tipis atau tanda kecil tetap perlu ditinjau pada sampel lain untuk menilai pengaruh penyaringan.
- PDF A4 menyimpan glyph pada skala sumber 10 px/mm; PNG 300 DPI RGB. Kedua format menggambar watermark setiap halaman. ID dan jenis dokumen dalam Subject PDF; ID/statistik lain di JSON terpisah, tanpa isi teks atau identitas tambahan di PNG.
- `outputs/` diabaikan Git, dan folder hasil lama tidak ditimpa. Pengujian memakai bank buatan sementara tanpa menyimpan sampel pengguna dalam repositori.

---

## D-019: Batas layout mengikuti glyph setelah jitter

- **Tanggal**: 2026-11-19
- **Status**: aktif; memperjelas D-009 dan memperbaiki aturan tumpang tindih pada RENDER.md

**Keputusan**
Pilih varian dan jitter sekali sebelum word wrap. Lebar token memakai gambar setelah skala/rotasi, ditambah jarak dasar 0,15 × lebar tinta rata-rata label dan variasi ±0,3 mm dengan minimum 0,1 mm. Spasi antarkata tetap 2,5 × jarak dasar rata-rata seluruh label. Pertahankan pengali tinggi baris 2,4, dengan x-height median label a,c,e,m,n,o,r,s,u,v,w,x. Tinggi baris tidak boleh kurang dari envelope seluruh glyph setelah jitter ditambah ruang offset baseline ±0,3 mm dan 0,1 mm pemisah. Posisi halaman mengikuti batas gambar aktual agar tidak keluar margin.

**Alasan**
- Word wrap harus memakai ukuran yang benar-benar ditempel, termasuk kapital, placeholder, dan kata panjang.
- Instruksi lama untuk mengurangi spasi saat terjadi tumpukan keliru; spasi positif dan envelope baris mencegah tumpukan tanpa mengubah batas jitter awal.

**Konsekuensi**
- Tinggi baris bisa melebihi 2,4 × x-height untuk teks yang memerlukan envelope lebih tinggi. Nilai awal lainnya tetap dan diuji sebelum perubahan lebih lanjut.
- Catatan bermargin 20 mm, surat 25 mm; undangan ditolak sesuai D-011. Karakter hilang menjadi placeholder dan daftar pada laporan, tanpa dibuang.
- Parameter yang dipakai dan hasil 10 seed dicatat pada Uji 3 di `EVALUATION.md`; kemiripan persepsi belum dinyatakan tercapai.

---

## D-020: Evaluasi segmentasi memakai anotasi eksplisit dan bukti berkas

- **Tanggal**: 2026-11-19
- **Status**: aktif

**Keputusan**
Audit segmentasi memakai perbandingan visual kotak sumber dengan crop, anotasi true/false/null per label/varian, identitas pemeriksa, serta hash manifest, sumber scan, dan glyph. Status ok/touches_edge tidak otomatis menjadi anotasi benar. Tanpa anotasi, ketepatan pemotongan null; anotasi parsial dilaporkan dengan denominator jumlah yang benar-benar diperiksa, dan tidak dianggap lengkap. Audit agent dipisahkan dari penilaian manusia independen.

**Alasan**
- Mengubah hasil tinjauan menjadi angka harus dapat ditelusuri dan tidak boleh menganggap semua kotak benar hanya dari status algoritme.
- Metrik dari scan/glyph lama tidak berlaku setelah berkas berubah.

**Konsekuensi**
- Tambahkan evaluator segmentasi dan uji penolakan anotasi tidak valid; bukti pribadi tetap lokal dan diabaikan Git.
- Uji performa tetap 10 seed teks standar, ditambah opsi pengulangan untuk beban padat/multihalaman tanpa mengganti teks standar asli. Durasi per halaman adalah durasi dokumen dibagi jumlah halaman; bukan waktu tiap halaman secara terpisah.
- Tidak mengubah parameter segmentasi/render atau geometri. Uji persepsi belum dijalankan: tidak membuat skor manusia atau menggandakan dua baris pangram menjadi 20 referensi independen. Watermark tetap wajib; pilihan protokol penilaian yang sesuai masih memerlukan keputusan pemilik project.

---

## D-021: Sedikit melebarkan spasi antarkata

- **Tanggal**: 2026-11-19
- **Status**: aktif; menggantikan pengali spasi kata pada D-009 dan D-019

**Keputusan**
Naikkan pengali spasi antarkata dari 2,5 menjadi 3,0 kali jarak dasar, yaitu kenaikan 20% pada token spasi. Pada bank yang sedang diuji, token spasi bertambah dari sekitar 1,137 menjadi 1,365 mm. Jarak antarhuruf, ukuran tulisan, jitter, dan margin tetap.

**Alasan**
- Pemilik menilai hasil render terlalu rapat dan meminta sedikit pelebaran spasi.

**Konsekuensi**
- Word wrap dapat berubah karena kata-kata memerlukan ruang lebih lebar. Bandingkan paragraf dan seed yang sama dengan hasil sebelumnya, lalu jalankan kembali pengujian renderer.
- Ini penyesuaian berdasarkan umpan balik pemilik; belum merupakan hasil uji persepsi banyak penilai. Hasil benchmark lama tetap menjadi riwayat parameter sebelumnya.

---

## D-022: Hapus teks referensi abu-abu pada area kalimat contoh

- **Tanggal**: 2026-11-19
- **Status**: aktif; memperbarui konten area contoh pada D-015 dan D-016

**Keputusan**
Sesuai permintaan pemilik, hapus teks cetak abu-abu `The quick brown fox jumps over the lazy dog` dari TPL-03. Kalimat yang harus ditulis tetap dijelaskan di `TEMPLATE.md`. Pertahankan judul, dua kotak tulis, garis panduan, dan marker.

**Alasan**
- Teks samar mengganggu area kalimat contoh dan dapat bertumpuk dengan tulisan pengguna.

**Konsekuensi**
- Buat ulang PDF template dan selaraskan dokumentasi pengisian. Tidak ada perubahan geometri, ekstraksi glyph, atau engine render; template yang sudah diisi tetap dapat diproses.

---

## D-023: Antarmuka editor lokal dengan FastAPI

- **Tanggal**: 2026-11-19
- **Status**: aktif

**Keputusan**
Bangun antarmuka HTML/CSS/JavaScript lokal dengan FastAPI dan Uvicorn, menghubungkan editor teks, jenis catatan/surat, opsi seed/panduan, pratinjau halaman, dan unduhan PDF/PNG ke engine yang sudah ada. Server default hanya mendengarkan 127.0.0.1 dan memakai satu ID pemilik yang ditentukan saat dijalankan. Tidak menambahkan upload sampel atau publikasi website pada tahap ini.

**Alasan**
- Engine selesai dan pengguna meminta antarmuka untuk memakainya. Halaman khusus memberi ruang editor serta pratinjau A4 tanpa pengiriman data ke layanan lain.

**Konsekuensi**
- Tambahkan FastAPI dan Uvicorn ke dependensi runtime; httpx hanya untuk pengujian HTTP lokal melalui `requirements-dev.txt`. Pydantic, Starlette, dan dependensi transitif mengikuti FastAPI. Tidak memakai ML atau layanan eksternal.
- Validasi persetujuan, tinjauan, dan coverage tetap dilakukan engine. Teks tidak disimpan oleh antarmuka atau dicatat ke log; hasil disimpan di `outputs/ui/` dengan ID acak per render dan tidak di-commit. Tidak ada autosave teks di browser.
- Render JSON dibatasi 12.000 karakter dan dijalankan bergantian. Unduhan hanya boleh mengakses file hasil yang terdaftar pada render tersebut, tanpa menerima path berkas bebas. Origin/Host lokal diverifikasi dan cache respons pribadi dinonaktifkan.
- Halaman memakai aset lokal, label Bahasa Indonesia, navigasi keyboard, indikator proses, pesan karakter hilang, dan penanda saat hasil perlu diperbarui setelah teks berubah. Watermark wajib tetap ada; tidak ada opsi menghapusnya.
- Aturan render dan geometri template tidak berubah. Teks awal adalah contoh catatan netral yang bisa diganti atau dikosongkan; pratinjau awal dirender lokal melalui API yang sama.
