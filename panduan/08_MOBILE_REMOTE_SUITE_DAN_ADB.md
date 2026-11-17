# 📱 Panduan 08: Mobile & Remote Hub (ADB, Looper & Scrcpy)

Modul **Mobile & Remote Hub** dirancang untuk menghubungkan PC kerja Anda langsung ke smartphone Android fisik melalui kabel USB atau jaringan WiFi lokal menggunakan teknologi **Android Debug Bridge (ADB)**.

Modul ini juga dilengkapi alat canggih: **Seamless Video Looper** (memperpanjang durasi klip loop secara mulus) dan **High-Contrast Hook Text Overlay**.

---

## 🎯 Cara Membuka Mobile & Remote Hub

1. Pada bilah navigasi atas (Top Navbar), klik tombol:  
   **`📱 Mobile & Remote`** (dilengkapi indikator titik hijau).
2. Atau dari jendela modal posting, buka tab:  
   **`📱 Mobile & Remote Suite (ADB · Looper)`**.

---

## 🔌 1. Menghubungkan Smartphone Android via ADB

Fitur ADB memungkinkan PC Anda mengontrol HP Android untuk melakukan pratinjau konten, mengunggah video langsung dari galeri HP, atau menampilkan layar HP di monitor PC (*mirroring*).

### Persiapan di HP Android:
1. Buka **Pengaturan** di HP Anda.
2. Masuk ke **Tentang Ponsel** (*About Phone*) dan ketuk **Nomor Bentukan** (*Build Number*) sebanyak 7 kali berturut-turut hingga muncul pesan: *"Anda sekarang adalah pengembang!"*.
3. Masuk ke menu **Opsi Pengembang** (*Developer Options*).
4. Aktifkan:
   - **Debugging USB (*USB Debugging*)**
   - **Instal via USB** (opsional)
5. Hubungkan HP ke PC menggunakan kabel data USB yang bagus.
6. Pada layar HP, akan muncul kotak dialog: *"Izinkan debugging USB?"*, centang *"Selalu izinkan dari komputer ini"* dan tekan **OK**.

### Memeriksa Koneksi di ClipperAI Studio:
1. Pada kartu **Koneksi Perangkat Android (ADB)**:
2. Klik tombol **`🔍 Pindai HP Terhubung`**.
3. Jika berhasil, sistem akan mendeteksi seri HP Anda (contoh: `device: SM-G998B (Samsung Galaxy S21 Ultra)` atau `device: Redmi Note 12`).

### Menampilkan Layar HP di Komputer (*Scrcpy Mirroring*):
1. Klik tombol **`📱 Buka Layar HP (Scrcpy)`**.
2. Jendela cermin (*screen mirror*) ponsel akan terbuka di PC Anda dengan latensi sangat rendah.
3. Anda dapat mengontrol HP menggunakan mouse dan keyboard komputer tanpa harus menyentuh ponsel fisik.

---

## 🔄 2. Seamless Video Looper (Membuat Video Loop Mulus)

Seringkali Anda memiliki klip animasi pendek berdurasi 5 atau 9 detik (misalnya animasi partikel dari MotionCode Studio) dan ingin memperpanjangnya menjadi video 60 detik atau 120 detik tanpa patahan yang kasar.

Fitur **Seamless Video Looper** mengatasi hal ini dengan teknik *cross-fade audio/video blend*:

1. Buka bagian **A. Seamless Video Looper**.
2. Masukkan target durasi dalam detik (misal: `60` detik).
3. Klik tombol **`🔄 Loop Mulus`**.
4. Sistem akan menduplikasi video tersebut secara cerdas, menyambung frame akhir ke frame awal dengan transisi halus, dan menghasilkan video 60 detik utuh yang siap upload ke Shorts/Reels.

---

## 🔥 3. High-Contrast Hook Text Overlay (Stiker Teks Menusuk)

Penonton Shorts memutuskan apakah akan lanjut menonton atau *swipe* hanya dalam tempo **1,5 detik pertama**. Teks hook berwarna kontras tinggi terbukti meningkatkan retensi awal penonton secara dramatis.

1. Buka bagian **B. Teks Hook Kontras Tinggi**.
2. Masukkan kalimat hook pemicu rasa penasaran, contohnya:
   - `JANGAN SKIP JIKA MAU KAYA!`
   - `TAHUKAH KAMU FAKTA INI?`
   - `3 RAHASIA YANG DISEMBUNYIKAN`
3. Klik tombol **`🔥 Tempel`**.
4. Sistem akan menempelkan banner teks berlatar belakang hitam/kuning dengan outline tebal di bagian sepertiga atas video, memastikan teks tetap terbaca jelas meskipun pemirsa menonton di luar ruangan dengan layar redup.

---

> ➡️ **Langkah Selanjutnya**:  
> Baca tips praktis alur kerja profesional dan penanganan kendala di [09_TIPS_TRIK_DAN_TROUBLESHOOTING.md](file:///E:/PROJECTS/kajian_clipper/panduan/09_TIPS_TRIK_DAN_TROUBLESHOOTING.md)!
