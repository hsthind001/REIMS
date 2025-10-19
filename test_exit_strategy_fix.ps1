# Test Exit Strategy Fix
# This script tests the fix for the "Failed to load properties" error

Write-Host "Testing Exit Strategy Fix"
Write-Host "========================="
Write-Host ""

# Test 1: Properties API
Write-Host "1. Testing /api/properties endpoint..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/properties" -ErrorAction Stop
    Write-Host "   SUCCESS: Properties API responding" -ForegroundColor Green
    Write-Host "   Properties count: $($response.properties.Count)" -ForegroundColor Cyan
    foreach ($prop in $response.properties) {
        Write-Host "     - $($prop.name): `$$($prop.current_market_value / 1000000)M" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ERROR: Properties API not responding" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""

# Test 2: Exit Strategy API (may need backend restart)
Write-Host "2. Testing /api/exit-strategy/analyze/1 endpoint..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/exit-strategy/analyze/1" -ErrorAction Stop
    Write-Host "   SUCCESS: Exit Strategy API responding" -ForegroundColor Green
    Write-Host "   Property: $($response.property_name)" -ForegroundColor Cyan
    Write-Host "   Recommended: $($response.recommended_strategy)" -ForegroundColor Cyan
} catch {
    Write-Host "   ERROR: Exit Strategy API not responding" -ForegroundColor Red
    Write-Host "   This may need backend restart to pick up new route" -ForegroundColor Yellow
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""

# Test 3: Open Exit Strategy page
Write-Host "3. Opening Exit Strategy page..."
Start-Process "http://localhost:3001/exit"

Write-Host ""
Write-Host "Test Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Expected Results:" -ForegroundColor Yellow
Write-Host "  - Properties API should return 2 properties with full data" -ForegroundColor White
Write-Host "  - Exit Strategy API may need backend restart" -ForegroundColor White
Write-Host "  - Exit page should show property selector dropdown" -ForegroundColor White
Write-Host "  - No more 'Failed to load properties' error" -ForegroundColor White
Write-Host ""
Write-Host "If Exit Strategy API still fails:" -ForegroundColor Yellow
Write-Host "  1. Restart the backend service" -ForegroundColor White
Write-Host "  2. Wait for it to fully start" -ForegroundColor White
Write-Host "  3. Test again" -ForegroundColor White
