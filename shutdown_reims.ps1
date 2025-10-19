# REIMS Services Shutdown Script
# Stops all running REIMS processes and services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "REIMS Services Shutdown" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Stop Python processes (Backend and Worker)
Write-Host "Stopping Python processes..." -ForegroundColor Yellow
$pythonProcesses = Get-Process | Where-Object {$_.ProcessName -like "*python*"}
if ($pythonProcesses) {
    foreach ($proc in $pythonProcesses) {
        try {
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
            if ($cmdLine -match "uvicorn|direct_worker|worker") {
                Write-Host "  Stopping: $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor White
                Stop-Process -Id $proc.Id -Force
                Write-Host "    ✓ Stopped" -ForegroundColor Green
            }
        } catch {
            Write-Host "    ⚠ Could not stop process $($proc.Id)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  No Python processes found" -ForegroundColor Gray
}

# Stop Node processes (Frontend)
Write-Host "Stopping Node processes..." -ForegroundColor Yellow
$nodeProcesses = Get-Process | Where-Object {$_.ProcessName -like "*node*"}
if ($nodeProcesses) {
    foreach ($proc in $nodeProcesses) {
        try {
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
            if ($cmdLine -match "vite|dev|frontend") {
                Write-Host "  Stopping: $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor White
                Stop-Process -Id $proc.Id -Force
                Write-Host "    ✓ Stopped" -ForegroundColor Green
            }
        } catch {
            Write-Host "    ⚠ Could not stop process $($proc.Id)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  No Node processes found" -ForegroundColor Gray
}

# Stop Docker containers
Write-Host "Stopping Docker containers..." -ForegroundColor Yellow
try {
    $containers = docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String "reims-"
    if ($containers) {
        Write-Host "  Found REIMS containers:" -ForegroundColor White
        $containers | ForEach-Object { Write-Host "    $_" -ForegroundColor White }
        
        Write-Host "  Stopping containers..." -ForegroundColor White
        docker stop reims-redis reims-minio 2>$null
        Write-Host "    ✓ Redis container stopped" -ForegroundColor Green
        Write-Host "    ✓ MinIO container stopped" -ForegroundColor Green
    } else {
        Write-Host "  No REIMS containers running" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ⚠ Docker command failed or containers already stopped" -ForegroundColor Yellow
}

# Check for any remaining processes
Write-Host "Checking for remaining processes..." -ForegroundColor Yellow
$remainingProcesses = Get-Process | Where-Object {
    $_.ProcessName -like "*python*" -or 
    $_.ProcessName -like "*node*"
} | Where-Object {
    $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
    $cmdLine -match "uvicorn|direct_worker|worker|vite|dev|frontend"
}

if ($remainingProcesses) {
    Write-Host "  Remaining processes found:" -ForegroundColor Red
    $remainingProcesses | ForEach-Object {
        Write-Host "    PID $($_.Id): $($_.ProcessName)" -ForegroundColor Red
    }
} else {
    Write-Host "  ✓ No REIMS processes remaining" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "REIMS Services Shutdown Complete" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "All REIMS services have been stopped:" -ForegroundColor White
Write-Host "  ✓ Backend API (FastAPI/Uvicorn)" -ForegroundColor Green
Write-Host "  ✓ Frontend (Vite/React)" -ForegroundColor Green
Write-Host "  ✓ Worker Service" -ForegroundColor Green
Write-Host "  ✓ Redis Container" -ForegroundColor Green
Write-Host "  ✓ MinIO Container" -ForegroundColor Green
Write-Host ""
Write-Host "To restart services, run:" -ForegroundColor Yellow
Write-Host "  docker-compose up -d redis minio" -ForegroundColor Cyan
Write-Host "  python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8001 --reload" -ForegroundColor Cyan
Write-Host "  cd frontend && npm run dev" -ForegroundColor Cyan
Write-Host "  python queue_service/direct_worker.py" -ForegroundColor Cyan
Write-Host ""
