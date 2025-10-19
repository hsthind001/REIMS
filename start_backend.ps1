# PowerShell script to start the REIMS backend server
Write-Host "Starting REIMS Backend Server..." -ForegroundColor Green

# Change to the REIMS directory
Set-Location "C:\REIMS"

# Set environment variables for PostgreSQL
$env:DATABASE_URL = "postgresql://postgres:dev123@localhost:5432/reims"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:MINIO_ENDPOINT = "localhost:9000"
$env:MINIO_ACCESS_KEY = "minioadmin"
$env:MINIO_SECRET_KEY = "minioadmin"
$env:OLLAMA_BASE_URL = "http://localhost:11434"

Write-Host "Environment configured:" -ForegroundColor Cyan
Write-Host "  Database: PostgreSQL (localhost:5432/reims)" -ForegroundColor Gray
Write-Host "  Redis: localhost:6379" -ForegroundColor Gray
Write-Host "  MinIO: localhost:9000" -ForegroundColor Gray
Write-Host "  Ollama: localhost:11434" -ForegroundColor Gray
Write-Host ""

# Start the FastAPI server
try {
    Write-Host "Starting uvicorn server on port 8001..." -ForegroundColor Yellow
    python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8001 --reload
} catch {
    Write-Host "Error starting server: $_" -ForegroundColor Red
    exit 1
}