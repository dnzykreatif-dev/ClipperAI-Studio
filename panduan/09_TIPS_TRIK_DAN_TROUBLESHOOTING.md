# 🛠️ Panduan 09: Tips, Trik & Troubleshooting (Pemecahan Masalah)

Panduan ini berisi kumpulan tips efisiensi kerja dari kreator profesional serta solusi cepat untuk mengatasi kendala teknis yang mungkin Anda temui saat mengoperasikan ClipperAI Studio.

---

## ⚡ 5 Langkah Alur Kerja Cepat (Dari Video Mentah ➔ Terupload dalam 5 Menit)

Agar proses kerja harian Anda sangat cepat dan efisien, ikuti alur standar berikut:

1. **Langkah 1 (Input)**: Tempelkan link YouTube kajian / podcast favorit Anda ke kolom **Magic Bar** (atau pilih file PC).
2. **Langkah 2 (Preset)**:
   - Pilih Kategori Niche yang sesuai (misal: *Kajian & Dakwah* atau *Bisnis*).
   - Pilih Whisper model: `Base AI (Cepat)`.
   - Pilih Target Klip: `7 Klip (Populer)`.
3. **Langkah 3 (Render)**: Klik **`🚀 Buat Shorts Sekarang`** dan biarkan AI bekerja selama 1-2 menit.
4. **Langkah 4 (Review)**:
   - Periksa klip-klip yang muncul di galeri bawah.
   - Putar pratinjau klip dengan skor viralitas tertinggi (`🔥 96% Virality`).
5. **Langkah 5 (Publikasi)**:
   - Klik tombol **`🚀 Publikasikan`**.
   - Periksa judul dan deskripsi otomatis.
   - Klik **`🚀 Posting Sekaligus (1-Klik)`**.
   - Video Anda langsung live di YouTube Shorts, TikTok, dan Facebook Reels!

---

## 🔧 Pemecahan Masalah Umum (*Troubleshooting*)

### 1. Masalah: "Alamat http://127.0.0.1:8000/ Tidak Bisa Diakses"
- **Penyebab**: Server Uvicorn belum berjalan atau proses tertutup tanpa sengaja.
- **Solusi**:
  1. Buka folder `E:\PROJECTS\kajian_clipper`.
  2. Klik ganda pada file `Start_ClipperAI.bat`.
  3. Pastikan jendela Command Prompt tetap terbuka dan menampilkan log:  
     `Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)`.
  4. Refresh peramban browser Anda.

### 2. Masalah: "Error HTTP 429: Quota Exceeded / Too Many Requests"
- **Penyebab**: API Key Google Gemini Anda mencapai batas kuota per menit.
- **Solusi**:
  1. Klik tombol **`🧠 AI Router`** di navbar atas.
  2. Buka [Google AI Studio](https://aistudio.google.com/) dan buat 1 atau 2 API Key baru (gratis).
  3. Tempelkan kunci-kunci tersebut dipisahkan dengan koma (`,`) pada kolom API Key.
  4. Pastikan opsi **`☑ Auto-Rotasi API Key jika Limit`** aktif.
  5. Klik **`Simpan Konfigurasi`**. Sistem akan otomatis berpindah kunci jika ada limit.

### 3. Masalah: "Proses Transkripsi Terasa Lambat"
- **Penyebab**: Anda memilih model Whisper `Small AI` pada video yang sangat panjang (lebih dari 1 jam).
- **Solusi**:
  - Ubah pengaturan **Model Whisper AI** menjadi: `Base AI (Cepat & Rekomendasi)`. Model ini 4x lebih cepat dan tetap akurat untuk bahasa Indonesia.
  - Ubah **Rentang Pindai Video** menjadi: `15 Menit Awal` atau `30 Menit Awal`.

### 4. Masalah: "Wajah Pembicara Tidak Berada di Tengah pada Video 9:16"
- **Penyebab**: Video asli memiliki pencahayaan sangat gelap atau pembicara sering membelakangi kamera.
- **Solusi**:
  - Sistem menggunakan model AI Face Tracking **YuNet DNN** yang mencari landmark mata, hidung, dan mulut. Pastikan video sumber memiliki pencahayaan wajah yang cukup.
  - Jika video berupa podcast dua orang (host & narasumber), sistem otomatis menggunakan multi-shot switching untuk membagi fokus kamera saat masing-masing orang berbicara.

### 5. Masalah: "Suara Narasi di Faceless Studio Terdengar Terpotong"
- **Penyebab**: Koneksi internet sempat terputus saat mengambil audio Edge-TTS.
- **Solusi**:
  - Periksa koneksi internet laptop/PC Anda.
  - Klik ulang tombol render. Edge-TTS membutuhkan koneksi stabil untuk menyintesis suara natural.

---

## 📖 Glosarium Istilah Penting

- **9:16**: Rasio aspek video vertikal layar penuh standar untuk smartphone (1080x1920 piksel), digunakan oleh YouTube Shorts, TikTok, dan Instagram Reels.
- **LUFS (Loudness Units Full Scale)**: Standar pengukuran desibel kenyaringan suara siaran. ClipperAI Studio menargetkan angka **-14 LUFS (0 dB)** agar suara terdengar lantang dan bersih tanpa sember di telinga penonton yang menggunakan headset.
- **Punch-In Camera**: Teknik editing video di mana kamera secara berkala memperbesar (*zoom-in*) frame sebesar 1.15x atau 1.3x pada kata-kata penting untuk mencegah rasa bosan pemirsa.
- **Argon LUT (Look-Up Table)**: Formula pewarnaan warna sinematik profesional yang membuat rekaman video biasa terlihat seperti kamera bioskop (kaya kontras dan warna kulit natural).
- **WebCodecs**: Standar browser modern yang memungkinkan JavaScript mengakses langsung encoder perangkat keras GPU komputer Anda untuk merender video 60 FPS secara instan.
- **YuNet DNN**: Model Deep Neural Network super ringan dan akurat untuk mendeteksi wajah manusia secara real-time pada resolusi tinggi.

---

> ➡️ **Selesai!**  
> Anda kini telah menguasai seluruh konsep dan fitur di ClipperAI Studio. Buka [README.md](file:///E:/PROJECTS/kajian_clipper/panduan/README.md) untuk melihat daftar isi seluruh modul panduan ini kapan saja.
