@echo off
title ARIS Content Automation - Pipeline Runner
echo ========================================================
echo     ARIS Content Automation - Pipeline Runner
echo ========================================================
echo.
cd /d "%~dp0"

echo Select an option:
echo  [1] Auto-Source Viral Clip Online & Process (Anti-Copyright + 1080p)
echo  [2] Process Local Clips in data\approved_clips\ (Review Mode)
echo  [3] Run in Dry-Run Mode (Simulate without posting)
echo  [4] Full Auto-Publish Mode to YouTube
echo.
set /p choice="Enter choice (1/2/3/4) [Default: 1]: "

if "%choice%"=="2" (
    echo [*] Running on local clips in Review mode...
    python scripts\pipeline_orchestrator.py
) else if "%choice%"=="3" (
    echo [*] Running in Dry-Run mode...
    python scripts\pipeline_orchestrator.py --dry-run
) else if "%choice%"=="4" (
    echo [*] Running in Full Auto-Publish mode...
    python scripts\pipeline_orchestrator.py --auto
) else (
    echo [*] Auto-sourcing viral clip online and remastering...
    python scripts\clip_downloader.py
    python scripts\pipeline_orchestrator.py
)

echo.
pause
