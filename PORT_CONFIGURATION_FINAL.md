# 🔧 REIMS Port Configuration (FINAL)

**Last Updated:** 2025-10-12  
**Status:** ✅ **PERMANENTLY FIXED**

---

## 📊 Port Assignments

| Service | Port | URL | Status |
|---------|------|-----|--------|
| **Frontend** | **3001** | `http://localhost:3001` | ✅ FIXED |
| **Backend** | **8001** | `http://localhost:8001` | ✅ FIXED |
| PostgreSQL | 5432 | `localhost:5432` | ✅ Active |
| Redis | 6379 | `localhost:6379` | ✅ Active |
| MinIO API | 9000 | `http://localhost:9000` | ✅ Active |
| MinIO Console | 9001 | `http://localhost:9001` | ✅ Active |
| Prometheus | 9090 | `http://localhost:9090` | ✅ Active |
| Grafana | 3000 | `http://localhost:3000` | ⚠️ Conflicts |
| Ollama | 11434 | `http://localhost:11434` | ✅ Active |

---

## 🎯 PRIMARY URLS

### **Frontend (React + Vite)**
- **URL:** `http://localhost:3001`
- **Config Files:**
  - `frontend/vite.config.js` → `port: 3001, strictPort: true`
  - `frontend/package.json` → `"dev": "vite --host localhost --port 3001"`
- **Why 3001?** Port 3000 is used by Grafana

### **Backend (FastAPI)**
- **URL:** `http://localhost:8001`
- **Config Files:**
  - `run_backend.py` → `port=8001`
- **API Docs:** `http://localhost:8001/docs`
- **Health Check:** `http://localhost:8001/health`

---

## 🔄 CORS Configuration

Backend allows these origins:

```python
allow_origins=[
    "http://localhost:3001",  # ← PRIMARY frontend port
    "http://localhost:3000",  # Alternative
    "http://localhost:5173",  # Alternative
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173"
]
```

**File:** `backend/api/main.py` (lines 50-59)

---

## 🚀 How to Start Services

### **Start Backend (Port 8001)**
```bash
python run_backend.py
```

Expected output:
```
✅ Connected to PostgreSQL database (or SQLite fallback)
Starting REIMS Backend Server on http://localhost:8001
```

### **Start Frontend (Port 3001)**
```bash
cd frontend
npm run dev
```

Expected output:
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:3001/
```

---

## ✅ Verification Tests

### **1. Backend Health Check**
```bash
curl http://localhost:8001/health
```
Expected: `{"status":"healthy"}`

### **2. Backend API Docs**
Open in browser: `http://localhost:8001/docs`

### **3. Backend Analytics**
```bash
curl http://localhost:8001/api/analytics
```
Expected: JSON with portfolio data

### **4. Frontend Access**
Open in browser: `http://localhost:3001`

---

## 📝 Files Modified

### **Frontend Configuration**
1. ✅ `frontend/vite.config.js`
   - Changed `port: 3000` → `port: 3001`
   - Changed `strictPort: false` → `strictPort: true`

2. ✅ `frontend/package.json`
   - Changed `"dev": "vite --host localhost --port 3000"`
   - To: `"dev": "vite --host localhost --port 3001"`

3. ✅ `frontend/src/api/client.js`
   - Already configured: `baseURL: 'http://localhost:8001'`

### **Backend Configuration**
1. ✅ `backend/api/main.py`
   - Added `http://localhost:3001` to CORS origins (line 53)

2. ✅ `run_backend.py`
   - Already configured: `port=8001`

3. ✅ Created `backend/api/database.py`
   - Database session management
   - PostgreSQL with SQLite fallback

4. ✅ Created/Updated `backend/api/dependencies.py`
   - Redis and MinIO dependency injection

---

## ⚠️ Common Issues & Solutions

### **Issue 1: Frontend says "Port 3001 is in use"**
**Solution:**
```bash
# Kill process on port 3001
netstat -ano | findstr :3001
taskkill /PID <PID> /F
```

### **Issue 2: Backend says "Port 8001 is in use"**
**Solution:**
```bash
# Kill process on port 8001
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

### **Issue 3: Backend shows "Internal Server Error" on /api/analytics**
**Cause:** Database tables don't exist

**Solution:** Run migrations
```bash
cd backend/db/migrations
psql -U postgres -d reims -f 001_create_properties.sql
psql -U postgres -d reims -f 002_create_stores.sql
# ... etc
```

Or use SQLite (automatic fallback):
- Backend will use `reims.db` file
- Tables created automatically

### **Issue 4: CORS errors in browser console**
**Check:**
1. Backend CORS includes `http://localhost:3001` ✅
2. Frontend API client uses `http://localhost:8001` ✅
3. No trailing slashes in URLs ✅

---

## 🎯 Quick Start Commands

```bash
# Terminal 1: Start Backend
python run_backend.py

# Terminal 2: Start Frontend
cd frontend && npm run dev

# Terminal 3: Test Everything
curl http://localhost:8001/health
curl http://localhost:8001/api/analytics
start http://localhost:3001
start http://localhost:8001/docs
```

---

## 📊 Port Usage Summary

```
Frontend (React):    3001 ← USER INTERFACE
Backend (FastAPI):   8001 ← API SERVER
Grafana:             3000 ← MONITORING DASHBOARDS
PostgreSQL:          5432 ← DATABASE
Redis:               6379 ← CACHE & QUEUE
MinIO:               9000 ← OBJECT STORAGE API
MinIO Console:       9001 ← STORAGE WEB UI
Prometheus:          9090 ← METRICS
Ollama:             11434 ← AI/ML
```

---

## 🔐 Environment Variables

### **Frontend (.env file)**
```env
VITE_API_URL=http://localhost:8001
```

### **Backend (system environment or .env)**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/reims
REDIS_HOST=localhost
REDIS_PORT=6379
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

---

## ✅ Verification Checklist

- [x] Frontend runs on port **3001** (fixed in vite.config.js)
- [x] Backend runs on port **8001** (fixed in run_backend.py)
- [x] CORS allows port **3001** (added to main.py)
- [x] API client targets port **8001** (already configured)
- [x] Documentation updated (this file + others)
- [x] Database module created (database.py)
- [x] Dependencies module created (dependencies.py)
- [x] Backend imports successfully
- [x] Health endpoint works ✅
- [x] API docs accessible ✅

---

**Status:** 🟢 **PORTS PERMANENTLY FIXED**

**Next Steps:**
1. Run database migrations (if using PostgreSQL)
2. Start both services
3. Open `http://localhost:3001` in browser
4. Verify KPIs load correctly

---

**Note:** These port configurations are now **hardcoded** with `strictPort: true` to prevent future conflicts.

