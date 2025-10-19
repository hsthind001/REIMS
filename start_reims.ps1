# REIMS Unified Startup Script
# Ensures backend starts before frontend with proper health checks

param(
    [switch]$SkipHealthCheck,
    [int]$HealthCheckTimeout = 30
)

$ErrorActionPreference = "Stop"

Write-Host "`n╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "║                      REIMS STARTUP SCRIPT                            ║" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# =============================================================================
# STEP 1: STOP ANY EXISTING PROCESSES
# =============================================================================
Write-Host "Step 1: Cleaning up existing processes..." -ForegroundColor Yellow

# Stop Python processes (backend)
$pythonProcesses = Get-Process python* -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "  Stopping existing backend processes..." -ForegroundColor Gray
    $pythonProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "  ✓ Backend processes stopped" -ForegroundColor Green
} else {
    Write-Host "  ✓ No existing backend processes" -ForegroundColor Green
}

# Stop Node processes (frontend)
$nodeProcesses = Get-Process node* -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "  Stopping existing frontend processes..." -ForegroundColor Gray
    $nodeProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "  ✓ Frontend processes stopped" -ForegroundColor Green
} else {
    Write-Host "  ✓ No existing frontend processes" -ForegroundColor Green
}

# Free port 3001 (Frontend) if occupied
Write-Host "  Checking port 3001..." -ForegroundColor Gray
try {
    $processes3001 = Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue | 
                     Select-Object -ExpandProperty OwningProcess -Unique
    if ($processes3001) {
        foreach ($processId in $processes3001) {
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            Write-Host "  ✓ Freed port 3001 from process $processId" -ForegroundColor Green
        }
    } else {
        Write-Host "  ✓ Port 3001 is free" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✓ Port 3001 is free" -ForegroundColor Green
}

# Free port 8001 (Backend) if occupied
Write-Host "  Checking port 8001..." -ForegroundColor Gray
try {
    $processes8001 = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue | 
                     Select-Object -ExpandProperty OwningProcess -Unique
    if ($processes8001) {
        foreach ($processId in $processes8001) {
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            Write-Host "  ✓ Freed port 8001 from process $processId" -ForegroundColor Green
        }
    } else {
        Write-Host "  ✓ Port 8001 is free" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✓ Port 8001 is free" -ForegroundColor Green
}

# Wait for ports to be fully released
Start-Sleep -Seconds 1

# =============================================================================
# STEP 2: START BACKEND
# =============================================================================
Write-Host "`nStep 2: Starting Backend..." -ForegroundColor Yellow

# Check if simple_backend.py exists
if (-not (Test-Path "simple_backend.py")) {
    Write-Host "  ✗ ERROR: simple_backend.py not found!" -ForegroundColor Red
    exit 1
}

# Start backend
Write-Host "  Starting backend on port 8001..." -ForegroundColor Gray
$backendProcess = Start-Process python -ArgumentList "simple_backend.py" `
    -WindowStyle Hidden -PassThru -RedirectStandardOutput "backend_startup.log" `
    -RedirectStandardError "backend_error.log"

Write-Host "  ✓ Backend process started (PID: $($backendProcess.Id))" -ForegroundColor Green

# =============================================================================
# STEP 3: WAIT FOR BACKEND TO BE READY
# =============================================================================
Write-Host "`nStep 3: Waiting for backend to be ready..." -ForegroundColor Yellow

if (-not $SkipHealthCheck) {
    $backendReady = $false
    $attempts = 0
    $maxAttempts = $HealthCheckTimeout
    
    Write-Host "  Health check URL: http://localhost:8001/health" -ForegroundColor Gray
    
    while (-not $backendReady -and $attempts -lt $maxAttempts) {
        $attempts++
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8001/health" `
                -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            
            if ($response.StatusCode -eq 200) {
                $backendReady = $true
                Write-Host "  ✓ Backend is healthy and ready!" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "  ⏳ Attempt $attempts/$maxAttempts - Backend not ready yet..." -ForegroundColor Gray
            Start-Sleep -Seconds 1
        }
    }
    
    if (-not $backendReady) {
        Write-Host "`n  ✗ ERROR: Backend failed to start within $HealthCheckTimeout seconds!" -ForegroundColor Red
        Write-Host "  Check backend_error.log for details" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "  ⚠ Skipping health check (waiting 5 seconds)" -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    Write-Host "  ✓ Backend startup delay complete" -ForegroundColor Green
}

# Verify backend port
$backendPort = Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue
if ($backendPort) {
    Write-Host "  ✓ Backend listening on port 8001" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Warning: Backend port 8001 not detected" -ForegroundColor Yellow
}

# =============================================================================
# STEP 4: START FRONTEND
# =============================================================================
Write-Host "`nStep 4: Starting Frontend..." -ForegroundColor Yellow

# Check if frontend directory exists
if (-not (Test-Path "frontend")) {
    Write-Host "  ✗ ERROR: Frontend directory not found!" -ForegroundColor Red
    exit 1
}

# Check if package.json exists
if (-not (Test-Path "frontend\package.json")) {
    Write-Host "  ✗ ERROR: frontend\package.json not found!" -ForegroundColor Red
    exit 1
}

# Start frontend
Write-Host "  Starting frontend on port 3001..." -ForegroundColor Gray
Set-Location frontend

$frontendProcess = Start-Process cmd -ArgumentList "/c npm run dev" `
    -WindowStyle Normal -PassThru

Set-Location ..

Write-Host "  ✓ Frontend process started (PID: $($frontendProcess.Id))" -ForegroundColor Green

# =============================================================================
# STEP 5: WAIT FOR FRONTEND TO BE READY
# =============================================================================
Write-Host "`nStep 5: Waiting for frontend to be ready..." -ForegroundColor Yellow

$frontendReady = $false
$attempts = 0
$maxAttempts = 20

while (-not $frontendReady -and $attempts -lt $maxAttempts) {
    $attempts++
    
    $frontendPort = Get-NetTCPConnection -LocalPort 3001 -State Listen -ErrorAction SilentlyContinue
    if ($frontendPort) {
        $frontendReady = $true
        Write-Host "  ✓ Frontend is ready on port 3001!" -ForegroundColor Green
    } else {
        Write-Host "  ⏳ Waiting for frontend... ($attempts/$maxAttempts)" -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
}

if (-not $frontendReady) {
    Write-Host "  ⚠ Warning: Frontend may still be starting" -ForegroundColor Yellow
} else {
    # Additional check - try to access frontend
    Start-Sleep -Seconds 2
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3001" `
            -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        Write-Host "  ✓ Frontend is accessible!" -ForegroundColor Green
    }
    catch {
        Write-Host "  ⚠ Frontend port open but not responding yet" -ForegroundColor Yellow
    }
}

# =============================================================================
# STEP 6: VERIFY ALL SERVICES
# =============================================================================
Write-Host "`nStep 6: Verifying all services..." -ForegroundColor Yellow

$services = @(
    @{Name="Backend"; Port=8001; URL="http://localhost:8001"},
    @{Name="Frontend"; Port=3001; URL="http://localhost:3001"},
    @{Name="Redis"; Port=6379; URL=$null},
    @{Name="MinIO"; Port=9000; URL=$null},
    @{Name="Ollama"; Port=11434; URL=$null}
)

$allGood = $true

foreach ($service in $services) {
    $port = Get-NetTCPConnection -LocalPort $service.Port -State Listen -ErrorAction SilentlyContinue
    
    if ($port) {
        Write-Host "  ✓ $($service.Name): Port $($service.Port) listening" -ForegroundColor Green
    } else {
        if ($service.Name -in @("Backend", "Frontend")) {
            Write-Host "  ✗ $($service.Name): Port $($service.Port) NOT listening" -ForegroundColor Red
            $allGood = $false
        } else {
            Write-Host "  ⚠ $($service.Name): Port $($service.Port) not available" -ForegroundColor Yellow
        }
    }
}

# =============================================================================
# SUMMARY
# =============================================================================
Write-Host "`n╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan

if ($allGood) {
    Write-Host "║                    ✓ REIMS STARTED SUCCESSFULLY                      ║" -ForegroundColor Green
} else {
    Write-Host "║                ⚠ REIMS STARTED WITH WARNINGS                         ║" -ForegroundColor Yellow
}

Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:8001" -ForegroundColor White
Write-Host "  Frontend: http://localhost:3001" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8001/docs" -ForegroundColor White

Write-Host "`nProcess IDs:" -ForegroundColor Cyan
Write-Host "  Backend PID:  $($backendProcess.Id)" -ForegroundColor White
Write-Host "  Frontend PID: $($frontendProcess.Id)" -ForegroundColor White

Write-Host "`nLogs:" -ForegroundColor Cyan
Write-Host "  Backend output: backend_startup.log" -ForegroundColor White
Write-Host "  Backend errors: backend_error.log" -ForegroundColor White

Write-Host "`nTo stop services:" -ForegroundColor Cyan
Write-Host "  .\stop_reims.ps1" -ForegroundColor White
Write-Host "  OR: Get-Process python*,node* | Stop-Process" -ForegroundColor White

Write-Host "`n" + ("="*70) + "`n"

# Open browser if everything is good
if ($allGood) {
    Start-Sleep -Seconds 2
    Write-Host "Opening frontend in browser..." -ForegroundColor Cyan
    Start-Process "http://localhost:3001"
}

