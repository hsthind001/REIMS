# REIMS Ports & Services Status Report

**Generated:** 2025-10-12  
**Status Check:** Complete ✅

---

## 🎯 Executive Summary

**System Status:** ⚠️ **ISSUES FOUND** - Backend not running, Port conflict detected

### Critical Issues
1. 🔴 **Backend API not running** (Port 8001)
2. 🟡 **Port 3000 conflict** - Grafana is using the frontend port
3. 🟡 **Ollama unhealthy** (AI service degraded)
4. 🟡 **Nginx unhealthy** (Reverse proxy degraded)

### Infrastructure Health
- ✅ PostgreSQL, Redis, MinIO, Prometheus: All healthy
- ✅ Storage systems: Functional
- ⚠️ AI/LLM services: Degraded

---

## 📊 Port Status Overview

| Port | Service | Status | Process | Docker Container |
|------|---------|--------|---------|------------------|
| **80** | Nginx HTTP | ⚠️ Unhealthy | wslrelay | reims-nginx |
| **443** | Nginx HTTPS | ⚠️ Unhealthy | wslrelay | reims-nginx |
| **3000** | **Grafana** | ✅ Running | wslrelay | reims-grafana |
| **3000** | ~~Frontend~~ | ❌ **CONFLICT** | - | - |
| **5432** | PostgreSQL | ✅ Healthy | postgres | reims-postgres |
| **6379** | Redis | ✅ Healthy | wslrelay | reims-redis |
| **8001** | Backend API | ❌ Not Running | - | - |
| **9000** | MinIO API | ✅ Healthy | wslrelay | reims-minio |
| **9001** | MinIO Console | ✅ Healthy | wslrelay | reims-minio |
| **9090** | Prometheus | ✅ Healthy | wslrelay | reims-prometheus |
| **11434** | Ollama | ⚠️ Unhealthy | wslrelay | reims-ollama |

---

## 🔍 Detailed Service Status

### 1. Backend API (FastAPI) ❌
```
Port:           8001
Status:         NOT RUNNING
Expected:       Python/Uvicorn process
Health Check:   http://localhost:8001/health
API Docs:       http://localhost:8001/docs
```

**Issue:** Backend server is not started

**Impact:**
- Frontend cannot connect to API
- No document upload functionality
- No analytics or KPI data
- No AI processing capabilities

**Solution:**
```bash
# Start backend
python run_backend.py
```

---

### 2. Frontend (React + Vite) ⚠️
```
Configured Port: 3000
Status:          PORT CONFLICT
Blocker:         Grafana is using port 3000
Expected:        Node/Vite dev server
URL:             http://localhost:3000 (currently Grafana)
```

**Issue:** Grafana Docker container is occupying port 3000

**Impact:**
- Frontend cannot start on configured port 3000
- Need to either:
  - Move Frontend to different port (e.g., 3001, 5173)
  - Move Grafana to different port (e.g., 3001)
  - Stop Grafana if not needed

**Solutions:**

**Option A: Run Frontend on Port 5173 (Vite Default)**
```bash
cd frontend
npm run dev -- --port 5173
```
Update API client to accept frontend on 5173:
```javascript
// backend/api/main.py - Already configured!
allow_origins=[
    "http://localhost:3000",
    "http://localhost:5173",  // ✅ Already included
]
```

**Option B: Move Grafana to Different Port**
```yaml
# docker-compose.yml
services:
  grafana:
    ports:
      - "3001:3000"  # Map to 3001 instead
```

**Option C: Stop Grafana (if not needed)**
```bash
docker stop reims-grafana
```

---

### 3. PostgreSQL ✅
```
Port:           5432
Status:         RUNNING & HEALTHY
Container:      reims-postgres
Uptime:         49 minutes
Health:         ✅ Healthy
Connection:     postgres://reims_user@localhost:5432/reims_db
```

**Status:** ✅ **OPERATIONAL**

