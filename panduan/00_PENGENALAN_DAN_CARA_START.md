# 🚀 Panduan 00: Pengenalan & Cara Menjalankan ClipperAI Studio

Selamat datang di **ClipperAI Studio (Universal Pro)**!  
Panduan ini dirancang untuk membimbing Anda dari nol agar dapat menguasai seluruh alur kerja pembuatan video pendek viral, video faceless, motion graphics, dan otomatisasi upload media sosial.

---

## 📌 Apa itu ClipperAI Studio?

**ClipperAI Studio** adalah aplikasi all-in-one desktop/web studio berbasis AI yang dirancang untuk:
1. **Memotong & Mengolah Video Panjang Menjadi Shorts/Reels/TikTok Viral**:
   - Mendeteksi wajah pembicara secara otomatis (AI Face Tracking 9:16).
   - Membuang keheningan/jeda canggung tanpa jeda audio (*Silence Cutting*).
   - Menambahkan subtitle dinamis gaya Alex Hormozi (pop-bounce per kata).
   - Dynamic Camera Punch-In (zoom kamera bergantian agar tidak membosankan).
   - Color Grading sinematik LUT Argon-X & Normalisasi Audio ke 0 dB (standar siaran -14 LUFS).
2. **Membuat Video Faceless dari Teks (AI Faceless Motion Studio)**:
   - Ketik ide naskah, AI langsung membacakannya dengan suara natural narator (Ardi/Gadis) dan animasi grafis dinamis 9:16 (100% Gratis).
3. **Studio Visual & Storyboard (Master Agency Prompts)**:
   - 45+ template prompt komersial untuk thumbnail high-CTR, 10 viral hooks, foto produk e-commerce, kuliner UMKM, hingga mainan 3D Pop Mart.
4. **MotionCode Studio (In-Browser WebCodecs 60 FPS)**:
   - Studio animasi visual berbahan kode JavaScript Canvas API yang diekspor langsung di memori browser menjadi MP4/WebM tanpa membebani server.
5. **Otomatisasi Publikasi Multi-Platform**:
   - Sekali klik langsung mempublikasikan video ke YouTube Shorts, TikTok, dan Facebook Reels lengkap dengan judul viral, riset kata kunci, dan deskripsi SEO.

---

## 🖥️ Cara Menjalankan Aplikasi

Ada tiga cara praktis untuk menyalakan ClipperAI Studio di komputer Anda:

### Cara 1: Menggunakan Shortcut Desktop (Paling Direkomendasikan)
Di layar Desktop Windows Anda telah tersedia 2 shortcut resmi:
1. **`ClipperAI Studio.lnk`**:
   - Dilengkapi teknologi *Smart Port Detection* dan *Zero Error Screen*.
   - Jika server belum aktif, script akan memuat modul AI di latar belakang dan **baru membuka browser persis saat server sudah 100% siap** (tidak akan muncul layar error `ERR_CONNECTION_REFUSED`).
   - Jika server sudah menyala sebelumnya, shortcut ini akan langsung membuka browser seketika tanpa bentrok port.
2. **`ClipperAI Studio Web.url`**:
   - Shortcut web instan 1-klik untuk langsung mengakses `http://127.0.0.1:8000` di browser default Anda saat server sedang berjalan.

### Cara 2: Menggunakan File Batch Launcher di Folder Proyek
1. Buka folder proyek di: `E:\PROJECTS\kajian_clipper`.
2. Klik ganda (*double-click*) pada:
   - **`Start_ClipperAI.bat`**: Menyalakan server utama FastAPI dan otomatis membuka browser saat siap.
   - **`Start_3D_Studio.bat`**: Menyalakan server pendukung Remotion 3D.

### Cara 3: Menjalankan via Terminal (PowerShell / Command Prompt)
1. Buka terminal PowerShell.
2. Ketikkan perintah berikut:
   ```powershell
   cd E:\PROJECTS\kajian_clipper
   python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
   ```
3. Akses alamat di peramban browser:
   👉 **http://127.0.0.1:8000/**

---

## 🧭 Anatomi Navigasi Halaman Utama

Saat Anda membuka `http://127.0.0.1:8000/`, berikut adalah elemen-elemen penting di layar:

1. **Bilah Navigasi Atas (Top Navbar)**:
   - **🧠 AI Router**: Tombol untuk mengatur API Key AI (Google Gemini, SumoPod, 9Router, Groq).
   - **⚡ MotionCode Studio**: Tombol pintas untuk membuka studio animasi Canvas 60 FPS di tab baru.
   - **📤 Upload PC**: Tombol cepat untuk mengunggah file video lokal langsung ke YouTube.
   - **🌐 Akun Medsos**: Hub koneksi untuk akun YouTube, TikTok, dan Facebook.
   - **📱 Mobile & Remote**: Menu kontrol ADB untuk HP Android dan Looper video.

2. **Pengalih Mode Studio (Segmented Dock)**:
   - **[🎬 AI Video Clipper]**: Mode default untuk memotong video rekaman panjang.
   - **[✨ AI Faceless Studio]**: Mode pembuatan video vertikal dari naskah teks.
   - **[🎨 Visual & Storyboard]**: Mode perancangan prompt grafis komersial & MotionCode.

3. **Magic Input Bar**:
   - Tempat menempelkan link YouTube/TikTok/Drive/Photos atau memilih file video komputer.

4. **Dek Konfigurasi 4-Kolom**:
   - Blok pengaturan rapi untuk Niche, AI Whisper, Jumlah Klip, Editing Pro, dan Subtitle.

5. **Galeri Video Shorts Hasil AI**:
   - Grid bento di bagian bawah tempat semua video hasil render muncul lengkap dengan pemutar video, skor viralitas, tombol unduh MP4/Thumbnail, dan tombol publikasi 1-klik.

---

> ➡️ **Langkah Selanjutnya**:  
> Lanjutkan membaca [01_AI_VIDEO_CLIPPER.md](file:///E:/PROJECTS/kajian_clipper/panduan/01_AI_VIDEO_CLIPPER.md) untuk mempelajari cara mengubah video panjang menjadi shorts viral ber-motion!
