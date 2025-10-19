#!/usr/bin/env powershell
<#
.SYNOPSIS
    REIMS Optimized System Launcher
.DESCRIPTION
    High-performance startup script for the complete REIMS system with monitoring and optimization features.
    This script ensures optimal startup sequence, dependency checking, and performance monitoring.
.NOTES
    Version: 2.1.0
    Optimized for production-ready performance
#>

param(
    [string]$Mode = "development",  # development, production, or testing
    [switch]$SkipDependencyCheck,
    [switch]$Monitor,
    [switch]$Quiet
)

# REIMS Optimized Configuration
$REIMS_CONFIG = @{
    FRONTEND_PORT = 5173
    BACKEND_PORT = 8001
    MINIO_API_PORT = 9000
    MINIO_CONSOLE_PORT = 9001
    REDIS_PORT = 6379
    STARTUP_TIMEOUT = 60
    HEALTH_CHECK_INTERVAL = 5
    MAX_RETRY_ATTEMPTS = 3
}

# Performance tracking
$StartTime = Get-Date
$ProcessIds = @{}
$ServiceStatus = @{}

# Logging functions
function Write-REIMSLog {
    param([string]$Message, [string]$Level = "INFO")
    
    if (-not $Quiet) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $color = switch ($Level) {
            "INFO" { "White" }
            "SUCCESS" { "Green" }
            "WARNING" { "Yellow" }
            "ERROR" { "Red" }
            "DEBUG" { "Gray" }
            default { "White" }
        }
        Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
    }
}

function Write-REIMSBanner {
    if (-not $Quiet) {
        Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║                  🏠 REIMS SYSTEM LAUNCHER 🚀                  ║
║              Real Estate Information Management               ║
║                     Optimized Edition v2.1                  ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan
    }
}

# Performance monitoring functions
function Test-ServicePort {
    param([int]$Port, [int]$TimeoutSeconds = 5)
    
    try {
        $connection = Test-NetConnection localhost -Port $Port -WarningAction SilentlyContinue -InformationLevel Quiet
        return $connection.TcpTestSucceeded
    }
    catch {
        return $false
    }
}

function Stop-ServiceOnPort {
    param([int]$Port, [string]$ServiceName = "Unknown")
    
    $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($processes) {
        Write-REIMSLog "Stopping existing service on port $Port ($ServiceName)" "WARNING"
        foreach ($proc in $processes) {
            try {
                Stop-Process -Id $proc.OwningProcess -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 1
            }
            catch {
                Write-REIMSLog "Could not stop process $($proc.OwningProcess)" "WARNING"
            }
        }
    }
}

function Test-Dependencies {
    Write-REIMSLog "Checking system dependencies..." "INFO"
    
    $dependencies = @(
        @{ Name = "Node.js"; Command = "node"; Args = "--version"; MinVersion = "18.0.0" },
        @{ Name = "NPM"; Command = "npm"; Args = "--version"; MinVersion = "9.0.0" },
        @{ Name = "Python"; Command = "python"; Args = "--version"; MinVersion = "3.8.0" }
    )
    
    $allDepsOk = $true
    
    foreach ($dep in $dependencies) {
        try {
            $version = & $dep.Command $dep.Args 2>$null
            if ($version) {
                Write-REIMSLog "✓ $($dep.Name): $version" "SUCCESS"
            } else {
                Write-REIMSLog "✗ $($dep.Name): Not found" "ERROR"
                $allDepsOk = $false
            }
        }
        catch {
            Write-REIMSLog "✗ $($dep.Name): Not found or error" "ERROR"
            $allDepsOk = $false
        }
    }
    
    if (-not $allDepsOk) {
        Write-REIMSLog "Dependency check failed. Please install missing dependencies." "ERROR"
        return $false
    }
    
    Write-REIMSLog "All dependencies satisfied" "SUCCESS"
    return $true
}

