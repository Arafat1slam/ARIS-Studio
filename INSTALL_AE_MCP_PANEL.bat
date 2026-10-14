@echo off
title Install Adobe MCP Bridge Panel (Premiere Pro & After Effects)
cd /d "%~dp0"

echo =================================================================
echo       INSTALL ADOBE MCP BRIDGE PANEL (PREMIERE PRO / AFTER EFFECTS)
echo =================================================================
echo.
echo [*] Enabling PlayerDebugMode in Windows Registry for Adobe CSXS...
for /L %%v in (9,1,18) do (
    reg add "HKCU\Software\Adobe\CSXS.%%v" /v PlayerDebugMode /t REG_SZ /d 1 /f >nul 2>&1
)

echo [*] Adobe CEP extension com.aemcpbridge is already installed in:
echo     %APPDATA%\Adobe\CEP\extensions\com.aemcpbridge

echo.
echo =================================================================
echo  Next steps in Adobe Premiere Pro or After Effects:
echo   1. Launch Premiere Pro 2026 (or After Effects).
echo   2. Go to top menu: Window ^> Extensions ^> AE MCP Bridge.
echo   3. The panel will open and show: "Listening on 127.0.0.1:7788".
echo   4. ARIS Studio will connect and communicate directly with Adobe!
echo =================================================================
pause
