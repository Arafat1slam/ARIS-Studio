@echo off
title ARIS Content Automation - Run Pipeline
echo ========================================================
echo     ARIS Content Automation - Pipeline Runner
echo ========================================================
echo.
cd /d "%~dp0"

echo Select an option:
echo  [1] Run Pipeline in Review Mode (Generate & Queue for Review)
echo  [2] Run Pipeline in Dry-Run Mode (Simulate without posting)
echo  [3] Run Pipeline in Full Auto-Publish Mode
echo.
set /p choice="Enter choice (1/2/3) [Default: 1]: "

if "%choice%"=="2" (
    echo [*] Running in Dry-Run mode...
    python scripts\pipeline_orchestrator.py --dry-run
) else if "%choice%"=="3" (
    echo [*] Running in Full Auto-Publish mode...
    python scripts\pipeline_orchestrator.py --auto
) else (
    echo [*] Running in Review mode...
    python scripts\pipeline_orchestrator.py
)

echo.
pause
