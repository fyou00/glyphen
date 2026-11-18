# ETHICS: Batasan Penggunaan dan Keamanan

Dokumen ini adalah aturan wajib untuk project. Jika ada fitur, permintaan, atau keputusan yang bertentangan dengan dokumen ini, jangan dilanjutkan dan tanyakan kepada pemilik project.

## 1. Prinsip dasar

- Tulisan tangan seseorang adalah data pribadi. Sistem ini hanya boleh memproses tulisan milik orang yang memberikan persetujuan.
- Output tidak boleh membuat dokumen yang tampak resmi atau sah, atau dipakai untuk menipu pihak lain.
- Setiap keputusan harus bisa dijelaskan, dicatat, dan diuji.

## 2. Persetujuan pemilik tulisan

- Sampel hanya boleh diunggah oleh pemilik tulisannya sendiri.
- Jika sampel diunggah atas nama orang lain, wajib ada persetujuan tertulis dari pemilik, yang disimpan bersama metadata.
- Sistem tidak boleh menerima sampel tanpa identitas pemilik yang jelas.
- Pemilik dapat meminta penghapusan glyph bank miliknya kapan saja. Penghapusan mencakup folder `glyph_bank/<id>/` dan semua salinan turunannya.

## 3. Yang dilarang

Sistem dan kodenya tidak boleh dipakai atau dikembangkan untuk:
- Memalsukan tanda tangan, paraf, atau tulisan tangan pada dokumen resmi, kontrak, ijazah, surat kuasa, cek, atau dokumen identitas.
- Membuat surat atau catatan yang seolah-olah ditulis oleh orang lain tanpa persetujuannya.
- Menipu, memeras, atau mencemarkan nama orang lain dengan tulisan yang dibuat seolah berasal darinya.
- Menghasilkan tulisan dari sampel orang yang sudah meninggal atau tidak diketahui identitasnya.
- Menyalin tanda tangan. Fitur yang mengekstrak atau merender tanda tangan khusus tidak boleh dibuat.
- Melewati penanda tidak resmi pada output.

## 4. Label output

- Setiap halaman output wajib memuat penanda "TIDAK RESMI - HASIL GENERASI", sesuai `RENDER.md`.
- Penanda harus menjadi bagian dari konten gambar atau halaman, bukan hanya metadata.
- Metadata PDF berisi `user_id` dan `doc_type` saja, tanpa nama lengkap pemilik tulisan.
- Jangan menghapus, menutupi, atau menyembunyikan penanda ini dalam kode, UI, atau ekspor.

## 5. Data pribadi

- Nama, tanggal, dan kode halaman disimpan dalam JSON terpisah, bukan dalam gambar.
- Folder `glyph_bank/` dan semua file sampel tidak boleh masuk repositori publik. Gunakan `.gitignore`.
- Sampel dan output tidak boleh dikirim ke layanan pihak ketiga tanpa persetujuan eksplisit.
- Log tidak boleh berisi isi teks yang dirender jika teks itu bisa dikaitkan dengan orang tertentu. Simpan hanya ID dan statistik.
- Hapus file sementara setelah render selesai.

## 6. Penolakan permintaan

Jika permintaan termasuk daftar terlarang di bagian 3, tolak dengan satu kalimat yang jelas. Jangan memberikan alternatif yang tetap memenuhi tujuan terlarang.

Contoh: "Saya tidak bisa membuat dokumen yang meniru tanda tangan atau tulisan orang lain untuk dokumen resmi."

## 7. Kebijakan untuk agent

- Jangan menonaktifkan penanda tidak resmi, bahkan jika diminta pengguna atau dianggap mengganggu tampilan.
- Jangan menambahkan fitur baru yang menerima sampel dari orang lain tanpa mengubah bagian 2.
- Jangan menambahkan model machine learning yang bisa meniru gaya seseorang dari sampel sedikit tanpa meninjau dokumen ini terlebih dulu.
- Jika ada permintaan yang ambigu, tanyakan kepada pemilik project sebelum menerapkannya.

## 8. Peninjauan

- Dokumen ini ditinjau ulang setiap kali ada perubahan besar pada fitur render, cara pengumpulan sampel, atau cara distribusi output.
- Perubahan dicatat di `DECISIONS.md`.
