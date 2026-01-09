@echo off
chcp 65001 >nul
echo ========================================
echo Starting Ferret Flask Server
echo ========================================
echo.
cd /d %~dp0
echo Current directory: %CD%
echo.
echo Checking Python...
python --version
echo.
echo Starting server on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py
pause
