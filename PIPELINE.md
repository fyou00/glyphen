# PIPELINE: Dari Foto Template ke Glyph Bank

Dokumen ini menjelaskan alur ekstraksi yang dijalankan oleh `extract_glyphs.py`. Geometri halaman mengikuti `TEMPLATE.md`. Status dan format output harus sesuai dengan `SPEC.md` bagian 5.

## Gambaran umum

```
foto TPL-01, TPL-02, TPL-03
        │
        ▼
[1] Baca gambar
        │
        ▼
[2] Deteksi 4 marker sudut
        │
        ▼
[3] Koreksi perspektif ke A4 (10 px/mm)
        │
        ▼
[4] Potong setiap kotak (inset 1,2 mm)
        │
        ▼
[5] Klasifikasi kotak: ok / empty / touches_edge
        │
        ▼
[6] Simpan glyph + manifest.json + debug_page*.png
        │
        ▼
[7] Validasi coverage (coverage.json)
```

## Masukan

| Item | Keterangan |
|---|---|
| Foto | JPG atau PNG, satu foto per halaman |
| Urutan | Wajib TPL-01, TPL-02, TPL-03 |
| ID pengguna | String, dipakai sebagai nama folder |
| Syarat foto | Keempat marker sudut harus masuk ke dalam foto |

Perintah:
```bash
python extract_glyphs.py --user <id> --pages tpl01.jpg tpl02.jpg tpl03.jpg
```

## Tahap 1: Baca gambar

- Foto dibaca dengan OpenCV dalam format BGR.
- Jika gambar tidak bisa dibaca, proses berhenti dengan pesan error.

## Tahap 2: Deteksi marker

Kandidat marker dicari dengan langkah berikut:

1. Konversi ke grayscale, lalu blur Gaussian 5 × 5.
2. Threshold Otsu pada grayscale yang sudah diblur, tinta dibuat putih (D-017).
3. Cari kontur luar dengan `RETR_EXTERNAL`.
4. Saring kandidat:
   - Minimal 90% piksel kotak pembatas berupa tinta pada mask Otsu; kotak garis ditolak. Pemeriksaan ini menggantikan penolakan semua kontur berlubang yang gagal pada marker scan bertekstur (D-017).
   - Luas antara 0,015% dan 1% luas foto.
   - Rasio lebar terhadap tinggi antara 0,75 dan 1,33.
   - Pejal: luas kontur / luas kotak pembatas minimal 0,9.
5. Untuk setiap sudut foto (kiri-atas, kanan-atas, kanan-bawah, kiri-bawah), pilih kandidat terdekat.

Kegagalan:
- Kurang dari 4 kandidat: error.
- Kandidat terdekat lebih dari 25% sisi terpendek foto dari sudut: error.
- Dua sudut memilih kandidat yang sama: error.

Marker dibedakan oleh posisi, bukan bentuk. Karena itu urutan pemasangan selalu sama selama keempat marker terlihat.

## Tahap 3: Koreksi perspektif

- Empat titik sumber (marker di foto) dipetakan ke empat titik tujuan (posisi marker di A4 pada 10 px/mm) dengan `getPerspectiveTransform`.
- Hasil diwarp ke ukuran 2100 × 2970 px dengan latar putih.

## Tahap 4: Potong kotak

- Setiap kotak diambil dari `page_layout(n)` dalam satuan mm.
- Inset 1,2 mm dari setiap sisi, supaya garis kotak tidak ikut terpotong.
- Konversi koordinat: sumbu y dibalik karena PDF dihitung dari bawah dan gambar dari atas.

## Tahap 5: Klasifikasi kotak

Setiap kotak diberi salah satu status:

| Status | Syarat | Tindakan |
|---|---|---|
| `empty` | Rasio piksel tinta (di bawah 128) < 0,3% | Tidak disimpan |
| `touches_edge` | Ada tinta dalam 3 piksel dari tepi | Disimpan, tandai untuk ditinjau |
| `ok` | Selain di atas | Disimpan |

Garis panduan abu-abu tidak dihitung sebagai tinta karena lebih terang dari ambang.

