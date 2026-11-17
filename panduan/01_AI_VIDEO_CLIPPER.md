# 🎬 Panduan 01: AI Video Clipper (Video Panjang ➔ Shorts Viral)

Fitur **AI Video Clipper** adalah mesin inti untuk mengubah rekaman video horizontal panjang (seperti Kajian, Khutbah, Podcast, Wawancara, Kuliah/Edukasi, Bisnis, atau Gaming) menjadi klip vertikal **9:16** siap upload ke YouTube Shorts, Instagram Reels, dan TikTok.

---

## 📥 Sumber Input yang Didukung

Anda dapat memasukkan video melalui dua metode pada kolom **Magic Bar**:

1. **Memasukkan Tautan (URL Link)**:
   - Tempel (*paste*) tautan langsung ke kolom input:
     - Tautan YouTube (video panjang atau siaran langsung)
     - Tautan TikTok
     - Tautan publik Google Drive
     - Tautan album/video Google Photos
2. **Memilih File Video dari Komputer (File Lokal)**:
   - Klik ikon folder 📁 di sisi kiri kolom input.
   - Pilih file video berekstensi `.mp4`, `.mkv`, atau `.mov` dari harddisk Anda.
   - File otomatis terunggah ke sistem untuk diproses.

---

## ⚙️ Menyesuaikan Parameter di Dek Konfigurasi

Sebelum menekan tombol render, periksa dan sesuaikan pengaturan di **Dek Konfigurasi 4-Kolom**:

```
+---------------------+---------------------+---------------------+---------------------+
| 🏷️ NICHE & KATEGORI | 🧠 AI & TRANSKRIPSI | ✂️ KLIP & EDITING   | 🛡️ SUBTITLE & BRAND |
+---------------------+---------------------+---------------------+---------------------+
```

### Kolom 1: 🏷️ Niche & Kategori
- **Kategori Konten**:
  - `🌐 Universal / Semua Video`: Cocok untuk video umum atau campuran topik.
  - `🕌 Kajian & Dakwah`: Mengoptimalkan deteksi hadits, dalil, dan terminologi bahasa Arab.
  - `🎙️ Podcast & Wawancara`: Mengoptimalkan pergantian shot dua arah antara host dan bintang tamu.
  - `💡 Bisnis & Finansial`: Menyoroti tips omset, keuangan, dan investasi.
  - `🚀 Motivasi & Mindset`: Menyoroti kutipan inspiratif berenergi tinggi.
  - `📚 Edukasi & Kuliah`: Menyoroti penjelasan konsep terstruktur.
  - `🎮 Gaming & Hiburan`: Menyoroti momen lucu (*funny moments*) dan reaksi seru.
- **Header Teks (Opsional)**:
  - Tuliskan judul tema yang akan ditempelkan di bagian atas frame video (misal: `✨ MUTIARA HIKMAH`, `💡 TIPS BISNIS 2026`). Biarkan kosong jika ingin otomatis ditentukan oleh AI.

### Kolom 2: 🧠 AI & Transkripsi
- **Model Whisper AI**:
  - `Base AI (Cepat & Rekomendasi)`: Model seimbang yang sangat cepat dan akurat untuk sebagian besar bahasa Indonesia sehari-hari.
  - `Small AI (Akurasi Tinggi)`: Model lebih detail, sangat disarankan untuk istilah fiqih, kajian Islam, atau istilah teknis ilmiah.
  - `Turbo Tiny (Super Cepat)`: Mengutamakan kecepatan pemrosesan jika spesifikasi PC terbatas.
- **Rentang Pindai Video**:
  - `15 Menit Awal (1-2 Mnt)`: Sangat cepat, ideal untuk mencari klip pembuka yang menarik perhatian.
  - `30 Menit Awal`: Pilihan seimbang untuk materi berdurasi sedang.
  - `Seluruh Video`: Memindai seluruh durasi video dari awal hingga akhir (memerlukan waktu lebih lama).

### Kolom 3: ✂️ Klip & Editing Pro
- **Target Jumlah Klip**:
  - Pilih jumlah video yang ingin dihasilkan: `1`, `3`, `5`, `7 (Populer)`, `10`, `15`, `20`, `30`, atau `🔥 Semua Momen Viral (Uncapped)`.
