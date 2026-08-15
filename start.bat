@echo off
title HariMarg_Launcher

echo ============================================================
echo   Hari Marg - Starting Development Server
echo ============================================================

powershell -Command "if (Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue) { exit 1 } else { exit 0 }"
if %errorlevel% neq 0 (
    echo [WARNING] Hari Marg server is ALREADY running on port 5000!
    echo           Please run stop.bat first if you wish to restart it.
    echo ============================================================
    pause
    exit /b
)

if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment venv
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment .venv
    call .venv\Scripts\activate.bat
)

echo [INFO] Starting Hari Marg server on http://127.0.0.1:5000
start "HariMarg_Server" cmd /k "title HariMarg_Server && python app.py"

echo [SUCCESS] Server started in a separate window titled HariMarg_Server
echo [URL]     Access App: http://127.0.0.1:5000
echo [STOP]    Run stop.bat anytime to shut down the server
echo ============================================================
