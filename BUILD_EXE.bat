@echo off
title Build ARIS Studio AI Standalone EXE
cd /d "%~dp0"

echo =================================================================
echo        BUILDING STANDALONE ARIS STUDIO .EXE APPLICATION
echo =================================================================
echo [*] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] PyInstaller not found. Installing PyInstaller...
    pip install pyinstaller
)

echo [*] Compiling studio_app.py into dist\ARIS_Studio.exe ...
pyinstaller --noconfirm --onedir --console ^
    --name "ARIS_Studio" ^
    --add-data "scripts;scripts" ^
    --add-data "config;config" ^
    --add-data "tools;tools" ^
    studio_app.py

if %errorlevel% equ 0 (
    echo =================================================================
    echo [+] SUCCESS! Your executable has been built:
    echo     Location: "%~dp0dist\ARIS_Studio\ARIS_Studio.exe"
    echo =================================================================
) else (
    echo [-] Build failed. Please inspect the log above.
)
pause
