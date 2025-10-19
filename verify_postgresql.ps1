# Quick verification script to check if backend is using PostgreSQL

Write-Host "`n🔍 VERIFYING DATABASE CONNECTION...`n" -ForegroundColor Cyan

Write-Host "Checking PostgreSQL..." -ForegroundColor Yellow
$pgCount = docker exec reims-postgres psql -U postgres -d reims -t -c "SELECT COUNT(*) FROM documents;" 2>$null
if ($pgCount) {
    $pgCount = $pgCount.Trim()
    Write-Host "  ✅ PostgreSQL is accessible" -ForegroundColor Green
    Write-Host "  📊 Documents in PostgreSQL: $pgCount" -ForegroundColor White
} else {
    Write-Host "  ❌ Cannot access PostgreSQL" -ForegroundColor Red
}

Write-Host "`nChecking SQLite..." -ForegroundColor Yellow
if (Test-Path "reims.db") {
    $sqliteCount = python -c "import sqlite3; conn = sqlite3.connect('reims.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM documents'); print(cursor.fetchone()[0]); conn.close()" 2>$null
    if ($sqliteCount) {
        Write-Host "  ⚠️  SQLite database exists" -ForegroundColor Yellow
        Write-Host "  📊 Documents in SQLite: $sqliteCount" -ForegroundColor White
    }
} else {
    Write-Host "  ✅ No SQLite database" -ForegroundColor Green
}

Write-Host "`nChecking Backend API..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/documents" -Method Get -TimeoutSec 3
    $apiCount = $response.Count
    Write-Host "  ✅ Backend API is responding" -ForegroundColor Green
    Write-Host "  📊 Documents returned by API: $apiCount" -ForegroundColor White
    
    if ($apiCount -eq $pgCount) {
        Write-Host "`n✅ SUCCESS! Backend is using PostgreSQL!" -ForegroundColor Green
    } elseif ($apiCount -eq $sqliteCount) {
        Write-Host "`n⚠️  WARNING! Backend is still using SQLite!" -ForegroundColor Red
        Write-Host "   Please restart backend with: python start_with_postgresql.py" -ForegroundColor Yellow
    } else {
        Write-Host "`n❓ Cannot determine which database backend is using" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠️  Backend API is not responding" -ForegroundColor Red
    Write-Host "   Make sure backend is running" -ForegroundColor Yellow
}

Write-Host ""














