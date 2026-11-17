# ⚡ Panduan 04: MotionCode Studio (In-Browser WebCodecs 60 FPS)

**MotionCode Studio** adalah studio animasi visual berbasis kode (Code-to-Video) pertama di ClipperAI Studio yang memanfaatkan standar mutakhir **WebCodecs API**. Studio ini memungkinkan Anda membuat video motion graphics 60 FPS beresolusi Full HD hingga 4K langsung di browser tanpa memerlukan server GPU mahal atau rendering FFmpeg yang berat.

---

## 🌟 Mengapa MotionCode Studio Sangat Istimewa?

1. **Rendering 100% Client-Side di Browser Anda**:
   - Proses pengkodean video berjalan di memori peramban (Chrome / Edge) Anda melalui **Web Worker** latar belakang.
   - Server backend Anda tidak terbebani sama sekali!
2. **Deterministik Frame-by-Frame (Nol Frame Patah / Dropped Frames)**:
   - Waktu dievaluasi secara matematis per frame:  
     $$\text{time} = \frac{\text{frameIndex}}{\text{fps}}$$
   - Meskipun laptop Anda sedang sibuk, hasil video tetap mulus sempurna di 60 FPS murni tanpa loncat frame.
3. **Muxing MP4 & WebM Transparan**:
   - Menggunakan `mp4-muxer` untuk menghasilkan file `.mp4` dengan struktur atom `moov` di depan (*fast-start* siap upload ke microstock dan YouTube).
   - Menggunakan `webm-muxer` dengan codec VP9 Alpha untuk menghasilkan video transparan (*transparent overlay VFX*) yang bisa Anda tumpuk di atas video lain.
4. **Injeksi Procedural Film Grain**:
   - Memasukkan noise halus 512x512 untuk mencegah efek belang warna (*8-bit color banding*) yang sering membuat video ditolak di Adobe Stock / Shutterstock.

---

## 🚀 3 Cara Membuka MotionCode Studio

Anda dapat mengakses MotionCode Studio melalui tiga jalur:

1. **Klik Tombol Navbar Atas**:
   - Klik tombol **`⚡ MotionCode Studio (60 FPS)`** di bilah navigasi paling atas. Tab studio akan langsung terbuka.
2. **Akses URL Langsung**:
   - Buka peramban dan ketik: **[http://127.0.0.1:8000/motioncode/](http://127.0.0.1:8000/motioncode/)**
3. **Melalui Visual Studio Preset**:
   - Di tab **Visual & Storyboard**, pilih kartu **`⚡ MotionCode Canvas`**.
   - Klik tombol hijau: **`🚀 Buka di MotionCode Studio`**.

---

## 💻 Anatomi Antarmuka MotionCode Studio

Saat halaman studio terbuka, Anda akan melihat tiga area kerja utama:

```
+------------------------------------+------------------------------------+
| 📝 Monaco Code Editor (Kiri)       | 👁️ Live Canvas Preview (Kanan)    |
| - Tempat menulis kode JavaScript   | - Pratinjau animasi real-time 60fps|
| - Format draw(ctx, time, w, h)     | - Slider timeline & tombol Play/Pause|
+------------------------------------+------------------------------------+
| ⚙️ Panel Kontrol Render (Bawah)                                         |
| - Preset Komersial | Resolusi (FHD/4K/9:16) | Durasi | Ekspor MP4/WebM  |
+-------------------------------------------------------------------------+
```

### 1. Monaco Code Editor (Sisi Kiri)
Tempat menulis logika gambar menggunakan standar Canvas 2D API JavaScript:
```javascript
function draw(ctx, time, width, height) {
  // Latar belakang
  ctx.fillStyle = "#070a12";
  ctx.fillRect(0, 0, width, height);

  // Lingkaran berputar dinamis mengikuti 'time'
  const cx = width / 2;
  const cy = height / 2;
  const radius = 120 + Math.sin(time * 3) * 20;

  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.strokeStyle = "#6366f1";
  ctx.lineWidth = 6;
  ctx.stroke();
}
```
Setiap kali Anda mengubah kode di editor, pratinjau di sebelah kanan akan langsung terbarui secara instan (*live hot-reload*).

### 2. Live Canvas Preview (Sisi Kanan)
- Menampilkan gerakan animasi secara real-time.
- Tombol **Play / Pause** untuk menghentikan animasi di detik tertentu.
- Scrub bar untuk memeriksa detail frame per frame.

### 3. Panel Kontrol & Ekspor (Bawah)
- **Pilihan Resolusi**:
  - `1920x1080 (16:9 Landscape)`: Standar Full HD YouTube dan Microstock.
  - `3840x2160 (4K UHD)`: Resolusi ultra tajam untuk display premium.
  - `1080x1920 (9:16 Vertical)`: Format Shorts, Reels, dan TikTok.
  - `1080x1080 (1:1 Square)`: Format postingan feed Instagram.
- **Durasi Video**: Atur durasi klip (misal: 5 detik, 10 detik, atau 15 detik loop).
- **Target FPS**: Pilih `30 FPS` atau `60 FPS` (Super Halus).
- **Tombol Ekspor**:
  - **`Export MP4`**: Menghasilkan file video H.264 standar universal.
  - **`Export WebM (Alpha)`**: Menghasilkan video transparan tanpa latar belakang.

---

## 📚 5 Preset Komersial Bawaan Siap Pakai

Tersedia 5 preset siap pakai yang dapat langsung dipilih dari menu preset:

1. **Adobe Stock FHD Standard Loop**:
   - Gelombang partikel teknologi modern dengan gradasi warna ungu-cyan yang sangat digemari pembeli aset microstock.
2. **4K UHD Luxury Silk Flow**:
   - Kain sutra emas hitam 3D bergelombang halus dengan pencahayaan mewah, cocok untuk latar belakang presentasi korporat.
3. **Sci-Fi HUD Holographic VFX (Alpha Transparent)**:
   - Grafis radar dan interface futuristik dengan transparansi penuh untuk ditumpuk di atas rekaman video game atau teknologi.
4. **Vertical 9:16 Neon Portal**:
   - Efek terowongan neon vertikal berenergi tinggi untuk pembuka video Shorts/Reels.
5. **Square 1:1 Social Feed Visualizer**:
   - Gelombang equalizer audio dinamis untuk promosi musik di feed Instagram.

---

## 🤖 Menghasilkan Animasi Baru Menggunakan AI

Anda tidak perlu menulis kode manual dari nol! Di tab **Visual & Storyboard**:
1. Pilih preset **`⚡ MotionCode Canvas`**.
2. Pilih satu dari **15 Kategori Industri** (Teknologi, Finansial, Sains, Alam, Medis, dll.) dan **13 Gaya Visual** (Minimalist, Cyberpunk, Luxury, Abstract 3D, dll.).
3. Klik **`🤖 Eksekusi Otomatis via AI`**.
4. AI Brain akan langsung membuatkan kode JavaScript fungsi `draw(ctx, time, w, h)` yang siap Anda salin ke MotionCode Studio untuk langsung dirender!

---

> ➡️ **Langkah Selanjutnya**:  
> Pelajari cara mengonfigurasi API Key AI dan auto-rotasi di [05_AI_ROUTER_DAN_MULTI_KEY.md](file:///E:/PROJECTS/kajian_clipper/panduan/05_AI_ROUTER_DAN_MULTI_KEY.md)!
