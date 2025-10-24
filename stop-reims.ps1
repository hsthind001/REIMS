# REIMS Shutdown Script
# Version: 1.0
# Description: Safely stops all REIMS services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REIMS System Shutdown Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop Frontend
Write-Host "[1/3] Stopping Frontend..." -ForegroundColor Cyan

# Find and stop Node processes (frontend)
$nodeProcesses = Get-Process node -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "  Stopping frontend development server..." -ForegroundColor Gray
    $nodeProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Frontend stopped" -ForegroundColor Green
} else {
    Write-Host "  [INFO] Frontend was not running" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Stop Backend API
Write-Host "[2/3] Stopping Backend API..." -ForegroundColor Cyan

# Find and stop Python processes (backend)
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*simple_backend*" -or $_.CommandLine -like "*simple_backend*"
}

if (-not $pythonProcesses) {
    # If specific filtering didn't work, stop all Python processes
    $pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
}

if ($pythonProcesses) {
    Write-Host "  Stopping backend API server..." -ForegroundColor Gray
    $pythonProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Backend API stopped" -ForegroundColor Green
} else {
    Write-Host "  [INFO] Backend API was not running" -ForegroundColor Yellow
}

Write-Host ""

# Step 3: Stop Docker Services
Write-Host "[3/3] Stopping Docker services..." -ForegroundColor Cyan

# Check if docker-compose services are running
$runningContainers = docker ps --filter "name=reims-" --format "{{.Names}}" 2>$null

if ($runningContainers) {
    Write-Host "  Stopping Docker Compose services..." -ForegroundColor Gray
    docker-compose down 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Docker services stopped" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] Some Docker services may not have stopped cleanly" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [INFO] No Docker services were running" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REIMS System Stopped!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "All services have been stopped." -ForegroundColor White
Write-Host "Data is preserved and will be available on next startup." -ForegroundColor Gray
Write-Host ""
Write-Host "To start REIMS again: .\start-reims.ps1" -ForegroundColor Yellow
Write-Host ""

