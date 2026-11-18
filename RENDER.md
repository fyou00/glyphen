# RENDER: Engine Render Tulisan Tangan

Dokumen ini menjelaskan cara engine render mengubah teks menjadi dokumen tulisan tangan dari glyph bank pengguna. Pembacaan glyph mengikuti `PIPELINE.md`, dan jenis dokumen mengikuti `SPEC.md` bagian 6 dan 7.

Status: engine awal diimplementasikan di `render_document.py` dan diuji pada glyph nyata; parameter masih perlu validasi persepsi. Lihat Uji 3 dan evaluasi teknis Tahap 5 pada Uji 4 di `EVALUATION.md`.

## Masukan

| Parameter | Tipe | Keterangan |
|---|---|---|
| `text` | string | Teks dengan baris baru (`\n`) |
| `user_id` | string | Harus punya `glyph_bank/<user_id>/manifest.json` dengan coverage valid |
| `doc_type` | string | `catatan` atau `surat`. `undangan` ditunda (lihat D-011) |
| `output` | list | `pdf`, `png`, atau keduanya |
| `seed` | int (opsional) | Untuk hasil yang bisa diulang saat debugging |

Jika `user_id` belum punya glyph bank, render dihentikan dengan pesan yang jelas. Engine tidak boleh memakai glyph dari pengguna lain.

## Jenis dokumen

| Jenis | Margin | Catatan |
|---|---|---|
| `catatan` | 20 mm | Garis panduan opsional |
| `surat` | 25 mm | Kop surat berupa teks biasa, tanpa logo |
| `undangan` | 30 mm | Ditunda ke tahap berikutnya (D-011). Rancangan: teks dipusatkan secara horizontal |

Ukuran kertas: A4, 210 × 297 mm.

## Alur render

```
text + user_id + doc_type
        │
        ▼
[1] Muat glyph bank dan coverage
        │
        ▼
[2] Normalisasi teks
        │
        ▼
[3] Pecah per baris (word wrap)
        │
        ▼
[4] Untuk setiap karakter: pilih varian, terapkan jitter dan spasi
        │
        ▼
[5] Susun baris di halaman (multi-halaman bila perlu)
        │
        ▼
[6] Tulis PDF / PNG + watermark
```

## Tahap 1: Muat glyph bank

- Baca `manifest.json` dan `coverage.json`.
- Cocokkan ID di manifest, coverage, dan `consent.json`; wajib ada persetujuan pemilik (`owner_is_uploader: true`) dan pernyataan persetujuan. Tinjauan `extraction_report.json` harus lulus, termasuk penerimaan setiap varian `touches_edge`.
- Verifikasi file glyph tetap dalam folder pengguna, terbaca, unik per path dan label/varian, memiliki tinta, dan jumlahnya cocok dengan coverage. Bank tidak lengkap atau tidak konsisten dihentikan.
- Simpan glyph `ok` dan `touches_edge` ke memori, dengan label sebagai kunci.
- Jika ada label dengan 0 varian, tandai karakter itu sebagai tidak tersedia.
- Render dihentikan jika ada huruf a–z atau A–Z dengan kurang dari 3 varian, sesuai D-012. Jangan mengisi kekurangan dengan varian huruf lain.
- Huruf dengan 3 sampai 4 varian boleh dirender, tetapi ditandai di log sebagai di bawah target ideal (5).
- Siapkan mask tinta pada ambang 128; buang komponen kurang dari maksimum 2 piksel atau 1% luas komponen terbesar. Pangkas ke batas tinta dan simpan offset baseline berdasarkan garis panduan 20% tinggi kotak. Gambar bank asli tidak diubah (D-018).

## Tahap 2: Normalisasi teks

- Ubah CRLF menjadi LF.
- Ganti tab dengan empat spasi.
- Gabungkan spasi berturut-turut menjadi satu, kecuali di awal baris.
- Jangan mengubah huruf besar atau kecil. Kapital harus diambil dari glyph `upper_*`.

## Tahap 3: Pemecahan baris

- Lebar area tulis = 210 mm − 2 × margin.
- Pecah per kata. Kata yang lebih lebar dari area tulis dipotong per karakter.
- Hitung lebar setiap kata dengan menjumlahkan lebar glyph yang akan dipakai, plus spasi antarhuruf.
- Baris baru dari `\n` selalu dimulai baris baru, meski baris sebelumnya belum penuh.
- Tinggi baris dasar = x-height × 2,4. X-height diperkirakan dari median tinggi tinta varian a, c, e, m, n, o, r, s, u, v, w, x. Tinggi aktual minimal sebesar envelope glyph yang sudah diberi jitter, ditambah ruang jitter baseline dan 1 piksel, agar baris tidak bertumpuk (D-019).

## Tahap 4: Pemilihan varian dan jitter

### Pemilihan varian
- Untuk setiap karakter, pilih satu varian secara acak dari daftar `ok` atau `touches_edge` milik label tersebut.
- Pemilihan diatur oleh `seed` agar bisa diulang.
- Hindari memilih varian yang sama dua kali berurutan jika tersedia lebih dari satu.

