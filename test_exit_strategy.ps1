# Test Exit Strategy Page
# Opens the Exit Strategy page in browser

Write-Host "Testing Exit Strategy Page with Real Data"
Write-Host "=========================================="
Write-Host ""

# Test backend API endpoint
Write-Host "1. Testing backend API endpoint..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/exit-strategy/analyze/1" -ErrorAction Stop
    Write-Host "   SUCCESS: Backend API responding" -ForegroundColor Green
    Write-Host "   Property: $($response.property_name)" -ForegroundColor Cyan
    Write-Host "   Recommended Strategy: $($response.recommended_strategy)" -ForegroundColor Cyan
} catch {
    Write-Host "   ERROR: Backend API not responding" -ForegroundColor Red
    Write-Host "   Make sure backend is running on port 8001" -ForegroundColor Yellow
}

Write-Host ""

# Test for both properties
Write-Host "2. Testing data for both properties..."
Write-Host "   Property 1 (Empire State Plaza):" -ForegroundColor Cyan
try {
    $prop1 = Invoke-RestMethod -Uri "http://localhost:8001/api/exit-strategy/analyze/1"
    Write-Host "     Current Value: `$$($prop1.current_value / 1000000)M" -ForegroundColor Green
    Write-Host "     NOI: `$$($prop1.noi / 1000000)M" -ForegroundColor Green
    Write-Host "     Recommended: $($prop1.recommended_strategy)" -ForegroundColor Green
} catch {
    Write-Host "     ERROR: Could not fetch data" -ForegroundColor Red
}

Write-Host ""
Write-Host "   Property 2 (Wendover Commons):" -ForegroundColor Cyan
try {
    $prop2 = Invoke-RestMethod -Uri "http://localhost:8001/api/exit-strategy/analyze/2"
    Write-Host "     Current Value: `$$($prop2.current_value / 1000000)M" -ForegroundColor Green
    Write-Host "     NOI: `$$($prop2.noi / 1000000)M" -ForegroundColor Green
    Write-Host "     Recommended: $($prop2.recommended_strategy)" -ForegroundColor Green
} catch {
    Write-Host "     ERROR: Could not fetch data" -ForegroundColor Red
}

Write-Host ""
Write-Host "3. Opening Exit Strategy page in browser..."
Start-Process "http://localhost:3001/exit"

Write-Host ""
Write-Host "Test Complete!" -ForegroundColor Green
Write-Host "Check the browser to verify:"
Write-Host "  - Property selector dropdown appears"
Write-Host "  - Property data loads and displays"
Write-Host "  - Three strategy cards show real calculations"
Write-Host "  - Recommended strategy is highlighted"
Write-Host "  - All styling uses inline styles"
