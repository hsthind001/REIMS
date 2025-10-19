# REIMS Startup Order Guide

**Version:** 2.0  
**Date:** October 11, 2025  
**Status:** ✅ Backend-First Startup Configured  

---

## Overview

REIMS now has unified startup scripts that **ensure the backend always starts before the frontend**, with proper health checks and dependency management.

---

## Why Startup Order Matters

### The Problem
If frontend starts before backend:
- Frontend makes API calls to backend
- Backend not ready yet
- API calls fail
- Frontend shows errors
- Poor user experience

### The Solution
**Backend-First Startup:**
1. ✅ Backend starts first
2. ✅ Health check verifies backend ready
3. ✅ Frontend starts after backend confirms healthy
4. ✅ No failed API calls
5. ✅ Perfect user experience

---

## Quick Start

### Option 1: PowerShell (Recommended)
```powershell
.\start_reims.ps1
```

### Option 2: Batch File
```bat
start_reims.bat
```

### Option 3: Manual
```powershell
# 1. Start backend
python run_backend.py

# 2. Wait 10 seconds

# 3. Start frontend
cd frontend
npm run dev
```

---

## Startup Scripts

### 1. start_reims.ps1 (PowerShell)

**Features:**
- ✅ Stops any existing processes
- ✅ Starts backend first
- ✅ Health check with 30-second timeout
- ✅ Waits for backend to be ready
- ✅ Starts frontend only after backend ready
- ✅ Verifies all services
- ✅ Opens browser automatically
- ✅ Provides detailed status

**Usage:**
```powershell
# Basic usage
.\start_reims.ps1

# Skip health check (faster but less safe)
.\start_reims.ps1 -SkipHealthCheck

# Custom health check timeout
.\start_reims.ps1 -HealthCheckTimeout 60
```

**Startup Flow:**
```
Step 1: Clean up existing processes
  ↓
Step 2: Start backend (port 8001)
  ↓
Step 3: Wait for backend health check
  → Checks http://localhost:8001/health
  → Retries every second
  → Max 30 attempts
  ↓
Step 4: Start frontend (port 3000)
  ↓
Step 5: Wait for frontend to be ready
  ↓
Step 6: Verify all services
  ↓
Step 7: Open browser
```

### 2. start_reims.bat (Batch File)

**Features:**
- ✅ Stops any existing processes
- ✅ Starts backend first
- ✅ Simple health check
- ✅ Starts frontend after delay
- ✅ Opens browser automatically
- ✅ Compatible with all Windows versions

**Usage:**
```bat
start_reims.bat
```

**Simpler than PowerShell but equally effective!**

---

## Shutdown Scripts

### Stop All Services

**PowerShell:**
```powershell
.\stop_reims.ps1
```

**Batch:**
```bat
stop_reims.bat
```

**Manual:**
```powershell
Get-Process python*,node* | Stop-Process -Force
```

---

## Startup Sequence Details

### Phase 1: Cleanup (2 seconds)
```
→ Stop existing Python processes (backend)
→ Stop existing Node processes (frontend)
→ Wait for ports to be released
```

### Phase 2: Backend Startup (5-30 seconds)
```
→ Start: python run_backend.py
→ Backend initializes:
  - Loads configuration from .env
  - Connects to SQLite database
  - Initializes Redis connection
  - Sets up MinIO client
  - Loads Ollama configuration
  - Starts FastAPI server on port 8001
→ Health check begins
→ Waits for GET /health to return 200 OK
→ Backend confirmed ready
```

### Phase 3: Frontend Startup (5-10 seconds)
```
→ Start: npm run dev (in frontend directory)
→ Frontend initializes:
  - Vite dev server starts
  - Compiles React app
  - Starts on port 3000
→ Waits for port 3000 to be listening
→ Frontend confirmed ready
```

### Phase 4: Verification
```
→ Checks all service ports:
  - Backend (8001)
  - Frontend (3000)
  - Redis (6379) - optional
  - MinIO (9000) - optional
  - Ollama (11434) - optional
```

### Phase 5: Ready
```
→ Opens http://localhost:3000 in browser
→ Display status summary
→ Provide process IDs for monitoring
```

---

## Health Check Details

### Backend Health Endpoint

**URL:** `http://localhost:8001/health`

**Response:**
```json
{
  "status": "healthy"
}
```

**Health Check Process:**
1. Send GET request to /health
2. If 200 OK → Backend ready
3. If connection refused → Backend not ready, retry
4. If timeout (30s) → Show error, stop startup

### Why Health Checks?

❌ **Without Health Check:**
```
0s:  Backend starts
1s:  Frontend starts
2s:  Frontend makes API call
3s:  Backend still loading... → 502 Error
```

✅ **With Health Check:**
```
0s:  Backend starts
5s:  Backend loading...
8s:  Backend ready! Health check passes
9s:  Frontend starts
10s: Frontend makes API call → Success!
```

---

## Configuration Files

