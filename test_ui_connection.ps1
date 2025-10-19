# REIMS UI Connection Diagnostic Script
# Avoids PowerShell proxy issues by using -NoProxy flag

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "║          REIMS UI DATA CONNECTION DIAGNOSTICS                  ║" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Disable proxy for this session (works with all PowerShell versions)
$originalProxy = [System.Net.WebRequest]::DefaultWebProxy
[System.Net.WebRequest]::DefaultWebProxy = $null

# Test 1: Backend Health
Write-Host "🔍 Testing Backend Health..." -ForegroundColor Yellow
try {
    $backend = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✅ Backend Health: $($backend.StatusCode) - " -NoNewline -ForegroundColor Green
    $healthData = $backend.Content | ConvertFrom-Json
    Write-Host "$($healthData.status)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Backend Health: FAILED" -ForegroundColor Red
    Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 2: Properties API
Write-Host "🔍 Testing Properties API..." -ForegroundColor Yellow
try {
    $props = Invoke-WebRequest -Uri "http://localhost:8001/api/properties" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✅ Properties API: $($props.StatusCode)" -ForegroundColor Green
    $propsData = $props.Content | ConvertFrom-Json
    Write-Host "     Found $($propsData.total) properties" -ForegroundColor Green
    foreach ($prop in $propsData.properties) {
        Write-Host "       - ID: $($prop.id), Name: $($prop.name)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  ❌ Properties API: FAILED" -ForegroundColor Red
    Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Frontend
Write-Host "🔍 Testing Frontend..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3001" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✅ Frontend: $($frontend.StatusCode)" -ForegroundColor Green
    if ($frontend.Content -match "REIMS") {
        Write-Host "     Frontend HTML contains 'REIMS' - Looks good!" -ForegroundColor Green
    }
} catch {
    Write-Host "  ❌ Frontend: FAILED" -ForegroundColor Red
    Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Restore original proxy
[System.Net.WebRequest]::DefaultWebProxy = $originalProxy

Write-Host ""

# Test 4: Check ports
Write-Host "🔍 Checking Port Status..." -ForegroundColor Yellow
$port8001 = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
$port3001 = Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue

if ($port8001) {
    Write-Host "  ✅ Port 8001 (Backend): LISTENING" -ForegroundColor Green
} else {
    Write-Host "  ❌ Port 8001 (Backend): NOT LISTENING" -ForegroundColor Red
}

if ($port3001) {
    Write-Host "  ✅ Port 3001 (Frontend): LISTENING" -ForegroundColor Green
} else {
    Write-Host "  ❌ Port 3001 (Frontend): NOT LISTENING" -ForegroundColor Red
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""
Write-Host "📋 NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open browser to: http://localhost:3001" -ForegroundColor White
Write-Host "2. Press F12 to open DevTools" -ForegroundColor White
Write-Host "3. Go to Console tab - Check for errors" -ForegroundColor White
Write-Host "4. Go to Network tab - Refresh page and check API calls" -ForegroundColor White
Write-Host "5. Look for failed requests (red) or CORS errors" -ForegroundColor White
Write-Host ""
Write-Host "Opening browser with DevTools..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
Start-Process "http://localhost:3001"
Write-Host ""
Write-Host "✅ Diagnostic complete! Check browser console for errors." -ForegroundColor Green
Write-Host ""

