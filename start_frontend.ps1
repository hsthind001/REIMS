# REIMS Frontend Startup Script
# This script ensures the frontend always starts from the correct directory

Write-Host "Starting REIMS Frontend..." -ForegroundColor Green

# Set the working directory to the frontend folder
$frontendPath = "C:\REIMS\frontend"

# Check if frontend directory exists
if (-Not (Test-Path $frontendPath)) {
    Write-Host "Error: Frontend directory not found at $frontendPath" -ForegroundColor Red
    exit 1
}

# Check if package.json exists in frontend directory
if (-Not (Test-Path "$frontendPath\package.json")) {
    Write-Host "Error: package.json not found in $frontendPath" -ForegroundColor Red
    exit 1
}

# Change to frontend directory
Set-Location $frontendPath
Write-Host "Changed to directory: $(Get-Location)" -ForegroundColor Yellow

# Check if node_modules exists, install if needed
if (-Not (Test-Path "$frontendPath\node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: npm install failed" -ForegroundColor Red
        exit 1
    }
}

# Start the development server
Write-Host "Starting Vite development server..." -ForegroundColor Yellow
Write-Host "Frontend will be available at: http://localhost:5173" -ForegroundColor Cyan

# Start npm dev server
npm run dev