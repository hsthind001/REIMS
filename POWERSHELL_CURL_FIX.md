# PowerShell Curl/Proxy Issue - Permanent Fix

**Date:** October 12, 2025  
**Issue:** PowerShell curl alias conflicts causing proxy password prompts  
**Status:** ✅ PERMANENTLY FIXED

## The Problem

When running commands like:
```powershell
curl -s http://localhost:3000 -UseBasicParsing | Select-Object -First 1
```

PowerShell would get stuck asking for a proxy password:
```
Enter proxy password for user 'seBasicParsing':
```

## Root Cause

PowerShell has a built-in alias `curl` → `Invoke-WebRequest`, and the parameter `-UseBasicParsing` can be misinterpreted in certain configurations, causing PowerShell to think it's a username for proxy authentication.

## The Solution

### ✅ Use Custom Health Check Scripts

We've created dedicated PowerShell scripts that use proper `Invoke-WebRequest` syntax:

#### 1. Check Complete System Status
```powershell
.\check_reims_status.ps1
```

**Output:**
```
╔══════════════════════════════════════════════════════╗
║          REIMS Application Status Check             ║
╚══════════════════════════════════════════════════════╝

🔧 Checking Backend Server (http://localhost:8000)...
   ✅ Backend is RUNNING
   Service: REIMS API v2.0
   Status: healthy
   Routers: upload, analytics, property_management, ai_processing
   API Docs: http://localhost:8000/docs

🎨 Checking Frontend Server (http://localhost:3000)...
   ✅ Frontend is RUNNING
   Status Code: 200
   Content Length: 586 bytes
   Open in browser: http://localhost:3000

═══════════════════════════════════════════════════════
✅ ALL SYSTEMS OPERATIONAL

🌐 Access your application at: http://localhost:3000
```

#### 2. Check Frontend Only
```powershell
.\check_frontend_health.ps1
```

### Alternative Methods

If you need to use curl-like commands in PowerShell, use one of these approaches:

#### Method 1: Use Invoke-WebRequest Directly
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
$response.StatusCode
```

#### Method 2: Use curl.exe Explicitly
```powershell
curl.exe -s http://localhost:3000
```

#### Method 3: Use Test-NetConnection
```powershell
Test-NetConnection -ComputerName localhost -Port 3000
```

#### Method 4: Simple Status Check
```powershell
try {
    Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Running"
} catch {
    Write-Host "❌ Not Running"
}
```

## Files Created

1. **`check_reims_status.ps1`** - Complete system health check (backend + frontend)
2. **`check_frontend_health.ps1`** - Frontend-only health check

## Best Practices

### ✅ DO:
- Use `.\check_reims_status.ps1` for health checks
- Use `Invoke-WebRequest` directly when needed
- Use `curl.exe` if you need actual curl utility

### ❌ DON'T:
- Don't use `curl` alias with complex parameters
- Don't pipe curl output with `Select-Object` directly
- Don't mix curl syntax with PowerShell cmdlet syntax

## Updated Startup Guide

The `STARTUP_GUIDE.md` has been updated to use the new health check scripts instead of curl commands.

## Technical Details

### Why This Happens

1. PowerShell's `curl` is an alias for `Invoke-WebRequest`
2. Parameters are interpreted differently than real curl
3. The `-UseBasicParsing` parameter can trigger proxy authentication logic
4. PowerShell may interpret the parameter as a username in certain contexts

### The Fix

Our scripts use proper PowerShell cmdlet syntax:

```powershell
# Correct way
$response = Invoke-WebRequest -Uri "http://localhost:3000" -Method Get -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop

# Instead of
curl -s http://localhost:3000 -UseBasicParsing
```

## Verification

Run the health check script:
```powershell
.\check_reims_status.ps1
```

Expected output:
- ✅ Backend status with routers loaded
- ✅ Frontend status with response code
- ✅ Clear indication of system operational status

## Future Usage

**Always use the health check scripts:**

```powershell
# Quick status check
.\check_reims_status.ps1

# Frontend only
.\check_frontend_health.ps1
```

These scripts:
- ✅ Never get stuck on proxy prompts
- ✅ Provide clear, formatted output
- ✅ Include helpful error messages
- ✅ Give startup suggestions if services are down
- ✅ Return proper exit codes for automation

---

**Problem:** SOLVED ✅  
**Scripts:** CREATED ✅  
**Documentation:** COMPLETE ✅
















