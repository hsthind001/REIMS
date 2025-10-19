@echo off
REM REIMS Frontend Startup Batch Script
REM This ensures the frontend always starts from the correct directory

echo Starting REIMS Frontend...

REM Set the working directory to the frontend folder
set FRONTEND_PATH=C:\REIMS\frontend

REM Check if frontend directory exists
if not exist "%FRONTEND_PATH%" (
    echo Error: Frontend directory not found at %FRONTEND_PATH%
    pause
    exit /b 1
)

REM Check if package.json exists in frontend directory
if not exist "%FRONTEND_PATH%\package.json" (
    echo Error: package.json not found in %FRONTEND_PATH%
    pause
    exit /b 1
)

REM Change to frontend directory
cd /d "%FRONTEND_PATH%"
echo Changed to directory: %CD%

REM Check if node_modules exists, install if needed
if not exist "%FRONTEND_PATH%\node_modules" (
    echo Installing dependencies...
    npm install
    if errorlevel 1 (
        echo Error: npm install failed
        pause
        exit /b 1
    )
)

REM Start the development server
echo Starting Vite development server...
echo Frontend will be available at: http://localhost:5173

REM Start npm dev server
npm run dev

pause