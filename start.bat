@echo off
echo ================================================
echo   F1 2026 - Race Intelligence Dashboard
echo ================================================
cd /d %~dp0
echo.
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies.
        pause
        exit
    )
)
echo.
echo Starting Flask server at http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
start "" "http://localhost:5000"
python app.py
pause