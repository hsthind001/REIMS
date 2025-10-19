# REIMS Complete System Health Check & Auto-Start Script
# Comprehensive health monitoring and automatic service startup
# 
# Features:
# - Checks all Docker services (PostgreSQL, Redis, MinIO, Ollama, etc.)
# - Checks application services (Backend API, Frontend)
# - Auto-starts any services that are down
# - Provides both quick overview and detailed health checks
# - Comprehensive error reporting and troubleshooting

param(
    [switch]$SkipDocker,
    [switch]$SkipFrontend,
    [switch]$SkipBackend,
    [int]$HealthCheckTimeout = 30,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"

Write-Host "`n╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "║          REIMS Complete System Health Check & Auto-Start            ║" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

$script:services = @{
    Docker = @{}
    Backend = @{}
    Frontend = @{}
}

$script:overallStatus = "unknown"
$script:startTime = Get-Date

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

function Write-SectionHeader {
    param([string]$Title, [string]$Color = "Yellow")
    Write-Host "`n[$Title]" -ForegroundColor $Color
    Write-Host ("=" * 60) -ForegroundColor $Color
}

function Write-ServiceStatus {
    param(
        [string]$ServiceName,
        [string]$Status,
        [string]$Details = "",
        [string]$Action = ""
    )
    
    $statusIcon = switch ($Status) {
        "healthy" { "✅" }
        "running" { "✅" }
        "started" { "✅" }
        "unhealthy" { "❌" }
        "stopped" { "❌" }
        "failed" { "❌" }
        "warning" { "⚠️" }
        default { "❓" }
    }
    
    $color = switch ($Status) {
        "healthy" { "Green" }
        "running" { "Green" }
        "started" { "Green" }
        "unhealthy" { "Red" }
        "stopped" { "Red" }
        "failed" { "Red" }
        "warning" { "Yellow" }
        default { "White" }
    }
    
    Write-Host "  $statusIcon $ServiceName" -ForegroundColor $color -NoNewline
    if ($Details) {
        Write-Host " - $Details" -ForegroundColor Gray
    } else {
        Write-Host ""
    }
    
    if ($Action) {
        Write-Host "     → $Action" -ForegroundColor Cyan
    }
}

function Test-Port {
    param([int]$Port, [string]$HostName = "localhost")
    
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        return $connection -ne $null
    }
    catch {
        return $false
    }
}

