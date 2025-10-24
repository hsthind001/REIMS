# REIMS Startup Guide

Complete guide for starting, stopping, and troubleshooting the REIMS system.

---

## Quick Start (Tomorrow and Every Day)

### Starting REIMS

Open PowerShell in the REIMS project directory (`C:\REIMS_Copy`) and run:

```powershell
.\start-reims.ps1
```

That's it! The script will:
- Check Docker is running
- Start all Docker services with proper dependencies
- Start the backend API
- Start the frontend
- Verify everything is working

### Stopping REIMS

```powershell
.\stop-reims.ps1
```

This will safely shut down all services in the correct order.

---

## Manual Startup (If Needed)

If you prefer to start services manually or the automated script has issues:

### Step 1: Start Docker Services

```powershell
cd C:\REIMS_Copy
docker-compose up -d
```

Wait 30-60 seconds for services to initialize.

### Step 2: Verify Docker Services

```powershell
docker ps
```

You should see 9 running containers:
- `reims-postgres`
- `reims-redis`
- `reims-minio`
- `reims-worker`
- `reims-ollama`
- `reims-prometheus`
- `reims-grafana`
- `reims-nginx`
- `reims-pgadmin`

### Step 3: Start Backend API

```powershell
$env:DATABASE_URL="sqlite:///./reims.db"
python simple_backend.py > backend_output.log 2>&1 &
```

Wait 5 seconds, then verify:

```powershell
curl http://localhost:8001/health
```

Should return: `{"status":"healthy"}`

### Step 4: Start Frontend

Open a new PowerShell terminal:

```powershell
cd C:\REIMS_Copy\frontend
npm run dev
```

The frontend will start on `http://localhost:3001`

---

## Service URLs and Ports

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3001 | Main REIMS UI |
| **Backend API** | http://localhost:8001 | REST API |
| **Grafana** | http://localhost:3000 | Monitoring Dashboard |
| **MinIO Console** | http://localhost:9001 | Object Storage UI |
| **Prometheus** | http://localhost:9090 | Metrics Collection |
| **PgAdmin** | http://localhost:5050 | PostgreSQL Admin |

### Default Credentials

**MinIO:**
- Username: `minioadmin`
- Password: `minioadmin`

**Grafana:**
- Username: `admin`
- Password: `admin123`

**PgAdmin:**
- Email: `admin@example.com`
- Password: `admin123`

---

## Service Dependencies

REIMS services start in this order:

```
1. Base Layer (No dependencies)
   ├── PostgreSQL
   ├── Redis
   ├── MinIO
   ├── Ollama
   └── Prometheus

2. Dependent Services
   ├── Grafana (depends on PostgreSQL)
   ├── PgAdmin (depends on PostgreSQL)
   ├── Worker (depends on Redis, MinIO)
   └── Nginx (depends on Grafana)

3. Application Layer
   ├── Backend API (depends on Redis, MinIO, Worker)
   └── Frontend (depends on Backend API)
```

The `docker-compose.yml` file handles Docker service dependencies automatically.

---

## Verification Steps

### 1. Check Docker Services

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}"
```

All services should show "Up" and "(healthy)" status.

### 2. Check Backend API

```powershell
# Health check
curl http://localhost:8001/health

# Properties endpoint
curl http://localhost:8001/api/properties
```

### 3. Check Worker Service

```powershell
docker logs reims-worker --tail 20
```

Should show: "Listening on document-processing..."

### 4. Check Frontend

Open browser: http://localhost:3001

You should see the REIMS dashboard with 4 properties.

---

## Troubleshooting

### Problem: Docker services won't start

**Solution 1:** Check if Docker Desktop is running
   ```powershell
docker ps
   ```

**Solution 2:** Clean up and restart
   ```powershell
docker-compose down
docker system prune -f
docker-compose up -d
```

### Problem: Backend shows database error

**Error:** `unable to open database file`

**Solution:** Set the environment variable:
   ```powershell
$env:DATABASE_URL="sqlite:///./reims.db"
```

Then restart the backend.

### Problem: Port already in use

**Error:** `Port 8001 is already in use`

**Solution:** Find and kill the process:
   ```powershell
# Find the process
Get-Process python | Stop-Process -Force

# Or for specific port
$port = 8001
$process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if($process) { Stop-Process -Id $process -Force }
```

### Problem: Frontend won't start

**Error:** `Port 3001 is already in use`

**Solution 1:** Kill existing Node process:
   ```powershell
