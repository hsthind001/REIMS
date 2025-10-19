# 🚀 REIMS Quick Start Guide - Fixed Ports

**Status:** ✅ Ports Permanently Fixed  
**Date:** 2025-10-12

---

## 🎯 Port Configuration

| Service | Port | URL |
|---------|------|-----|
| **Frontend** | **3001** | `http://localhost:3001` |
| **Backend** | **8001** | `http://localhost:8001` |

**These ports are now HARDCODED and will NOT change.**

---

## ⚡ Quick Start (Fastest)

### Option 1: Use Startup Script

```powershell
.\start_reims_fixed_ports.ps1
```

This script will:
- ✅ Check if ports are available
- ✅ Kill any processes using those ports
- ✅ Start backend on port 8001
- ✅ Start frontend on port 3001
- ✅ Open browser tabs automatically

---

### Option 2: Manual Start

**Terminal 1 (Backend):**
```bash
python run_backend.py
```

Expected output:
```
✅ Connected to PostgreSQL database
Starting REIMS Backend Server on http://localhost:8001
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Expected output:
```
VITE ready in XXX ms
➜ Local: http://localhost:3001/
```

---

## ✅ Verification

### 1. Test Backend

```bash
# Health check
curl http://localhost:8001/health
# Expected: {"status":"healthy"}

# API documentation
start http://localhost:8001/docs
```

### 2. Test Frontend

```bash
# Open in browser
start http://localhost:3001
```

---

## 🔧 Troubleshooting

### Problem: "Port 3001 is already in use"

**Solution:**
```powershell
# Find process using port 3001
netstat -ano | findstr :3001

# Kill the process (replace <PID> with actual PID)
taskkill /PID <PID> /F
```

### Problem: "Port 8001 is already in use"

**Solution:**
```powershell
# Find process using port 8001
netstat -ano | findstr :8001

# Kill the process
taskkill /PID <PID> /F
```

### Problem: Backend shows "Internal Server Error"

**Possible Causes:**
1. Database tables don't exist
2. PostgreSQL not running (backend will fallback to SQLite automatically)

**Solution:**
- Backend will automatically use SQLite (`reims.db`) if PostgreSQL is unavailable
- For PostgreSQL: Run migrations in `backend/db/migrations/`

### Problem: CORS errors in browser

**Check:**
1. ✅ Frontend is on `http://localhost:3001`
2. ✅ Backend is on `http://localhost:8001`
3. ✅ No typos in API calls

**CORS is already configured for port 3001 in `backend/api/main.py`**

---

## 📊 What You Should See

### Backend Console:
```
Using SQLite database (or PostgreSQL)
INFO:document_processor_integration:Processed data table initialized
INFO:queue_manager:Connected to Redis successfully
Starting REIMS Backend Server on http://localhost:8001
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Frontend Console:
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:3001/
➜  Network: use --host to expose
```

### Browser (http://localhost:3001):
- Dashboard with KPI cards
- Portfolio value, properties count, etc.
- No CORS errors in console

---

## 🌐 Important URLs

```
Frontend:       http://localhost:3001
API Docs:       http://localhost:8001/docs
Health Check:   http://localhost:8001/health
Analytics:      http://localhost:8001/api/analytics
Properties:     http://localhost:8001/api/properties
Alerts:         http://localhost:8001/api/alerts
```

---

## 📁 Configuration Files

All port configurations have been updated in:

1. ✅ `frontend/vite.config.js` → port 3001, strictPort: true
2. ✅ `frontend/package.json` → scripts use port 3001
3. ✅ `backend/api/main.py` → CORS allows port 3001
4. ✅ `run_backend.py` → uses port 8001

---

## 🔄 Restart Services

### Stop Everything:
- Close the PowerShell windows or press `Ctrl+C` in each terminal

### Start Again:
```powershell
.\start_reims_fixed_ports.ps1
```

---

## ✅ Checklist

Before reporting issues, verify:

- [ ] Backend is running (check Terminal 1)
- [ ] Frontend is running (check Terminal 2)
- [ ] No port conflicts (ports 3001 and 8001 are free)
- [ ] Browser can access `http://localhost:3001`
- [ ] Health check works: `curl http://localhost:8001/health`
- [ ] No CORS errors in browser console

---

## 📚 More Information

- **Full URL Reference:** `REIMS_URL_REFERENCE.md`
- **Port Configuration:** `PORT_CONFIGURATION_FINAL.md`
- **Backend Endpoints:** `BACKEND_ENDPOINTS_COMPLETE.md`
- **Frontend Features:** `COMPLETE_FRONTEND_FEATURES_SUMMARY.md`

---

**Status:** 🟢 Ready to Use

**Next Steps:**
1. Run `.\start_reims_fixed_ports.ps1`
2. Open `http://localhost:3001` in browser
3. Explore the dashboard!

