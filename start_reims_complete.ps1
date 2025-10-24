# REIMS Complete Startup Script
# Ensures all services start correctly with proper configuration

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "REIMS Complete Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Start Docker Services
Write-Host "`n[1/5] Starting Docker services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be healthy
Write-Host "Waiting for services to be healthy (60s)..."
Start-Sleep -Seconds 60

# Step 2: Verify Docker Services
Write-Host "`n[2/5] Verifying Docker services..." -ForegroundColor Yellow
$services = @("reims-minio", "reims-redis", "reims-postgres", "reims-worker")
foreach ($service in $services) {
    $status = docker inspect --format='{{.State.Health.Status}}' $service 2>$null
    if ($status -eq "healthy") {
        Write-Host "  ✓ $service is healthy" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $service is not healthy: $status" -ForegroundColor Red
    }
}

# Step 3: Start Backend
Write-Host "`n[3/5] Starting backend..." -ForegroundColor Yellow

# Kill any existing backend processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait for port to be released
Start-Sleep -Seconds 3

# Start backend with correct environment
$env:DATABASE_URL="sqlite:///./reims.db"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $PWD; `$env:DATABASE_URL='sqlite:///./reims.db'; python simple_backend.py" -WindowStyle Normal

Write-Host "  Backend starting on http://localhost:8001" -ForegroundColor Green

# Wait for backend to start
Start-Sleep -Seconds 5

# Test backend
$response = Invoke-WebRequest -Uri "http://localhost:8001/api/properties" -UseBasicParsing -ErrorAction SilentlyContinue
if ($response.StatusCode -eq 200) {
    Write-Host "  ✓ Backend is responding" -ForegroundColor Green
} else {
    Write-Host "  ✗ Backend may not be ready yet" -ForegroundColor Yellow
}

# Step 4: Start Frontend
Write-Host "`n[4/5] Starting frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $PWD\frontend; npm run dev" -WindowStyle Normal
Write-Host "  Frontend starting on http://localhost:3001" -ForegroundColor Green

# Step 5: Summary
Write-Host "`n[5/5] Startup Complete!" -ForegroundColor Green
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "REIMS is now running:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3001" -ForegroundColor White
Write-Host "  Backend:  http://localhost:8001" -ForegroundColor White
Write-Host "  MinIO:    http://localhost:9001" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
