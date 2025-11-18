@echo off
echo ============================================================
echo Starting Phoenix-SmartCaseAI Web Service
echo ============================================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    python -m phoenix_smartcaseai.main
) else (
    echo [WARNING] Virtual environment not found. Using system Python.
    python -m phoenix_smartcaseai.main
)

pause

