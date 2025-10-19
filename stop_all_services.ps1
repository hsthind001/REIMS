# REIMS - Stop All Services Script
# Gracefully stops all REIMS services

Write-Host "`n╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          🛑 STOPPING ALL REIMS SERVICES 🛑                           ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Stopping Python processes (Backend & Worker)..." -ForegroundColor Yellow

# Stop all Python processes related to REIMS
Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*" -or 
    $_.CommandLine -like "*worker.py*" -or
    $_.CommandLine -like "*backend*" -or
    $_.CommandLine -like "*REIMS*"
} | ForEach-Object {
    Write-Host "  Stopping process: $($_.ProcessName) (PID: $($_.Id))" -ForegroundColor Gray
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

Write-Host "  ✅ Python processes stopped`n" -ForegroundColor Green

Write-Host "Stopping Node processes (Frontend)..." -ForegroundColor Yellow

# Stop all Node processes (frontend)
Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*vite*" -or 
    $_.CommandLine -like "*frontend*"
} | ForEach-Object {
    Write-Host "  Stopping process: $($_.ProcessName) (PID: $($_.Id))" -ForegroundColor Gray
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

Write-Host "  ✅ Node processes stopped`n" -ForegroundColor Green

Start-Sleep -Seconds 2

Write-Host "Checking remaining processes..." -ForegroundColor Yellow
$remainingPython = Get-Process -Name python -ErrorAction SilentlyContinue
$remainingNode = Get-Process -Name node -ErrorAction SilentlyContinue

if (-not $remainingPython -and -not $remainingNode) {
    Write-Host "  ✅ All REIMS processes stopped successfully!`n" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Some processes may still be running`n" -ForegroundColor Yellow
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "`n📊 DOCKER SERVICES STATUS:`n" -ForegroundColor Cyan

Write-Host "Docker services are still running (this is OK):" -ForegroundColor White
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-String "reims"

Write-Host "`n💡 Docker Services:" -ForegroundColor Magenta
Write-Host "  • PostgreSQL, Redis, MinIO, Ollama, pgAdmin are still running" -ForegroundColor White
Write-Host "  • This is GOOD - they'll be ready tomorrow!" -ForegroundColor Green
Write-Host "  • Data is persisted in Docker volumes`n" -ForegroundColor White

Write-Host "To stop Docker services (optional):" -ForegroundColor Yellow
Write-Host "  docker-compose down" -ForegroundColor Gray
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "`n✅ SERVICES STOPPED - SESSION END`n" -ForegroundColor Green

Write-Host "📝 Status saved in:" -ForegroundColor Cyan
Write-Host "  SESSION_END_STATUS_2025-10-13.md`n" -ForegroundColor White

Write-Host "🔄 Tomorrow, to resume:" -ForegroundColor Cyan
Write-Host "  .\restart_all_services.ps1`n" -ForegroundColor White

Write-Host "Have a great rest! 😴`n" -ForegroundColor Green














