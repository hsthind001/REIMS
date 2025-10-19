# Start backend and capture output
Write-Host "🚀 Starting backend..." -ForegroundColor Cyan

# Start backend in a new job so we can control it
$job = Start-Job -ScriptBlock {
    Set-Location "C:\REIMS"
    python run_backend.py 2>&1
}

# Wait for backend to start
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Test the upload
Write-Host "`n📤 Testing file upload..." -ForegroundColor Cyan
python test_minimal_upload.py

# Show backend output
Write-Host "`n📋 Backend Output (last 30 lines):" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Receive-Job -Job $job | Select-Object -Last 30
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Stop backend
Write-Host "`n🛑 Stopping backend..." -ForegroundColor Yellow
Stop-Job -Job $job
Remove-Job -Job $job

Write-Host "✅ Test complete" -ForegroundColor Green















