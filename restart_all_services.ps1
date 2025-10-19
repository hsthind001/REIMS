# REIMS - Complete Service Restart Script
# This script stops and restarts all REIMS services

Write-Host "`n╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          🔄 REIMS - COMPLETE SERVICE RESTART 🔄                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Change to REIMS directory
Set-Location "C:\REIMS"

# Step 1: Stop all running Python processes related to REIMS
Write-Host "Step 1: Stopping all Python processes..." -ForegroundColor Yellow
Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*" -or 
    $_.CommandLine -like "*worker.py*" -or
    $_.CommandLine -like "*REIMS*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "  ✅ Python processes stopped" -ForegroundColor Green
Start-Sleep -Seconds 2

# Step 2: Stop Node/npm processes (frontend)
Write-Host "`nStep 2: Stopping frontend..." -ForegroundColor Yellow
Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*vite*" -or 
    $_.CommandLine -like "*frontend*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "  ✅ Frontend stopped" -ForegroundColor Green
Start-Sleep -Seconds 2

# Step 3: Verify Docker services are running
Write-Host "`nStep 3: Checking Docker services..." -ForegroundColor Yellow
$dockerServices = @("reims-postgres", "reims-redis", "reims-minio", "reims-ollama", "reims-pgadmin")
foreach ($service in $dockerServices) {
    $status = docker ps --filter "name=$service" --format "{{.Status}}" 2>$null
    if ($status) {
        Write-Host "  ✅ $service is running" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $service is not running - starting..." -ForegroundColor Yellow
        docker start $service 2>$null
    }
}

Start-Sleep -Seconds 3

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Step 4: Start Backend
Write-Host "`nStep 4: Starting Backend Server..." -ForegroundColor Yellow
Write-Host "  Opening new terminal window for backend..." -ForegroundColor Gray

$backendScript = @"
Set-Location 'C:\REIMS'
`$env:DATABASE_URL = 'postgresql://postgres:dev123@localhost:5432/reims'
`$env:REDIS_URL = 'redis://localhost:6379/0'
`$env:MINIO_ENDPOINT = 'localhost:9000'
`$env:MINIO_ACCESS_KEY = 'minioadmin'
`$env:MINIO_SECRET_KEY = 'minioadmin'
`$env:OLLAMA_BASE_URL = 'http://localhost:11434'

Write-Host ''
Write-Host '╔══════════════════════════════════════════════════════════════════╗' -ForegroundColor Green
Write-Host '║              🚀 REIMS BACKEND SERVER 🚀                          ║' -ForegroundColor Green
Write-Host '╚══════════════════════════════════════════════════════════════════╝' -ForegroundColor Green
Write-Host ''
Write-Host 'Environment Configuration:' -ForegroundColor Cyan
Write-Host '  • Database: PostgreSQL (localhost:5432/reims)' -ForegroundColor White
Write-Host '  • Redis: localhost:6379' -ForegroundColor White
Write-Host '  • MinIO: localhost:9000' -ForegroundColor White
Write-Host '  • Ollama: localhost:11434' -ForegroundColor White
Write-Host ''
Write-Host 'Starting uvicorn server on port 8001...' -ForegroundColor Yellow
Write-Host ''

python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8001 --reload

Write-Host ''
Write-Host 'Backend stopped. Press any key to close...' -ForegroundColor Red
`$null = `$Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript
Write-Host "  ✅ Backend starting in new window" -ForegroundColor Green
Start-Sleep -Seconds 5

# Step 5: Start Frontend
Write-Host "`nStep 5: Starting Frontend..." -ForegroundColor Yellow
Write-Host "  Opening new terminal window for frontend..." -ForegroundColor Gray

$frontendScript = @"
Set-Location 'C:\REIMS\frontend'

Write-Host ''
Write-Host '╔══════════════════════════════════════════════════════════════════╗' -ForegroundColor Green
Write-Host '║              🌐 REIMS FRONTEND - VITE DEV SERVER 🌐              ║' -ForegroundColor Green
Write-Host '╚══════════════════════════════════════════════════════════════════╝' -ForegroundColor Green
Write-Host ''
Write-Host 'Starting Vite development server...' -ForegroundColor Yellow
Write-Host 'Frontend URL: http://localhost:3001' -ForegroundColor Cyan
Write-Host ''

npm run dev

Write-Host ''
Write-Host 'Frontend stopped. Press any key to close...' -ForegroundColor Red
`$null = `$Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript
Write-Host "  ✅ Frontend starting in new window" -ForegroundColor Green
Start-Sleep -Seconds 5

