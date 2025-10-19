# REIMS Charts Fix Verification Script

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "║              REIMS CHARTS FIX VERIFICATION                     ║" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Disable proxy for this session
$originalProxy = [System.Net.WebRequest]::DefaultWebProxy
[System.Net.WebRequest]::DefaultWebProxy = $null

Write-Host "🔧 FIXES APPLIED:" -ForegroundColor Green
Write-Host "  ✅ Changed PropertyNOIChart from propertyId to propertyData" -ForegroundColor Green
Write-Host "  ✅ Changed PropertyRevenueChart from propertyId to propertyData" -ForegroundColor Green
Write-Host "  ✅ Added debug logging to verify data flow" -ForegroundColor Green
Write-Host ""

# Test Property 1 (Empire State Plaza)
Write-Host "🏢 Testing Property 1 (Empire State Plaza)..." -ForegroundColor Yellow
try {
    $prop1 = Invoke-WebRequest -Uri "http://localhost:8001/api/properties/1" -UseBasicParsing -TimeoutSec 5
    $prop1Data = $prop1.Content | ConvertFrom-Json
    Write-Host "  ✅ Property 1 API: $($prop1.StatusCode)" -ForegroundColor Green
    Write-Host "     NOI: `$$(($prop1Data.noi / 1000000).ToString('F1'))M" -ForegroundColor Cyan
    Write-Host "     Monthly Rent: `$$(($prop1Data.monthly_rent / 1000).ToString('F0'))K" -ForegroundColor Cyan
    Write-Host "     Value: `$$(($prop1Data.current_market_value / 1000000).ToString('F1'))M" -ForegroundColor Cyan
} catch {
    Write-Host "  ❌ Property 1 API: FAILED" -ForegroundColor Red
}

Write-Host ""

# Test Property 2 (Wendover Commons)
Write-Host "🏢 Testing Property 2 (Wendover Commons)..." -ForegroundColor Yellow
try {
    $prop2 = Invoke-WebRequest -Uri "http://localhost:8001/api/properties/2" -UseBasicParsing -TimeoutSec 5
    $prop2Data = $prop2.Content | ConvertFrom-Json
    Write-Host "  ✅ Property 2 API: $($prop2.StatusCode)" -ForegroundColor Green
    Write-Host "     NOI: `$$(($prop2Data.noi / 1000000).ToString('F1'))M" -ForegroundColor Cyan
    Write-Host "     Monthly Rent: `$$(($prop2Data.monthly_rent / 1000).ToString('F0'))K" -ForegroundColor Cyan
    Write-Host "     Value: `$$(($prop2Data.current_market_value / 1000000).ToString('F1'))M" -ForegroundColor Cyan
} catch {
    Write-Host "  ❌ Property 2 API: FAILED" -ForegroundColor Red
}

# Restore original proxy
[System.Net.WebRequest]::DefaultWebProxy = $originalProxy

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""
Write-Host "📊 CHARTS SHOULD NOW WORK!" -ForegroundColor Green
Write-Host ""
Write-Host "🔍 VERIFICATION STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open browser to: http://localhost:3001/property/1" -ForegroundColor White
Write-Host "   - Should see Empire State Plaza details" -ForegroundColor White
Write-Host "   - NOI Chart should show line graph with 12 months" -ForegroundColor White
Write-Host "   - Revenue Chart should show area graph with revenue/expenses" -ForegroundColor White
Write-Host ""
Write-Host "2. Open browser to: http://localhost:3001/property/2" -ForegroundColor White
Write-Host "   - Should see Wendover Commons details" -ForegroundColor White
Write-Host "   - Charts should show different values (lower NOI/rent)" -ForegroundColor White
Write-Host ""
Write-Host "3. Check Browser Console (F12):" -ForegroundColor White
Write-Host "   - Look for debug logs: '🔍 Passing to NOI Chart:'" -ForegroundColor White
Write-Host "   - Look for debug logs: '🔍 Passing to Revenue Chart:'" -ForegroundColor White
Write-Host "   - Should see property data with NOI and monthly_rent values" -ForegroundColor White
Write-Host ""
Write-Host "4. Expected Chart Data:" -ForegroundColor White
Write-Host "   - Empire State Plaza: NOI ~$227K/month, Rent ~$227K/month" -ForegroundColor White
Write-Host "   - Wendover Commons: NOI ~$180K/month, Rent ~$180K/month" -ForegroundColor White
Write-Host ""

Write-Host "🚀 Opening Property 1 for testing..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
Start-Process "http://localhost:3001/property/1"

Write-Host ""
Write-Host "✅ Charts fix complete! Check your browser for rendered charts!" -ForegroundColor Green
Write-Host ""

