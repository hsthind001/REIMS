# How to Fix .env File for PostgreSQL

## 🔒 Why Can't AI Edit .env?

The `.env` file is protected by Cursor IDE's security features because:
- Contains sensitive data (passwords, API keys, secrets)
- Prevents accidental exposure of credentials
- Stops AI from auto-committing secrets to Git
- **This is a GOOD security practice!**

The protection is built into Cursor's global settings (not a file in your project).

---

## ✅ **SOLUTION 1: Manual Edit (EASIEST - 2 MINUTES)**

### Step 1: Open the .env file
```
Location: C:\REIMS\.env
```

Open it in:
- Cursor (Right-click → Open)
- Notepad
- VSCode
- Any text editor

### Step 2: Find and Change Line 10

**FIND THIS (line 10):**
```env
DATABASE_URL=sqlite:///./reims.db
```

**CHANGE TO:**
```env
DATABASE_URL=postgresql://postgres:dev123@localhost:5432/reims
```

### Step 3: Save the File
Press `Ctrl+S` or File → Save

### Step 4: Restart Backend
1. Go to backend terminal window
2. Press `Ctrl+C` to stop
3. Wait for it to fully stop
4. Run:
   ```powershell
   python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8001 --reload
   ```

### Step 5: Verify Success
Look for this message in backend terminal:
```
Connected to PostgreSQL  ✅
```

NOT this:
```
Using SQLite database  ❌
```

---

## 🐍 **SOLUTION 2: Use Python Script (NO EDITING NEEDED!)**

I created a Python wrapper that sets PostgreSQL **before** loading `.env`:

### Just Run This:
```powershell
cd C:\REIMS
python start_with_postgresql.py
```

### What It Does:
- Sets `DATABASE_URL` environment variable to PostgreSQL
- Starts uvicorn with PostgreSQL already configured
- `.env` file settings are overridden
- No file editing required!

### Verify It Worked:
```powershell
.\verify_postgresql.ps1
```

---

## 🔓 **SOLUTION 3: Disable Protection (NOT RECOMMENDED)**

### Where Protection Comes From:
- **Cursor Global Settings** (built-in)
- Not from a file in your project
- Protects ALL `.env` files in ALL projects

### To Disable (Advanced):
1. Open Cursor Settings
   - `Ctrl+,` or File → Preferences → Settings
2. Search for: `"ignore"` or `"rules"` or `"cursor rules"`
3. Look for global ignore patterns
4. Remove `.env` from the list

### ⚠️ WARNING:
- Reduces security for ALL projects
- AI might accidentally expose credentials
- Could commit secrets to Git
- **Manual editing is much safer!**

---

## 📊 Current Status

### Your Data Location:
- **SQLite:** 11 documents (old uploads)
- **PostgreSQL:** 0 documents (waiting for new uploads)
- **MinIO:** All files safely stored

### After Fix:
- New uploads → PostgreSQL ✅
- Old uploads → Still in SQLite (we can migrate later)
- MinIO files → Remain accessible

---

## 🧪 Testing After Fix

### 1. Upload a Test File
```
http://localhost:3001/upload
```

### 2. Check Backend Terminal
Should see:
```
POST /api/documents/upload
Status: 200 OK
```

### 3. Verify in PostgreSQL (pgAdmin)
```
URL: http://localhost:5050
Login: admin@example.com / admin123
Navigate: Tables → documents → View Data
```

### 4. Run Verification Script
```powershell
.\verify_postgresql.ps1
```

Should show:
```
✅ SUCCESS! Backend is using PostgreSQL!
```

---

## 💡 Quick Reference

### Start Backend with PostgreSQL (After .env Edit):
```powershell
cd C:\REIMS
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8001 --reload
```

### Start Backend with Python Wrapper (No .env Edit):
```powershell
cd C:\REIMS
python start_with_postgresql.py
```

### Verify Which Database Is Being Used:
```powershell
.\verify_postgresql.ps1
```

### Check Documents in PostgreSQL:
```powershell
docker exec reims-postgres psql -U postgres -d reims -c "SELECT filename, status FROM documents LIMIT 10;"
```

---

## ❓ Troubleshooting

### Still Seeing "Using SQLite"?
1. Make sure .env file is saved
2. Completely stop backend (Ctrl+C)
3. Wait 5 seconds
4. Start backend again
5. Check first few lines of output

### "Connected to PostgreSQL" but no data?
1. You need to upload NEW files
2. Old files are in SQLite
3. Refresh pgAdmin (F5)
4. Check documents table after new upload

### Can't Save .env File?
1. Close Cursor/VSCode
2. Open .env in Notepad
3. Edit and save
4. Reopen Cursor

---

## 📝 Summary

**Recommended Approach:**
1. **Easiest:** Manually edit `.env` file (2 minutes)
2. **Alternative:** Use `python start_with_postgresql.py` (no editing)
3. **Not Recommended:** Disable protection globally

**Best Practice:**
- Keep AI protection on `.env` files
- Manually edit when needed
- Use environment-specific config files for sensitive data

---

## ✅ Success Checklist

- [ ] Backend shows "Connected to PostgreSQL"
- [ ] Upload a test file from frontend
- [ ] See file in pgAdmin documents table
- [ ] `verify_postgresql.ps1` shows PostgreSQL in use
- [ ] No more "Using SQLite database" messages

---

**Created:** 2025-10-13  
**Purpose:** Guide for fixing .env database configuration  
**Files Needed:** `.env`, `start_with_postgresql.py`, `verify_postgresql.ps1`