**Details:**
- 10 PostgreSQL processes running
- Docker container healthy
- Accessible on localhost:5432
- Database: `reims_db`
- User: `reims_user`

**Test Connection:**
```bash
psql -h localhost -p 5432 -U reims_user -d reims_db
# Password: reims_password
```

---

### 4. Redis ✅
```
Port:           6379
Status:         RUNNING & HEALTHY
Container:      reims-redis
Uptime:         49 minutes
Health:         ✅ Healthy
```

**Status:** ✅ **OPERATIONAL**

**Usage:**
- Caching layer
- Celery message broker
- Session storage
- Queue backend

**Test Connection:**
```bash
redis-cli -h localhost -p 6379 ping
# Expected: PONG
```

---

### 5. MinIO (Object Storage) ✅
```
Port:           9000 (API), 9001 (Console)
Status:         RUNNING & HEALTHY
Container:      reims-minio
Uptime:         49 minutes
Health:         ✅ Healthy
API:            http://localhost:9000
Console:        http://localhost:9001
```

**Status:** ✅ **OPERATIONAL**

**Details:**
- Storage: 0.06 MB used
- Accessible via HTTP
- Console available for management
- Health endpoint responding

**Access:**
```
API:            http://localhost:9000
Console:        http://localhost:9001
Username:       minioadmin
Password:       minioadmin
```

**Test:**
```bash
curl http://localhost:9000/minio/health/live
# Expected: HTTP 200
```

---

### 6. Ollama (AI/LLM) ⚠️
```
Port:           11434
Status:         RUNNING but UNHEALTHY
Container:      reims-ollama
Uptime:         49 minutes
Health:         ⚠️ Unhealthy
API:            http://localhost:11434
```

**Status:** ⚠️ **DEGRADED**

**Issue:** Container reports unhealthy status

**Impact:**
- AI document processing may fail
- LLM-powered features unavailable
- Market intelligence analysis unavailable
- Tenant recommendations unavailable

**Diagnosis:**
```bash
# Check container logs
docker logs reims-ollama --tail 50

# Check container health
docker inspect reims-ollama | jq '.[0].State.Health'

# Test API
curl http://localhost:11434/api/tags
```

**Possible Causes:**
1. Ollama still initializing (can take time)
2. Insufficient memory
3. No models downloaded
4. Health check configuration issue

**Solutions:**
```bash
# Pull required models
docker exec reims-ollama ollama pull llama2
docker exec reims-ollama ollama pull mistral

# Restart container
docker restart reims-ollama

# Check available models
curl http://localhost:11434/api/tags
```

---

### 7. Prometheus (Monitoring) ✅
```
Port:           9090
Status:         RUNNING & HEALTHY
Container:      reims-prometheus
Uptime:         49 minutes
Health:         ✅ Healthy
URL:            http://localhost:9090
```

**Status:** ✅ **OPERATIONAL**

**Access:**
- Dashboard: http://localhost:9090
- Health: http://localhost:9090/-/healthy
- Metrics: http://localhost:9090/metrics

**Monitoring:**
- System metrics collection
- Performance monitoring
- Service health tracking

---

### 8. Grafana (Visualization) ✅
```
Port:           3000
Status:         RUNNING & HEALTHY
Container:      reims-grafana
Uptime:         49 minutes
Health:         ✅ Healthy
URL:            http://localhost:3000
```

**Status:** ✅ **OPERATIONAL** (but blocking frontend port)

**Issue:** Using port 3000 which frontend needs

**Access:**
- Dashboard: http://localhost:3000
- Default login: admin/admin

**Note:** Consider moving to port 3001 to free up 3000 for frontend

---

### 9. Nginx (Reverse Proxy) ⚠️
```
Ports:          80 (HTTP), 443 (HTTPS)
Status:         RUNNING but UNHEALTHY
Container:      reims-nginx
Uptime:         49 minutes
Health:         ⚠️ Unhealthy
```

**Status:** ⚠️ **DEGRADED**

**Issue:** Container reports unhealthy status

