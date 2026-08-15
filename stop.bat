@echo off
title HariMarg_Stopper

echo ============================================================
echo   Hari Marg - Stopping Development Server
echo ============================================================

powershell -Command "Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
taskkill /FI "WINDOWTITLE eq HariMarg_Server*" /F /T >nul 2>&1

echo [SUCCESS] Stop process completed.
echo ============================================================
