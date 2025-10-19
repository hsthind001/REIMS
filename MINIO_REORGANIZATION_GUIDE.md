# MinIO Bucket Reorganization Guide

**Date:** October 13, 2025  
**Goal:** Organize MinIO files as `PropertyName/Year/DocumentType/filename`

---

## 📊 Current vs Desired Structure

### Current Structure:
```
reims-files/
  └── properties/1/[uuid]_ESP 2024 Income Statement.pdf
  └── properties/1/[uuid]_ESP 2024 Cash Flow Statement.pdf
  └── properties/1/[uuid]_ESP 2024 Balance Sheet.pdf
```

### Desired Structure:
```
reims-files/
  └── ESP/
      └── 2024/
          ├── Income_Statement/
          │   └── ESP 2024 Income Statement.pdf
          ├── Cash_Flow_Statement/
          │   └── ESP 2024 Cash Flow Statement.pdf
          └── Balance_Sheet/
              └── ESP 2024 Balance Sheet.pdf
```

---

## 🔄 Migration Process

The migration script (`migrate_and_reorganize_minio.py`) performs these steps:

### Step 1: Extract Metadata from Filenames
- Parses existing filenames using the `filename_parser` utility
- Extracts: property_name, document_year, document_type, document_period
- Updates `financial_documents` table with extracted metadata

### Step 2: Reorganize MinIO Files
- Reads files with metadata from database
- Creates new path: `PropertyName/Year/DocumentType/filename`
- Copies files to new location in MinIO
- Updates database with new file paths
- Deletes old files from MinIO

### Step 3: Verification
- Displays final MinIO structure
- Shows summary of changes

---

## 🚀 How to Run

### Option 1: Automatic Migration (Recommended)

```bash
cd C:\REIMS
python migrate_and_reorganize_minio.py
```

Follow the prompts:
- Review the migration plan
- Type `yes` to proceed
- Wait for completion
- View the new structure

### Option 2: Step-by-Step

1. **Preview first:**
   ```bash
   python preview_minio_structure.py
   ```

2. **Run migration:**
   ```bash
   python migrate_and_reorganize_minio.py
   ```

3. **Verify:**
   ```bash
   python check_uploaded_files.py
   ```

---

## 📝 What Gets Updated

### Database (`financial_documents` table):
- ✅ `property_name` column populated with "ESP"
- ✅ `document_year` column populated with 2024
- ✅ `document_type` column populated with "Income Statement", etc.
- ✅ `document_period` column populated with "Annual"
- ✅ `file_path` column updated to new structure

### MinIO (`reims-files` bucket):
- ✅ Files copied to new location
- ✅ Old files deleted
- ✅ New structure: `ESP/2024/Income_Statement/`

---

## ⚠️ Important Notes

### Bucket Limitations
**Note:** MinIO doesn't support nested buckets. The structure `ESP 2024/Income_Statement` refers to object paths within a single bucket, not separate buckets.

You **cannot** create:
- ❌ Bucket: `ESP 2024`
- ❌ Bucket: `ESP/2024/Income_Statement`

You **can** create (what we're doing):
- ✅ Bucket: `reims-files`
- ✅ Object: `ESP/2024/Income_Statement/file.pdf`

### Backup
The migration script:
- ✅ Copies files before deleting
- ✅ Updates database only after successful copy
- ✅ Can be run multiple times safely (skips already migrated files)

### Rollback
If you need to undo:
1. Database changes are in `financial_documents` table
2. Old files are deleted from MinIO (cannot be recovered)
3. **Recommendation:** Test with a few files first

---

## 🎯 Example: ESP Files

### Before Migration:

**Database:**
```sql
file_name: ESP 2024 Income Statement.pdf
file_path: properties/1/578bd248-71aa-422b-b768-043b2486c62c_ESP 2024 Income Statement.pdf
property_name: NULL
document_year: NULL
document_type: financial_statement
```

**MinIO:**
```
reims-files/properties/1/578bd248-71aa-422b-b768-043b2486c62c_ESP 2024 Income Statement.pdf
```

### After Migration:

**Database:**
```sql
file_name: ESP 2024 Income Statement.pdf
file_path: ESP/2024/Income_Statement/ESP 2024 Income Statement.pdf
property_name: ESP
document_year: 2024
document_type: Income Statement
```

**MinIO:**
```
reims-files/ESP/2024/Income_Statement/ESP 2024 Income Statement.pdf
```

---

## 🔍 Verification

### Check Database:
```bash
python -c "
import sqlite3
conn = sqlite3.connect('reims.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT file_name, property_name, document_year, file_path
    FROM financial_documents
    WHERE file_name LIKE '%ESP%'
    LIMIT 3
''')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]} / {row[2]} / {row[3]}')
conn.close()
"
```

### Check MinIO:
```bash
python check_uploaded_files.py
```

---

## 🌟 Benefits

### Before:
- ❌ Flat structure: `properties/1/uuid_filename`
- ❌ Hard to browse
- ❌ No organization by property/year
- ❌ UUID makes it harder to identify files

### After:
- ✅ Hierarchical: `ESP/2024/Income_Statement/filename`
- ✅ Easy to browse and navigate
- ✅ Organized by property and year
- ✅ Clear folder structure
- ✅ Queryable by property/year in database

---

## 🔮 Future Uploads

### Automatic Organization
After migration, the updated `/api/documents/upload` endpoint will automatically:

1. Parse filename for metadata
2. Store files in new structure: `PropertyName/Year/DocumentType/`
3. Update database with correct paths

### Example:
```
Upload: "Downtown Tower 2025 Rent Roll.pdf"
  → MinIO: reims-files/Downtown_Tower/2025/Rent_Roll/Downtown Tower 2025 Rent Roll.pdf
  → Database: property_name=Downtown Tower, year=2025, type=Rent Roll
```

---

## 📋 Checklist

Before running migration:
- [ ] Backend is running (or stopped - doesn't matter)
- [ ] MinIO is running (check: http://localhost:9000)
- [ ] Database is accessible (check: `reims.db` exists)
- [ ] You have backups (optional but recommended)

After migration:
- [ ] Check database metadata is populated
- [ ] Verify new MinIO structure
- [ ] Test file downloads still work
- [ ] Re-upload a test file to verify new structure

---

## ⚡ Quick Start

```bash
# Run the complete migration
cd C:\REIMS
python migrate_and_reorganize_minio.py

# When prompted, type: yes

# Wait for completion

# Verify the result
python check_uploaded_files.py
```

**That's it!** Your files will be organized as:
- `ESP/2024/Income_Statement/`
- `ESP/2024/Cash_Flow_Statement/`
- `ESP/2024/Balance_Sheet/`

---

**Status:** ✅ Ready to execute  
**Risk Level:** Low (copies before deleting, reversible via database)  
**Time:** < 1 minute for current files



