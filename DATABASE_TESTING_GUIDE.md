# REIMS Database Testing Guide

## 📋 Tables with Your Uploaded Data

### 1. **`documents`** - Main File Metadata
**Contains:** Information about uploaded files

**Key Fields:**
- `document_id` - Unique identifier
- `original_filename` - File name (e.g., "ESP 2024 Balance Sheet.pdf")
- `property_id` - Property identifier (your files: property 1)
- `file_size` - Size in bytes
- `content_type` - MIME type (application/pdf)
- `status` - Processing status (uploaded/processed)
- `minio_bucket` - MinIO storage bucket name
- `minio_object_name` - Path in MinIO
- `storage_type` - Where stored (minio/local)

**Your Data:** ✅ 3 records (all 3 PDFs)

---

### 2. **`extracted_data`** - Extracted Content
**Contains:** Text and data extracted from documents

**Key Fields:**
- `document_id` - Links to documents table
- `data_type` - File type (pdf/csv/excel)
- `extracted_content` - Full extracted text (JSON)
- `page_count` - Number of pages (PDFs only)
- `word_count` - Word count
- `row_count` - Rows (Excel/CSV only)
- `column_count` - Columns (Excel/CSV only)

**Your Data:** ✅ 3 records
- Balance Sheet: 5 pages, 990 words
- Income Statement: 5 pages, 1,561 words
- Cash Flow Statement: 9 pages, 3,032 words

---

### 3. **`processing_jobs`** - Processing Status
**Contains:** Status of document processing jobs

**Key Fields:**
- `job_id` - Unique job identifier
- `document_id` - Links to documents table
- `status` - Job status (queued/processing/completed/failed)
- `created_at` - When job started
- `completed_at` - When job finished
- `processing_result` - Extraction metrics (JSON)

**Your Data:** ✅ 3 records (all completed)

---

### 4. **`financial_documents`** - Financial Statements
**Contains:** Structured financial data (currently populated from your files)

**Your Data:** ✅ 3 records

---

### 5. **Tables Ready for Population**

These tables are empty but ready to receive parsed financial data:

- **`properties`** - Property master records
- **`financial_transactions`** - Individual transactions
- **`tenants`** - Tenant information
- **`leases`** - Lease agreements

---

## 🔍 How to Test/Check Your Data

### Method 1: Use the Test Script (Easiest)
```powershell
python test_database_data.py
```
This shows all data with nice formatting.

---

### Method 2: Direct SQL Queries

#### Check Documents
```sql
SELECT original_filename, file_size, status, property_id
FROM documents;
```

#### Check Extracted Content
```sql
SELECT d.original_filename, e.page_count, e.word_count, e.data_type
FROM documents d
JOIN extracted_data e ON d.document_id = e.document_id;
```

#### Check Processing Status
```sql
SELECT d.original_filename, j.status, j.created_at, j.completed_at
FROM documents d
JOIN processing_jobs j ON d.document_id = j.document_id;
```

#### Get Extracted Text Preview
```sql
SELECT d.original_filename, 
       json_extract(e.extracted_content, '$.text_preview') as preview
FROM documents d
JOIN extracted_data e ON d.document_id = e.document_id;
```

---

### Method 3: Python Script

```python
import sqlite3
import json

conn = sqlite3.connect('reims.db')
cursor = conn.cursor()

# Get all documents
cursor.execute("SELECT document_id, original_filename, status FROM documents")
for doc_id, filename, status in cursor.fetchall():
    print(f"{filename}: {status}")
    
    # Get extracted data for this document
    cursor.execute("""
        SELECT page_count, word_count, extracted_content 
        FROM extracted_data 
        WHERE document_id = ?
    """, (doc_id,))
    
    result = cursor.fetchone()
    if result:
        pages, words, content_json = result
        content = json.loads(content_json)
        print(f"  Pages: {pages}, Words: {words}")
        print(f"  Preview: {content.get('text_preview', '')[:100]}...")
    print()

conn.close()
```

---

### Method 4: Visual Database Browser

```powershell
# If VIEW_DATABASE.bat exists
.\VIEW_DATABASE.bat

# Or use any SQLite browser
# Open: reims.db
```

---

### Method 5: API Endpoints

Your data is also accessible via the backend API:

```powershell
# Get list of documents
Invoke-WebRequest -Uri http://localhost:8001/api/documents/list -UseBasicParsing

# Get specific document
Invoke-WebRequest -Uri "http://localhost:8001/api/documents/{document_id}" -UseBasicParsing

# Get extracted data
Invoke-WebRequest -Uri "http://localhost:8001/api/processed-data/{document_id}" -UseBasicParsing
```

---

## 📊 Quick Verification Commands

### Count records in each table:
```sql
SELECT 'documents' as table_name, COUNT(*) as count FROM documents
UNION ALL
SELECT 'extracted_data', COUNT(*) FROM extracted_data
UNION ALL
SELECT 'processing_jobs', COUNT(*) FROM processing_jobs
UNION ALL
SELECT 'properties', COUNT(*) FROM properties;
```

### Check processing completion rate:
```sql
SELECT 
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM processing_jobs), 2) as percentage
FROM processing_jobs
GROUP BY status;
```

### Get file statistics:
```sql
SELECT 
    COUNT(*) as total_files,
    SUM(file_size) as total_bytes,
    ROUND(SUM(file_size) / 1024.0 / 1024.0, 2) as total_mb,
    AVG(file_size) as avg_file_size
FROM documents;
```

---

## 🎯 Current Data Summary

Based on your uploaded files:

| Metric | Value |
|--------|-------|
| **Total Documents** | 3 |
| **Total Pages** | 19 (5+5+9) |
| **Total Words** | 5,583 (990+1,561+3,032) |
| **Total Size** | 47.9 KB |
| **Property** | Property ID: 1 (ESP) |
| **Document Types** | PDF Financial Statements |
| **Processing Status** | 100% Complete |

**Files:**
1. ESP 2024 Balance Sheet (5 pages, 990 words)
2. ESP 2024 Income Statement (5 pages, 1,561 words)
3. ESP 2024 Cash Flow Statement (9 pages, 3,032 words)

---

## 🔗 Related Commands

```powershell
# Run the comprehensive test
python test_database_data.py

# Check MinIO files
python -c "from minio import Minio; c=Minio('localhost:9000','minioadmin','minioadmin',secure=False); [print(f'{o.object_name} ({o.size} bytes)') for o in c.list_objects('reims-files', recursive=True)]"

# Quick database status
python -c "import sqlite3; conn=sqlite3.connect('reims.db'); c=conn.cursor(); c.execute('SELECT COUNT(*) FROM documents'); print(f'Documents: {c.fetchone()[0]}'); c.execute('SELECT COUNT(*) FROM extracted_data'); print(f'Extracted: {c.fetchone()[0]}'); conn.close()"
```

---

## ✅ Success Indicators

Your data is correctly loaded if you see:

- ✅ 3 records in `documents` table
- ✅ 3 records in `extracted_data` table  
- ✅ 3 records in `processing_jobs` with status "completed"
- ✅ All documents have status "processed"
- ✅ Extracted content contains text from PDFs
- ✅ Page counts and word counts are > 0

---

## 📝 Notes

- The `extracted_content` field contains JSON with full extracted text
- Text is stored in both `text_preview` (first 500 chars) and `full_text` (complete)
- You can search the full text using SQL LIKE or JSON functions
- All timestamps are in UTC
- Document IDs are UUIDs for uniqueness

---

**Test Script Location:** `test_database_data.py`  
**Database File:** `reims.db`  
**Backup Location:** `backups/`