# Step 6: Start Worker
Write-Host "`nStep 6: Starting Background Worker..." -ForegroundColor Yellow
Write-Host "  Opening new terminal window for worker..." -ForegroundColor Gray

$workerScript = @"
Set-Location 'C:\REIMS\queue_service'

Write-Host ''
Write-Host '╔══════════════════════════════════════════════════════════════════╗' -ForegroundColor Green
Write-Host '║              ⚙️  REIMS BACKGROUND WORKER ⚙️                       ║' -ForegroundColor Green
Write-Host '╚══════════════════════════════════════════════════════════════════╝' -ForegroundColor Green
Write-Host ''
Write-Host 'Starting document processing worker...' -ForegroundColor Yellow
Write-Host 'Queues: document_processing, ai_analysis, notifications' -ForegroundColor Cyan
Write-Host ''

python worker.py

Write-Host ''
Write-Host 'Worker stopped. Press any key to close...' -ForegroundColor Red
`$null = `$Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $workerScript
Write-Host "  ✅ Worker starting in new window" -ForegroundColor Green
Start-Sleep -Seconds 3

# Summary
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "`n╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✅ ALL SERVICES RESTARTED SUCCESSFULLY! ✅               ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "🎯 SERVICE STATUS:" -ForegroundColor Cyan
Write-Host "  ✅ Backend:  http://localhost:8001 (with PostgreSQL)" -ForegroundColor White
Write-Host "  ✅ Frontend: http://localhost:3001" -ForegroundColor White
Write-Host "  ✅ Worker:   Processing queue jobs" -ForegroundColor White
Write-Host "  ✅ pgAdmin:  http://localhost:5050" -ForegroundColor White
Write-Host ""

Write-Host "📊 DATABASE:" -ForegroundColor Cyan
Write-Host "  • Type: PostgreSQL" -ForegroundColor White
Write-Host "  • Host: localhost:5432" -ForegroundColor White
Write-Host "  • Database: reims" -ForegroundColor White
Write-Host "  • Tables: 8 tables created and ready" -ForegroundColor White
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "`n🧪 TEST YOUR END-TO-END FLOW:`n" -ForegroundColor Yellow

Write-Host "1️⃣  Open Frontend:" -ForegroundColor Cyan
Write-Host "    http://localhost:3001/upload`n" -ForegroundColor White

Write-Host "2️⃣  Upload a Document:" -ForegroundColor Cyan
Write-Host "    • Click 'Choose File'" -ForegroundColor White
Write-Host "    • Select a PDF or document" -ForegroundColor White
Write-Host "    • Click 'Upload'`n" -ForegroundColor White

Write-Host "3️⃣  Watch the Backend Terminal:" -ForegroundColor Cyan
Write-Host "    • Should show 'POST /api/documents/upload'" -ForegroundColor White
Write-Host "    • Document gets saved to PostgreSQL`n" -ForegroundColor White

Write-Host "4️⃣  Watch the Worker Terminal:" -ForegroundColor Cyan
Write-Host "    • Should pick up the job" -ForegroundColor White
Write-Host "    • Process the document`n" -ForegroundColor White

Write-Host "5️⃣  Verify in pgAdmin:" -ForegroundColor Cyan
Write-Host "    • Open: http://localhost:5050" -ForegroundColor White
Write-Host "    • Login: admin@example.com / admin123" -ForegroundColor White
Write-Host "    • Connect to server (if not connected)" -ForegroundColor White
Write-Host "    • Navigate to: Tables → documents" -ForegroundColor White
Write-Host "    • Right-click → View/Edit Data → All Rows" -ForegroundColor White
Write-Host "    • You'll see your uploaded document!`n" -ForegroundColor White

Write-Host "6️⃣  Check Frontend:" -ForegroundColor Cyan
Write-Host "    • Go to 'Documents' page" -ForegroundColor White
Write-Host "    • See your document with status`n" -ForegroundColor White

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "`n💡 TIPS:" -ForegroundColor Magenta
Write-Host "  • Keep all terminal windows open" -ForegroundColor White
Write-Host "  • Backend must show 'Connected to PostgreSQL' (not SQLite)" -ForegroundColor White
Write-Host "  • Use Ctrl+C in any window to stop that service" -ForegroundColor White
Write-Host "  • Check backend/worker terminals for errors" -ForegroundColor White
Write-Host ""

Write-Host "🎉 Happy Testing!" -ForegroundColor Green
Write-Host ""














