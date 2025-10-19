@echo off
REM Cleanup Ports Script for REIMS - Batch Version

echo.
echo ================================================================
echo              REIMS PORT CLEANUP UTILITY
echo ================================================================
echo.

REM Kill processes on specific ports
echo Cleaning up ports...

REM Port 3000 (Frontend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
    echo Killing process %%a on port 3000
    taskkill /F /PID %%a >nul 2>&1
)

REM Port 8001 (Backend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo Killing process %%a on port 8001
    taskkill /F /PID %%a >nul 2>&1
)

REM Alternative: Kill by process name
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1

echo.
echo ================================================================
echo Cleanup complete - All ports freed
echo ================================================================
echo.

REM Wait for ports to be released
timeout /t 2 >nul

















