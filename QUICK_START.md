# REIMS Quick Start Guide

## Daily Startup (Recommended)

**Option 1: Automated (Easiest)**
```powershell
.\start_reims_complete.ps1
```

**Option 2: Manual**

```powershell
# 1. Start Docker
docker-compose up -d

# 2. Start Backend
$env:DATABASE_URL="sqlite:///./reims.db"
python simple_backend.py

# 3. Start Frontend (in new terminal)
cd frontend
npm run dev
```

## Verify Everything Works

```powershell
python final_verification.py
```

Expected output: `FINAL QUALITY SCORE: 100/100`

## If Something Goes Wrong

### Backend shows wrong data:

```powershell
# Check database is correct
python final_verification.py

# If database is wrong, fix it
python fix_database_values.py

# Restart backend
Get-Process python | Stop-Process -Force
$env:DATABASE_URL="sqlite:///./reims.db"
python simple_backend.py
```

### Port already in use:

```powershell
# Backend (port 8001)
Get-Process python | Stop-Process -Force

# Frontend (port 3001)
netstat -ano | findstr :3001
taskkill /F /PID <PID>
```

## Important Files

- `simple_backend.py` - Backend API (lines 288-296 critical)
- `reims.db` - SQLite database (contains all data)
- `fix_database_values.py` - Database repair utility
- `final_verification.py` - Quality check tool

## Critical Settings

- **DATABASE_URL:** Must be `sqlite:///./reims.db`
- **Backend Port:** 8001
- **Frontend Port:** 3001
- **Occupancy Rate:** Stored as decimal (0.84 = 84%)
- **Column Index:** occupancy_rate is `row[16]` not `row[15]`
