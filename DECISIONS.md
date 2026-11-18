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