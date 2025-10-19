@echo off
REM REIMS Startup Script - Batch Version
REM Ensures backend starts before frontend

echo.
echo ================================================================
echo                    REIMS STARTUP SCRIPT
echo ================================================================
echo.

REM Step 1: Stop existing processes and free ports
echo Step 1: Cleaning up existing processes and ports...

REM Kill processes by name
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1

REM Free port 3000 (Frontend) if occupied
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING" 2^>nul') do (
    echo   Freeing port 3000...
    taskkill /F /PID %%a >nul 2>&1
)

REM Free port 8001 (Backend) if occupied
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING" 2^>nul') do (
    echo   Freeing port 8001...
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 /nobreak >nul
echo   [OK] Cleanup complete
echo.

REM Step 2: Start Backend
echo Step 2: Starting Backend...
echo   Starting backend on port 8001...
start /B python run_backend.py > backend_startup.log 2> backend_error.log
echo   [OK] Backend process started
echo.

REM Step 3: Wait for Backend
echo Step 3: Waiting for backend to be ready...
set /a attempts=0
set /a max_attempts=30

:wait_backend
set /a attempts+=1
if %attempts% GTR %max_attempts% goto backend_timeout

timeout /t 1 /nobreak >nul
curl -s http://localhost:8001/health >nul 2>&1
if errorlevel 1 (
    echo   Attempt %attempts%/%max_attempts% - Backend not ready yet...
    goto wait_backend
)

echo   [OK] Backend is ready!
echo.
goto backend_ready

:backend_timeout
echo   [ERROR] Backend failed to start within %max_attempts% seconds!
echo   Check backend_error.log for details
exit /b 1

:backend_ready

REM Step 4: Start Frontend
echo Step 4: Starting Frontend...
echo   Starting frontend on port 3000...
cd frontend
start cmd /k "npm run dev"
cd ..
echo   [OK] Frontend process started
echo.

REM Step 5: Wait for Frontend
echo Step 5: Waiting for frontend to be ready...
timeout /t 5 /nobreak >nul
echo   [OK] Frontend should be starting
echo.

REM Summary
echo ================================================================
echo                  REIMS STARTED SUCCESSFULLY
echo ================================================================
echo.
echo Services:
echo   Backend:  http://localhost:8001
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8001/docs
echo.
echo Logs:
echo   Backend output: backend_startup.log
echo   Backend errors: backend_error.log
echo.
echo To stop services:
echo   stop_reims.bat
echo.
echo ================================================================
echo.

REM Open browser
timeout /t 2 /nobreak >nul
start http://localhost:3000

pause
