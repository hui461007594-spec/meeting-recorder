@echo off
echo ====================================
echo Meeting Recorder - Start Backend Server
echo ====================================
echo.

cd /d "%~dp0"

echo Starting backend server...
echo Server address: http://0.0.0.0:5000
echo.
echo Please ensure:
echo 1. Phone and PC are on the same WiFi network
echo 2. Firewall allows port 5000
echo.
echo Press Ctrl+C to stop the server
echo ====================================
echo.

python mobile_backend.py

pause