### Pemetaan karakter ke label
- Huruf kecil: `lower_<c>`
- Huruf kapital: `upper_<C>`
- Angka: `digit_<n>`
- Tanda baca: nama dari tabel di `TEMPLATE.md`, misalnya `punct_question`.
- Spasi tidak punya glyph. Spasi dirender sebagai jarak tetap.

### Jitter (dibatasi)
| Parameter | Nilai awal | Batas |
|---|---|---|
| Rotasi per karakter | acak ±3° | ±2° sampai ±4° |
| Offset vertikal per karakter | acak ±0,4 mm | ±0,2 mm sampai ±0,6 mm |
| Offset baseline per baris | acak ±0,3 mm | maksimum ±0,5 mm |
| Skala per karakter | acak 0,95 sampai 1,05 | jangan melebihi ±5% |

Jitter tidak boleh membuat karakter bertumpuk dengan tetangganya. Penempatan memakai lebar gambar setelah rotasi dan spasi positif, sehingga jarak ditambah bila diperlukan. Mengurangi spasi justru memperparah tumpang tindih; aturan lama diperbaiki melalui D-019.

### Spasi antarhuruf
- Jarak dasar = 0,15 × lebar glyph rata-rata label.
- Tambahkan variasi acak kecil (±0,3 mm).
- Jarak minimum 1 piksel sumber (0,1 mm) agar jitter spasi tidak membuat jarak negatif (D-019).
- Spasi antarkata = 3,0 × jarak dasar, naik 20% dari nilai awal 2,5 sesuai D-021.
- Untuk spasi antarkata tetap, jarak dasar memakai rata-rata lebar tinta seluruh label. Setiap varian dan jitter dipilih sekali sebelum word wrap, sehingga ukuran yang dihitung sama dengan yang dirender.

## Tahap 5: Susun di halaman

- Mulai dari batas atas area tulis (margin atas = margin dokumen).
- Setiap baris diletakkan dengan tinggi tetap. Jika baris berikutnya tidak muat, mulai halaman baru.
- Layout `undangan` belum diimplementasikan, sesuai D-011.
- Untuk `catatan`, garis panduan opsional digambar dengan warna abu-abu muda dan tidak ikut terhitung sebagai tinta.

## Tahap 6: Output

### PDF
- Ukuran A4.
- Glyph ditempel sebagai gambar dengan resolusi asli (10 px/mm).
- Metadata berisi `user_id` dan `doc_type`, tanpa nama pengguna.
- Keduanya disimpan di Subject JSON; Author dikosongkan. Watermark juga digambar sebagai teks halaman, bukan hanya metadata.

### PNG
- Resolusi 300 DPI (sekitar 2480 × 3508 px).
- Latar putih, tanpa transparansi.
- PNG tidak memuat ID pengguna. `render_report.json` terpisah berisi ID, jenis dokumen, seed, berkas hasil, karakter hilang, coverage di bawah ideal, jumlah glyph, tinggi baris, dan durasi; tidak menyimpan isi teks.

### Watermark tidak resmi
Setiap output wajib memiliki penanda "TIDAK RESMI - HASIL GENERASI" yang:
- Terlihat, di bagian bawah halaman, dengan warna abu-abu dan ukuran kecil.
- Tidak bisa dihapus dari PDF dengan mengubah metadata saja. Penanda harus berupa bagian dari gambar atau konten halaman.
- Ada di setiap halaman, termasuk halaman lanjutan.

## Penanganan karakter yang tidak ada

- Jika karakter tidak punya glyph (misalnya `@` atau `#` bila tidak ada di template), render kotak placeholder kosong dengan ukuran rata-rata.
- Catat karakter tersebut di log dan kembalikan daftar karakter yang hilang bersama output.
- Jangan membuang karakter diam-diam.

## Performa

- Target: kurang dari 2 detik per halaman A4 pada laptop biasa tanpa GPU.
- Glyph dimuat sekali per sesi render, bukan per karakter.
- Tulis PDF dengan satu pass, tidak menulis ulang halaman.

## API dan CLI

```python
from render_document import render_document
result = render_document(text, user_id, doc_type="catatan",
                         output_dir="outputs/catatan-01", seed=42)
```

CLI menerima `--user`, `--text-file` UTF-8, `--doc-type catatan|surat`, `--out`, `--format pdf png`, `--seed`, `--bank-root`, dan `--guidelines`. Tidak ada opsi menghilangkan watermark. Gunakan folder keluaran baru: hasil lama tidak ditimpa agar halaman PNG lama tidak bercampur. Teks kosong tetap menghasilkan satu halaman berwatermark. Karakter selain spasi dan baris baru yang tidak terpetakan tetap menjadi placeholder.

## Parameter yang perlu diuji

Angka-angka berikut adalah perkiraan awal dan wajib diuji sebelum dianggap baku:
- Rasio tinggi baris terhadap x-height (2,4).
- Batas jitter rotasi dan offset.
- Jarak dasar antarhuruf (0,15).
- Pengali spasi antarkata (3,0; penyesuaian awal dari 2,5 sesuai D-021).

Perubahan nilai harus dicatat di `DECISIONS.md`.

## Hal yang tidak dicakup

- Tulisan bersambung (cursive).
- Tekanan tinta dan variasi ketebalan garis.
- Koreksi kemiringan halaman di sisi render.
- Gaya cepat. Tahap awal hanya memakai satu gaya dari template (D-013).
