# REIMS End-to-End Upload Testing Script
# Tests your uploaded documents through the complete workflow

param(
    [string[]]$DocumentIds = @(
        "2c34fa2c-cf24-4bbb-b9ad-4af92cde13e6",  # ESP 2024 Cash Flow Statement
        "59f4550c-5686-4ba9-9df1-51a7c436e4c2"   # ESP 2024 Balance Sheet
    )
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "`n╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           REIMS END-TO-END DOCUMENT TESTING SUITE                   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "📋 Testing $($DocumentIds.Count) uploaded documents`n" -ForegroundColor Yellow

# Test counter
$totalTests = 0
$passedTests = 0
$failedTests = 0

function Test-Service {
    param($Name, $Port, $URL)
    
    $totalTests++
    $port = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    
    if ($port) {
        Write-Host "  ✅ $Name (Port $Port)" -ForegroundColor Green
        $script:passedTests++
        return $true
    } else {
        Write-Host "  ❌ $Name (Port $Port) - NOT RUNNING" -ForegroundColor Red
        $script:failedTests++
        return $false
    }
}

function Test-Document {
    param($DocumentId)
    
    Write-Host "`n┌─────────────────────────────────────────────────────────────────┐" -ForegroundColor Gray
    Write-Host "│ Testing Document: $DocumentId" -ForegroundColor White
    Write-Host "└─────────────────────────────────────────────────────────────────┘" -ForegroundColor Gray
    
    # Test 1: Document exists in API
    Write-Host "`n[Test 1] Checking Backend API..." -ForegroundColor Yellow
    $script:totalTests++
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8001/api/documents/$DocumentId/status" -ErrorAction Stop
        
        $filename = $response.data.filename
        $status = $response.data.status
        
        Write-Host "  ✅ Document Found" -ForegroundColor Green
        Write-Host "     Filename: $filename" -ForegroundColor Gray
        Write-Host "     Status: $status" -ForegroundColor $(
            if ($status -eq "processed") { "Green" }
            elseif ($status -eq "processing") { "Yellow" }
            else { "Cyan" }
        )
        $script:passedTests++
    } catch {
        Write-Host "  ❌ Document Not Found in API" -ForegroundColor Red
        $script:failedTests++
        return
    }
    
    # Test 2: Document viewable (MinIO storage)
    Write-Host "`n[Test 2] Checking MinIO Storage..." -ForegroundColor Yellow
    $script:totalTests++
    try {
        $viewUrl = "http://localhost:8001/api/documents/$DocumentId/view"
        $headResponse = Invoke-WebRequest -Uri $viewUrl -Method Head -ErrorAction Stop
        
        if ($headResponse.StatusCode -eq 200) {
            Write-Host "  ✅ File Exists in MinIO" -ForegroundColor Green
            Write-Host "     Size: $($headResponse.Headers['Content-Length']) bytes" -ForegroundColor Gray
            Write-Host "     Type: $($headResponse.Headers['Content-Type'])" -ForegroundColor Gray
            $script:passedTests++
        }
    } catch {
        Write-Host "  ❌ File Not Found in MinIO" -ForegroundColor Red
        $script:failedTests++
    }
    
    # Test 3: Processing status
    Write-Host "`n[Test 3] Checking Processing Status..." -ForegroundColor Yellow
    $script:totalTests++
    
    if ($status -eq "processed") {
        Write-Host "  ✅ Document Fully Processed" -ForegroundColor Green
        $script:passedTests++
        
        # Test 4: AI Results Available
        Write-Host "`n[Test 4] Checking AI Processing Results..." -ForegroundColor Yellow
        $script:totalTests++
        
        if ($response.data.metrics) {
            Write-Host "  ✅ AI Extracted Data Available" -ForegroundColor Green
            Write-Host "     Metrics Count: $(($response.data.metrics | Get-Member -MemberType NoteProperty).Count)" -ForegroundColor Gray
            $script:passedTests++
            
            # Show extracted data
            Write-Host "`n  📊 Extracted Data:" -ForegroundColor Cyan
            $response.data.metrics | Format-List | Out-String | ForEach-Object { Write-Host "     $_" -ForegroundColor Gray }
        } else {
            Write-Host "  ⚠️  No Metrics Found (Processing may not be complete)" -ForegroundColor Yellow
            $script:failedTests++
        }
        
    } elseif ($status -eq "processing") {
        Write-Host "  🔄 Document Currently Processing..." -ForegroundColor Yellow
        Write-Host "     Wait a few seconds and test again" -ForegroundColor Gray
        $script:failedTests++
        
    } elseif ($status -eq "queued") {
        Write-Host "  ⏳ Document Queued for Processing" -ForegroundColor Cyan
        Write-Host "     Check if worker is running:" -ForegroundColor Gray
        Write-Host "     cd C:\REIMS\queue_service && python worker.py" -ForegroundColor Gray
        $script:failedTests++
        
    } elseif ($status -eq "failed") {
        Write-Host "  ❌ Processing Failed" -ForegroundColor Red
        $script:failedTests++
        
    } else {
        Write-Host "  ⚠️  Unknown Status: $status" -ForegroundColor Yellow
        $script:failedTests++
    }
    
    # Test 5: Database Entry
    Write-Host "`n[Test 5] Checking PostgreSQL Database..." -ForegroundColor Yellow
    $script:totalTests++
    
    # Try to connect to PostgreSQL
    $env:PGPASSWORD = "dev123"
    $dbCheck = psql -h localhost -p 5432 -U postgres -d reims -t -c "SELECT COUNT(*) FROM documents WHERE id = '$DocumentId'" 2>$null
    
    if ($dbCheck -match "\d+" -and [int]$dbCheck -gt 0) {
        Write-Host "  ✅ Document Found in Database" -ForegroundColor Green
        $script:passedTests++
        
        # Get database details
        $dbData = psql -h localhost -p 5432 -U postgres -d reims -t -c "SELECT filename, status, upload_date FROM documents WHERE id = '$DocumentId'" 2>$null
        if ($dbData) {
            Write-Host "     $dbData" -ForegroundColor Gray
        }
    } else {
        Write-Host "  ⚠️  Could not verify database (psql may not be installed)" -ForegroundColor Yellow
        Write-Host "     You can check manually:" -ForegroundColor Gray
        Write-Host "     psql -h localhost -p 5432 -U postgres -d reims" -ForegroundColor Gray
        Write-Host "     SELECT * FROM documents WHERE id = '$DocumentId';" -ForegroundColor Gray
    }
    
    Write-Host ""
}

