# REIMS Startup Verification Checklist

## After Every Restart

### 1. Docker Services ✓
```bash
docker ps
```

Expected: All services showing "Up" and "healthy"

### 2. Backend Health ✓

```bash
python final_verification.py
```

Expected: "FINAL QUALITY SCORE: 100/100"

### 3. Database Integrity ✓

```bash
sqlite3 reims.db "SELECT id, name, annual_noi, occupancy_rate FROM properties;"
```

Expected:

- NOI values > $100,000
- Occupancy rates between 0.5 and 1.0

### 4. API Response ✓

Open browser: http://localhost:8001/api/properties

Expected: All properties with correct NOI and occupancy

### 5. Frontend Display ✓

Open browser: http://localhost:3001

Navigate to Portfolio page

Expected: All properties display with correct data

## If Quality Drops

1. **Check database:**
   ```bash
   python final_verification.py
   ```

2. **If needed, restore quality:**
   ```bash
   python fix_database_values.py
   ```

3. **Restart backend:**
   ```bash
   Get-Process python | Stop-Process -Force
   $env:DATABASE_URL="sqlite:///./reims.db"; python simple_backend.py
   ```

4. **Verify again:**
   ```bash
   python final_verification.py
   ```