function Initialize-Database {
    Write-REIMSLog "Initializing optimized database..." "INFO"
    
    try {
        # Run database initialization
        $pythonCode = @"
import sys
sys.path.append('backend')
from database_optimized import init_database, optimize_database
if init_database():
    optimize_database()
    print('Database initialized and optimized successfully')
else:
    print('Database initialization failed')
    sys.exit(1)
"@
        
        python -c $pythonCode | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-REIMSLog "Database initialized and optimized" "SUCCESS"
            return $true
        } else {
            Write-REIMSLog "Database initialization failed" "ERROR"
            return $false
        }
    }
    catch {
        Write-REIMSLog "Database initialization error: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-OptimizedBackend {
    Write-REIMSLog "Starting optimized backend server..." "INFO"
    
    # Clean up any existing processes
    Stop-ServiceOnPort -Port $REIMS_CONFIG.BACKEND_PORT -ServiceName "Backend"
    
    try {
        # Start optimized backend
        $process = Start-Process -FilePath "python" -ArgumentList "optimized_backend.py" -WindowStyle Minimized -PassThru
        $ProcessIds.Backend = $process.Id
        
        # Wait for startup with timeout
        $attempts = 0
        $maxAttempts = $REIMS_CONFIG.STARTUP_TIMEOUT / $REIMS_CONFIG.HEALTH_CHECK_INTERVAL
        
        do {
            Start-Sleep -Seconds $REIMS_CONFIG.HEALTH_CHECK_INTERVAL
            $isRunning = Test-ServicePort -Port $REIMS_CONFIG.BACKEND_PORT
            $attempts++
            
            if ($attempts -gt $maxAttempts) {
                throw "Backend startup timeout"
            }
        } while (-not $isRunning)
        
        # Verify health endpoint
        try {
            $health = Invoke-RestMethod -Uri "http://localhost:$($REIMS_CONFIG.BACKEND_PORT)/health" -TimeoutSec 10
            Write-REIMSLog "Backend server healthy: $($health.status)" "SUCCESS"
            $ServiceStatus.Backend = "healthy"
            return $true
        }
        catch {
            Write-REIMSLog "Backend started but health check failed" "WARNING"
            $ServiceStatus.Backend = "unhealthy"
            return $true
        }
    }
    catch {
        Write-REIMSLog "✗ Backend startup failed: $($_.Exception.Message)" "ERROR"
        $ServiceStatus.Backend = "failed"
        return $false
    }
}

function Start-OptimizedFrontend {
    Write-REIMSLog "Starting optimized frontend..." "INFO"
    
    # Clean up any existing processes
    Stop-ServiceOnPort -Port $REIMS_CONFIG.FRONTEND_PORT -ServiceName "Frontend"
    
    try {
        # Change to frontend directory and start
        Push-Location "frontend"
        
        # Check if node_modules exists and is recent
        $nodeModulesExists = Test-Path "node_modules"
        $packageJsonDate = (Get-Item "package.json").LastWriteTime
        $nodeModulesDate = if ($nodeModulesExists) { (Get-Item "node_modules").LastWriteTime } else { [DateTime]::MinValue }
        
        if (-not $nodeModulesExists -or $packageJsonDate -gt $nodeModulesDate) {
            Write-REIMSLog "Installing/updating frontend dependencies..." "INFO"
            npm install --silent
        }
        
        # Start development server
        $process = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Minimized -PassThru
        $ProcessIds.Frontend = $process.Id
        
        Pop-Location
        
        # Wait for startup
        $attempts = 0
        $maxAttempts = $REIMS_CONFIG.STARTUP_TIMEOUT / $REIMS_CONFIG.HEALTH_CHECK_INTERVAL
        
        do {
            Start-Sleep -Seconds $REIMS_CONFIG.HEALTH_CHECK_INTERVAL
            $isRunning = Test-ServicePort -Port $REIMS_CONFIG.FRONTEND_PORT
            $attempts++
            
            if ($attempts -gt $maxAttempts) {
                throw "Frontend startup timeout"
            }
        } while (-not $isRunning)
        
        Write-REIMSLog "Frontend server started successfully" "SUCCESS"
        $ServiceStatus.Frontend = "healthy"
        return $true
    }
    catch {
        Write-REIMSLog "Frontend startup failed: $($_.Exception.Message)" "ERROR"
        $ServiceStatus.Frontend = "failed"
        Pop-Location
        return $false
    }
}

