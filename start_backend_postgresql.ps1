# REIMS Backend Startup Script - PostgreSQL Mode
# This script forces the backend to use PostgreSQL instead of SQLite

Write-Host "`n╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║          🚀 STARTING REIMS BACKEND - POSTGRESQL MODE 🚀              ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

# Change to REIMS directory
Set-Location "C:\REIMS"

# CRITICAL: Set environment variables BEFORE starting Python
# These will override the .env file settings
$env:DATABASE_URL = "postgresql://postgres:dev123@localhost:5432/reims"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:MINIO_ENDPOINT = "localhost:9000"
$env:MINIO_ACCESS_KEY = "minioadmin"
$env:MINIO_SECRET_KEY = "minioadmin"
$env:OLLAMA_BASE_URL = "http://localhost:11434"

Write-Host "🔧 Environment Configuration:" -ForegroundColor Cyan
Write-Host "  DATABASE: PostgreSQL @ localhost:5432/reims" -ForegroundColor White
Write-Host "  REDIS:    localhost:6379" -ForegroundColor White
Write-Host "  MINIO:    localhost:9000" -ForegroundColor White
Write-Host "  OLLAMA:   localhost:11434" -ForegroundColor White
Write-Host ""

Write-Host "⏳ Starting uvicorn server on port 8001..." -ForegroundColor Yellow
Write-Host "   Look for message: 'Connected to PostgreSQL'" -ForegroundColor Gray
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

try {
    # Start the FastAPI server with environment variables already set
    python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8001 --reload
} catch {
    Write-Host "`n❌ Error starting server: $_" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}














