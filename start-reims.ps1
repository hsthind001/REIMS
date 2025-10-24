# REIMS Startup Script
# Version: 1.0
# Description: Starts all REIMS services in the correct dependency order

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REIMS System Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if Docker is running
function Test-DockerRunning {
    try {
        $null = docker ps 2>&1
        return $true
    } catch {
        return $false
    }
}

# Function to wait for service health
function Wait-ForServiceHealth {
    param(
        [string]$ServiceName,
        [int]$MaxAttempts = 30,
        [int]$DelaySeconds = 2
    )
    
    Write-Host "Waiting for $ServiceName to be healthy..." -ForegroundColor Yellow
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        $status = docker ps --filter "name=$ServiceName" --format "{{.Status}}" 2>$null
        
        if ($status -match "healthy") {
            Write-Host "  [OK] $ServiceName is healthy" -ForegroundColor Green
            return $true
        }
        
        if ($i -eq $MaxAttempts) {
            Write-Host "  [WARN] $ServiceName health check timeout" -ForegroundColor Yellow
            return $false
        }
        
        Start-Sleep -Seconds $DelaySeconds
    }
}

# Function to check if port is in use
function Test-PortInUse {
    param([int]$Port)
    
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $connection -ne $null
}

# Step 1: Check Docker
Write-Host "[1/6] Checking Docker..." -ForegroundColor Cyan
if (-not (Test-DockerRunning)) {
    Write-Host "  [ERROR] Docker is not running!" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}
Write-Host "  [OK] Docker is running" -ForegroundColor Green
Write-Host ""

# Step 2: Start Docker Compose Services
Write-Host "[2/6] Starting Docker services..." -ForegroundColor Cyan
Write-Host "  Starting: PostgreSQL, Redis, MinIO, Ollama, Prometheus..." -ForegroundColor Gray

docker-compose up -d 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Failed to start Docker services" -ForegroundColor Red
    exit 1
}

Write-Host "  [OK] Docker Compose services started" -ForegroundColor Green
Write-Host ""

# Step 3: Wait for critical services to be healthy
Write-Host "[3/6] Waiting for services to be healthy..." -ForegroundColor Cyan

$criticalServices = @(
    "reims-postgres",
    "reims-redis",
    "reims-minio",
    "reims-worker"
)

foreach ($service in $criticalServices) {
    Wait-ForServiceHealth -ServiceName $service
}

Write-Host ""

# Step 4: Start Backend API
Write-Host "[4/6] Starting Backend API..." -ForegroundColor Cyan

# Check if backend is already running
if (Test-PortInUse -Port 8001) {
    Write-Host "  [INFO] Backend API is already running on port 8001" -ForegroundColor Yellow
} else {
    # Set environment variable and start backend
    $env:DATABASE_URL = "sqlite:///./reims.db"
    
    Write-Host "  Starting Python backend (simple_backend.py)..." -ForegroundColor Gray
    Start-Process -FilePath "python" -ArgumentList "simple_backend.py" -RedirectStandardOutput "backend_output.log" -RedirectStandardError "backend_error.log" -NoNewWindow
    
    # Wait for backend to start
    Start-Sleep -Seconds 5
    
    # Verify backend is running
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "  [OK] Backend API is running on http://localhost:8001" -ForegroundColor Green
        }
    } catch {
        Write-Host "  [WARN] Backend API may not be fully ready yet" -ForegroundColor Yellow
        Write-Host "  Check backend_output.log for details" -ForegroundColor Gray
    }
}

Write-Host ""

# Step 5: Start Frontend
Write-Host "[5/6] Starting Frontend..." -ForegroundColor Cyan

# Check if frontend is already running
if (Test-PortInUse -Port 3001) {
    Write-Host "  [INFO] Frontend is already running on port 3001" -ForegroundColor Yellow
} else {
    Write-Host "  Starting frontend development server..." -ForegroundColor Gray
    Write-Host "  (This will open in a new window)" -ForegroundColor Gray
    
    # Start frontend in a new PowerShell window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\REIMS_Copy\frontend; npm run dev"
    
    Write-Host "  [OK] Frontend is starting..." -ForegroundColor Green
    Write-Host "  It will be available at http://localhost:3001 in a few seconds" -ForegroundColor Gray
}

Write-Host ""

# Step 6: Verify All Services
Write-Host "[6/6] Verifying all services..." -ForegroundColor Cyan

# Check Docker services
$dockerServices = docker ps --format "{{.Names}}" 2>$null
$dockerCount = ($dockerServices | Measure-Object).Count

Write-Host "  Docker Services: $dockerCount running" -ForegroundColor Gray

# Check backend
$backendStatus = if (Test-PortInUse -Port 8001) { "[OK]" } else { "[--]" }
Write-Host "  Backend API (8001): $backendStatus" -ForegroundColor $(if ($backendStatus -eq "[OK]") { "Green" } else { "Yellow" })

# Check frontend
$frontendStatus = if (Test-PortInUse -Port 3001) { "[OK]" } else { "[--]" }
Write-Host "  Frontend (3001): $frontendStatus" -ForegroundColor $(if ($frontendStatus -eq "[OK]") { "Green" } else { "Yellow" })

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REIMS System Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "  Frontend:    http://localhost:3001" -ForegroundColor White
Write-Host "  Backend API: http://localhost:8001" -ForegroundColor White
Write-Host "  Grafana:     http://localhost:3000" -ForegroundColor White
Write-Host "  MinIO:       http://localhost:9001" -ForegroundColor White
Write-Host "  Prometheus:  http://localhost:9090" -ForegroundColor White
Write-Host "  PgAdmin:     http://localhost:5050" -ForegroundColor White
Write-Host ""
Write-Host "Logs:" -ForegroundColor Cyan
Write-Host "  Backend: backend_output.log" -ForegroundColor Gray
Write-Host "  Docker:  docker-compose logs -f [service-name]" -ForegroundColor Gray
Write-Host ""
Write-Host "To stop REIMS: .\stop-reims.ps1" -ForegroundColor Yellow
Write-Host ""