- **Intensitas Dynamic Cut**:
  - `⚡ Pro Normal`: Kombinasi multi-shot camera punch-in, transisi halus, B-Roll card penjelas, dan grading warna Argon LUT.
  - `🔥 Pro Agresif`: Potongan cepat (*fast cut*), pergantian sudut zoom setiap 2-3 detik, sangat cocok untuk konten viral energi tinggi.
  - `✨ Pro Halus`: Zoom kamera lambat dan tenang, cocok untuk renungan, nasihat santai, atau puisi.

### Kolom 4: 🛡️ Subtitle & Branding
- **Ukuran Subtitle Hormozi**:
  - `Kecil & Rapi (56px) [Default]`: Ukuran standar estetis, tidak menutupi wajah pembicara.
  - `Super Mini (46px)`: Ukuran kompak minimalis.
  - `Sedang (68px)`: Lebih mencolok untuk pemirsa di layar smartphone kecil.
  - `Besar (82px)`: Sangat kontras dan tebal untuk gaya hype.
- **Logo Brand Watermark**:
  - Pilih posisi logo Anda: `Kanan Atas`, `Kiri Atas`, `Tengah Atas`, `Kanan Bawah`, atau `Tanpa Logo`.
  - Secara default menampilkan logo brand Anda (`dn-zy watermark`).

---

## 🚀 Memulai Pemrosesan & Memantau Pipeline AI

1. Klik tombol **`🚀 Buat Shorts Sekarang`**.
2. **Kartu Live Progress (Alur Kerja Galih Pranowo)** akan otomatis muncul dan menampilkan 6 tahapan pemrosesan:
   - **Tahap 1**: *Transkrip kata-per-kata* (Faster-Whisper mengenali setiap kata dan timestamp milidetiknya).
   - **Tahap 2**: *AI pilihkan momen paling viral* (Algoritma scoring menganalisis hook 3 detik awal, kepadatan insight, dan emosi).
   - **Tahap 3**: *Jeda kosong terbuang* (Menghapus jeda hening dan nafas tanpa merusak kelancaran vokal).
   - **Tahap 4**: *Crop 9:16 ikutin wajah* (AI Face Tracking YuNet DNN menjaga posisi wajah tetap di tengah layar).
   - **Tahap 5**: *Subtitle per kata* (Memasang subtitle bergerak gaya Alex Hormozi dengan warna dinamis).
   - **Tahap 6**: *Suara rata · 0 dB (Loudnorm)* (Normalisasi audio siaran EBU R128 agar jernih dan tidak mendem).

---

## 🎞️ Mengelola Hasil Video di Galeri

Setelah proses selesai, kartu video akan otomatis muncul di bagian bawah pada **Galeri Video Shorts Hasil AI**:

Setiap kartu video dilengkapi dengan:
1. **Skor Viralitas (*Virality Score*)**: Indikator potensi FYP (contoh: `🔥 96% Virality`).
2. **Pemutar Video Vertikal 9:16**: Pratinjau langsung dengan tombol navigasi cepat `↺ -5s` dan `+5s ↻`.
3. **Spesifikasi Teknis**: Menampilkan jumlah potongan kamera (*cuts*), kartu B-Roll, profil warna LUT, dan desibel audio.
4. **Judul & Ringkasan Konten**: Menampilkan headline viral serta ringkasan pesan utama kutipan.
5. **Tombol Tindakan Cepat**:
   - **`⬇️ MP4`**: Mengunduh video berkualitas tinggi ke folder unduhan PC Anda.
   - **`🖼️ Thumb`**: Mengunduh gambar thumbnail resolusi tinggi untuk sampul video.
   - **`📋 Naskah`**: Menyalin judul, caption, dan hashtag sekaligus ke clipboard.
   - **`🔍 Lembar Kontak Visual (QA Check)`**: Membuka lembar komparasi frame untuk memastikan kualitas gambar prima.
   - **`🚀 Publikasikan (YT · FB · TikTok)`**: Membuka studio pengunggahan untuk upload instan ke media sosial.

---

> ➡️ **Langkah Selanjutnya**:  
> Baca [02_AI_FACELESS_STUDIO.md](file:///E:/PROJECTS/kajian_clipper/panduan/02_AI_FACELESS_STUDIO.md) untuk mempelajari cara membuat video vertikal dari nol tanpa perlu rekaman video!
