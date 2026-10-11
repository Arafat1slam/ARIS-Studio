@echo off
title Connect YouTube Channel - ARIS Automation
echo ========================================================
echo     Connect YouTube Channel to ARIS Automation
echo ========================================================
echo.
cd /d "%~dp0"
python scripts\auth_youtube.py
echo.
pause
