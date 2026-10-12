@echo off
title ARIS Content Automation - MASTER CONTROL
color 0B
cd /d "%~dp0"

:MENU
cls
echo ===================================================================
echo             ARIS CONTENT AUTOMATION SYSTEM - MASTER CONTROL
echo ===================================================================
echo   Channel 1 : itachi Live  [Anime -^> anime.ariswork.site]
echo               Slots: 01:30 PM ^| 06:30 PM ^| 09:30 PM (BST)
echo.
echo   Channel 2 : ArisVexx     [Dark Psychology -^> USA High-CPM Focus]
echo               Slots: 10:00 PM ^| 01:30 AM ^| 06:30 AM (BST = US PEAK)
echo ===================================================================
echo.
echo   [1] Start 24/7 Dual-Channel Auto Pilot (Anime + Dark Psychology)
echo   [2] Trigger Instant Upload to itachi Live (Anime Short)
echo   [3] Trigger Instant Upload to ArisVexx (Dark Psychology Short)
echo   [4] Start n8n Workflow Web Server (http://localhost:5678)
echo   [5] View Published History Ledger
echo   [6] Exit
echo.
echo ===================================================================
set /p choice="Select an option (1-6) [Default: 1]: "

if "%choice%"=="" set choice=1
if "%choice%"=="1" goto AUTOPILOT
if "%choice%"=="2" goto INSTANT_CH1
if "%choice%"=="3" goto INSTANT_CH2
if "%choice%"=="4" goto N8N
if "%choice%"=="5" goto LEDGER
if "%choice%"=="6" exit

:AUTOPILOT
cls
echo [*] Launching 24/7 Dual-Channel Auto Pilot...
python scripts\scheduler.py
pause
goto MENU

:INSTANT_CH1
cls
echo ===================================================================
echo         TRIGGERING INSTANT UPLOAD: itachi Live (Anime Short)
echo ===================================================================
python scripts\pipeline_orchestrator.py --auto
echo.
pause
goto MENU

:INSTANT_CH2
cls
echo ===================================================================
echo         TRIGGERING INSTANT UPLOAD: ArisVexx (Dark Psychology)
echo ===================================================================
python scripts\dark_psychology_generator.py
echo.
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
python -c "import json, os; p='config/ledger.json'; data=json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}; print('\n'.join([f'- [{r.get(\"channel\", \"itachi Live\")}] [{r.get(\"published_at\",\"\")[:10]}] {r.get(\"title\",\"\")} (https://youtube.com/shorts/{r.get(\"youtube_id\",\"\")})' for r in data.get('records', [])]) if data.get('records') else print('No videos in ledger yet.')"
echo.
pause
goto MENU
