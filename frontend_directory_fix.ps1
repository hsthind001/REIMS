# REIMS Frontend Directory Fix Script
# This script provides functions to properly start the frontend with correct directory context

function Start-REIMSFrontend {
    param(
        [switch]$Background = $false
    )
    
    Write-Host "🚀 Starting REIMS Frontend with directory fix..." -ForegroundColor Green
    
    # Define paths
    $reimsRoot = "C:\REIMS"
    $frontendPath = "$reimsRoot\frontend"
    
    # Validate paths
    if (-not (Test-Path $frontendPath)) {
        Write-Host "❌ Frontend directory not found: $frontendPath" -ForegroundColor Red
        return $false
    }
    
    if (-not (Test-Path "$frontendPath\package.json")) {
        Write-Host "❌ package.json not found in frontend directory" -ForegroundColor Red
        return $false
    }
    
    # Save current location
    $originalLocation = Get-Location
    
    try {
        # Change to frontend directory
        Set-Location $frontendPath
        Write-Host "📁 Working directory: $(Get-Location)" -ForegroundColor Yellow
        
        # Check dependencies
        if (-not (Test-Path "$frontendPath\node_modules")) {
            Write-Host "📦 Installing npm dependencies..." -ForegroundColor Yellow
            npm install
            if ($LASTEXITCODE -ne 0) {
                throw "npm install failed"
            }
        }
        
        # Start development server
        Write-Host "🌐 Starting Vite development server..." -ForegroundColor Cyan
        Write-Host "🔗 Frontend will be available at: http://localhost:5173" -ForegroundColor Green
        
        if ($Background) {
            # Start in background
            Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory $frontendPath -WindowStyle Hidden
            Write-Host "✅ Frontend started in background" -ForegroundColor Green
        } else {
            # Start in foreground
            npm run dev
        }
        
        return $true
        
    } catch {
        Write-Host "❌ Error starting frontend: $_" -ForegroundColor Red
        return $false
    } finally {
        # Restore original location
        Set-Location $originalLocation
    }
}

function Test-REIMSServices {
    Write-Host "🔍 Checking REIMS service status..." -ForegroundColor Cyan
    
    # Check backend
    try {
        $backendResponse = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 5 -UseBasicParsing
        if ($backendResponse.StatusCode -eq 200) {
            Write-Host "✅ Backend is running on port 8001" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ Backend not responding on port 8001" -ForegroundColor Red
    }
    
    # Check frontend
    $frontendPort = netstat -ano | Select-String ":5173"
    if ($frontendPort) {
        Write-Host "✅ Frontend is running on port 5173" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend not running on port 5173" -ForegroundColor Red
    }
}

function Stop-REIMSServices {
    Write-Host "🛑 Stopping REIMS services..." -ForegroundColor Yellow
    
    # Kill processes on REIMS ports
    $processes = netstat -ano | Select-String ":8001|:5173" | ForEach-Object {
        $line = $_.Line.Trim()
        $parts = $line -split '\s+'
        if ($parts.Count -ge 5) {
            $parts[4]
        }
    } | Sort-Object -Unique
    
    foreach ($processId in $processes) {
        if ($processId -and $processId -match '^\d+$') {
            try {
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                Write-Host "✅ Stopped process $processId" -ForegroundColor Green
            } catch {
                Write-Host "⚠️ Could not stop process $processId" -ForegroundColor Yellow
            }
        }
    }
}

# Export functions for use in other scripts
Export-ModuleMember -Function Start-REIMSFrontend, Test-REIMSServices, Stop-REIMSServices

# If script is run directly, start the frontend
if ($MyInvocation.InvocationName -eq $MyInvocation.MyCommand.Path) {
    Start-REIMSFrontend
}