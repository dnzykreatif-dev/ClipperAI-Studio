# 🧠 Panduan 05: AI Router & Multi-Key Configuration

**AI Brain & Multi-Provider Router** adalah pusat kecerdasan ClipperAI Studio yang bertanggung jawab melakukan kurasi momen paling viral, memperbaiki transkrip audio, membuat judul SEO, serta menyusun naskah dan kode animasi Canvas.

Modul ini dirancang agar Anda **tidak pernah terhenti oleh batas kuota (*rate limit*)**, berkat dukungan **multi-provider** dan **auto-rotasi API Key cadangan**.

---

## 🎯 Cara Membuka Modal Konfigurasi AI

1. Di bilah navigasi atas (Top Navbar), klik tombol:  
   **`🧠 AI Router: Atur API Key`** (atau tombol status model AI yang sedang aktif).
2. Jendela dialog **AI Brain & Multi-Provider API Router** akan terbuka.

---

## 🌐 6 Provider AI yang Didukung

Anda bebas memilih provider mana yang ingin digunakan:

1. **✨ Google Gemini Resmi (Disarankan & Gratis)**:
   - Menggunakan API Key gratis dari [Google AI Studio](https://aistudio.google.com/).
   - Model yang didukung: `gemini-2.5-flash` (sangat cepat & cerdas) atau `gemini-1.5-pro`.
   - Kuota gratis resmi Google cukup besar untuk ratusan klip per hari.
2. **🚀 SumoPod AI (`ai.sumopod.com`)**:
   - Provider proxy multi-model ramah pengguna untuk pengguna yang berlangganan token SumoPod.
3. **🔀 9Router (`9router.com` / Router Lokal)**:
   - Memungkinkan Anda menghubungkan router model AI lokal atau proxy khusus.
4. **🌐 OpenRouter (`openrouter.ai`)**:
   - Mengakses ratusan model kelas dunia (Claude 3.5 Sonnet, GPT-4o, DeepSeek R1, Llama 3) hanya dengan satu saldo OpenRouter.
5. **⚡ Groq Cloud (`console.groq.com`)**:
   - Eksekusi Llama 3.3 70B dengan kecepatan inferensi super tinggi (~300 token/detik).
6. **🔧 Custom OpenAI-Compatible**:
   - Bisa diarahkan ke Ollama, vLLM, LM Studio, atau server AI buatan sendiri.

---

## 🔄 Fitur Unggulan: Auto-Rotasi API Key (Bebas Error 429)

Salah satu masalah terbesar saat membuat konten massal dengan AI adalah munculnya pesan kesalahan **HTTP 429 (Too Many Requests / Quota Exceeded)**.

ClipperAI Studio menyelesaikan masalah ini dengan sistem **Key Pool**:
1. Anda dapat memasukkan **beberapa API Key sekaligus** pada kolom API Key.
   - Pisahkan setiap kunci dengan **koma (`,`)** atau **baris baru (Enter)**:
     ```
     AIzaSyBxxx_KeyUtama1,
     AIzaSyCyyy_KeyCadangan2,
     AIzaSyDzzz_KeyCadangan3
     ```
2. Centang opsi: **`☑ Auto-Rotasi API Key jika Limit`**.
3. **Cara Kerja**:
   - Sistem akan menggunakan Key #1 terlebih dahulu.
   - Jika Google atau provider memberikan respon bahwa kuota Key #1 habis (HTTP 429), sistem **secara instan berpindah ke Key #2** tanpa memutus proses yang sedang berjalan.
   - Dengan memasukkan 3-5 API key gratis, Anda praktis memiliki akses AI tanpa batas secara cuma-cuma.

---

## 🛠️ Langkah Demi Langkah Mengatur API Key

1. **Aktifkan Centang**: Pastikan opsi `☑ Aktifkan Otak AI` tercentang.
2. **Pilih Provider**: Pilih `Google Gemini Resmi` (atau provider lain sesuai akun Anda).
3. **Periksa Endpoint Base URL**: Otomatis terisi default (misal: `https://generativelanguage.googleapis.com/v1beta`).
4. **Tempelkan API Key**: Masukkan kunci API Anda ke kolom teks API Key.
5. **Pilih Model**:
   - Pilih `gemini-2.5-flash` untuk performa terbaik dan respon paling cepat.
   - Atau klik tombol **`🔄 Tarik Model`** untuk mengambil daftar model terbaru yang tersedia dari akun Anda.
6. **Uji Koneksi**:
   - Klik tombol **`⚡ Tes Koneksi AI`**.
   - Sistem akan mengirimkan pesan uji singkat. Jika berhasil, badge hijau akan bertuliskan **`✓ Koneksi AI Berhasil & Siap Digunakan!`**.
7. **Simpan Pengaturan**:
   - Klik tombol **`💾 Simpan Konfigurasi`**.
   - Pengaturan akan tersimpan secara permanen di file lokal [E:/PROJECTS/kajian_clipper/ai_config.json](file:///E:/PROJECTS/kajian_clipper/ai_config.json).

---

> ➡️ **Langkah Selanjutnya**:  
> Pelajari cara memaksimalkan riset judul viral dan upload otomatis di [06_YOUTUBE_SEO_DAN_AUTO_PUBLISHER.md](file:///E:/PROJECTS/kajian_clipper/panduan/06_YOUTUBE_SEO_DAN_AUTO_PUBLISHER.md)!
