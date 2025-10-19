#!/usr/bin/env pwsh
# REIMS System Restart Script
# Run this script to start all REIMS services

Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  REIMS - Real Estate Information Management System" -ForegroundColor Cyan
Write-Host "  Starting All Services..." -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill any existing Python/Node processes
Write-Host "[1/5] Stopping existing services..." -ForegroundColor Yellow
taskkill /F /IM python.exe /T 2>$null | Out-Null
taskkill /F /IM python3.13.exe /T 2>$null | Out-Null
taskkill /F /IM node.exe /T 2>$null | Out-Null
Start-Sleep -Seconds 2
Write-Host "  Services stopped" -ForegroundColor Green
Write-Host ""

# Step 2: Clean Python cache
Write-Host "[2/5] Cleaning Python cache..." -ForegroundColor Yellow
Remove-Item -Recurse -Force backend\**\__pycache__ -ErrorAction SilentlyContinue
Write-Host "  Cache cleaned" -ForegroundColor Green
Write-Host ""

# Step 3: Start Docker services (if not already running)
Write-Host "[3/5] Verifying Docker services..." -ForegroundColor Yellow
docker-compose ps -q 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Starting Docker services..." -ForegroundColor Yellow
    docker-compose up -d
} else {
    Write-Host "  Docker services already running" -ForegroundColor Green
}
Write-Host ""

# Step 4: Start Backend (from root directory - CRITICAL!)
Write-Host "[4/5] Starting Backend on port 8001..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'Backend Server - Port 8001' -ForegroundColor Cyan; python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8001 --reload"
Start-Sleep -Seconds 8
Write-Host "  Backend started" -ForegroundColor Green
Write-Host ""

# Step 5: Start Frontend
Write-Host "[5/5] Starting Frontend on port 3001..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host 'Frontend Server - Port 3001' -ForegroundColor Cyan; npm run dev"
Start-Sleep -Seconds 5
Write-Host "  Frontend started" -ForegroundColor Green
Write-Host ""

# Verify services
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  Service Status Check" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Checking Backend Health..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -TimeoutSec 5 2>$null
    Write-Host "  Backend: HEALTHY" -ForegroundColor Green
    Write-Host "  URL: http://localhost:8001" -ForegroundColor White
} catch {
    Write-Host "  Backend: NOT RESPONDING (may need more time to start)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Checking Frontend..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3001" -UseBasicParsing -TimeoutSec 5 2>$null
    Write-Host "  Frontend: RUNNING" -ForegroundColor Green
    Write-Host "  URL: http://localhost:3001" -ForegroundColor White
} catch {
    Write-Host "  Frontend: NOT RESPONDING (may need more time to start)" -ForegroundColor Red
}

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  REIMS Services Started Successfully!" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your application at: http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: Backend and Frontend are running in separate terminal windows." -ForegroundColor Yellow
Write-Host "      Close those windows to stop the services." -ForegroundColor Yellow
Write-Host ""

