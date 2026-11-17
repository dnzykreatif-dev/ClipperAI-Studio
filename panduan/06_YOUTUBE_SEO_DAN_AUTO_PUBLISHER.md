# 📈 Panduan 06: YouTube SEO & Auto-Publisher

Modul **YouTube SEO & Auto-Publisher** mengotomatiskan seluruh pekerjaan riset kata kunci, penulisan metadata viral, hingga pengunggahan video langsung ke kanal YouTube Anda tanpa perlu membuka YouTube Studio manual.

---

## 🎯 Mengapa Metadata SEO Sangat Penting?

Sebagus apa pun video Shorts yang Anda hasilkan, video tersebut tidak akan mendapatkan jutaan penonton jika:
1. Judulnya membosankan dan tidak memicu rasa penasaran (*low click-through rate*).
2. Deskripsinya tidak mengandung kata kunci yang sedang dicari pemirsa.
3. Tag video tidak relevan dengan tren algoritma YouTube saat ini.

ClipperAI Studio memecahkan masalah ini dengan menganalisis intisari ucapan di video dan menyusun metadata menggunakan formula psikologi penonton YouTube modern.

---

## 🧠 Fitur Otomatisasi SEO yang Dihasilkan

Setiap klip video yang Anda buat secara otomatis memiliki:

1. **Judul Viral Otomatis (*Viral Hook Title*)**:
   - Memanfaatkan formula *Curiosity Gap* dan *Negativity Bias* (contoh: `TAHUKAH KAMU? JANGAN TARUH POIN INI DI AKHIR! #Shorts`).
   - Panjang judul dijaga di bawah 70 karakter agar tidak terpotong di layar smartphone.
2. **Deskripsi SEO Terstruktur**:
   - Paragraf ringkasan padat berisi kata kunci utama.
   - Kutipan penting naskah pembicara.
   - Daftar cap waktu (*timestamps*) otomatis jika video berdurasi lebih dari 60 detik.
   - Kumpulan hashtag relevan (seperti `#Kajian #Podcast #Shorts #Trending`).
3. **Pill Tag Rekomendasi (*Live Suggested Tags*)**:
   - Kumpulan tag kata kunci berbobot pencarian tinggi yang dapat Anda klik untuk menambah atau menghapus tag dalam sekejap.
4. **Rekomendasi Jam Tayang (*Optimal Schedule*)**:
   - Saran waktu upload terbaik berdasarkan niche konten Anda (misal: Pukul 11.30 WIB siang atau 18.30 WIB malam).

---

## 🔗 Cara Menghubungkan Akun YouTube (OAuth2)

Untuk mengaktifkan pengunggahan 1-klik, hubungkan akun YouTube Anda sekali saja:

1. Klik tombol **`🌐 Akun Medsos`** di navbar atas (atau klik tombol **`🚀 Publikasikan`** pada salah satu kartu video, lalu pilih tab **Hubungkan Akun**).
2. Terdapat dua pilihan metode:
   - **Metode A: Upload File JSON Kredensial (Paling Mudah)**:
     1. Buat project gratis di [Google Cloud Console](https://console.cloud.google.com/) dan aktifkan **YouTube Data API v3**.
     2. Unduh file kredensial OAuth2 dan simpan sebagai `client_secret.json`.
     3. Klik tombol **`📁 Pilih File client_secret.json`**.
   - **Metode B: Tempel Client ID & Secret**:
     1. Masukkan Client ID dan Client Secret ke kolom yang tersedia.
     2. Klik **`Simpan Kredensial`**.
3. Klik tombol **`🔑 Login dengan Akun YouTube`**.
4. Browser akan membuka jendela otentikasi Google. Pilih akun kanal YouTube Anda dan berikan izin akses upload video.
5. Setelah berhasil, status akan bertuliskan **`✓ Akun YouTube Terhubung: [Nama Kanal Anda]`**.

---

## 📤 Cara Upload Video ke YouTube (Sekali Klik)

### 1. Upload Klip Hasil AI:
1. Pada kartu video mana saja di galeri hasil, klik tombol:  
   **`🚀 Publikasikan (YT · FB · TikTok)`**.
2. Jendela **Multi-Platform Studio** akan terbuka dengan judul dan deskripsi yang sudah otomatis terisi dan siap diedit jika diinginkan.
3. Pastikan centang platform **`▶️ YouTube Shorts`** aktif.
4. Tentukan status visibilitas:
   - **`Publik (*Public*)`**: Langsung tayang untuk semua orang.
   - **`Tidak Publik (*Unlisted*)`**: Hanya bisa dilihat lewat link (cocok untuk materi kursus).
   - **`Pribadi (*Private*)`**: Hanya Anda yang dapat melihat.
5. Klik tombol merah di sudut kanan bawah: **`🚀 Posting Sekaligus (1-Klik)`**.
6. Video otomatis terunggah lengkap dengan judul, deskripsi, tag, dan thumbnail custom!

### 2. Upload File Video Langsung dari PC ke YouTube:
Jika Anda memiliki video yang diedit di aplikasi lain (misal: Premiere Pro, CapCut, DaVinci):
1. Klik tombol **`📤 Upload PC`** di navbar atas.
2. Pilih file video dari harddisk komputer Anda.
3. Studio posting akan terbuka dan Anda bisa langsung memasukkan metadata lalu menekan upload.

---

> ➡️ **Langkah Selanjutnya**:  
> Pelajari cara mempublikasikan video secara serentak ke TikTok dan Facebook Reels di [07_MULTI_PLATFORM_POSTING_STUDIO.md](file:///E:/PROJECTS/kajian_clipper/panduan/07_MULTI_PLATFORM_POSTING_STUDIO.md)!
