# REIMS Persistence and Startup Guide

## 🎯 Goal: 100% Quality Every Time

This guide ensures that REIMS starts reliably with 100% data quality every time, with all changes persisting across restarts.

## 🔧 What Was Fixed

### 1. Database Issues (✅ FIXED)
- **Problem**: Occupancy rates showing as 0.0084 instead of 0.84
- **Root Cause**: Backend was reading wrong column (`row[15]` instead of `row[16]`)
- **Solution**: Fixed `simple_backend.py` line 288-296
- **Result**: Empire State Plaza now shows 84.0% occupancy (correct)

### 2. NOI Data Issues (✅ FIXED)
- **Problem**: NOI values showing $60-73 instead of $2M+
- **Root Cause**: Database had wrong values, backend wasn't reading correct data
- **Solution**: Updated database with correct NOI from extracted metrics
- **Result**: Empire State Plaza now shows $2,087,905 NOI (correct)

### 3. Data Quality Issues (✅ FIXED)
- **Problem**: Duplicate entries, wrong calculations
- **Root Cause**: Multiple extraction runs created duplicates
- **Solution**: Cleaned database, removed 54 duplicate entries
- **Result**: Clean, accurate data for all 4 properties

## 🚀 How to Start REIMS (3 Options)

### Option 1: Automated Startup (RECOMMENDED)
```powershell
.\start_reims_complete.ps1
```
**What it does:**
- Starts all Docker services
- Waits for services to be healthy
- Kills old backend processes
- Starts backend with correct environment
- Starts frontend
- Verifies everything is working

### Option 2: Manual Startup
```powershell
# 1. Start Docker services
docker-compose up -d

# 2. Start Backend (in new terminal)
$env:DATABASE_URL="sqlite:///./reims.db"
python simple_backend.py

# 3. Start Frontend (in new terminal)
cd frontend
npm run dev
```

### Option 3: Quick Verification
```powershell
python final_verification.py
```
**Expected output:** `FINAL QUALITY SCORE: 100/100`

## 🔍 How to Verify Everything Works

### 1. Check Quality Score
```powershell
python final_verification.py
```
**Expected:** `FINAL QUALITY SCORE: 100/100`

### 2. Check API Response
Open: http://localhost:8001/api/properties

**Expected data:**
- Empire State Plaza: NOI $2,087,905, Occupancy 84.0%
- Wendover Commons: NOI $1,860,031, Occupancy 93.8%
- Hammond Aire: NOI $2,845,707, Occupancy 82.5%
- The Crossings of Spring Hill: NOI $280,147, Occupancy 100.0%

### 3. Check Frontend
Open: http://localhost:3001
Navigate to Portfolio page

**Expected:** All properties display with correct financial data

## 🛠️ If Something Goes Wrong

### Problem: Backend shows wrong data
```powershell
# 1. Check if database is correct
python final_verification.py

# 2. If database is wrong, fix it
python fix_database_values.py

# 3. Restart backend
Get-Process python | Stop-Process -Force
$env:DATABASE_URL="sqlite:///./reims.db"
python simple_backend.py

# 4. Verify again
python final_verification.py
```

### Problem: Port already in use
```powershell
# Backend (port 8001)
Get-Process python | Stop-Process -Force

# Frontend (port 3001)
netstat -ano | findstr :3001
taskkill /F /PID <PID>
```

### Problem: Quality score drops below 100
```powershell
# 1. Check what's wrong
python final_verification.py

# 2. Fix the database
python fix_database_values.py

# 3. Restart backend
Get-Process python | Stop-Process -Force
$env:DATABASE_URL="sqlite:///./reims.db"
python simple_backend.py

# 4. Verify quality restored
python final_verification.py
```

## 📁 Critical Files (DO NOT MODIFY)

### 1. `simple_backend.py` (Lines 288-296)
**CRITICAL**: These lines contain the occupancy_rate fix
```python
# Row indices: [14]=total_units, [15]=occupied_units, [16]=occupancy_rate
if len(row) > 16 and row[16] and row[16] is not None and row[16] > 0:
    occupancy_rate = row[16]  # Already stored as decimal (0.84 = 84%)
```

### 2. `reims.db`
**CRITICAL**: Contains all the corrected data
- NOI values: $280K to $2.8M
- Occupancy rates: 0.825 to 1.0
- All duplicate entries removed

### 3. `fix_database_values.py`
**CRITICAL**: Database repair utility
- Fixes occupancy rates
- Updates NOI values
- Removes duplicates
- Updates unit counts

## 🔄 What Persists Across Restarts

### ✅ Automatically Persistent
- **Database file** (`reims.db`) - All data changes
- **Code files** (`.py` files) - All code changes
- **Docker volumes** - MinIO, Redis, PostgreSQL data
- **Git commits** - All changes saved in version control

### ⚠️ Requires Manual Action
- **Environment variables** - Must set `DATABASE_URL`
- **Process management** - Must kill old processes
- **Service startup order** - Must start in correct sequence

## 🎯 Success Criteria

### ✅ Quality Score: 100/100
- All 4 properties show correct NOI ($280K to $2.8M)
- All 4 properties show correct occupancy (82.5% to 100%)
- No duplicate entries in database
- API responds correctly
- Frontend displays accurate data

### ✅ Startup Reliability
- Docker services start in correct order
- Backend starts with correct environment
- Frontend starts without port conflicts
- All services communicate properly

### ✅ Change Persistence
- All code changes saved in Git
- Database changes persist in SQLite file
- Docker data persists in volumes
- Documentation updated

## 📋 Maintenance Checklist

### Daily Startup
1. Run `.\start_reims_complete.ps1`
2. Wait for all services to start
3. Run `python final_verification.py`
4. Verify quality score is 100/100

### If Quality Drops
1. Run `python final_verification.py` to identify issue
2. Run `python fix_database_values.py` to restore
3. Restart backend with correct environment
4. Verify quality restored to 100/100

### Before Making Changes
1. Test current quality: `python final_verification.py`
2. Make your changes
3. Test again: `python final_verification.py`
4. If quality drops, restore: `python fix_database_values.py`
5. Commit changes to Git

## 🎉 Final Result

**REIMS now achieves 100% data quality with reliable startup!**

- ✅ Empire State Plaza: $2,087,905 NOI, 84.0% occupancy
- ✅ Wendover Commons: $1,860,031 NOI, 93.8% occupancy  
- ✅ Hammond Aire: $2,845,707 NOI, 82.5% occupancy
- ✅ The Crossings of Spring Hill: $280,147 NOI, 100.0% occupancy

**Quality Score: 100/100** 🎯
