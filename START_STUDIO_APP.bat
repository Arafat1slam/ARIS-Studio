@echo off
title ARIS Studio AI - Desktop Control Center
cd /d "%~dp0"

echo =================================================================
echo        ARIS STUDIO AI - DESKTOP CONTROL CENTER
echo =================================================================
echo [*] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [-] Python is not installed or not in PATH! Please install Python 3.10+.
    pause
    exit /b 1
)

echo [*] Launching ARIS Studio Desktop Web App on http://localhost:8585 ...
echo [*] Your default browser will open automatically.
echo [*] Press Ctrl+C in this window to stop the studio.
echo =================================================================
python studio_app.py
pause
