@echo off
title Connect YouTube Channel 2 (ArisVexx)
color 0A
cd /d "%~dp0"

echo ========================================================
echo     Connect YouTube Channel 2: ArisVexx
echo ========================================================
echo.
echo [*] Launching Google Authorization in browser...
echo [*] Please select 'ArisVexx' channel when prompted.
echo.

python scripts\auth_youtube_channel2.py

echo.
pause