**Impact:**
- Reverse proxy may not be routing correctly
- SSL/TLS termination may not work
- Load balancing unavailable

**Diagnosis:**
```bash
# Check logs
docker logs reims-nginx --tail 50

# Test HTTP
curl http://localhost:80

# Check configuration
docker exec reims-nginx nginx -t
```

**Common Issues:**
1. Upstream services not available (backend on 8001 not running!)
2. Configuration syntax error
3. SSL certificate issues
4. Health check expecting backend to respond

---

## 💾 Storage Status

### SQLite Database
```
Location:       C:\REIMS\reims.db
Size:           0.34 MB
Status:         ✅ EXISTS
```

**Contents:**
- Local development database
- May contain test data
- Used as fallback when PostgreSQL unavailable

### MinIO Object Storage
```
Location:       C:\REIMS\minio-data\
Size:           0.06 MB
Status:         ✅ EXISTS
Buckets:        Initialized
```

**Contents:**
- Document uploads
- Processed files
- Backup data

### Uploads Folder
```
Location:       C:\REIMS\uploads\
Files:          0
Status:         ✅ EXISTS (empty)
```

**Purpose:**
- Temporary upload staging
- Currently empty (no uploads yet)

---

## 🔧 Action Plan

### Immediate Actions (Critical)

#### 1. Start Backend API ⚠️ REQUIRED
```bash
# Navigate to project root
cd C:\REIMS

# Start backend
python run_backend.py
```

**Expected Result:**
- Backend starts on port 8001
- Health check responds at http://localhost:8001/health
- API docs available at http://localhost:8001/docs

#### 2. Resolve Frontend Port Conflict ⚠️ REQUIRED

**Choose ONE of these solutions:**

**Solution A: Run Frontend on Port 5173**
```bash
cd C:\REIMS\frontend
npm run dev -- --port 5173
```
Then access: http://localhost:5173

**Solution B: Move Grafana to Port 3001**
```bash
# Stop Grafana
docker stop reims-grafana

# Edit docker-compose.yml to change Grafana port to 3001
# Restart Grafana
docker start reims-grafana

# Now start frontend on 3000
cd frontend
npm run dev
```

**Solution C: Stop Grafana (if not needed)**
```bash
docker stop reims-grafana
cd frontend
npm run dev
```

**Recommendation:** Use Solution A (port 5173) - quickest and safest.

---

### Secondary Actions (Important)

#### 3. Fix Ollama Health
```bash
# Check logs
docker logs reims-ollama

# Pull required models
docker exec reims-ollama ollama pull llama2
docker exec reims-ollama ollama pull mistral

# Restart
docker restart reims-ollama

# Wait 2-3 minutes for initialization
# Check health again
docker ps | grep ollama
```

#### 4. Fix Nginx Health
```bash
# Nginx is likely failing because backend (8001) isn't running
# After starting backend, restart nginx
docker restart reims-nginx

# Verify configuration
docker exec reims-nginx nginx -t
```

---

### Verification Steps

After completing actions above:

```bash
# 1. Check all ports
Get-NetTCPConnection -LocalPort 3000,5173,8001,5432,6379,9000,11434 -State Listen

# 2. Test backend
curl http://localhost:8001/health

# 3. Test frontend
curl http://localhost:5173  # or 3000 if Grafana moved

# 4. Check Docker containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 5. Run full system check
.\check_reims_status.ps1
```

---

## 📋 Quick Reference

### Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **Backend API** | http://localhost:8001 | - |
| **Backend Docs** | http://localhost:8001/docs | - |
| **Frontend** | http://localhost:5173 (recommended) | - |
| **Grafana** | http://localhost:3000 | admin/admin |
| **MinIO Console** | http://localhost:9001 | minioadmin/minioadmin |
| **Prometheus** | http://localhost:9090 | - |
| **Nginx** | http://localhost:80 | - |

### Database Connections

**PostgreSQL:**
```
Host:     localhost
Port:     5432
Database: reims_db
User:     reims_user
Password: reims_password
```

