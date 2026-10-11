@echo off
title ARIS Content Automation - Review Approvals
echo ========================================================
echo   ARIS Content Automation - Review & Approvals Gate
echo ========================================================
echo.
cd /d "%~dp0"
python scripts\review_manager.py
echo.
pause