# ============================================================================
# MAIN TESTING SEQUENCE
# ============================================================================

# Step 1: Check Services
Write-Host "STEP 1: Verifying REIMS Services" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Test-Service "Backend API" 8001
Test-Service "Frontend" 3001
Test-Service "PostgreSQL" 5432
Test-Service "Redis Queue" 6379
Test-Service "MinIO Storage" 9000

# Check worker
Write-Host "`n  Worker Status:" -ForegroundColor Cyan
$totalTests++
$workerProcess = Get-Process python -ErrorAction SilentlyContinue
if ($workerProcess) {
    Write-Host "  ✅ Document Worker Running ($($workerProcess.Count) process(es))" -ForegroundColor Green
    $passedTests++
} else {
    Write-Host "  ⚠️  Document Worker Not Running" -ForegroundColor Yellow
    Write-Host "     Start with: cd C:\REIMS\queue_service && python worker.py" -ForegroundColor Gray
    $failedTests++
}

# Step 2: Test Each Document
Write-Host "`n`nSTEP 2: Testing Uploaded Documents" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

foreach ($docId in $DocumentIds) {
    Test-Document -DocumentId $docId
    Start-Sleep -Milliseconds 500
}

# ============================================================================
# SUMMARY
# ============================================================================

Write-Host "`n╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                         TEST SUMMARY                                 ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$successRate = if ($totalTests -gt 0) { [math]::Round(($passedTests / $totalTests) * 100, 1) } else { 0 }

Write-Host "  Total Tests:    $totalTests" -ForegroundColor White
Write-Host "  ✅ Passed:      $passedTests" -ForegroundColor Green
Write-Host "  ❌ Failed:      $failedTests" -ForegroundColor Red
Write-Host "  Success Rate:   $successRate%" -ForegroundColor $(
    if ($successRate -ge 90) { "Green" }
    elseif ($successRate -ge 70) { "Yellow" }
    else { "Red" }
)

# Recommendations
Write-Host "`n📋 RECOMMENDATIONS:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

if ($failedTests -eq 0) {
    Write-Host "`n  🎉 ALL TESTS PASSED! Your system is working perfectly!" -ForegroundColor Green
    Write-Host "  ✨ Your documents are uploaded, processed, and ready to view!" -ForegroundColor Green
} else {
    Write-Host ""
    
    if ($DocumentIds | ForEach-Object {
        (Invoke-RestMethod "http://localhost:8001/api/documents/$_/status" -ErrorAction SilentlyContinue).data.status
    } | Where-Object { $_ -eq "queued" }) {
        Write-Host "  ⚠️  Documents stuck in 'queued' status" -ForegroundColor Yellow
        Write-Host "     → Start the worker:" -ForegroundColor White
        Write-Host "       cd C:\REIMS\queue_service && python worker.py`n" -ForegroundColor Gray
    }
    
    if (-not $workerProcess) {
        Write-Host "  ⚠️  Worker not running - documents won't process" -ForegroundColor Yellow
        Write-Host "     → Start with:" -ForegroundColor White
        Write-Host "       cd C:\REIMS\queue_service && python worker.py`n" -ForegroundColor Gray
    }
}

# Quick Access Links
Write-Host "`n🌐 QUICK ACCESS LINKS:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "  Frontend:  http://localhost:3001" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:8001/docs" -ForegroundColor White
Write-Host "  MinIO:     http://localhost:9001 (minioadmin/minioadmin)" -ForegroundColor White

# View Documents
Write-Host "`n📄 VIEW YOUR DOCUMENTS:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
foreach ($docId in $DocumentIds) {
    $docInfo = Invoke-RestMethod "http://localhost:8001/api/documents/$docId/status" -ErrorAction SilentlyContinue
    if ($docInfo) {
        Write-Host "  $($docInfo.data.filename)" -ForegroundColor White
        Write-Host "    View: http://localhost:8001/api/documents/$docId/view" -ForegroundColor Gray
        Write-Host "    Status: $($docInfo.data.status)" -ForegroundColor $(
            if ($docInfo.data.status -eq "processed") { "Green" }
            else { "Yellow" }
        )
    }
}

Write-Host "`n" + ("="*70) + "`n"














