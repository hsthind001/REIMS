# REIMS Startup Script - Fixed Ports
# Frontend: 3001, Backend: 8001

Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                               ║" -ForegroundColor Cyan
Write-Host "║              REIMS APPLICATION STARTUP                        ║" -ForegroundColor Cyan
Write-Host "║              (FIXED PORTS: 3001 & 8001)                       ║" -ForegroundColor Cyan
Write-Host "║                                                               ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Function to check if port is in use
function Test-PortInUse {
    param([int]$Port)
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $connections -ne $null
}

# Function to kill process on port
function Stop-ProcessOnPort {
    param([int]$Port)
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connections) {
        $pid = $connections[0].OwningProcess
        Write-Host "  ⚠️  Port $Port is in use by PID $pid" -ForegroundColor Yellow
        Write-Host "  🔄 Stopping process..." -ForegroundColor Yellow
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Write-Host "  ✅ Port $Port freed" -ForegroundColor Green
    }
}

Write-Host "🔍 CHECKING PORTS..." -ForegroundColor Yellow
Write-Host ""

# Check Backend Port (8001)
Write-Host "  Backend Port (8001): " -NoNewline
if (Test-PortInUse -Port 8001) {
    Write-Host "⚠️  IN USE" -ForegroundColor Yellow
    Stop-ProcessOnPort -Port 8001
} else {
    Write-Host "✅ Available" -ForegroundColor Green
}

# Check Frontend Port (3001)
Write-Host "  Frontend Port (3001): " -NoNewline
if (Test-PortInUse -Port 3001) {
    Write-Host "⚠️  IN USE" -ForegroundColor Yellow
    Stop-ProcessOnPort -Port 3001
} else {
    Write-Host "✅ Available" -ForegroundColor Green
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# Start Backend
Write-Host "🚀 STARTING BACKEND (Port 8001)..." -ForegroundColor Cyan
Write-Host ""
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python run_backend.py"
Write-Host "  ⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test backend health
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 5
    if ($response.status -eq "healthy") {
        Write-Host "  ✅ Backend is HEALTHY" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠️  Backend health check failed (may still be starting...)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# Start Frontend
Write-Host "🚀 STARTING FRONTEND (Port 3001)..." -ForegroundColor Cyan
Write-Host ""
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"
Write-Host "  ⏳ Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ REIMS APPLICATION STARTED!" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host ""
Write-Host "📊 ACCESS URLS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Frontend:       http://localhost:3001" -ForegroundColor White
Write-Host "  Backend API:    http://localhost:8001" -ForegroundColor White
Write-Host "  API Docs:       http://localhost:8001/docs" -ForegroundColor White
Write-Host "  Health Check:   http://localhost:8001/health" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Enter to open URLs in browser..." -ForegroundColor Cyan
$null = Read-Host

Start-Process "http://localhost:3001"
Start-Process "http://localhost:8001/docs"

Write-Host ""
Write-Host "✅ Browser tabs opened!" -ForegroundColor Green
Write-Host ""
Write-Host "To stop services, close the PowerShell windows." -ForegroundColor Yellow
Write-Host ""
