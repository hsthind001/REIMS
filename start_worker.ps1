# REIMS Queue Worker Startup Script
# PowerShell script to start the background worker

param(
    [string]$WorkerId = $null,
    [string]$Queues = "document_processing,ai_analysis,notifications"
)

Write-Host "Starting REIMS Background Worker..." -ForegroundColor Green

# Navigate to queue service directory
$QueueServicePath = Join-Path $PSScriptRoot "queue_service"
Push-Location $QueueServicePath

try {
    # Check if Python is available
    if (!(Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Error "Python not found in PATH. Please install Python or activate a Python environment."
        exit 1
    }

    # Check if required packages are installed
    Write-Host "Checking dependencies..." -ForegroundColor Yellow
    
    # Install dependencies if requirements file exists
    if (Test-Path "queue_requirements.txt") {
        Write-Host "Installing queue service dependencies..." -ForegroundColor Yellow
        python -m pip install -r queue_requirements.txt
    }

    # Build command
    $Command = "python worker.py"
    if ($WorkerId) {
        $Command += " --worker-id $WorkerId"
    }
    if ($Queues) {
        $Command += " --queues $Queues"
    }

    Write-Host "Starting worker with command: $Command" -ForegroundColor Green
    Write-Host "Worker will process queues: $Queues" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the worker" -ForegroundColor Yellow
    Write-Host ""

    # Start the worker
    Invoke-Expression $Command

} catch {
    Write-Error "Error starting worker: $_"
    exit 1
} finally {
    Pop-Location
}