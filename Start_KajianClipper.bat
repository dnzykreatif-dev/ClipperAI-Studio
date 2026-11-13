@echo off
title ClipperAI Studio - Universal AI Shorts Generator
color 0B
echo ========================================================
echo     CLIPPERAI STUDIO - UNIVERSAL AI SHORTS GENERATOR
echo   (Podcast, Bisnis, Edukasi, Motivasi, Gaming, Dakwah)
echo ========================================================
echo Membuka server aplikasi lokal di http://127.0.0.1:8000 ...
cd /d "E:\PROJECTS\kajian_clipper"

start "" http://127.0.0.1:8000
python -m uvicorn app:app --host 127.0.0.1 --port 8000

pause
