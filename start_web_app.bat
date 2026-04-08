@echo off
echo ====================================
echo Meeting Recorder - Start Web Version
echo ====================================
echo.

cd /d "%~dp0"

echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install flask flask-cors
)

echo.
echo ====================================
echo Starting server...
echo ====================================
echo.
echo Please follow these steps:
echo.
echo [1] Check your computer's IP address:
echo     Press Win+R, type cmd, then type ipconfig
echo     Find "IPv4 Address" (e.g., 192.168.1.100)
echo.
echo [2] Make sure phone and PC are on the same WiFi network
echo.
echo [3] Open browser on phone and visit:
echo     http://YOUR_PC_IP:5000
echo.
echo [4] Add to home screen for app-like experience!
echo.
echo ====================================
echo Press Ctrl+C to stop the server
echo ====================================
echo.

python web_mobile_app.py

pause
