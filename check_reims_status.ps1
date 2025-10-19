# REIMS Complete Status Check Script
# Checks both backend and frontend services
# Permanent fix for PowerShell curl/proxy issues

Write-Host "`n╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          REIMS Application Status Check             ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$backendRunning = $false
$frontendRunning = $false

# Check Backend (Port 8000)
Write-Host "🔧 Checking Backend Server (http://localhost:8000)..." -ForegroundColor Yellow
try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    
    if ($backendResponse.StatusCode -eq 200) {
        Write-Host "   ✅ Backend is RUNNING" -ForegroundColor Green
        
        # Parse JSON response
        $healthData = $backendResponse.Content | ConvertFrom-Json
        Write-Host "   Service: $($healthData.service)" -ForegroundColor White
        Write-Host "   Status: $($healthData.status)" -ForegroundColor White
        Write-Host "   Routers: $($healthData.routers_loaded -join ', ')" -ForegroundColor White
        Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
        $backendRunning = $true
    }
} catch {
    Write-Host "   ❌ Backend is NOT RUNNING" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor DarkGray
}

Write-Host ""

# Check Frontend (Port 3000)
Write-Host "🎨 Checking Frontend Server (http://localhost:3000)..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -Method Get -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "   ✅ Frontend is RUNNING" -ForegroundColor Green
        Write-Host "   Status Code: $($frontendResponse.StatusCode)" -ForegroundColor White
        Write-Host "   Content Length: $($frontendResponse.Content.Length) bytes" -ForegroundColor White
        Write-Host "   Open in browser: http://localhost:3000" -ForegroundColor Cyan
        $frontendRunning = $true
    }
} catch {
    Write-Host "   ❌ Frontend is NOT RUNNING" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

# Summary
if ($backendRunning -and $frontendRunning) {
    Write-Host "✅ ALL SYSTEMS OPERATIONAL" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access your application at: http://localhost:3000" -ForegroundColor White
    exit 0
} elseif ($backendRunning -or $frontendRunning) {
    Write-Host "⚠️  PARTIAL SYSTEM STATUS" -ForegroundColor Yellow
    Write-Host ""
    if (-not $backendRunning) {
        Write-Host "💡 Start Backend: python start_optimized_server.py" -ForegroundColor Yellow
    }
    if (-not $frontendRunning) {
        Write-Host "💡 Start Frontend: cd frontend; npm run dev" -ForegroundColor Yellow
    }
    exit 1
} else {
    Write-Host "❌ ALL SYSTEMS DOWN" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Quick Start Commands:" -ForegroundColor Yellow
    Write-Host "   Backend:  python start_optimized_server.py" -ForegroundColor White
    Write-Host "   Frontend: cd frontend; npm run dev" -ForegroundColor White
    exit 2
}

Write-Host ""
