Get-Process node | Stop-Process -Force
   ```

**Solution 2:** Use a different port:
   ```powershell
cd frontend
npm run dev -- --port 3002
   ```

### Problem: Worker service shows errors

**Check worker logs:**
   ```powershell
docker logs reims-worker -f
```

**Common issues:**
- Redis not ready: Wait 30 seconds after docker-compose up
- MinIO not ready: Verify MinIO is healthy with `docker ps`

**Restart worker:**
   ```powershell
docker restart reims-worker
   ```

### Problem: MinIO buckets are missing

**Solution:** Buckets are persistent. If they're missing:
```powershell
docker exec reims-minio /usr/bin/mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec reims-minio /usr/bin/mc ls local
```

If empty, buckets will be recreated on next file upload.

---

## Viewing Logs

### Backend Logs

```powershell
# Real-time logs
Get-Content backend_output.log -Wait

# Last 20 lines
Get-Content backend_output.log -Tail 20
```

### Docker Service Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f reims-worker

# Last 50 lines
docker-compose logs --tail 50 reims-worker
```

### Frontend Logs

The frontend terminal window shows live logs.

---

## Clean Shutdown

Always use the stop script for clean shutdown:

```powershell
.\stop-reims.ps1
```

This ensures:
- Services stop gracefully
- No orphaned processes
- Data is properly saved
- Ports are released

**Never force-close terminals** without stopping services first.

---

## Data Persistence

### What Persists

The following data is preserved across restarts:

- **Database:** `reims.db` (SQLite file in project root)
- **MinIO Storage:** Docker volume `reims_copy_minio_data`
- **PostgreSQL:** Docker volume `reims_copy_postgres_data`
- **Redis:** Docker volume `reims_copy_redis_data`

### What Doesn't Persist

- Running processes (backend, frontend)
- In-memory caches
- Temporary logs

---

## Performance Tips

### First Startup

First startup takes 30-60 seconds for all services to initialize.

### Subsequent Startups

After first run, services start in 10-20 seconds.

### Keep Docker Running

If you use REIMS daily, keep Docker Desktop running to avoid startup delay.

---

## Emergency Reset

If REIMS is completely broken:

### Soft Reset (Keep Data)

```powershell
.\stop-reims.ps1
docker-compose down
docker-compose up -d
.\start-reims.ps1
```

### Hard Reset (Delete Everything)

**⚠️ WARNING: This deletes all data!**

```powershell
.\stop-reims.ps1
docker-compose down -v  # Removes volumes
docker system prune -a -f
docker-compose up -d
.\start-reims.ps1
```

You'll need to re-upload all documents after a hard reset.

---

## System Requirements

- **OS:** Windows 10/11
- **Docker Desktop:** Latest version
- **Python:** 3.11+
- **Node.js:** 18+
- **RAM:** 8GB minimum (16GB recommended)
- **Disk:** 10GB free space

---

## Getting Help

### Check Service Status

```powershell
# Docker services
docker ps

# Backend
curl http://localhost:8001/health

# Worker
docker logs reims-worker --tail 20
```

### Common Commands

```powershell
# Restart specific Docker service
docker restart reims-worker

# Rebuild Docker service
docker-compose up -d --build reims-worker

# View all containers (including stopped)
docker ps -a

# Check disk usage
docker system df
```

---

## Daily Workflow

### Morning Startup

```powershell
cd C:\REIMS_Copy
.\start-reims.ps1
```

### During Work

Access frontend at http://localhost:3001

### Evening Shutdown

```powershell
.\stop-reims.ps1
```

---

## Advanced Configuration

### Environment Variables

Create a `.env` file in project root:

```env
DATABASE_URL=sqlite:///./reims.db
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Custom Ports

Edit `docker-compose.yml` to change Docker service ports.

Edit `frontend/vite.config.js` to change frontend port.

Backend port is set in `simple_backend.py` (line with `uvicorn.run`).

---

## Support

For issues not covered here:

1. Check logs: `backend_output.log` and `docker-compose logs`
2. Verify all services: `docker ps`
3. Try soft reset: `.\stop-reims.ps1` then `.\start-reims.ps1`

---

**Last Updated:** 2025-10-23
**REIMS Version:** 2.1.0
