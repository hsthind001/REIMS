# REIMS Change Persistence Checklist

## Files That Persist Automatically (No Docker Rebuild Needed)

### ✅ Local Files (Always Persist)
- `simple_backend.py` - Backend API (runs locally with Python)
- `frontend/src/**` - All frontend code (runs locally with npm)
- `reims.db` - SQLite database file
- `docker-compose.yml` - Docker configuration

### ✅ Docker-Mounted Files (Persist with Volume Mounts)
- `queue_service/simple_worker.py` - Worker code (mounted)
- `queue_service/document_processor.py` - Processing logic (mounted)

### ⚠️ Data That Persists (Docker Volumes)
- MinIO data - `/data` volume (all uploaded files)
- PostgreSQL data - `postgres_data` volume
- Redis data - `redis_data` volume

---

## Before Shutting Down REIMS

### Step 1: Save All Open Files
- ✅ Ctrl+S or Cmd+S in your editor
- ✅ Verify no unsaved changes indicator

### Step 2: Commit Changes to Git (Recommended)
```powershell
git status  # Check what changed
git add .
git commit -m "Describe your changes here"
```

### Step 3: Document What You Changed
- Update this checklist with new files if needed
- Note any new configuration changes

---

## Starting REIMS (Correct Sequence)

### Step 1: Start Docker Services
```powershell
docker-compose up -d
```

**Wait for services to be healthy (30-60 seconds)**

### Step 2: Start Backend (Local)
```powershell
$env:DATABASE_URL="sqlite:///./reims.db"
python simple_backend.py > backend.log 2>&1 &
```

### Step 3: Start Frontend (Local)
```powershell
cd frontend
npm run dev
```

### Step 4: Verify All Services
```powershell
# Check Docker services
docker ps

# Check backend
curl http://localhost:8001/health

# Check frontend
# Open browser: http://localhost:3001
```

---

## After Restarting (Verification)

### ✅ Verify Your Recent Changes Are Active

**Backend Changes:**
```powershell
# Check if backend has your changes
Get-Content simple_backend.py | Select-String "detect_document_type_from_filename"
```

**Frontend Changes:**
```powershell
# Check if frontend has your changes
Get-Content frontend/src/components/DocumentUploadCenter.jsx | Select-String "detectDocumentType"
```

**Worker Changes:**
```powershell
# Check if worker container sees your code
docker exec reims-worker ls -la /app/queue_service
```

---

## Troubleshooting: Changes Not Applied

### Backend Changes Missing
**Problem:** Old backend still running
**Solution:**
```powershell
Get-Process python | Stop-Process -Force
$env:DATABASE_URL="sqlite:///./reims.db"
python simple_backend.py > backend.log 2>&1 &
```

### Worker Changes Missing
**Problem:** Worker not using mounted code
**Solution:**
```powershell
docker-compose restart worker
docker logs reims-worker --tail 20
```

### Frontend Changes Missing
**Problem:** Browser cache or dev server not restarted
**Solution:**
```powershell
# Hard refresh browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
# Or restart dev server:
cd frontend
npm run dev
```

---

## Key Files and Their Persistence

| File/Directory | Persistence Method | Restart Required? |
|----------------|-------------------|-------------------|
| `simple_backend.py` | Local file | Restart Python process |
| `frontend/src/` | Local file + hot reload | No (auto-reload) |
| `queue_service/` | Volume mount | Restart worker container |
| `docker-compose.yml` | Local file | `docker-compose up -d` |
| `reims.db` | Local file + volume | No |
| MinIO data | Docker volume | No |

---

## Emergency: Restore Lost Changes

### If you have Git commits:
```powershell
git log --oneline -10  # Find your commit
git show <commit-hash>  # View changes
git checkout <commit-hash> -- <file>  # Restore specific file
```

### If no Git commits:
- Check backup files (`.bak`, `~` suffixes)
- Check editor auto-save/recovery
- Review recent log files for clues

---

## Best Practices

1. **Commit Often**: `git commit` after each feature
2. **Use Descriptive Messages**: Explain what changed and why
3. **Test After Restart**: Always verify changes survived restart
4. **Document Custom Configs**: Note any environment variables
5. **Backup Database**: `cp reims.db reims.db.backup` before major changes

---

## Quick Reference Commands

```powershell
# Full REIMS restart
docker-compose down
docker-compose up -d
$env:DATABASE_URL="sqlite:///./reims.db"; python simple_backend.py &
cd frontend; npm run dev

# Quick worker code update (no rebuild)
docker-compose restart worker

# Check what's running
docker ps  # Docker services
Get-Process python  # Backend
netstat -ano | findstr "3001"  # Frontend

# Git safety net
git status
git diff  # See uncommitted changes
git add .
git commit -m "Document type detection improvements"
```

---

## Recent Changes Made

### Document Type Auto-Detection (Implemented)
- ✅ Backend: Added `detect_document_type_from_filename()` function
- ✅ Frontend: Added `detectDocumentType()` function  
- ✅ MinIO: Files now stored in correct folders by document type
- ✅ Volume Mount: Worker container now sees code changes without rebuild

### Files Modified:
- `simple_backend.py` - Document type detection logic
- `frontend/src/components/DocumentUploadCenter.jsx` - Frontend detection
- `docker-compose.yml` - Added queue_service volume mount
- `PERSIST_CHANGES.md` - This checklist (new)

### Test Results:
- ✅ ESP files moved to correct folders
- ✅ Wendover files uploaded to correct folders
- ✅ Document type detection working for all file types
- ✅ MinIO structure: `reims-files/Financial Statements/{YEAR}/{TYPE}/`
