# 📖 BUKU PANDUAN LENGKAP & DOKUMENTASI SISTEM: CLIPPERAI STUDIO PRO
> **Repositori Resmi**: `https://github.com/dnzykreatif-dev/ClipperAI-Studio.git`  
> **Folder Utama di PC**: `E:\PROJECTS\kajian_clipper`  
> **Lisensi**: MIT (Bebas Dipakai, 100% Gratis, Tanpa Kuota Token/Langganan)

---

## 📑 DAFTAR ISI
1. [Penjelasan Folder Proyek & Status Bersih](#1-penjelasan-folder-proyek--status-bersih)
2. [Peta File & Arsitektur Kode](#2-peta-file--arsitektur-kode)
3. [Fitur Utama Sistem](#3-fitur-utama-sistem)
   - [Mode 1: AI Video Clipper (Video Panjang ➔ Shorts Viral)](#mode-1-ai-video-clipper)
   - [Mode 2: AI Faceless Studio (Teks Naskah ➔ Shorts Motion)](#mode-2-ai-faceless-studio)
   - [Mode 3: Otomatisasi YouTube & Sinkronisasi LMS Web dnzykreatif](#mode-3-otomatisasi-youtube--lms)
4. [Panduan Menjalankan di Komputer Ini (1-Klik)](#4-panduan-menjalankan-di-komputer-ini)
5. [Panduan Pindah / Setup di Laptop atau PC Lain](#5-panduan-pindah--setup-di-laptop-lain)
6. [Konfigurasi Google Cloud & YouTube API](#6-konfigurasi-google-cloud--youtube-api)
7. [Konfigurasi Database LMS Spreadsheet Web dnzykreatif](#7-konfigurasi-database-lms-spreadsheet)
8. [Tanya Jawab & Pemecahan Masalah (Troubleshooting)](#8-tanya-jawab--troubleshooting)

---

## 1. PENJELASAN FOLDER PROYEK & STATUS BERSIH

Sebelumnya di direktori `E:\PROJECTS\` terdapat beberapa folder yang mirip:
- `E:\PROJECTS\kajian_clipper` ➔ **FOLDER UTAMA & AKTIF (PRODUCTION)**. Inilah seluruh kode aplikasi ClipperAI Studio yang terhubung ke Git GitHub.
- `E:\PROJECTS\AutoClip_Studio` ➔ Folder draft / prototipe lama (tanggal 13 Nov pagi). Sudah dipindahkan dan dirapikan ke `E:\PROJECTS\archive\AutoClip_Studio_Draft_Awal`.
- `E:\PROJECTS\motion_render` ➔ Folder eksperimen render animasi promosi Santri Analytics berbasis Node.js/Puppeteer. Sudah dipindahkan dan dirapikan ke `E:\PROJECTS\archive\Santri_Analytics_Promo_Experiment`.

> [!IMPORTANT]
> **Selalu gunakan folder `E:\PROJECTS\kajian_clipper`**. Segala pengembangan, penambahan fitur, dan perbaikan selalu dilakukan di folder ini dan tersinkronisasi ke Git GitHub `dnzykreatif-dev/ClipperAI-Studio`.

---

## 2. PETA FILE & ARSITEKTUR KODE

Di dalam folder `E:\PROJECTS\kajian_clipper`, berikut adalah daftar file dan fungsinya:

```text
E:\PROJECTS\kajian_clipper/
│
├── app.py                      # [FastAPI] Backend server utama: REST API, Background Jobs, routing
├── clipper_engine.py           # [AI Clipper Engine] Transkripsi Faster-Whisper, Dynamic Punch-In zoom, Alex Hormozi Pop ASS, Deteksi Viral Hook
├── pro_editor.py               # [Pro Video Editor Engine] Face-tracking YuNet, multi-shot jump cuts (close/medium/broll/wide), Argon 3D LUTs, light-leaks, SFX
├── faceless_engine.py          # [AI Faceless Engine] Text-to-Video Engine: Edge-TTS natural voice, Hormozi sync, Procedural Radial Motion Canvas
├── yt_seo_engine.py            # [AI SEO Engine] Generator Judul Viral, Timestamps, Deskripsi SEO, Tags (<500 char), dan Riset Tren YouTube
├── yt_uploader.py              # [YouTube Engine] Google OAuth2 & YouTube Data API v3 Uploader (Mendukung Publik & Unlisted)
├── course_sync.py              # [LMS Sync Engine] Sinkronisasi otomatis ke Google Spreadsheet Web dnzykreatif (Sheet 'Lessons')
│
├── remotion_studio/            # [3D Cartoon Remotion Engine] Mesin animasi 3D Three.js + Remotion untuk video kartun vertikal bergaya Kurzgesagt/OverSimplified
│   ├── src/videos/bridge/      # Pipeline 3D: Bridge.tsx, toon.ts (karakter 2D bean-head), world.ts (dunia 3D), story.ts (kamera sinematik)
│   ├── package.json            # Dependensi React 19, Three.js 0.178, @remotion/three, @react-three/fiber
│   └── Start_Animated_Studio.bat # Skrip membuka preview visual real-time di browser (http://localhost:3000)
│
├── Start_ClipperAI.bat         # Skrip 1-klik menjalankan server lokal ClipperAI Studio (http://127.0.0.1:8000)
├── Start_3D_Studio.bat         # Skrip 1-klik menjalankan Remotion 3D Animation Studio (http://localhost:3000)
│
├── templates/
│   └── index.html              # [Frontend UI] Antarmuka web modern (Tailwind CSS, Glassmorphism, Dual Mode Switcher, Studio Modal)
│
├── static/
│   ├── gui_preview.png         # Gambar preview UI untuk dokumentasi
│   └── sfx/                    # Efek suara (Whoosh SFX transisi pop)
│
├── outputs/                    # Folder penyimpanan video hasil render (.mp4) dan metadata SEO (.json)
├── uploads/                    # Folder temporary video input, download GDrive/YouTube, dan file audio wav
│
├── requirements.txt            # Daftar pustaka Python yang dibutuhkan
├── install_requirements.bat    # Skrip 1-klik untuk menginstal seluruh dependensi Python
├── Start_ClipperAI.bat         # Skrip 1-klik untuk menjalankan server dan membuka web di browser
├── create_shortcut.ps1         # Skrip PowerShell untuk membuat shortcut desktop
├── client_secrets.json         # (Opsional) Kredensial OAuth2 Google Cloud untuk YouTube API
├── token.json                  # (Dibuat otomatis) Token sesi YouTube yang tersimpan
└── README.md                   # Ringkasan dokumentasi publik untuk GitHub
```

---

## 3. FITUR UTAMA SISTEM

### Mode 1: AI Video Clipper
- **Input**: Link YouTube, Link Google Drive publik, Link Dropbox, atau pilih file video langsung dari PC.
- **Transkripsi Super Cepat**: Menggunakan model `Faster-Whisper` (base/tiny) yang berjalan secara lokal di CPU/GPU.
- **Dynamic Camera Punch-In Zoom**: Zoom otomatis 1.30x bergantian setiap 4 detik untuk mencegah video terasa monoton dan meningkatkan retensi penonton (*watch time*).
- **Subtitle Alex Hormozi**: Subtitle dinamis pop-bounce per kata dengan warna neon terang.
- **Viral Hook Scout**: AI mendeteksi kalimat pembuka paling menarik berdasarkan niche (Kajian, Bisnis, Podcast, Edukasi, Motivasi, Gaming, Universal).

### Mode 2: AI Faceless Studio (Teks Naskah ➔ Shorts Motion)
- **100% Bebas Token & Tanpa Batas**: Menggantikan kebutuhan tool berbayar seperti *Motion Priz* (Rp 99.000 / 10 token).
- **Natural Neural TTS**: Pilihan suara Ardi (Pria Tegas & Berwibawa) dan Gadis (Wanita Ramah & Edukatif).
- **Procedural Radial Motion Canvas**: Background dinamis gelap berkualitas tinggi tanpa memerlukan stok video berat.
- **Multi-Track Audio**: Suara narasi otomatis dimixing pada level broadcast standar (0 dB) bersama transisi *whoosh* lembut.
- **4 Preset Tema**:
  1. 🌌 *Dark Cyber / Tech* (Neon Yellow Highlight)
  2. 🕌 *Islamic Emerald Gold* (Gold Amber Highlight)
  3. 💼 *Modern Business / Cuan* (Neon Green Highlight)
  4. 🔥 *High Energy Motivasi* (Ruby Crimson Highlight)

### Mode 3: Otomatisasi YouTube & LMS
- **Upload untuk Umum (Publik)**:
  - Format judul < 60 karakter, tagar `#Shorts`, deskripsi viral, dan jadwal tayang prime time (WIB).
- **Materi Kursus (Unlisted)**:
  - Otomatis diset sebagai *Unlisted* agar tidak bisa ditonton publik gratis.
  - 1-Klik sinkronisasi langsung menambahkan baris baru ke Google Spreadsheet database kursus [Web dnzykreatif](file:///E:/PROJECTS/apps-script/Web%20dnzykreatif/CourseView.html) pada sheet `Lessons` dengan format HTML `.hadith-box` (`Faedah:`, `Artinya:`) dan navigasi timestamps.

### Mode 4: AI 3D Cartoon Story Animator (Three.js + Remotion)
- **Konsep**: Membuat video animasi kartun 3D storytelling berdurasi 55–70 detik (ala *Kurzgesagt*, *OverSimplified*, atau animasi sejarah/sains viral).
- **100% Render Lokal**: Tidak memerlukan AI video cloud mahal (seperti Runway atau Kling). Seluruh visual 3D dirender secara lokal menggunakan Three.js di dalam Remotion.
- **Karakter Bean-Head 2D di Dunia 3D**: Karakter prosedural di `remotion_studio/src/videos/bridge/toon.ts` dengan ekspresi wajah dinamis, bayangan kontak, dan seragam.
- **Sinematografi Dinamis**: Kamera meluncur (*smootherstep glides*), *creeping push-in* terus-menerus pada setiap hold (0.15%–0.35%/frame), dan preset pencahayaan Siang Terang vs *Golden Hour* Sunset.
- **Cara Preview**: Klik dua kali file `Start_3D_Studio.bat` untuk membuka dashboard visual real-time di `http://localhost:3000`.

---

## 4. PANDUAN MENJALANKAN DI KOMPUTER INI

1. Buka folder `E:\PROJECTS\kajian_clipper`.
2. Klik dua kali file **`Start_ClipperAI.bat`**.
3. Browser akan otomatis membuka alamat **`http://127.0.0.1:8000`**.
4. Selesai! Aplikasi siap digunakan.

---

## 5. PANDUAN PINDAH / SETUP DI LAPTOP LAIN

Jika suatu saat Anda ingin memindahkan proyek ini ke laptop lain atau PC baru:

### Langkah 1: Pastikan Prasyarat Terinstal di Laptop Baru
1. **Python (Versi 3.10, 3.11, atau 3.12)**:
   - Unduh dari [python.org](https://www.python.org/downloads/).
   - ⚠️ **PENTING**: Saat menginstal di Windows, beri centang pada kotak **"Add Python to PATH"**.
2. **FFmpeg (Alat Render Video)**:
   - Unduh build rilis essentials dari [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/).
   - Ekstrak folder (misal ke `C:\ffmpeg`).
   - Masukkan folder `C:\ffmpeg\bin` ke dalam Environment Variable `PATH` Windows.
   - Uji di terminal/PowerShell dengan mengetik: `ffmpeg -version`.

### Langkah 2: Ambil Kode dari GitHub
Buka terminal / PowerShell di laptop baru, lalu jalankan:
```bash
git clone https://github.com/dnzykreatif-dev/ClipperAI-Studio.git
cd ClipperAI-Studio
```

### Langkah 3: Instal Dependensi Otomatis
Cukup klik dua kali file:
```text
install_requirements.bat
```
Atau ketik di terminal:
```bash
pip install -r requirements.txt
```

### Langkah 4: Jalankan Aplikasi
Klik dua kali file:
```text
Start_ClipperAI.bat
```
Aplikasi akan langsung berjalan di `http://127.0.0.1:8000`!

---

## 6. KONFIGURASI GOOGLE CLOUD & YOUTUBE API

Jika Anda ingin fitur tombol upload langsung ke akun YouTube berfungsi:

1. Buka [Google Cloud Console](https://console.cloud.google.com/).
2. Buat project baru (atau pakai yang sudah ada, misalnya `dnzy-kreatif`).
3. Masuk ke menu **APIs & Services** ➔ **Library**, cari **YouTube Data API v3**, lalu klik **Enable**.
4. Masuk ke **OAuth Consent Screen**:
   - Pilih User Type: **External**.
   - Tambahkan email Anda sebagai *Test User*.
   - Tambahkan Scope: `https://www.googleapis.com/auth/youtube.upload` dan `https://www.googleapis.com/auth/youtube`.
5. Masuk ke **Credentials** ➔ **Create Credentials** ➔ **OAuth client ID**:
   - Application type: **Desktop app**.
   - Nama: `ClipperAI Studio`.
   - Unduh file JSON yang dihasilkan, ubah namanya menjadi **`client_secrets.json`**, dan letakkan di dalam folder `E:\PROJECTS\kajian_clipper\`.
6. Saat pertama kali menekan tombol upload di antarmuka web, browser akan meminta login Google sekali saja untuk membuat file `token.json`. Setelah itu, upload akan berjalan otomatis tanpa login ulang.

> [!TIP]
> Jika `client_secrets.json` belum dipasang, Anda tetap bisa menggunakan tombol **"📋 Salin Semua Metadata"** dan tombol **"Buka YouTube Studio Web"** untuk upload manual di browser hanya dalam beberapa detik.

---

## 7. KONFIGURASI DATABASE LMS SPREADSHEET (WEB DNZYKREATIF)

Integrasi Web Kursus DN-ZY Kreatif dikendalikan oleh file [course_sync.py](file:///E:/PROJECTS/kajian_clipper/course_sync.py):
- **Spreadsheet ID**: `1uhes6wkdRqdgqGtFQ57BWfAZt5pvTukuzO3-vBw-TR4`
- **Katalog Kursus Standar**:
  - `apps-script-bundle`: Bundling Komplit Master Google Apps Script
  - `apps-script-basic`: Dasar-Dasar Fundamental Google Apps Script
  - `apps-script-intermediate`: Web App & Spreadsheet Database Relasional
  - `apps-script-pro`: Otomatisasi Bisnis, Bot & Integrasi API Lanjutan
  - `bahasa-arab-dasar`: Belajar Bahasa Arab & Kaidah Nahwu Sharaf
- **Format Baris Sheet `Lessons`**:
  `[LessonId, CourseSlug, ModuleId, Title, "video", Content, VideoURL, "", SortOrder, "publish"]`

Jika Anda ingin mengubah ID Spreadsheet di kemudian hari, cukup buka `course_sync.py` dan ubah variabel `SPREADSHEET_ID`.

---

## 8. TANYA JAWAB & PEMECAHAN MASALAH (TROUBLESHOOTING)

#### Q: Port 8000 sudah terpakai oleh aplikasi lain?
Buka `Start_ClipperAI.bat` dan ubah port, misalnya:
`python -m uvicorn app:app --host 127.0.0.1 --port 8080`

#### Q: Di mana hasil video tersimpan?
Semua video hasil render disimpan di folder **`outputs/`**. Video yang belum diunggah dapat langsung diputar di pemutar media apa saja (VLC, Windows Media Player, Chrome).

#### Q: Apakah bisa dijalankan tanpa koneksi internet?
- **AI Clipper (Memotong video lokal dari PC)**: 100% OFFLINE tanpa kuota internet sama sekali.
- **AI Faceless Video**: Memerlukan sedikit koneksi internet saat mengunduh suara natural `edge-tts` (~1-2 detik), selebihnya render dan subtitle berjalan 100% offline di komputer Anda.
- **Download GDrive / Upload YouTube**: Memerlukan internet untuk proses unduh/unggah.

---

## 9. SUITE CLIPPERAI REMOTE & MOBILE AUTOMATION (REMOTE HP, WIRELESS ADB, GDRIVE, SEAMLESS LOOPER)

Modul `automation_bridge.py` menambahkan 5 kapabilitas otomasi kelas industri ke dalam ClipperAI Studio:

1. **🌐 Cloudflare Quick Tunnel (Akses Remote Smartphone Tanpa Konfigurasi)**:
   - Mengunduh otomatis biner resmi `cloudflared.exe` (~35MB).
   - Menghasilkan tautan publik instan `https://[subdomain].trycloudflare.com`.
   - Mengizinkan pengguna mengontrol ClipperAI Studio dari smartphone di luar jaringan Wi-Fi rumah tanpa perlu buka port router atau langganan IP publik.

2. **🤖 Wireless ADB Android Bridge (Shopee Video & TikTok Auto-Poster)**:
   - Mendukung Android 11+ Wireless Debugging (pairing 6-digit kode & port nirkabel).
   - Mentransfer video hasil kliping langsung ke `/sdcard/DCIM/Camera/` HP dan memicu broadcast MediaScanner.
   - Menyalin *caption* dan *#hashtag* ke clipboard HP dengan metode aman tanpa terpotong bug karakter shell.

3. **☁️ Google Drive Session Uploader (Tanpa Google Cloud API)**:
   - Mengunggah video langsung ke folder Google Drive menggunakan sesi akun Chrome yang aktif.
   - Menggunakan teknik *JavaScript Prototype Hooking* pada `HTMLInputElement.prototype.click` sehingga dialog berkas sistem ditekan dan input berkas dialihkan secara otomatis tanpa batasan kuota OAuth.

4. **🔄 Mathematical Seamless Video Looper**:
   - Algoritma *Alpha Crossfade Filtergraph FFmpeg* untuk mengulang klip video pendek (misal animasi Veo / Remotion 8-10 detik) menjadi durasi panjang (30-180 detik) tanpa terlihat adanya patahan (*jump cut*).
   - Pilihan *mix* atau *replace* audio untuk menyinkronkan video perulangan ke durasi lagu penuh.

5. **🔥 High-Contrast Hook Styler**:
   - Membubuhkan *banner badge* teks kontras tinggi (kuning emas `#fde047` dengan kotak gelap transparan dan lis tebal) di sepertiga atas video (area fokus retensi penonton) yang dioptimalkan untuk rasio vertikal 9:16 Shorts / Reels.

---

*Dokumentasi ini dibuat otomatis dan dapat terus diperbarui seiring perkembangan fitur ClipperAI Studio.*
