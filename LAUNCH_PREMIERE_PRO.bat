@echo off
title Launch Adobe Premiere Pro 2026
cd /d "%~dp0"

echo =================================================================
echo             LAUNCH ADOBE PREMIERE PRO 2026
echo =================================================================
echo [*] Starting Adobe Premiere Pro 2026...
start "" "C:\Program Files\Adobe\Adobe Premiere Pro 2026\Adobe Premiere Pro.exe"
echo [OK] Premiere Pro launched!
timeout /t 3 >nul
