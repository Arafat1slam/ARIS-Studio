@echo off
title Install Adobe After Effects MCP Bridge Panel
cd /d "%~dp0"

echo =================================================================
echo       INSTALL ADOBE AFTER EFFECTS MCP BRIDGE PANEL
echo =================================================================
echo.
echo [*] Installing com.aemcpbridge into Adobe CEP extensions directory...
call aftereffects-mcp\install.cmd

echo.
echo =================================================================
echo Next steps in Adobe After Effects:
echo   1. Launch (or restart) Adobe After Effects.
echo   2. Go to: Window ^> Extensions ^> AE MCP Bridge.
echo   3. The panel will open and show: "Listening on 127.0.0.1:7788".
echo   4. ARIS Studio will instantly connect and dispatch live to AE!
echo =================================================================
pause
