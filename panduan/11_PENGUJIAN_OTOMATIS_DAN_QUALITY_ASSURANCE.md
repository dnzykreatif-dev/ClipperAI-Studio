# 🧪 Panduan 11: Pengujian Otomatis & Quality Assurance (QA)

ClipperAI Studio dilengkapi dengan sistem pengujian otomatis (*End-to-End Automated Testing Suite*) menggunakan **Playwright**, **Python Sockets**, **REST Client**, dan **Windows Shell COM API**. Sistem ini memastikan aplikasi selalu dalam kondisi 100% stabil, bebas error, dan siap digunakan untuk produksi.

---

## ⚡ Cara Menjalankan Pengujian Otomatis (1-Klik)

Kapan pun Anda melakukan perubahan kode atau ingin memastikan seluruh fitur studio berfungsi normal, jalankan perintah berikut di PowerShell atau Command Prompt:

```powershell
cd E:\PROJECTS\kajian_clipper
python run_comprehensive_tests.py
```

Pengujian akan berjalan secara otomatis di latar belakang (*headless mode*) selama ~8 detik dan menampilkan laporan lengkap di terminal.

---

## 📋 14 Pos Pengujian yang Dicek Otomatis

Suite pengujian mencakup 4 kategori pengujian komprehensif:

### 1. Launcher & Port Detection (TCP & HTTP)
* **`port_8000_listening`**: Memastikan port 8000 lokal aktif dan menerima koneksi soket TCP tanpa hambatan.
* **`http_200_readiness_check`**: Memvalidasi script [open_browser_when_ready.py](file:///E:/PROJECTS/kajian_clipper/open_browser_when_ready.py) merespon status `HTTP 200 OK` sebelum browser dibuka, menghilangkan layar error `ERR_CONNECTION_REFUSED`.

### 2. Desktop Shortcuts Integrity
* **`ClipperAI Studio.lnk`**: Memeriksa file shortcut di Desktop Windows, memastikan path mengarah ke [Start_ClipperAI.bat](file:///E:/PROJECTS/kajian_clipper/Start_ClipperAI.bat) lengkap dengan ikon resmi aplikasi.
* **`AutoClip Studio.lnk`**: Memastikan shortcut versi lama telah disinkronkan ke launcher utama.
* **`ClipperAI Studio Web.url`**: Memastikan shortcut web 1-klik terhubung ke `http://127.0.0.1:8000`.

### 3. Backend REST API Endpoints
* **`GET_root_html`**: Memastikan file template HTML antarmuka studio dimuat utuh (280KB+) tanpa ada tag yang rusak.
* **`GET_ai_config`**: Memastikan konfigurasi AI Router (Google Gemini, model, dan API keys) dapat diakses dengan benar.
* **`POST_ai_ideas_kaab_bin_malik`**: Menguji skenario pembuatan naskah AI untuk topik sejarah Islam (*Kisah taubatnya Ka'ab bin Malik*). Memastikan respons berupa naskah kaya (600+ karakter) berstatus 200 OK.

### 4. Playwright Headless Browser UI & E2E Workflow
* **`page_load_and_title`**: Membuka browser Chromium nyata di background dan memverifikasi judul halaman.
* **`tab_navigation_faceless`**: Menyimulasikan klik tombol navigasi `#tab-mode-faceless` untuk beralih ke studio Faceless.
* **`fill_ai_topic_input`**: Mengetikkan topik ke kolom input `#faceless-ai-topic`.
* **`ai_script_generation_flow`**: Mengklik tombol *"Tulis Naskah AI"*, menunggu transmisi network selesai, dan memverifikasi textarea `#faceless-script-input` terisi naskah narasi.
* **`no_error_alerts`**: Memasang pendeteksi popup browser dialog untuk memastikan **tidak ada pesan alert gagal/error**.
* **`clean_browser_console`**: Memantau konsol browser untuk memastikan **0 error JavaScript**.

---

## 📸 Bukti Visual Otomatis (Screenshots)

Setiap kali pengujian dijalankan, Playwright secara otomatis mengambil foto viewport antarmuka studio dan menyimpannya di folder artefak:
1. `test_ui_initial_load.png`: Kondisi antarmuka saat pertama kali dibuka.
2. `test_ui_generated_script.png`: Kondisi antarmuka setelah naskah AI berhasil dibuat dan masuk ke editor.
3. `test_execution_summary.json`: Ringkasan hasil pengujian dalam format terstruktur.

---

## 🛠️ Menambahkan Pengujian Baru
Jika Anda ingin menambahkan pengujian untuk fitur baru (misal: pengetesan tombol render klip atau auto-publisher YouTube), Anda cukup menambahkan fungsi assertion pada file [run_comprehensive_tests.py](file:///E:/PROJECTS/kajian_clipper/run_comprehensive_tests.py).
