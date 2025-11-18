@echo off
echo ============================================================
echo Stopping Phoenix-SmartCaseAI Web Service
echo ============================================================
echo.

REM Find and stop Python processes running the web service
for /f "tokens=2" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping process on port 8000...
    taskkill /F /PID %%a >nul 2>&1
)

REM Also try to find uvicorn processes
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *phoenix*" >nul 2>&1

echo Server stopped.
pause

