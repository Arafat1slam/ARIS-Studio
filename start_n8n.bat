@echo off
title ARIS Content Automation - n8n Server
echo ========================================================
echo        ARIS Content Automation System - n8n Server
echo ========================================================
echo.
cd /d "%~dp0"

:: Set local environment defaults if .env exists
if exist .env (
    echo [*] Loading configuration from .env ...
)

echo [*] Starting n8n Community Edition on http://localhost:5678 ...
echo [*] Press Ctrl+C anytime to stop n8n.
echo.

set NODES_EXCLUDE=[]
set N8N_RUNNERS_ENABLED=false
cmd /c n8n start

pause
