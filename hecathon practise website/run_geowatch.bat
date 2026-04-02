@echo off
echo ==========================================
echo    GeoWatch AI - Automated Backend Setup
echo ==========================================
echo.

cd /d "%~dp0backend"

echo [1/3] Checking for missing dependencies...
pip install -r requirements.txt

echo.
echo [2/3] Verifying Python package structure...
echo # Backend initialization > __init__.py

echo.
echo [3/3] Starting GeoWatch AI Server on Port 8000...
echo.
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] The server failed to start.
    echo Running diagnostic script...
    python debug_server.py
    pause
)

pause
