@echo off
title ClipperAI Studio - Universal AI Shorts Generator
color 0B
cd /d "%~dp0"

echo ========================================================
echo     CLIPPERAI STUDIO - UNIVERSAL AI SHORTS GENERATOR
echo   (Podcast, Bisnis, Edukasi, Motivasi, Gaming, Dakwah)
echo ========================================================
echo.

:: 1. Cek apakah server sudah aktif di port 8000
netstat -ano | findstr :8000 | findstr LISTENING >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Server ClipperAI Studio SUDAH AKTIF di Port 8000!
    echo Membuka antarmuka di browser default Anda...
    echo URL: http://127.0.0.1:8000
    start "" "http://127.0.0.1:8000"
    echo.
    echo Jendela ini akan tertutup otomatis dalam 2 detik...
    ping 127.0.0.1 -n 3 >nul
    exit /b 0
)

:: 2. Jika server belum aktif, jalankan background watcher yang menunggu server benar-benar SIAP
echo [1/2] Memulai server ClipperAI Studio...
echo       (Memuat modul AI Whisper, PyTorch, MoviePy, Remotion)
echo       Browser akan otomatis terbuka saat server sudah SIAP 100%% (tanpa layar error).
echo.

:: Jalankan watcher di background tanpa jendela tambahan menggunakan pythonw
where pythonw >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    start "" pythonw "%~dp0open_browser_when_ready.py"
) else (
    start "" /b python "%~dp0open_browser_when_ready.py"
)

:: 3. Jalankan server FastAPI Uvicorn
echo [2/2] Menjalankan server aplikasi di http://127.0.0.1:8000 ...
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [PERINGATAN] Server berhenti atau terjadi error.
    pause
)
