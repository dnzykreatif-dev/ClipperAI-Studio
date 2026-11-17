# 🌐 Panduan 07: Multi-Platform Posting Studio & Web Kursus

Modul **Multi-Platform Posting Studio** memungkinkan Anda mempublikasikan satu video yang sama ke berbagai jejaring media sosial terpopuler secara serentak (YouTube Shorts, TikTok, dan Facebook Reels), serta menyinkronkannya langsung ke sistem e-learning kelas online Anda.

---

## 🚀 Mengapa Perlu Multi-Platform Publishing?

Di era algoritma saat ini, membatasi konten hanya di satu platform adalah kerugian besar. Sebuah video yang mendapatkan 1.000 penonton di YouTube bisa saja meledak hingga 1.000.000 penonton di TikTok atau Facebook Reels.

Dengan Multi-Platform Studio, Anda cukup menekan **satu tombol**, dan konten Anda langsung terdistribusi ke seluruh saluran audiens Anda.

---

## 🎯 Cara Membuka Multi-Platform Studio

1. Pada kartu video hasil render di galeri bawah, klik tombol:  
   **`🚀 Publikasikan (YT · FB · TikTok)`**.
2. Atau dari bilah navigasi atas, klik tombol **`🌐 Akun Medsos`**.

---

## 📱 Memilih Platform Tujuan Posting

Di bagian atas modal posting, Anda akan melihat kartu pemilih 3 platform:

```
+--------------------+--------------------+--------------------+
| ▶️ YouTube Shorts  | 🎵 TikTok          | 🔵 Facebook Reels  |
| [✓ Aktif]          | [✓ Aktif]          | [✓ Aktif]          |
+--------------------+--------------------+--------------------+
```

- Cukup klik pada kartu platform untuk mengaktifkan atau menonaktifkan tujuan posting.
- Badge status akan menunjukkan berapa platform yang dipilih (misal: `3 Platform Dipilih`).

### 1. YouTube Shorts
- Diunggah langsung via API resmi YouTube Data API v3.
- Mengisi judul, deskripsi panjang, hashtag, dan custom thumbnail.

### 2. TikTok
- Terhubung via TikTok for Developers API atau Creator Center Webhook.
- Otomatis memformat judul pendek dan hashtag FYP TikTok.

### 3. Facebook Reels & Pages
- Menggunakan Facebook Graph API v19.0 untuk upload video vertikal ke Halaman Facebook (*Facebook Page*) Anda.
- Memerlukan Page Access Token dan Page ID dari Facebook Developer Console.

---

## 👥 Pengaturan Target Audiens: Umum vs Materi Kursus

Tersedia dua mode segmentasi penonton yang sangat praktis:

### Opsi 1: Untuk Umum (Viral Publik FYP)
- Video diatur dengan visibilitas **Publik**.
- Judul dan hashtag dioptimalkan untuk menarik penonton baru dan menjangkau algoritma rekomendasi YouTube/TikTok/Reels.

### Opsi 2: Materi Kursus / Kelas Berbayar (*Unlisted*)
- Video diatur secara otomatis ke status **Tidak Publik (*Unlisted*)**.
- Video tidak akan muncul di beranda umum kanal Anda, hanya pemegang link atau siswa kelas Anda yang dapat menontonnya.
- Otomatis membuka tab integrasi kursus.

---

## 🎓 Integrasi Web Kursus DN-ZY Kreatif

Jika Anda mengelola platform kursus online atau website e-learning:
1. Buka tab **Web Kursus DN-ZY** di dalam modal studio.
2. Pilih nama kursus (misal: *Masterclass Video Editing AI*).
3. Pilih modul/bab pelajaran yang dituju.
4. Tautan video YouTube Unlisted dan cap waktu rangkuman materi (*timestamps*) akan otomatis terisi.
5. Klik **`🚀 Simpan & Sinkronkan ke Web Kursus`**.
6. Siswa di website e-learning Anda bisa langsung mempelajari materi video baru tersebut tanpa Anda perlu menyalin link manual!

---

## ☁️ Tab Impor Cloud (Google Drive & Direct Link)

Jika video sumber Anda tersimpan di cloud dan Anda tidak ingin mengunduhnya manual ke harddisk:
1. Buka tab **Impor Google Drive / URL**.
2. Masukkan tautan berbagi (*share link*) Google Drive atau tautan file direct `.mp4`.
3. Klik tombol **`📥 Tarik Video dari Cloud`**.
4. Server lokal akan mengunduh video tersebut di latar belakang dan langsung memasukkannya ke antrean pembuatan Shorts.

---

## 🌐 Tombol Pintas Web Studio Kreator

Di bagian bawah jendela modal, terdapat dropdown **`🌐 Buka Web Studio ▾`**:
- **YouTube Studio Web**: Membuka `studio.youtube.com` di browser Anda.
- **TikTok Creator Center**: Membuka `tiktok.com/creator-center`.
- **Facebook Reels Studio**: Membuka `business.facebook.com/creatorstudio`.

Fitur ini berguna jika Anda ingin memeriksa performa analitik penonton (*views, watch time, retention graph*) secara mendalam di masing-masing platform.

---

> ➡️ **Langkah Selanjutnya**:  
> Pelajari cara menghubungkan smartphone Android dan menggunakan Looper video di [08_MOBILE_REMOTE_SUITE_DAN_ADB.md](file:///E:/PROJECTS/kajian_clipper/panduan/08_MOBILE_REMOTE_SUITE_DAN_ADB.md)!
