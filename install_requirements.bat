@echo off
title ClipperAI Studio - Setup & Installation
color 0B
echo ========================================================
echo        CLIPPERAI STUDIO - INSTALLING DEPENDENCIES
echo ========================================================
cd /d "%~dp0"

echo [1/2] Memastikan pip versi terbaru...
python -m pip install --upgrade pip

echo [2/2] Menginstal paket Python (FastAPI, Faster-Whisper, yt-dlp, dll)...
pip install -r requirements.txt

echo.
echo ========================================================
echo Instalasi selesai! Anda sekarang dapat menjalankan:
echo Start_ClipperAI.bat
echo ========================================================
pause
