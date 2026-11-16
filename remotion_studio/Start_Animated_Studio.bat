@echo off
title Animated Shorts Studio (Remotion + Three.js)
color 0A
echo ========================================================
echo     ANIMATED SHORTS STUDIO (REMOTION + THREE.JS)
echo   3D Procedural Cartoon World + Storytelling Studio
echo ========================================================
echo Membuka Remotion Studio di browser (http://localhost:3000)...
cd /d "%~dp0"

start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:3000"
npm run dev

pause
