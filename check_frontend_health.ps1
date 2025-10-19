# REIMS Frontend Health Check Script
# Permanent fix for curl/PowerShell proxy issues

Write-Host "`n=== REIMS Frontend Health Check ===" -ForegroundColor Cyan

try {
    # Use Invoke-WebRequest instead of curl alias to avoid proxy issues
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method Get -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend is RUNNING" -ForegroundColor Green
        Write-Host "   Status Code: $($response.StatusCode)" -ForegroundColor White
        Write-Host "   URL: http://localhost:3000" -ForegroundColor White
        Write-Host "   Content Length: $($response.Content.Length) bytes" -ForegroundColor White
        return $true
    } else {
        Write-Host "⚠️  Frontend responded with status: $($response.StatusCode)" -ForegroundColor Yellow
        return $false
    }
} catch {
    Write-Host "❌ Frontend is NOT RUNNING" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor White
    Write-Host "`n💡 Tip: Start frontend with 'cd frontend; npm run dev'" -ForegroundColor Yellow
    return $false
}

Write-Host ""
















