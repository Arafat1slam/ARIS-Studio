@echo off
title ARIS Content Automation - MASTER CONTROL
color 0B
cd /d "%~dp0"

:MENU
cls
echo ===================================================================
echo             ARIS CONTENT AUTOMATION SYSTEM - MASTER CONTROL
echo ===================================================================
echo   Channel  : itachi Live
echo   Website  : https://anime.ariswork.site
echo   Slots    : 01:30 PM ^| 06:30 PM ^| 09:30 PM (Daily 3x Viral Uploads)
echo ===================================================================
echo.
echo   [1] Start 24/7 Auto Pilot (Auto download, edit, upload at peak times)
echo   [2] Trigger 1 Video Upload RIGHT NOW (Instant test)
echo   [3] Start n8n Workflow Server (http://localhost:5678)
echo   [4] View Published History Ledger
echo   [5] Exit
echo.
echo ===================================================================
set /p choice="Select an option (1-5) [Default: 1]: "

if "%choice%"=="" set choice=1
if "%choice%"=="1" goto AUTOPILOT
if "%choice%"=="2" goto INSTANT
if "%choice%"=="3" goto N8N
if "%choice%"=="4" goto LEDGER
if "%choice%"=="5" exit

:AUTOPILOT
cls
echo [*] Launching 24/7 Automated Scheduler...
python scripts\scheduler.py
pause
goto MENU

:INSTANT
cls
echo ===================================================================
echo             TRIGGERING INSTANT VIRAL VIDEO PIPELINE
echo ===================================================================
echo [*] Downloading trending 4K viral anime clip...
echo [*] Applying anti-copyright remaster (1080x1920 HDR + Audio)...
echo [*] Generating Gemini AI metadata...
echo [*] Uploading to YouTube Shorts...
echo [*] Auto-deleting local video file...
echo ===================================================================
echo.
python scripts\pipeline_orchestrator.py --auto
echo.
echo [*] Instant pipeline execution completed!
pause
goto MENU

:N8N
cls
echo [*] Opening n8n web interface at http://localhost:5678 ...
start http://localhost:5678
set NODES_EXCLUDE=[]
set N8N_RUNNERS_ENABLED=false
cmd /c n8n start
pause
goto MENU

:LEDGER
cls
echo ===================================================================
echo                    RECENT PUBLISHED VIDEOS
echo ===================================================================
python -c "import json, os; p='config/ledger.json'; data=json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}; print('\n'.join([f'- [{r.get(\"published_at\",\"\")[:10]}] {r.get(\"title\",\"\")} (YT: https://youtube.com/shorts/{r.get(\"youtube_id\",\"\")})' for r in data.get('records', [])]) if data.get('records') else print('No videos in ledger yet.')"
echo.
pause
goto MENU