## Tahap 6: Simpan hasil

Struktur output:

```
glyph_bank/
└── <id>/
    ├── glyphs/
    │   ├── lower_a/
    │   │   ├── lower_a_01.png
    │   │   └── ...
    │   ├── upper_A/
    │   ├── digit_0/
    │   └── punct_question/
    ├── manifest.json
    ├── debug_page1.png
    ├── debug_page2.png
    └── debug_page3.png
```

Aturan penamaan:
- Varian dinomori dari 01. Angka dan tanda baca hanya sampai 03.
- Kotak berstatus `empty` tidak punya file, tetapi tetap tercatat di manifest.

Isi `manifest.json` per entri:

```json
{
  "label": "lower_a",
  "variant": 1,
  "page": 1,
  "status": "ok",
  "ink_ratio": 0.0412,
  "file": "<id>/glyphs/lower_a/lower_a_01.png"
}
```

`debug_page*.png` berisi hasil koreksi perspektif dengan kotak berwarna:
- Hijau: `ok`
- Kuning: `touches_edge`
- Merah: `empty`

## Tahap 7: Validasi coverage

Coverage dihitung dari manifest, lalu ditulis ke `glyph_bank/<id>/coverage.json`:
- Hitung varian `ok` dan `touches_edge` per label.
- Tandai label dengan kurang dari 3 varian sebagai tidak lengkap.
- Huruf dengan 5 varian dianggap lengkap.

Aturan dari `AGENTS.md`: jika coverage kurang, minta pengguna mengulang halaman tertentu. Jangan menyalin varian lain untuk mengisi kekurangan.

## Kegagalan dan penanganannya

| Kondisi | Penanganan |
|---|---|
| Marker kurang dari 4 | Berhenti, minta foto ulang |
| Marker tidak dekat sudut | Berhenti, minta foto ulang |
| Kotak salah potong (terlihat di debug) | Laporkan, jangan lanjut ke render |
| Banyak kotak `empty` | Minta pengguna mengulang halaman |
| Banyak kotak `touches_edge` | Tinjau manual, pertimbangkan tulis ulang |

## Integrasi profil melalui antarmuka

`profiles.py` memakai `process_page()` yang sama dengan CLI setelah identitas dan persetujuan pemilik tersimpan. Tiga JPEG/PNG diurutkan secara eksplisit sebagai TPL-01/02/03, dinormalisasi ke RGB tanpa metadata, diputar sesuai pilihan, dan disimpan bersama hasil percobaan dalam folder profil pribadi. Geometri dan ambang klasifikasi tidak berubah.

Ekstraksi menghasilkan manifest, status/kotak kosong tiap label, dan tiga debug dengan `visual_review.passed: false`. Pemilik harus memeriksa ketiga halaman dan menerima setiap varian tepi. Potongan salah menghentikan proses sebelum coverage. Setelah tinjauan lolos, hitung `coverage.json` dan periksa lagi dengan engine; jika huruf kurang dari 3 varian, profil tetap belum siap serta menampilkan halaman yang perlu diulang. Upload ulang mengganti hasil aktif setelah seluruh halaman berhasil, tanpa mencampur varian lama; setiap percobaan tetap tersimpan untuk keterlacakan dan ikut dihapus bersama profil.

Evaluator segmentasi mengenali `source_root: profile` pada consent baru; metadata lama tetap memakai `scan_demo/`. Semua jalur sumber harus berada dalam root yang sesuai. Gambar yang diupload dalam slot halaman salah belum dikenali lewat OCR: pemilik wajib memastikan urutan dan label saat meninjau.

## Batasan saat ini

- Pencahayaan kuat atau bayangan dapat membuat kotak kosong palsu. Ambang tinta bisa disesuaikan jika perlu.
- Tulisan yang terlalu tipis tidak terhitung sebagai tinta.
- Kalimat contoh di TPL-03 tidak diekstrak.
- Pipeline sudah diuji pada scan tulisan nyata (lihat Uji 1 dan Uji 2 di `EVALUATION.md`); ketahanan pada foto HP berbayang atau pencahayaan tidak merata belum diuji.