**Redis:**
```
Host: localhost
Port: 6379
Password: (none)
```

**SQLite:**
```
Path: C:\REIMS\reims.db
```

### Common Commands

```bash
# Start everything
.\start_reims.ps1

# Stop everything
.\stop_reims.ps1

# Check status
.\check_reims_status.ps1

# Start backend only
python run_backend.py

# Start frontend only
cd frontend && npm run dev

# View Docker containers
docker ps

# View Docker logs
docker logs <container-name>

# Restart a container
docker restart <container-name>

# Stop a container
docker stop <container-name>
```

---

## 🚨 Important Notes

### Port 3000 Conflict

**Current Situation:**
- Grafana (Docker) is using port 3000
- Frontend is configured for port 3000
- **They cannot both run on the same port**

**Options:**
1. ✅ **Recommended:** Run frontend on port 5173 (CORS already configured)
2. Move Grafana to different port
3. Stop Grafana if not needed for monitoring

### Backend API Required

**The backend MUST be running for the system to work:**
- Frontend needs backend API for all data
- Document upload requires backend
- Analytics requires backend
- All features require backend

**Start it now:**
```bash
python run_backend.py
```

### Docker Services

**All infrastructure services are running via Docker:**
- PostgreSQL, Redis, MinIO, Prometheus, Grafana, Ollama, Nginx
- Managed via `docker-compose.yml`
- Use Docker commands to manage them

**Check Docker status:**
```bash
docker ps
docker-compose ps
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    REIMS System Architecture                │
└─────────────────────────────────────────────────────────────┘

                          Internet
                             │
                             ▼
                    ┌─────────────────┐
                    │  Nginx (80/443) │  ⚠️ Unhealthy
                    │  Reverse Proxy  │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   ┌────────────┐   ┌──────────────┐   ┌──────────────┐
   │  Frontend  │   │  Backend API │   │   Grafana    │
   │ (Port ???) │   │  (Port 8001) │   │  (Port 3000) │
   │            │   │              │   │              │
   │ React/Vite │   │   FastAPI    │   │ Monitoring   │
   │            │   │   Uvicorn    │   │  Dashboard   │
   └────────────┘   └──────┬───────┘   └──────────────┘
     ❌ Blocked        ❌ Not Running      ✅ Running

                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
   ┌────────────┐   ┌────────────┐   ┌────────────┐
   │ PostgreSQL │   │   Redis    │   │   MinIO    │
   │ (Port 5432)│   │ (Port 6379)│   │ (Port 9000)│
   │            │   │            │   │            │
   │  Database  │   │   Cache    │   │  Storage   │
   └────────────┘   └────────────┘   └────────────┘
     ✅ Healthy       ✅ Healthy       ✅ Healthy

          │                │
          ▼                ▼
   ┌────────────┐   ┌────────────┐
   │  Ollama    │   │Prometheus  │
   │(Port 11434)│   │(Port 9090) │
   │            │   │            │
   │   AI/LLM   │   │ Monitoring │
   └────────────┘   └────────────┘
   ⚠️ Unhealthy      ✅ Healthy
```

---

## ✅ Next Steps

1. **Start Backend API** (CRITICAL)
   ```bash
   python run_backend.py
   ```

2. **Start Frontend on Port 5173** (RECOMMENDED)
   ```bash
   cd frontend
   npm run dev -- --port 5173
   ```

3. **Update API client config** (if needed)
   ```env
   # frontend/.env
   VITE_API_URL=http://localhost:8001
   ```

4. **Fix Ollama** (for AI features)
   ```bash
   docker exec reims-ollama ollama pull llama2
   docker restart reims-ollama
   ```

5. **Verify Everything**
   ```bash
   curl http://localhost:8001/health
   curl http://localhost:5173
   ```

---

**Status:** 📋 Action plan ready  
**Priority:** 🔴 Critical - Backend and Frontend need to start  
**Last Updated:** 2025-10-12

