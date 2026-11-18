# TEMPLATE: Halaman Sampel Tulisan Tangan

Dokumen ini menjelaskan geometri template yang dihasilkan `make_template.py` dan dibaca oleh `extract_glyphs.py`. Jika salah satu berubah, ketiganya harus diperbarui bersama.

File keluaran: `template_tulisan_A4.pdf` (3 halaman, A4 210 × 297 mm).
Cetak dengan ukuran 100%, jangan memakai "fit to page".

## Elemen yang ada di setiap halaman

- **Empat marker sudut**: kotak hitam pejal 8 × 8 mm.
  - Posisi kiri-bawah marker: (10, 10), (192, 10), (10, 279), (192, 279) mm dari kiri-bawah.
  - Pusat marker (koordinat dari kiri-atas, dipakai `extract_glyphs.py`): TL (14, 14), TR (196, 14), BR (196, 283), BL (14, 283) mm.
- **Judul dan petunjuk** di bagian atas.
- **Kode halaman** di bagian bawah tengah: `TPL-01`, `TPL-02`, atau `TPL-03`.
- **Kotak tulis** dengan garis panduan:
  - Garis putus-putus abu-abu di 20% tinggi (baseline).
  - Garis putus-putus abu-abu di 55% tinggi (x-height).
  - Tidak ada garis panduan di luar kotak.

## Halaman 1 (TPL-01): huruf kecil

| Parameter | Nilai |
|---|---|
| Isi | a–z (26 baris) |
| Varian per huruf | 5 |
| Posisi kolom label | x = 25 mm |
| Lebar label | 12 mm |
| Ukuran kotak | 22 × 8 mm |
| Jarak antar-kotak | 2 mm |
| Tinggi baris | 9,3 mm |
| Batas atas baris pertama | 32 mm dari atas |

Kunci label: `lower_a` sampai `lower_z`.

## Halaman 2 (TPL-02): huruf kapital

| Parameter | Nilai |
|---|---|
| Isi | A–Z, dibagi dua kolom |
| Kolom kiri | A–M (13 baris), x = 15 mm |
| Kolom kanan | N–Z (13 baris), x = 110 mm |
| Varian per huruf | 5 |
| Lebar label | 10 mm |
| Ukuran kotak | 14 × 12 mm |
| Jarak antar-kotak | 1,5 mm |
| Tinggi baris | 16 mm |
| Batas atas baris pertama | 32 mm dari atas |

Kunci label: `upper_A` sampai `upper_Z`.

## Halaman 3 (TPL-03): angka, tanda baca, dan kalimat contoh

### Angka (kiri)
| Parameter | Nilai |
|---|---|
| Isi | 0–9 (10 baris) |
| Posisi | x = 15 mm, judul "Angka 0-9" di 40 mm dari atas |
| Varian per angka | 3 |
| Lebar label | 10 mm |
| Ukuran kotak | 16 × 9 mm |
| Jarak antar-kotak | 2 mm |
| Tinggi baris | 12 mm |

Kunci label: `digit_0` sampai `digit_9`.

### Tanda baca (kanan)
| Parameter | Nilai |
|---|---|
| Isi | `. , ? ! : ; " ' - ( )` (11 baris) |
| Posisi | x = 110 mm, judul "Tanda baca" di 40 mm dari atas |
| Varian per tanda | 3 |
| Lebar label | 12 mm |
| Ukuran kotak | 16 × 9 mm |
| Jarak antar-kotak | 2 mm |
| Tinggi baris | 12 mm |

Kunci label tanda baca memakai nama, bukan simbol, supaya aman sebagai nama folder:

| Simbol | Kunci |
|---|---|
| `.` | `punct_dot` |
| `,` | `punct_comma` |
| `?` | `punct_question` |
| `!` | `punct_exclam` |
| `:` | `punct_colon` |
| `;` | `punct_semicolon` |
| `"` | `punct_dquote` |
| `'` | `punct_squote` |
| `-` | `punct_hyphen` |
| `(` | `punct_lparen` |
| `)` | `punct_rparen` |

### Kalimat contoh (bawah)
- Judul "Kalimat contoh" di 113 mm dari bawah. Teks referensi abu-abu tidak dicetak, sesuai D-022, agar tidak mengganggu area tulis.
- Dua kotak tulis, masing-masing 180 × 12 mm, mulai dari x = 15 mm dengan jarak 14 mm. Koordinat kiri-bawah kotak: (15, 97) dan (15, 83) mm dari kiri-bawah halaman (D-016).
- Tulis `The quick brown fox jumps over the lazy dog` dua kali: satu kalimat di setiap kotak besar. Kalimat referensi cukup dibaca dari dokumen ini. Dua garis putus-putus di dalam kotak adalah panduan tulisan, bukan dua baris terpisah.
- Bagian ini **tidak** diekstrak ke glyph bank. Dipakai untuk evaluasi gaya.

## Aturan cetak dan pengisian

- Gunakan pulpen hitam atau biru tua. Pensil dan pulpen tipis membuat ambang tinta tidak stabil.
- Tulis di dalam kotak. Tinta yang keluar kotak akan ditandai `touches_edge`.
- Jangan menggaris ulang atau menghapus garis panduan.
- Jika ada kotak yang salah, tulis ulang di kotak yang sama, jangan di kotak lain.
- Foto harus memuat keempat marker. Foto tanpa marker lengkap akan ditolak.

## Sinkronisasi

Jika mengubah salah satu nilai di atas:
1. Ubah `make_template.py`.
2. Ubah fungsi `page_layout()` di `extract_glyphs.py`.
3. Perbarui tabel di dokumen ini dan `SPEC.md` bagian 4.
4. Catat perubahan di `DECISIONS.md`.
