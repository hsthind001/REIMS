#!/usr/bin/env powershell
<#
.SYNOPSIS
    REIMS System Startup Script with Fixed Port Configuration
.DESCRIPTION
    Starts all REIMS services with predefined ports and checks for conflicts
#>

param(
    [switch]$CheckOnly,
    [switch]$KillConflicts
)

# Fixed port configuration
$FRONTEND_PORT = 5173
$BACKEND_PORT = 8001
$MINIO_PORT = 9000
$REDIS_PORT = 6379
$STORAGE_PORT = 8002

function Test-PortInUse {
    param([int]$Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
    return $connection.TcpTestSucceeded
}

function Get-ProcessUsingPort {
    param([int]$Port)
    $netstat = netstat -ano | Select-String ":$Port "
    if ($netstat) {
        $pid = ($netstat -split '\s+')[-1]
        if ($pid -match '^\d+$') {
            return Get-Process -Id $pid -ErrorAction SilentlyContinue
        }
    }
    return $null
}

function Write-PortStatus {
    param([int]$Port, [string]$Service)
    
    $inUse = Test-PortInUse -Port $Port
    if ($inUse) {
        $process = Get-ProcessUsingPort -Port $Port
        $processInfo = if ($process) { " (PID: $($process.Id), Process: $($process.ProcessName))" } else { "" }
        Write-Host "❌ Port $Port ($Service): IN USE$processInfo" -ForegroundColor Red
        return $false
    } else {
        Write-Host "✅ Port $Port ($Service): Available" -ForegroundColor Green
        return $true
    }
}

Write-Host "=== REIMS Port Configuration Check ===" -ForegroundColor Cyan
Write-Host ""

# Check all required ports
$allPortsAvailable = $true
$allPortsAvailable = (Write-PortStatus -Port $FRONTEND_PORT -Service "Frontend") -and $allPortsAvailable
$allPortsAvailable = (Write-PortStatus -Port $BACKEND_PORT -Service "Backend") -and $allPortsAvailable
$allPortsAvailable = (Write-PortStatus -Port $MINIO_PORT -Service "MinIO") -and $allPortsAvailable
$allPortsAvailable = (Write-PortStatus -Port $REDIS_PORT -Service "Redis") -and $allPortsAvailable
$allPortsAvailable = (Write-PortStatus -Port $STORAGE_PORT -Service "Storage") -and $allPortsAvailable

Write-Host ""

if ($CheckOnly) {
    if ($allPortsAvailable) {
        Write-Host "✅ All ports are available for REIMS services" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "❌ Some ports are in use. Use -KillConflicts to terminate conflicting processes" -ForegroundColor Red
        exit 1
    }
}

if ($KillConflicts) {
    Write-Host "Terminating processes using REIMS ports..." -ForegroundColor Yellow
    
    $ports = @($FRONTEND_PORT, $BACKEND_PORT, $MINIO_PORT, $REDIS_PORT, $STORAGE_PORT)
    foreach ($port in $ports) {
        $process = Get-ProcessUsingPort -Port $port
        if ($process) {
            Write-Host "Killing process $($process.ProcessName) (PID: $($process.Id)) using port $port"
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
    }
    
    Start-Sleep -Seconds 2
    Write-Host ""
    Write-Host "Rechecking ports..." -ForegroundColor Yellow
    
    # Recheck ports
    $allPortsAvailable = $true
    $allPortsAvailable = (Write-PortStatus -Port $FRONTEND_PORT -Service "Frontend") -and $allPortsAvailable
    $allPortsAvailable = (Write-PortStatus -Port $BACKEND_PORT -Service "Backend") -and $allPortsAvailable
    $allPortsAvailable = (Write-PortStatus -Port $MINIO_PORT -Service "MinIO") -and $allPortsAvailable
    $allPortsAvailable = (Write-PortStatus -Port $REDIS_PORT -Service "Redis") -and $allPortsAvailable
    $allPortsAvailable = (Write-PortStatus -Port $STORAGE_PORT -Service "Storage") -and $allPortsAvailable
}

if (-not $allPortsAvailable) {
    Write-Host ""
    Write-Host "❌ Cannot start REIMS - ports are in use!" -ForegroundColor Red
    Write-Host "Run with -KillConflicts to terminate conflicting processes" -ForegroundColor Yellow
    Write-Host "Or run with -CheckOnly to just check port status" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting REIMS services with fixed port configuration..." -ForegroundColor Green
Write-Host ""

# Service URLs for reference
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost:$FRONTEND_PORT" -ForegroundColor White
Write-Host "  Backend:   http://localhost:$BACKEND_PORT" -ForegroundColor White
Write-Host "  MinIO:     http://localhost:$MINIO_PORT" -ForegroundColor White
Write-Host "  Storage:   http://localhost:$STORAGE_PORT" -ForegroundColor White
Write-Host ""

Write-Host "✅ All ports verified. You can now start individual services." -ForegroundColor Green
Write-Host ""
Write-Host "To start services:" -ForegroundColor Yellow
Write-Host "  Frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host "  Backend:  python run_backend.py" -ForegroundColor White
Write-Host "  MinIO:    .\minio.exe server .\minio-data --console-address :9001" -ForegroundColor White