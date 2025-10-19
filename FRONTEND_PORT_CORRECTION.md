# ✅ Frontend Port Correction

**Date:** October 11, 2025  
**Status:** ✅ **CORRECTED**

---

## 🎯 Important: Frontend URL Changed

### ❌ OLD URL (Don't use):
```
http://localhost:5173/
```
*This was the default Vite port but is NO LONGER USED*

### ✅ NEW URL (Use this):
```
http://localhost:3000/
```
*This is the configured REIMS frontend port*

---

## 📝 What Changed

### Port Configuration

The frontend has been reconfigured to use **port 3000** instead of the default Vite port (5173).

**File:** `frontend/package.json`
```json
{
  "scripts": {
    "dev": "vite --host localhost --port 3000",
    "preview": "vite preview --port 3000"
  }
}
```

### Why Port 3000?

1. **Consistency:** Matches common React dev server port
2. **CORS Configuration:** Backend CORS is configured for port 3000
3. **Documentation:** All documentation references port 3000
4. **Startup Scripts:** Automated scripts expect port 3000

---

## 🚀 How to Access REIMS

### Automatic (Recommended)

1. **Start REIMS:**
   ```batch
   .\start_reims.bat
   ```
   or
   ```powershell
   .\start_reims.ps1
   ```

2. **Browser opens automatically to:**
   ```
   http://localhost:3000
   ```

### Manual

1. **Start services** (if not running)

2. **Open browser to:**
   ```
   http://localhost:3000
   ```

---

## 🌐 All REIMS URLs

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | http://localhost:3000 | ✅ Active |
| **Backend API** | http://localhost:8001 | ✅ Active |
| **API Docs** | http://localhost:8001/docs | ✅ Active |
| **MinIO Console** | http://localhost:9001 | Optional |

---

## ⚠️ If You Bookmarked Port 5173

### Update Your Bookmarks

**Old bookmark:**
```
http://localhost:5173/
```

**New bookmark:**
```
http://localhost:3000/
```

### Clear Browser Cache

If you're seeing issues:
1. Press `Ctrl + Shift + Delete`
2. Clear cached images and files
3. Close and reopen browser
4. Navigate to `http://localhost:3000`

---

## 🔧 Backend CORS Configuration

The backend is configured to accept requests from port 3000:

**File:** `backend/api/main.py`
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # ✓ Configured
        "http://127.0.0.1:3000",  # ✓ Configured
        # Port 5173 is NOT in the list
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

If you try to access from port 5173, you'll get CORS errors.

---

## 🔍 Verification

### Check What's Running

```powershell
# Check port 3000 (should be running)
Get-NetTCPConnection -LocalPort 3000

# Check port 5173 (should be empty)
Get-NetTCPConnection -LocalPort 5173
```

### Test Frontend

```powershell
# Test if frontend is accessible
curl http://localhost:3000
```

### Current Status

```
✓ Backend:  http://localhost:8001  (Running)
✓ Frontend: http://localhost:3000  (Running)
✗ Port 5173: (Not used)
```

---

## 📱 Mobile/Network Access

If you need to access from another device on your network:

1. **Find your IP:**
   ```powershell
   ipconfig
   # Look for IPv4 Address
   ```

2. **Update Vite config** (if needed):
   ```json
   "dev": "vite --host 0.0.0.0 --port 3000"
   ```

3. **Access from other device:**
   ```
   http://YOUR_IP:3000
   ```

---

## 🐛 Troubleshooting

### Frontend Not Loading at Port 3000

**Check if it's running:**
```powershell
Get-NetTCPConnection -LocalPort 3000
```

**If not running, start it:**
```powershell
.\start_reims.bat
```

### Still Trying to Access Port 5173?

**Port 5173 is NOT configured:**
- Clear browser cache
- Update bookmarks to port 3000
- Check `frontend/package.json` - should show `--port 3000`

### CORS Errors

**If you see CORS errors:**
- Make sure you're accessing `http://localhost:3000` (not 5173)
- Check backend is running on port 8001
- Verify `backend/api/main.py` has port 3000 in allow_origins

---

## 📚 Related Documentation

- **Startup Guide:** [STARTUP_ORDER_GUIDE.md](./STARTUP_ORDER_GUIDE.md)
- **Port Configuration:** [PORT_CONFIGURATION.md](./PORT_CONFIGURATION.md)
- **Port Cleanup:** [PORT_3000_FIX_COMPLETE.md](./PORT_3000_FIX_COMPLETE.md)

---

## ✅ Summary

| Item | Value |
|------|-------|
| **Correct Frontend URL** | http://localhost:3000 |
| **Old URL (don't use)** | ~~http://localhost:5173~~ |
| **Backend URL** | http://localhost:8001 |
| **Status** | ✅ Both Running |

---

## 🎉 Quick Start

```powershell
# 1. Start REIMS
.\start_reims.bat

# 2. Browser opens automatically to:
# http://localhost:3000

# 3. That's it! You're ready to use REIMS.
```

---

**Remember:** Always use **http://localhost:3000** for the frontend!

**Last Updated:** October 11, 2025  
**Status:** ✅ Services Running on Correct Ports

















