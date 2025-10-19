# REIMS Shutdown Script
# Gracefully stops all REIMS services

Write-Host "`n╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "║                     REIMS SHUTDOWN SCRIPT                            ║" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Stop Backend (Python processes)
Write-Host "Stopping Backend..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python* -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    $pythonProcesses | ForEach-Object {
        Write-Host "  Stopping process PID $($_.Id)..." -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  ✓ Backend stopped" -ForegroundColor Green
} else {
    Write-Host "  ✓ No backend processes running" -ForegroundColor Green
}

# Stop Frontend (Node processes)
Write-Host "`nStopping Frontend..." -ForegroundColor Yellow
$nodeProcesses = Get-Process node* -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    $nodeProcesses | ForEach-Object {
        Write-Host "  Stopping process PID $($_.Id)..." -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  ✓ Frontend stopped" -ForegroundColor Green
} else {
    Write-Host "  ✓ No frontend processes running" -ForegroundColor Green
}

# Wait for ports to be released
Start-Sleep -Seconds 2

# Verify ports are free
Write-Host "`nVerifying ports are free..." -ForegroundColor Yellow

$ports = @(3000, 8001)
$allFree = $true

foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "  ⚠ Port $port still in use" -ForegroundColor Yellow
        $allFree = $false
    } else {
        Write-Host "  ✓ Port $port is free" -ForegroundColor Green
    }
}

# Summary
Write-Host "`n╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan

if ($allFree) {
    Write-Host "║                 ✓ REIMS STOPPED SUCCESSFULLY                         ║" -ForegroundColor Green
} else {
    Write-Host "║              ⚠ SOME PROCESSES MAY STILL BE RUNNING                   ║" -ForegroundColor Yellow
}

Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "To start again:" -ForegroundColor Cyan
Write-Host "  .\start_reims.ps1" -ForegroundColor White
Write-Host "  OR: .\start_reims.bat`n" -ForegroundColor White

















