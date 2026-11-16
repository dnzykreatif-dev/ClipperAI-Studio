@echo off
title ClipperAI Studio - 3D Cartoon Remotion Engine
color 0A
echo ========================================================
echo     CLIPPERAI STUDIO - 3D CARTOON ANIMATION ENGINE
echo   (Three.js + Remotion Procedural Storytelling Studio)
echo ========================================================
echo Membuka Remotion Studio di browser (http://localhost:3000)...
cd /d "%~dp0remotion_studio"

start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:3000"
npm run dev

pause
