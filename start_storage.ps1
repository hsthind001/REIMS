# REIMS Storage Service Startup Script
# PowerShell script to start the MinIO object storage service

param(
    [string]$Port = "8002",
    [switch]$Development = $false
)

Write-Host "Starting REIMS Storage Service..." -ForegroundColor Green

# Navigate to storage service directory
$StorageServicePath = Join-Path $PSScriptRoot "storage_service"
Push-Location $StorageServicePath

try {
    # Check if Python is available
    if (!(Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Error "Python not found in PATH. Please install Python or activate a Python environment."
        exit 1
    }

    # Check if MinIO is available (optional for development)
    $MinIOAvailable = Get-Command minio -ErrorAction SilentlyContinue
    if (!$MinIOAvailable -and !$Development) {
        Write-Warning "MinIO server not found in PATH. Storage service will attempt to connect to localhost:9000"
        Write-Host "To install MinIO server:" -ForegroundColor Yellow
        Write-Host "  - Download from https://min.io/download" -ForegroundColor Yellow
        Write-Host "  - Or use: winget install MinIO.MinIO" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Starting storage service anyway (will use fallback if MinIO unavailable)..." -ForegroundColor Cyan
    }

    # Install dependencies if requirements file exists
    if (Test-Path "requirements.txt") {
        Write-Host "Installing storage service dependencies..." -ForegroundColor Yellow
        python -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Some dependencies may not have installed correctly. Continuing anyway..."
        }
    }

    # Set environment variables for development
    if ($Development) {
        $env:MINIO_ENDPOINT = "localhost:9000"
        $env:MINIO_ACCESS_KEY = "minioadmin"
        $env:MINIO_SECRET_KEY = "minioadmin"
        $env:MINIO_SECURE = "false"
        Write-Host "Development mode: Using default MinIO credentials" -ForegroundColor Cyan
    }

    # Build command
    $Command = "python api.py"
    
    Write-Host "Starting storage service on port $Port..." -ForegroundColor Green
    Write-Host "Storage service will be available at: http://localhost:$Port" -ForegroundColor Cyan
    Write-Host "API documentation: http://localhost:$Port/docs" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow
    Write-Host ""

    # Start the storage service
    $env:PORT = $Port
    Invoke-Expression $Command

} catch {
    Write-Error "Error starting storage service: $_"
    exit 1
} finally {
    Pop-Location
}