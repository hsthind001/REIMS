@echo off
echo Starting REIMS Services...
echo.

echo Killing existing processes...
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1

echo.
echo Starting Backend...
cd /d "C:\REIMS"
start "REIMS Backend" cmd /k "C:\REIMS\queue_service\venv\Scripts\python.exe simple_backend.py"

echo Waiting for backend to start...
timeout /t 3 >nul

echo.
echo Starting Frontend...
cd /d "C:\REIMS\frontend"
start "REIMS Frontend" cmd /k "npm run dev"

echo.
echo Services starting...
echo Backend will be on: http://localhost:8001
echo Frontend will be on: http://localhost:5173
echo.
pause