### Backend: run_backend.py
```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8001,  # Fixed port
    log_level="info"
)
```

### Frontend: package.json
```json
{
  "scripts": {
    "dev": "vite --host localhost --port 3000"
  }
}
```

### Environment: .env
```bash
API_PORT=8001
FRONTEND_URL=http://localhost:3000
```

---

## Troubleshooting

### Problem: Backend fails to start

**Symptoms:**
```
Step 3: Waiting for backend to be ready...
Attempt 30/30 - Backend not ready yet...
ERROR: Backend failed to start within 30 seconds!
```

**Solution:**
1. Check `backend_error.log`
2. Common issues:
   - Port 8001 already in use
   - Missing Python dependencies
   - Database connection error
   - Redis not available

**Fix:**
```powershell
# Check port
netstat -ano | findstr "8001"

# Kill process using port
taskkill /PID <pid> /F

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Problem: Frontend fails to start

**Symptoms:**
- Frontend window closes immediately
- Port 3000 not listening

**Solution:**
1. Check if `node_modules` exists
2. Check if port 3000 is free

**Fix:**
```powershell
cd frontend
npm install
npm run dev
```

### Problem: "Script cannot be loaded" (PowerShell)

**Symptoms:**
```
cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
# Run as administrator
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# Then try again
.\start_reims.ps1
```

**Alternative:**
Use the batch file instead:
```bat
start_reims.bat
```

---

## Service Dependencies

### Required Services
```
Backend → Database (SQLite) ✓ Always available (file-based)
Backend → Redis (optional) ⚠ Queue features require this
Backend → MinIO (optional) ⚠ Document storage requires this
Backend → Ollama (optional) ⚠ AI features require this
Frontend → Backend ✓ Must start after backend
```

### Startup Priority
```
Priority 1: Backend (required)
Priority 2: Frontend (required)
Priority 3: Redis (optional)
Priority 4: MinIO (optional)
Priority 5: Ollama (optional)
```

---

## Advanced Usage

### Custom Startup Order

If you need to start services individually:

```powershell
# 1. Start backend
python run_backend.py
# Wait for: "Application startup complete"

# 2. Verify backend
curl http://localhost:8001/health
# Should return: {"status":"healthy"}

# 3. Start frontend
cd frontend
npm run dev
# Wait for: "Local: http://localhost:3000"

# 4. Access application
start http://localhost:3000
```

### Background Startup

To start services in the background:

```powershell
# Backend in background
Start-Process python -ArgumentList "run_backend.py" -WindowStyle Hidden

# Wait
Start-Sleep -Seconds 10

# Frontend in background
cd frontend
Start-Process cmd -ArgumentList "/c npm run dev" -WindowStyle Normal
cd ..
```

---

## Monitoring

### Check Service Status

**PowerShell:**
```powershell
# Check ports
netstat -ano | findstr "3000 8001"

# Check processes
Get-Process python*,node*

# Test backend
curl http://localhost:8001/health

# Test frontend
curl http://localhost:3000
```

**Batch:**
```bat
netstat -ano | findstr "3000 8001"
tasklist | findstr "python node"
```

### View Logs

```powershell
# Backend output
Get-Content backend_startup.log -Tail 20

# Backend errors
Get-Content backend_error.log -Tail 20

# Watch live
Get-Content backend_startup.log -Wait
```

---

## Best Practices

### DO ✅
- Use the unified startup scripts
- Let backend fully start before frontend
- Check health endpoint before proceeding
- Monitor startup logs
- Stop services cleanly with stop scripts

### DON'T ❌
- Start frontend before backend
- Skip health checks in production
- Force kill processes without cleanup
- Start multiple instances
- Ignore startup errors

---

## Quick Reference

### Start
```powershell
.\start_reims.ps1        # PowerShell (recommended)
start_reims.bat          # Batch (alternative)
```

### Stop
```powershell
.\stop_reims.ps1         # PowerShell
stop_reims.bat           # Batch
```

### Status
```powershell
netstat -ano | findstr "3000 8001"
```

### Logs
```
backend_startup.log      # Backend output
backend_error.log        # Backend errors
```

### URLs
```
Frontend:  http://localhost:3000
Backend:   http://localhost:8001
API Docs:  http://localhost:8001/docs
```

---

## Summary

✅ **Startup Order Guaranteed:**
- Backend always starts first
- Health check ensures backend ready
- Frontend starts only after backend confirms healthy
- No failed API calls
- Better user experience

✅ **Scripts Provided:**
- `start_reims.ps1` - Full-featured PowerShell
- `start_reims.bat` - Simple batch file
- `stop_reims.ps1` - Clean shutdown
- `stop_reims.bat` - Simple stop

✅ **Features:**
- Automatic cleanup
- Health checks
- Status verification
- Browser launch
- Detailed logging

**Your REIMS application now has professional startup management!** 🚀

---

**Last Updated:** 2025-10-11 19:15:00  
**Script Version:** 2.0  
**Status:** Production Ready

















