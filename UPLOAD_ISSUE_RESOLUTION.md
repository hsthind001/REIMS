# Upload Issue Resolution

## Problem Summary
Files were being uploaded to MinIO successfully, but database records were not visible in PostgreSQL.

## Root Cause
The backend was falling back to SQLite database instead of using PostgreSQL due to:
1. Password mismatch in configuration
2. `.env` file not being loaded properly by the backend
3. Schema mismatches between code expectations and actual PostgreSQL tables

## Findings

### 1. Multiple Database Files
- `C:\REIMS\reims.db` (360 KB) - **ACTIVE** - Contains all upload records
- `C:\REIMS\backend\reims.db` (69 KB) - Old
- `C:\REIMS\queue_service\reims.db` (61 KB) - Old

### 2. Database Configuration Issues
- **`.env` file**: `DATABASE_URL=postgresql://postgres:dev123@localhost:5432/reims`
- **`backend/api/database.py`** default: `postgresql://postgres:postgres@localhost:5432/reims`
- Backend fails PostgreSQL connection → falls back to SQLite

### 3. Schema Mismatches Fixed
- Added missing columns to `documents` table in PostgreSQL
- Added missing columns to `financial_documents` table in PostgreSQL
- Created `extracted_data` table in PostgreSQL

### 4. Upload Endpoint  
- Actual endpoint: `/api/documents/upload` (from `backend/api/routes/documents.py`)
- **Required parameters**:
  - `file`: The file to upload
  - `property_id`: UUID of the property
  - `document_type`: Type (e.g., "financial_statement", "rent_roll", etc.)

## Data Location

### Current State (SQLite)
All 23 uploaded documents are in: `C:\REIMS\reims.db` → `financial_documents` table

Example records:
```
979b449e-5dbd-4a3b-bbab-89dea6a29bfb | test_upload_now.csv | queued
c9d4e907-8591-4157-a235-448eef8e7c1d | ESP 2024 Income Statement.pdf | queued
d25b77bd-8c4b-4dfe-8e64-87a33363de80 | ESP 2024 Cash Flow Statement.pdf | queued
```

### MinIO Storage
Files are correctly stored in MinIO bucket: `reims-files`
Path structure: `properties/{property_id}/{document_id}_{filename}`

## Solutions

### Option 1: Force Backend to Use PostgreSQL (RECOMMENDED)

1. **Update backend startup to load .env properly:**
   Create `start_backend_postgresql_fixed.ps1`:
   ```powershell
   $env:DATABASE_URL = "postgresql://postgres:dev123@localhost:5432/reims"
   cd backend
   python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
   ```

2. **Or update `backend/api/database.py` default password:**
   Change line 15 from:
   ```python
   "postgresql://postgres:postgres@localhost:5432/reims"
   ```
   To:
   ```python
   "postgresql://postgres:dev123@localhost:5432/reims"
   ```

### Option 2: Migrate Data from SQLite to PostgreSQL

Run migration script:
```python
# migrate_to_postgresql.py
import sqlite3
import psycopg2
from datetime import datetime

# Connect to both databases
sqlite_conn = sqlite3.connect('reims.db')
pg_conn = psycopg2.connect(
    "postgresql://postgres:dev123@localhost:5432/reims"
)

# Migrate financial_documents
sqlite_cursor = sqlite_conn.cursor()
pg_cursor = pg_conn.cursor()

records = sqlite_cursor.execute("""
    SELECT id, property_id, file_name, file_path, document_type, 
           status, upload_date
    FROM financial_documents
""").fetchall()

for record in records:
    pg_cursor.execute("""
        INSERT INTO financial_documents 
        (id, property_id, file_name, file_path, document_type, status, upload_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """, record)

pg_conn.commit()
print(f"Migrated {len(records)} records")
```

### Option 3: Continue Using SQLite (NOT RECOMMENDED)

If you want to keep using SQLite, just query the correct database:
- Database: `C:\REIMS\reims.db`
- Table: `financial_documents`

## Verification Steps

### Check Which Database is Being Used:
```powershell
# Check backend connection
Invoke-RestMethod -Uri "http://localhost:8001/api/documents"
```

### Query SQLite:
```python
import sqlite3
conn = sqlite3.connect('reims.db')
cursor = conn.cursor()
records = cursor.execute("""
    SELECT id, file_name, document_type, status, upload_date 
    FROM financial_documents 
    ORDER BY upload_date DESC
""").fetchall()
print(f"Found {len(records)} uploads")
```

### Query PostgreSQL:
```powershell
$env:PGPASSWORD = "dev123"
docker exec -i reims-postgres psql -U postgres -d reims -c `
"SELECT id, file_name, document_type, status, upload_date FROM financial_documents;"
```

## Testing Upload

```powershell
# Upload with all required fields
curl -X POST "http://localhost:8001/api/documents/upload" `
  -F "file=@test.csv;type=text/csv" `
  -F "property_id=550e8400-e29b-41d4-a716-446655440000" `
  -F "document_type=financial_statement"
```

## Summary

✅ **Files ARE being uploaded successfully**
✅ **Data IS being saved to database**
❌ **But to WRONG database (SQLite instead of PostgreSQL)**

**RECOMMENDATION**: Fix backend to use PostgreSQL by ensuring DATABASE_URL environment variable is properly loaded.