function Test-HttpEndpoint {
    param(
        [string]$Url,
        [int]$TimeoutSec = 5,
        [string]$Method = "GET"
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method $Method -TimeoutSec $TimeoutSec -UseBasicParsing -ErrorAction Stop
        return @{
            Success = $true
            StatusCode = $response.StatusCode
            Content = $response.Content
        }
    }
    catch {
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

function Start-BackendService {
    Write-Host "  Starting Backend Service..." -ForegroundColor Gray
    
    # Check if simple_backend.py exists
    if (-not (Test-Path "simple_backend.py")) {
        Write-ServiceStatus "Backend" "failed" "simple_backend.py not found"
        return $false
    }
    
    # Kill any existing Python processes
    Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    # Start backend
    $process = Start-Process python -ArgumentList "simple_backend.py" -WindowStyle Hidden -PassThru
    Write-Host "  Backend process started (PID: $($process.Id))" -ForegroundColor Gray
    
    # Wait for backend to be ready
    $ready = $false
    $attempts = 0
    $maxAttempts = $HealthCheckTimeout
    
    while (-not $ready -and $attempts -lt $maxAttempts) {
        $attempts++
        $response = Test-HttpEndpoint "http://localhost:8001/health" -TimeoutSec 2
        
        if ($response.Success -and $response.StatusCode -eq 200) {
            $ready = $true
            Write-ServiceStatus "Backend" "started" "Health check passed"
            return $true
        }
        
        Write-Host "  ⏳ Waiting for backend... ($attempts/$maxAttempts)" -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
    
    Write-ServiceStatus "Backend" "failed" "Failed to start within $HealthCheckTimeout seconds"
    return $false
}

function Start-FrontendService {
    Write-Host "  Starting Frontend Service..." -ForegroundColor Gray
    
    # Check if frontend directory exists
    if (-not (Test-Path "frontend")) {
        Write-ServiceStatus "Frontend" "failed" "frontend directory not found"
        return $false
    }
    
    # Check if package.json exists
    if (-not (Test-Path "frontend\package.json")) {
        Write-ServiceStatus "Frontend" "failed" "frontend\package.json not found"
        return $false
    }
    
    # Kill any existing Node processes
    Get-Process node* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    # Start frontend
    Push-Location frontend
    $process = Start-Process cmd -ArgumentList "/c npm run dev" -WindowStyle Normal -PassThru
    Pop-Location
    
    Write-Host "  Frontend process started (PID: $($process.Id))" -ForegroundColor Gray
    
    # Wait for frontend to be ready
    $ready = $false
    $attempts = 0
    $maxAttempts = 20
    
    while (-not $ready -and $attempts -lt $maxAttempts) {
        $attempts++
        
        if (Test-Port 3001) {
            $ready = $true
            Write-ServiceStatus "Frontend" "started" "Port 3001 listening"
            return $true
        }
        
        Write-Host "  ⏳ Waiting for frontend... ($attempts/$maxAttempts)" -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
    
    Write-ServiceStatus "Frontend" "failed" "Failed to start within 20 seconds"
    return $false
}

# =============================================================================
# DOCKER SERVICES CHECK
# =============================================================================

if (-not $SkipDocker) {
    Write-SectionHeader "Docker Services Check"
    
    # Check if Docker is installed and running
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-ServiceStatus "Docker" "running" "Docker is available"
        } else {
            Write-ServiceStatus "Docker" "stopped" "Docker not available" "Install Docker Desktop"
            $SkipDocker = $true
        }
    }
    catch {
        Write-ServiceStatus "Docker" "stopped" "Docker not available" "Install Docker Desktop"
        $SkipDocker = $true
    }
    
    if (-not $SkipDocker) {
        # Check if docker-compose.yml exists
        if (-not (Test-Path "docker-compose.yml")) {
            Write-ServiceStatus "Docker Compose" "failed" "docker-compose.yml not found"
        } else {
            # Get Docker services from docker-compose.yml
            $dockerServices = @(
                @{Name="postgres"; Container="reims-postgres"; Port=5432; HealthUrl=$null},
                @{Name="redis"; Container="reims-redis"; Port=6379; HealthUrl=$null},
                @{Name="minio"; Container="reims-minio"; Port=9000; HealthUrl="http://localhost:9000/minio/health/live"},
                @{Name="ollama"; Container="reims-ollama"; Port=11434; HealthUrl="http://localhost:11434/api/tags"},
                @{Name="prometheus"; Container="reims-prometheus"; Port=9090; HealthUrl="http://localhost:9090/-/healthy"},
                @{Name="grafana"; Container="reims-grafana"; Port=3000; HealthUrl="http://localhost:3000/api/health"},
                @{Name="nginx"; Container="reims-nginx"; Port=80; HealthUrl=$null},
                @{Name="pgadmin"; Container="reims-pgadmin"; Port=5050; HealthUrl=$null},
                @{Name="worker"; Container="reims-worker"; Port=$null; HealthUrl=$null}
            )
            
            $servicesToStart = @()
            
            foreach ($service in $dockerServices) {
                try {
                    # Check if container is running
                    $containerStatus = docker ps --filter "name=$($service.Container)" --format "{{.Status}}" 2>$null
                    
                    if ($containerStatus -and $containerStatus -like "*Up*") {
                        # Check port if applicable
                        if ($service.Port) {
                            if (Test-Port $service.Port) {
                                Write-ServiceStatus $service.Name "running" "Container up, port $($service.Port) listening"
                            } else {
                                Write-ServiceStatus $service.Name "warning" "Container up but port $($service.Port) not accessible"
                            }
                        } else {
                            Write-ServiceStatus $service.Name "running" "Container up"
                        }
                        
                        # Test health URL if available
                        if ($service.HealthUrl) {
                            $healthResponse = Test-HttpEndpoint $service.HealthUrl -TimeoutSec 3
                            if ($healthResponse.Success) {
                                Write-Host "     ✓ Health check passed" -ForegroundColor Green
                            } else {
                                Write-Host "     ⚠ Health check failed: $($healthResponse.Error)" -ForegroundColor Yellow
                            }
                        }
                    } else {
                        Write-ServiceStatus $service.Name "stopped" "Container not running"
                        $servicesToStart += $service.Name
                    }
                }
                catch {
                    Write-ServiceStatus $service.Name "stopped" "Container not running"
                    $servicesToStart += $service.Name
                }
            }
            
            # Start Docker services if needed
            if ($servicesToStart.Count -gt 0) {
                Write-Host "`n  Starting Docker services..." -ForegroundColor Yellow
                try {
                    $result = docker-compose up -d 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "  ✅ Docker services started successfully" -ForegroundColor Green
                        Start-Sleep -Seconds 10  # Wait for services to start
                    } else {
                        Write-Host "  ❌ Failed to start Docker services: $result" -ForegroundColor Red
                    }
                }
                catch {
                    Write-Host "  ❌ Error starting Docker services: $($_.Exception.Message)" -ForegroundColor Red
                }
            }
        }
    }
}

# =============================================================================
# BACKEND SERVICE CHECK
# =============================================================================

if (-not $SkipBackend) {
    Write-SectionHeader "Backend Service Check"
    
    # Check if backend is running on port 8001
    if (Test-Port 8001) {
        Write-ServiceStatus "Backend" "running" "Port 8001 listening"
        
        # Test health endpoint
        $healthResponse = Test-HttpEndpoint "http://localhost:8001/health" -TimeoutSec 5
        if ($healthResponse.Success -and $healthResponse.StatusCode -eq 200) {
            Write-ServiceStatus "Backend Health" "healthy" "Health endpoint responding"
            
            # Test properties endpoint
            $propertiesResponse = Test-HttpEndpoint "http://localhost:8001/api/properties" -TimeoutSec 5
            if ($propertiesResponse.Success -and $propertiesResponse.StatusCode -eq 200) {
                Write-ServiceStatus "Backend API" "healthy" "Properties endpoint responding"
            } else {
                Write-ServiceStatus "Backend API" "warning" "Properties endpoint failed: $($propertiesResponse.Error)"
            }
        } else {
            Write-ServiceStatus "Backend Health" "unhealthy" "Health endpoint failed: $($healthResponse.Error)"
        }
    } else {
        Write-ServiceStatus "Backend" "stopped" "Port 8001 not listening"
        Write-Host "  Starting Backend Service..." -ForegroundColor Yellow
        $backendStarted = Start-BackendService
        if (-not $backendStarted) {
            Write-ServiceStatus "Backend" "failed" "Failed to start backend service"
        }
    }
}

# =============================================================================
# FRONTEND SERVICE CHECK
# =============================================================================

if (-not $SkipFrontend) {
    Write-SectionHeader "Frontend Service Check"
    
    # Check if frontend is running on port 3001
    if (Test-Port 3001) {
        Write-ServiceStatus "Frontend" "running" "Port 3001 listening"
        
        # Test frontend accessibility
        $frontendResponse = Test-HttpEndpoint "http://localhost:3001" -TimeoutSec 5
        if ($frontendResponse.Success -and $frontendResponse.StatusCode -eq 200) {
            Write-ServiceStatus "Frontend Web" "healthy" "Frontend accessible"
        } else {
            Write-ServiceStatus "Frontend Web" "warning" "Frontend not accessible: $($frontendResponse.Error)"
        }
    } else {
        Write-ServiceStatus "Frontend" "stopped" "Port 3001 not listening"
        Write-Host "  Starting Frontend Service..." -ForegroundColor Yellow
        $frontendStarted = Start-FrontendService
        if (-not $frontendStarted) {
            Write-ServiceStatus "Frontend" "failed" "Failed to start frontend service"
        }
    }
}

# =============================================================================
# DETAILED HEALTH CHECK
# =============================================================================

Write-SectionHeader "Detailed Health Check" "Cyan"

# Test backend comprehensive health endpoint
$detailedHealthResponse = Test-HttpEndpoint "http://localhost:8001/health" -TimeoutSec 10

if ($detailedHealthResponse.Success -and $detailedHealthResponse.StatusCode -eq 200) {
    try {
        $healthData = $detailedHealthResponse.Content | ConvertFrom-Json
        
        Write-Host "  📊 Backend Health Details:" -ForegroundColor Cyan
        Write-Host "    Status: $($healthData.status)" -ForegroundColor White
        Write-Host "    Timestamp: $($healthData.timestamp)" -ForegroundColor Gray
        
        if ($healthData.services) {
            Write-Host "    Services:" -ForegroundColor White
            foreach ($service in $healthData.services.PSObject.Properties) {
                $serviceName = $service.Name
                $serviceStatus = $service.Value
                $statusIcon = if ($serviceStatus -eq "healthy") { "✅" } else { "❌" }
                Write-Host "      $statusIcon $serviceName`: $serviceStatus" -ForegroundColor $(if ($serviceStatus -eq "healthy") { "Green" } else { "Red" })
            }
        }
        
        if ($healthData.details) {
            Write-Host "    Details:" -ForegroundColor White
            foreach ($detail in $healthData.details.PSObject.Properties) {
                $detailName = $detail.Name
                $detailData = $detail.Value
                Write-Host "      $detailName`:" -ForegroundColor Gray
                if ($detailData -is [PSObject]) {
                    foreach ($prop in $detailData.PSObject.Properties) {
                        Write-Host "        $($prop.Name): $($prop.Value)" -ForegroundColor Gray
                    }
                } else {
                    Write-Host "        $detailData" -ForegroundColor Gray
                }
            }
        }
    }
    catch {
        Write-Host "  ⚠ Could not parse detailed health data: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ❌ Could not retrieve detailed health information" -ForegroundColor Red
}

# =============================================================================
# QUICK OVERVIEW
# =============================================================================

Write-SectionHeader "Quick Overview" "Green"

$overviewData = @(
    @{Name="Frontend"; Port=3001; Url="http://localhost:3001"; Status=(Test-Port 3001)},
    @{Name="Backend"; Port=8001; Url="http://localhost:8001"; Status=(Test-Port 8001)},
    @{Name="PostgreSQL"; Port=5432; Url="localhost:5432"; Status=(Test-Port 5432)},
    @{Name="Redis"; Port=6379; Url="localhost:6379"; Status=(Test-Port 6379)},
    @{Name="MinIO"; Port=9000; Url="http://localhost:9000"; Status=(Test-Port 9000)},
    @{Name="Ollama"; Port=11434; Url="http://localhost:11434"; Status=(Test-Port 11434)},
    @{Name="Prometheus"; Port=9090; Url="http://localhost:9090"; Status=(Test-Port 9090)},
    @{Name="Grafana"; Port=3000; Url="http://localhost:3000"; Status=(Test-Port 3000)},
    @{Name="PgAdmin"; Port=5050; Url="http://localhost:5050"; Status=(Test-Port 5050)}
)

Write-Host "`n┌─────────────────┬────────┬─────────────────────────────────────────┐" -ForegroundColor White
Write-Host "│ Service         │ Status │ URL                                      │" -ForegroundColor White
Write-Host "├─────────────────┼────────┼─────────────────────────────────────────┤" -ForegroundColor White

foreach ($service in $overviewData) {
    $status = if ($service.Status) { "✅ UP" } else { "❌ DOWN" }
    $statusColor = if ($service.Status) { "Green" } else { "Red" }
    
    Write-Host "│ $($service.Name.PadRight(15)) │ " -NoNewline -ForegroundColor White
    Write-Host "$status" -NoNewline -ForegroundColor $statusColor
    Write-Host " │ $($service.Url.PadRight(39)) │" -ForegroundColor White
}

Write-Host "└─────────────────┴────────┴─────────────────────────────────────────┘" -ForegroundColor White

# Count services
$upCount = ($overviewData | Where-Object { $_.Status }).Count
$totalCount = $overviewData.Count
$downCount = $totalCount - $upCount

Write-Host "`n  Services: $upCount/$totalCount UP, $downCount DOWN" -ForegroundColor $(if ($downCount -eq 0) { "Green" } else { "Yellow" })

# =============================================================================
# FINAL SUMMARY
# =============================================================================

$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host "`n╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan

if ($downCount -eq 0) {
    $script:overallStatus = "healthy"
    Write-Host "║                    ✅ ALL SYSTEMS OPERATIONAL! ✅                   ║" -ForegroundColor Green
} elseif ($downCount -le 2) {
    $script:overallStatus = "degraded"
    Write-Host "║                ⚠️  SYSTEM DEGRADED - MOSTLY OPERATIONAL           ║" -ForegroundColor Yellow
} else {
    $script:overallStatus = "unhealthy"
    Write-Host "║                    ❌ SYSTEM ISSUES DETECTED ❌                    ║" -ForegroundColor Red
}

Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
Write-Host "  Frontend:    http://localhost:3001" -ForegroundColor White
Write-Host "  Backend:     http://localhost:8001" -ForegroundColor White
Write-Host "  API Docs:    http://localhost:8001/docs" -ForegroundColor White
Write-Host "  Health:      http://localhost:8001/health" -ForegroundColor White

Write-Host "`n🔧 Management URLs:" -ForegroundColor Cyan
Write-Host "  MinIO:       http://localhost:9001 (minioadmin/minioadmin)" -ForegroundColor White
Write-Host "  Grafana:     http://localhost:3000 (admin/admin123)" -ForegroundColor White
Write-Host "  Prometheus:  http://localhost:9090" -ForegroundColor White
Write-Host "  PgAdmin:     http://localhost:5050 (admin@example.com/admin123)" -ForegroundColor White

Write-Host "`n⏱️  Check completed in $([math]::Round($duration, 1)) seconds" -ForegroundColor Gray

# Exit with appropriate code
if ($script:overallStatus -eq "healthy") {
    exit 0
} elseif ($script:overallStatus -eq "degraded") {
    exit 1
} else {
    exit 2
}
