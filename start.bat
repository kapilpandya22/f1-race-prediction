@echo off
echo ================================================
echo   F1 2026 - Race Intelligence Dashboard
echo ================================================
cd /d %~dp0
echo.
echo Activating virtual environment...
call .venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Could not activate venv
    echo Try running: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    pause
    exit
)
echo.
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing Flask...
    pip install flask flask-cors
)
echo.
echo Starting Flask server at http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
start "" "http://localhost:5000"
python app.py
pause