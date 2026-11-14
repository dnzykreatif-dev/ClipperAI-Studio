# ⚡ ClipperAI Studio — Universal AI Video Shorts & YouTube Automation
> **Open-Source Local Alternative untuk Opus Clip, Submagic, & Klap**  
> 100% Offline, Gratis Selamanya, Bebas Biaya Berlangganan, Bebas Kuota API Bulanan, serta Dilengkapi Otomatisasi Upload & SEO YouTube!

![ClipperAI Studio Preview](static/gui_preview.png)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Faster-Whisper](https://img.shields.io/badge/Faster--Whisper-1.0%2B-orange.svg)](https://github.com/SYSTRAN/faster-whisper)
[![YouTube Data API v3](https://img.shields.io/badge/YouTube_API-v3_Ready-red.svg)](https://developers.google.com/youtube/v3)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Pro_Motion-007808.svg)](https://ffmpeg.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌟 Apa itu ClipperAI Studio?
**ClipperAI Studio** adalah aplikasi desktop berbasis AI lokal yang mengubah video panjang (rekaman seminar, podcast, talkshow, edukasi kuliah, konten bisnis, gaming, hingga kajian/dakwah) menjadi **3–5 video vertikal Shorts/Reels viral (9:16)** secara otomatis hanya dalam 1 klik.

Bukan sekadar potong video monoton! ClipperAI Studio dilengkapi:
1. **Dynamic Motion Camera**: Punch-in zoom dinamis (1.30x) bergantian tiap 4 detik + transisi white flash cut untuk menjaga retensi penonton (*watch time*).
2. **Audio Jernih Siar (0 dB)**: Suara pembicara 100% jernih tanpa gangguan kresek-kresek atau suara mengecil, dipadukan dengan efek suara whoosh lembut.
3. **Floating B-Roll Cards**: Kartu visual intisari/hikmah otomatis muncul di menit penting video.
4. **Subtitle Pop-Bounce Gaya Alex Hormozi**: Teks kinetik beranimasi kata-demi-kata dengan highlight kontras tinggi.
5. **YouTube Automation & SEO (Shorts & Video Panjang)**: 1-klik upload langsung ke channel YouTube via official YouTube Data API v3, lengkap dengan riset kata kunci trending live, pembuat timestamps/chapters, dan penulisan deskripsi SEO otomatis.
6. **AI Faceless Video Maker (Text-to-Video)**: Ubah naskah atau ide tulisan menjadi video vertikal motion shorts dengan suara neural natural Indonesia dan visual kinetic gradient.
7. **Multi-Source Ingestion (Google Drive, Dropbox, YouTube, PC)**: Mendukung unduhan video langsung dari Google Drive, YouTube, atau folder PC lokal.

📖 **Buku Panduan & Deployment Lengkap**: Baca panduan teknis mendalam di [DOKUMENTASI_LENGKAP.md](DOKUMENTASI_LENGKAP.md).

---

## ✨ Fitur Unggulan

### 1. 🚀 Otomatisasi Upload YouTube (Shorts & Video Panjang)
- **Dukungan 2 Format Konten**:
  - 📱 **YouTube Shorts (9:16)**: Judul hook < 60 karakter, `#Shorts`, deskripsi vertikal ringkas.
  - 🎬 **Video Panjang (Full 16:9)**: Upload video utuh tanpa dipotong, judul sampai 100 karakter, lengkap dengan **Timestamps / Chapters** otomatis (`00:00 - Pembuka`, `02:15 - Inti`, dst.) serta rangkuman mendalam.
- **1-Click Auto Upload**: Unggah video langsung ke channel YouTube Anda via Google OAuth2.
- **Multi-Source Cloud Ingestion**: Masukkan tautan **Google Drive** publik (`drive.google.com/file/d/...`), Dropbox, atau YouTube — video langsung diunduh dan diproses.
- **Upload Langsung dari PC Tanpa Render Ulang**: Punya video jadi di PC? Tinggal pilih file, AI otomatis buatkan metadata & langsung upload.
- **Viral Title & Hook Generator**: Judul optimal sesuai format (Shorts atau Video Panjang).
- **Multiple Hook Variations**: Pilihan angle judul instan (⚡ Curiosity, ❓ Pertanyaan, ⚠️ Peringatan, 💎 Rahasia).
- **Manajemen Tags Ketat (< 500 Karakter)**: Menjamin tags tidak melebihi batas sistem YouTube.
- **Jadwal Posting Rekomendasi (WIB)**: Memberikan panduan jam tayang prime time (11:30–13:00 WIB & 17:30–20:30 WIB).
- **Opsi Instan Studio Web**: Tombol 1-klik salin seluruh metadata ke clipboard jika Anda ingin mengunggah via web browser secara manual.

### 2. 🎓 Integrasi Ruang Belajar: Web dnzykreatif (LMS Auto-Publish)
- **Terhubung Langsung ke Database Web dnzykreatif**: Otomatis tersinkronisasi ke Google Spreadsheet portal Anda (`1uhes6wkdRqdgqGtFQ57BWfAZt5pvTukuzO3-vBw-TR4`).
- **Mode Video Unlisted**: Mengunggah video materi sebagai *Unlisted* di YouTube agar aman dan hanya bisa diputar oleh siswa yang terdaftar.
- **Auto-Formatting Format Pembelajaran**: Menyusun format teks materi dengan standar CSS `.hadith-box` (`Faedah:` dan `Artinya:`) serta daftar menit materi (*timestamps*) yang kompatibel dengan pemutar video [CourseView.html](file:///E:/PROJECTS/apps-script/Web%20dnzykreatif/CourseView.html).
- **1-Klik Terbitkan ke Sheet `Lessons`**: Sekali klik tombol *Terbitkan*, materi langsung aktif di ruang belajar siswa tanpa perlu membuka admin website secara manual!

### 3. 🔎 Riset Tren Kata Kunci Live (YouTube Autocomplete API)
- Mengambil kata kunci trending pencarian real-time langsung dari mesin pencari YouTube Indonesia.
- **100% Bebas Biaya**: Bekerja langsung tanpa memerlukan kunci API berbayar.
- Cukup klik tombol tag untuk langsung memasukkannya ke daftar tags video Anda.

### 3. 🎬 Dynamic Punch-In Camera & Pro Motion Graphics
- Mengeliminasi video yang membosankan dan monoton dengan efek kamera *punch-in zoom* bergantian setiap 4 detik.
- Transisi *white flash cut* sinematik saat pergantian adegan.
- Floating B-roll cards intisari konten yang muncul secara otomatis.
- Subtitle kinetik ASS beranimasi *pop-bounce* kata-demi-kata gaya Alex Hormozi.

### 4. 🎙️ Audio Jernih & Multi-Track SFX
- Penanganan audio cerdas dengan normalisasi desibel (0 dB) sehingga suara asli pembicara terdengar lantang dan kristal.
- Dilengkapi kamus transliterasi istilah dan ayat suci agar ejaan subtitle tetap akurat.

### 5. 🌐 Dukungan Multi-Niche Universal
AI secara otomatis menyesuaikan gaya judul hook, header atas, dan hashtag sesuai topik video:
- 🌐 **Universal / Semua Topik**: Vlog, wawancara santai, tips harian, dan dokumenter.
- 🕌 **Kajian & Dakwah**: Nasihat agama, renungan hadits, dan pesan hikmah akhlak.
- 🎙️ **Podcast & Talkshow**: Fokus pada pertanyaan tajam, jawaban mengejutkan, dan interaksi seru.
- 💡 **Bisnis, Finansial & Tech**: Mengutamakan strategi omset, modal, investasi, dan kiat sukses.
- 🚀 **Motivasi & Mindset**: Menyoroti kutipan inspiratif dan pesan reflektif bertenaga.
- 📚 **Edukasi & Kuliah**: Penjelasan fakta penting, sains, wawasan baru, dan istilah penting.
- 🎮 **Gaming & Hiburan**: Momen lucu, clutch gameplay, dan reaksi seru.

---

## 🚀 Panduan Instalasi & Penggunaan

### Prasyarat
1. **Python 3.10+** terinstal di komputer.
2. **FFmpeg** terinstal dan terdaftar di PATH sistem (ketik `ffmpeg -version` di terminal untuk mengecek).

---

### Cara 1: Setup Cepat di Windows (Rekomendasi)

1. **Clone Repositori**:
   ```bash
   git clone https://github.com/dnzykreatif-dev/ClipperAI-Studio.git
   cd ClipperAI-Studio
   ```

2. **Jalankan Installer Dependensi**:
   Klik ganda file **`install_requirements.bat`**, atau jalankan di terminal:
   ```bash
   pip install -r requirements.txt
   ```

3. **Buat Shortcut Desktop (1-Klik)**:
   Klik kanan file `create_shortcut.ps1` -> *Run with PowerShell*, atau ketik di PowerShell:
   ```powershell
   powershell -ExecutionPolicy Bypass -File create_shortcut.ps1
   ```

4. **Jalankan Aplikasi**:
   Klik ganda **`Start_ClipperAI.bat`** (atau buka shortcut **ClipperAI Studio** di Desktop Anda).  
   Browser akan otomatis membuka `http://127.0.0.1:8000`.

---

### 🔑 Pengaturan YouTube Data API (Opsional untuk Fitur Auto-Upload)

Untuk mengaktifkan fitur upload langsung 1-klik ke channel YouTube Anda:
1. Buka [Google Cloud Console](https://console.cloud.google.com/) dan buat proyek baru.
2. Aktifkan **YouTube Data API v3** pada menu *APIs & Services > Library*.
3. Buka menu *Credentials* -> klik **Create Credentials** -> pilih **OAuth client ID** (Pilih tipe aplikasi: **Desktop App**).
4. Unduh file JSON kredensial tersebut, ubah namanya menjadi `client_secrets.json`, dan letakkan di folder utama `ClipperAI-Studio/`.
5. Di antarmuka ClipperAI Studio, klik tombol **"Hubungkan Akun YouTube Sekarang"**. Browser akan membuka halaman izin Google untuk mengotorisasi channel Anda.

*Catatan: Jika belum memiliki kredensial API, Anda tetap bisa menggunakan tombol **"Buka YouTube Studio Web"** di modal upload yang otomatis menyalin judul, deskripsi, dan tag ke clipboard Anda!*

---

## 📁 Struktur Repositori

```
ClipperAI-Studio/
├── app.py                  # Server FastAPI, Router API & Integrasi Modul
├── clipper_engine.py       # Engine Video: Faster-Whisper, Dynamic Zoom, SFX & Subtitle ASS
├── yt_seo_engine.py        # Engine SEO: Riset Tren YouTube & Generator Metadata Viral
├── yt_uploader.py          # Uploader: Google OAuth2 & YouTube Data API v3 Upload Resumable
├── Start_ClipperAI.bat     # File peluncur otomatis untuk Windows
├── install_requirements.bat# Script instalasi dependensi otomatis
├── create_shortcut.ps1     # Script pembuat shortcut Desktop
├── requirements.txt        # Daftar pustaka Python yang dibutuhkan
├── templates/
│   └── index.html          # Web GUI Modern Dark Glassmorphism + YouTube Studio Modal
├── static/
│   ├── gui_preview.png     # Screenshot tampilan antarmuka
│   └── sfx/                # Efek suara transisi (whoosh, pop, chime)
├── uploads/                # Direktori sementara video input
└── outputs/                # Direktori penyimpanan hasil video Shorts/Reels MP4 & Metadata SEO
```

---

## 📄 Lisensi
Didistribusikan di bawah lisensi open-source **MIT License**. Silakan gunakan, kembangkan, dan modifikasi secara bebas untuk kebutuhan personal maupun komersial.

---

*ClipperAI Studio dikembangkan dengan ❤️ untuk mendukung kreator konten mandiri menghasilkan karya berkualitas tinggi tanpa batasan biaya langganan.*
