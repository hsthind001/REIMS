@echo off
echo ========================================
echo REIMS Services Shutdown
echo ========================================
echo.

echo Stopping Python processes (Backend & Worker)...
taskkill /f /im python.exe 2>nul
if %errorlevel% equ 0 (
    echo   ✓ Python processes stopped
) else (
    echo   No Python processes found
)

echo.
echo Stopping Node processes (Frontend)...
taskkill /f /im node.exe 2>nul
if %errorlevel% equ 0 (
    echo   ✓ Node processes stopped
) else (
    echo   No Node processes found
)

echo.
echo Stopping Docker containers...
docker stop reims-redis reims-minio 2>nul
if %errorlevel% equ 0 (
    echo   ✓ Redis container stopped
    echo   ✓ MinIO container stopped
) else (
    echo   Docker containers already stopped or not running
)

echo.
echo ========================================
echo REIMS Services Shutdown Complete
echo ========================================
echo.
echo All REIMS services have been stopped:
echo   ✓ Backend API (FastAPI/Uvicorn)
echo   ✓ Frontend (Vite/React)  
echo   ✓ Worker Service
echo   ✓ Redis Container
echo   ✓ MinIO Container
echo.
echo To restart services later:
echo   docker-compose up -d redis minio
echo   python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8001 --reload
echo   cd frontend ^&^& npm run dev
echo   python queue_service/direct_worker.py
echo.
pause