#!/usr/bin/env powershell
<#
.SYNOPSIS
    Simple REIMS System Test Script
.DESCRIPTION
    Basic test script to verify REIMS components are working together
#>

Write-Host "=== REIMS System Test ===" -ForegroundColor Cyan

# Test Python availability
Write-Host "`nTesting Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "Python available: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found!" -ForegroundColor Red
    exit 1
}

# Test Node.js availability
Write-Host "`nTesting Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "Node.js available: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js not found!" -ForegroundColor Red
    exit 1
}

# Test backend database
Write-Host "`nTesting database..." -ForegroundColor Yellow
try {
    python -c "import sys; sys.path.append('backend'); from database_optimized import init_database; print('Database test passed') if init_database() else print('Database test failed')"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database test passed" -ForegroundColor Green
    } else {
        Write-Host "Database test failed" -ForegroundColor Red
    }
} catch {
    Write-Host "Database test error: $($_.Exception.Message)" -ForegroundColor Red
}

# Start optimized backend
Write-Host "`nStarting optimized backend..." -ForegroundColor Yellow
$backendProcess = Start-Process -FilePath "python" -ArgumentList "optimized_backend.py" -WindowStyle Minimized -PassThru

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test backend health
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 10
    Write-Host "Backend health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "Backend health check failed" -ForegroundColor Red
}

# Start frontend
Write-Host "`nStarting frontend..." -ForegroundColor Yellow
Push-Location "frontend"
$frontendProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Minimized -PassThru
Pop-Location

# Wait for frontend to start
Write-Host "Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test frontend availability
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 10 -UseBasicParsing
    Write-Host "Frontend available: Status $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "Frontend test failed" -ForegroundColor Red
}

Write-Host "`n=== System Status ===" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Backend API: http://localhost:8001" -ForegroundColor White
Write-Host "API Docs: http://localhost:8001/docs" -ForegroundColor White
Write-Host "Health Check: http://localhost:8001/health" -ForegroundColor White

Write-Host "`nPress any key to stop services..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Stop services
Write-Host "`nStopping services..." -ForegroundColor Yellow
if ($backendProcess) {
    Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
}
if ($frontendProcess) {
    Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
}

Write-Host "Test complete!" -ForegroundColor Green