function Start-SupportingServices {
    Write-REIMSLog "Checking supporting services..." "INFO"
    
    # Check Redis
    if (Test-ServicePort -Port $REIMS_CONFIG.REDIS_PORT) {
        Write-REIMSLog "Redis is running" "SUCCESS"
        $ServiceStatus.Redis = "healthy"
    } else {
        Write-REIMSLog "Redis is not running (optional)" "WARNING"
        $ServiceStatus.Redis = "not_running"
    }
    
    # Check MinIO
    if (Test-ServicePort -Port $REIMS_CONFIG.MINIO_API_PORT) {
        Write-REIMSLog "MinIO is running" "SUCCESS"
        $ServiceStatus.MinIO = "healthy"
    } else {
        Write-REIMSLog "MinIO is not running (optional)" "WARNING"
        $ServiceStatus.MinIO = "not_running"
        
        # Try to start MinIO if executable exists
        if (Test-Path "minio.exe") {
            Write-REIMSLog "Starting MinIO..." "INFO"
            $process = Start-Process -FilePath ".\minio.exe" -ArgumentList "server", ".\minio-data", "--console-address", ":$($REIMS_CONFIG.MINIO_CONSOLE_PORT)" -WindowStyle Minimized -PassThru
            $ProcessIds.MinIO = $process.Id
            Start-Sleep -Seconds 3
            
            if (Test-ServicePort -Port $REIMS_CONFIG.MINIO_API_PORT) {
                Write-REIMSLog "MinIO started successfully" "SUCCESS"
                $ServiceStatus.MinIO = "healthy"
            }
        }
    }
}

function Show-SystemStatus {
    $uptime = (Get-Date) - $StartTime
    
    Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                      🎯 SYSTEM STATUS                        ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

    Write-Host "Startup Time: " -NoNewline -ForegroundColor White
    Write-Host "$([math]::Round($uptime.TotalSeconds, 1)) seconds" -ForegroundColor Green
    
    Write-Host "`nServices:" -ForegroundColor White
    
    $services = @(
        @{ Name = "Frontend (Vite)"; Port = $REIMS_CONFIG.FRONTEND_PORT; Status = $ServiceStatus.Frontend; URL = "http://localhost:$($REIMS_CONFIG.FRONTEND_PORT)" },
        @{ Name = "Backend (FastAPI)"; Port = $REIMS_CONFIG.BACKEND_PORT; Status = $ServiceStatus.Backend; URL = "http://localhost:$($REIMS_CONFIG.BACKEND_PORT)" },
        @{ Name = "MinIO Storage"; Port = $REIMS_CONFIG.MINIO_API_PORT; Status = $ServiceStatus.MinIO; URL = "http://localhost:$($REIMS_CONFIG.MINIO_CONSOLE_PORT)" },
        @{ Name = "Redis Cache"; Port = $REIMS_CONFIG.REDIS_PORT; Status = $ServiceStatus.Redis; URL = "N/A" }
    )
    
    foreach ($service in $services) {
        $icon = switch ($service.Status) {
            "healthy" { "[OK]" }
            "unhealthy" { "[WARN]" }
            "failed" { "[FAIL]" }
            "not_running" { "[N/A]" }
            default { "[UNK]" }
        }
        
        $statusText = $service.Status -replace "_", " " | ForEach-Object { (Get-Culture).TextInfo.ToTitleCase($_) }
        Write-Host "  $icon $($service.Name.PadRight(20)) : $statusText (Port $($service.Port))" -ForegroundColor White
        
        if ($service.URL -ne "N/A" -and $service.Status -eq "healthy") {
            Write-Host "     $($service.URL)" -ForegroundColor Gray
        }
    }
    
    Write-Host "Performance URLs:" -ForegroundColor Cyan
    Write-Host "  - Main Application:  http://localhost:$($REIMS_CONFIG.FRONTEND_PORT)" -ForegroundColor White
    Write-Host "  - API Documentation: http://localhost:$($REIMS_CONFIG.BACKEND_PORT)/docs" -ForegroundColor White
    Write-Host "  - Health Check:      http://localhost:$($REIMS_CONFIG.BACKEND_PORT)/health" -ForegroundColor White
    Write-Host "  - System Stats:      http://localhost:$($REIMS_CONFIG.BACKEND_PORT)/api/system/stats" -ForegroundColor White
}

