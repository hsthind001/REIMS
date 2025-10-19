# MinIO Setup Script for REIMS
# Sets up MinIO object storage for development

param(
    [string]$DataPath = ".\minio-data",
    [string]$Port = "9000",
    [string]$ConsolePort = "9001",
    [switch]$Install = $false
)

Write-Host "REIMS MinIO Setup" -ForegroundColor Green
Write-Host "=================" -ForegroundColor Green

# Install MinIO if requested
if ($Install) {
    Write-Host "Installing MinIO..." -ForegroundColor Yellow
    
    # Try winget first
    try {
        winget install MinIO.MinIO
        Write-Host "MinIO installed via winget" -ForegroundColor Green
    } catch {
        Write-Warning "Winget installation failed. Please download MinIO manually from https://min.io/download"
        Write-Host "Download the Windows binary and add it to your PATH" -ForegroundColor Yellow
        exit 1
    }
}

# Check if MinIO is available
$MinIOCommand = Get-Command minio -ErrorAction SilentlyContinue
if (!$MinIOCommand) {
    Write-Error "MinIO not found in PATH. Please install MinIO first or use -Install parameter."
    Write-Host "Manual installation: Download from https://min.io/download" -ForegroundColor Yellow
    exit 1
}

# Create data directory
$FullDataPath = Resolve-Path $DataPath -ErrorAction SilentlyContinue
if (!$FullDataPath) {
    New-Item -ItemType Directory -Path $DataPath -Force | Out-Null
    $FullDataPath = Resolve-Path $DataPath
    Write-Host "Created data directory: $FullDataPath" -ForegroundColor Cyan
}

# Set environment variables
$env:MINIO_ROOT_USER = "minioadmin"
$env:MINIO_ROOT_PASSWORD = "minioadmin123"

Write-Host ""
Write-Host "MinIO Configuration:" -ForegroundColor Cyan
Write-Host "  Data Path: $FullDataPath" -ForegroundColor White
Write-Host "  Server Port: $Port" -ForegroundColor White
Write-Host "  Console Port: $ConsolePort" -ForegroundColor White
Write-Host "  Root User: $env:MINIO_ROOT_USER" -ForegroundColor White
Write-Host "  Root Password: $env:MINIO_ROOT_PASSWORD" -ForegroundColor White
Write-Host ""

Write-Host "Starting MinIO server..." -ForegroundColor Green
Write-Host "Console will be available at: http://localhost:$ConsolePort" -ForegroundColor Cyan
Write-Host "API will be available at: http://localhost:$Port" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start MinIO server
try {
    & minio server $FullDataPath --address ":$Port" --console-address ":$ConsolePort"
} catch {
    Write-Error "Error starting MinIO server: $_"
    exit 1
}