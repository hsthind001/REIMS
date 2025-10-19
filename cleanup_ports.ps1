# Cleanup Ports Script for REIMS
# Kills processes using REIMS ports before startup

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "             REIMS PORT CLEANUP UTILITY" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

$ports = @{
    3000 = "Frontend (Vite)"
    8001 = "Backend (FastAPI)"
    9000 = "MinIO Storage"
    6379 = "Redis"
    11434 = "Ollama AI"
}

$killedCount = 0

foreach ($port in $ports.Keys) {
    $serviceName = $ports[$port]
    Write-Host "Checking port $port ($serviceName)..." -ForegroundColor Yellow
    
    try {
        $processes = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | 
                     Select-Object -ExpandProperty OwningProcess -Unique
        
        if ($processes) {
            foreach ($processId in $processes) {
                try {
                    $processName = (Get-Process -Id $processId -ErrorAction SilentlyContinue).ProcessName
                    Stop-Process -Id $processId -Force -ErrorAction Stop
                    Write-Host "  [OK] Killed process $processId ($processName) on port $port" -ForegroundColor Green
                    $killedCount++
                } catch {
                    Write-Host "  [WARNING] Could not kill process $processId" -ForegroundColor Yellow
                }
            }
        } else {
            Write-Host "  [OK] Port $port is free" -ForegroundColor Green
        }
    } catch {
        Write-Host "  [OK] Port $port is free" -ForegroundColor Green
    }
}

Write-Host "`n================================================================" -ForegroundColor Cyan
if ($killedCount -gt 0) {
    Write-Host "Cleanup complete: $killedCount process(es) terminated" -ForegroundColor Green
} else {
    Write-Host "Cleanup complete: All ports were already free" -ForegroundColor Green
}
Write-Host "================================================================`n" -ForegroundColor Cyan

# Wait a moment for ports to be fully released
Start-Sleep -Seconds 2

