function Start-PerformanceMonitor {
    if (-not $Monitor) { return }
    
    Write-REIMSLog "Starting performance monitor..." "INFO"
    
    $monitorScript = {
        param($Ports, $Interval)
        
        while ($true) {
            Clear-Host
            Write-Host "🔍 REIMS Performance Monitor" -ForegroundColor Cyan
            Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
            Write-Host ""
            
            foreach ($port in $Ports) {
                $isRunning = Test-NetConnection localhost -Port $port -WarningAction SilentlyContinue -InformationLevel Quiet
                $status = if ($isRunning.TcpTestSucceeded) { "🟢 RUNNING" } else { "🔴 DOWN" }
                Write-Host "Port $port : $status" -ForegroundColor $(if ($isRunning.TcpTestSucceeded) { "Green" } else { "Red" })
            }
            
            Start-Sleep -Seconds $Interval
        }
    }
    
    $ports = @($REIMS_CONFIG.FRONTEND_PORT, $REIMS_CONFIG.BACKEND_PORT, $REIMS_CONFIG.MINIO_API_PORT)
    Start-Job -ScriptBlock $monitorScript -ArgumentList $ports, 10 | Out-Null
}

function Stop-AllServices {
    Write-REIMSLog "Stopping all REIMS services..." "INFO"
    
    foreach ($service in $ProcessIds.Keys) {
        try {
            $processId = $ProcessIds[$service]
            if (Get-Process -Id $processId -ErrorAction SilentlyContinue) {
                Stop-Process -Id $processId -Force
                Write-REIMSLog "Stopped $service (PID: $processId)" "SUCCESS"
            }
        }
        catch {
            Write-REIMSLog "Could not stop $service" "WARNING"
        }
    }
    
    # Stop any remaining processes on our ports
    foreach ($port in @($REIMS_CONFIG.FRONTEND_PORT, $REIMS_CONFIG.BACKEND_PORT, $REIMS_CONFIG.MINIO_API_PORT)) {
        Stop-ServiceOnPort -Port $port
    }
    
    Write-REIMSLog "All services stopped" "SUCCESS"
}

# Main execution function
function Start-REIMSSystem {
    Write-REIMSBanner
    
    Write-REIMSLog "Starting REIMS System in $Mode mode..." "INFO"
    
    # Trap Ctrl+C for graceful shutdown
    $null = Register-EngineEvent PowerShell.Exiting -Action {
        Stop-AllServices
    }
    
    try {
        # Step 1: Dependency check
        if (-not $SkipDependencyCheck) {
            if (-not (Test-Dependencies)) {
                throw "Dependency check failed"
            }
        }
        
        # Step 2: Initialize database
        if (-not (Initialize-Database)) {
            throw "Database initialization failed"
        }
        
        # Step 3: Start supporting services
        Start-SupportingServices
        
        # Step 4: Start backend
        if (-not (Start-OptimizedBackend)) {
            throw "Backend startup failed"
        }
        
        # Step 5: Start frontend
        if (-not (Start-OptimizedFrontend)) {
            throw "Frontend startup failed"
        }
        
        # Step 6: Show status
        Show-SystemStatus
        
        # Step 7: Start monitoring if requested
        Start-PerformanceMonitor
        
        Write-REIMSLog "🎉 REIMS System startup completed successfully!" "SUCCESS"
        Write-REIMSLog "Press Ctrl+C to stop all services" "INFO"
        
        # Keep script running
        try {
            while ($true) {
                Start-Sleep -Seconds 30
                
                # Periodic health checks
                if (-not (Test-ServicePort -Port $REIMS_CONFIG.BACKEND_PORT)) {
                    Write-REIMSLog "Backend health check failed - attempting restart..." "WARNING"
                    Start-OptimizedBackend
                }
                
                if (-not (Test-ServicePort -Port $REIMS_CONFIG.FRONTEND_PORT)) {
                    Write-REIMSLog "Frontend health check failed - attempting restart..." "WARNING"
                    Start-OptimizedFrontend
                }
            }
        }
        catch [System.Management.Automation.PipelineStoppedException] {
            # Graceful shutdown initiated
        }
        
    }
    catch {
        Write-REIMSLog "REIMS startup failed: $($_.Exception.Message)" "ERROR"
        return 1
    }
    finally {
        Stop-AllServices
        Write-REIMSLog "REIMS System shutdown complete" "INFO"
    }
    
    return 0
}

# Script entry point
if ($MyInvocation.InvocationName -ne ".") {
    exit (Start-REIMSSystem)
}