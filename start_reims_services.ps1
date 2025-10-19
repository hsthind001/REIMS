# REIMS Service Starter - PowerShell Script
# This script starts both backend and frontend services reliably

Write-Host "=== REIMS Service Starter ===" -ForegroundColor Green
Write-Host ""

# Kill any existing processes
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*node*" -or ($_.ProcessName -like "*python*" -and $_.Path -like "*REIMS*")} | Stop-Process -Force -ErrorAction SilentlyContinue

# Wait a moment
Start-Sleep -Seconds 2

# Start Backend
Write-Host "Starting Backend on port 8001..." -ForegroundColor Cyan
Set-Location "C:\REIMS"
Start-Process -FilePath "C:\REIMS\queue_service\venv\Scripts\python.exe" -ArgumentList "simple_backend.py" -WindowStyle Minimized

# Wait for backend to start
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting Frontend on port 5173..." -ForegroundColor Cyan
Set-Location "C:\REIMS\frontend"
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Normal

# Wait for frontend to start
Start-Sleep -Seconds 5

# Check services
Write-Host ""
Write-Host "Checking services..." -ForegroundColor Green
$backend = netstat -ano | findstr ":8001"
$frontend = netstat -ano | findstr ":5173"

if ($backend) {
    Write-Host "✅ Backend running on port 8001" -ForegroundColor Green
} else {
    Write-Host "❌ Backend not running" -ForegroundColor Red
}

if ($frontend) {
    Write-Host "✅ Frontend running on port 5173" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend not running" -ForegroundColor Red
}

Write-Host ""
Write-Host "Frontend URL: http://localhost:5173" -ForegroundColor Magenta
Write-Host "Backend API: http://localhost:8001" -ForegroundColor Magenta
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")