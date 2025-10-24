# Document Storage Standard

**Version:** 1.0  
**Date:** October 19, 2025  
**Status:** ✅ Implemented and Migrated

---

## Overview

This document defines the standardized structure for storing property documents in MinIO and database records for the REIMS system.

## Storage Architecture

### MinIO Structure

**Bucket:** `reims-files` (consolidated single bucket for all property documents)

**Path Pattern:**
```
properties/{property_id}/{doc_type}/{year}/{document_id}_{filename}
```

**Example Paths:**
```
properties/3/financial-statements/2024/abc123_Hammond_Aire_2024_Balance_Sheet.pdf
properties/7/rent-rolls/2025/def456_Hammond_Rent_Roll_April_2025.pdf
properties/1/offering-memos/2024/xyz789_ESP_Offering_Memo.pdf
```

### Document Type Folders

Standardized folder names for document types:

| Document Type | Folder Name |
|--------------|-------------|
| `financial_statement` | `financial-statements` |
| `rent_roll` | `rent-rolls` |
| `offering_memo` | `offering-memos` |
| `lease_agreement` | `lease-agreements` |
| `maintenance_record` | `maintenance-records` |
| `other` | `other` |

### Database Synchronization

**Two-Table Approach:** Documents are written to BOTH tables for compatibility:

1. **financial_documents** - Primary table for financial docs
2. **documents** - Secondary table for backward compatibility

Both tables maintain:
- Document ID
- Property ID and Name
- Document year and period
- File path in MinIO
- Upload metadata

---

## Upload Process

### Frontend Upload Flow

1. User selects file and property
2. Frontend calls `/api/documents/upload` endpoint
3. Backend extracts metadata from filename
4. File uploaded to MinIO with standardized path
5. Records created in both database tables
6. Document queued for processing (optional)

### Backend Logic

```python
# Extract metadata
year = document_year or datetime.utcnow().year
doc_type_folder = map_doc_type_to_folder(document_type)

# Build path
file_path = f"properties/{property_id}/{doc_type_folder}/{year}/{document_id}_{filename}"

# Upload to MinIO
minio_client.put_object(
    bucket_name="reims-files",
    object_name=file_path,
    data=file_content,
    length=file_size,
    content_type=content_type
)

# Write to both tables
insert_into_financial_documents(...)
insert_into_documents(...)
```

---

## Filename Parsing

The system automatically extracts metadata from filenames:

**Pattern Examples:**
- `Hammond Aire 2024 Balance Sheet.pdf` → Property: "Hammond Aire", Year: 2024
- `TCSH Rent Roll April 2025.pdf` → Property: "TCSH", Year: 2025, Period: "April"
- `ESP 2024 Income Statement.pdf` → Property: "ESP", Year: 2024

**Parser Logic:**
- Property name: First part before year
- Year: 4-digit number (2020-2029)
- Period: Month name or quarter (Q1-Q4)
- Document type: Keywords (rent roll, balance sheet, income statement, etc.)

---

## Migration Summary

**Date Completed:** October 19, 2025

### Files Migrated

- **Total files processed:** 26 files
- **Successfully migrated:** 15 files
- **Already standardized:** 11 files
- **Errors:** 0 files

### Migration Actions

1. Files moved from `reims-documents` bucket to `reims-files` bucket
2. Year folder added to path structure
3. Document type folders standardized
4. Database records updated in both tables
5. Old files retained for safety (not deleted)

### Before Migration

```
reims-documents/
  financial-statements/
    balance-sheets/TCSH 2024 Balance Sheet.pdf
    income-statements/TCSH 2024 Income Statement.pdf

reims-files/
  properties/3/
    Hammond_Aire_Balance_Sheet.pdf
```

### After Migration

```
reims-files/
  properties/3/
    financial-statements/
      2024/
        Hammond_Aire_2024_Balance_Sheet.pdf
  properties/6/
    financial-statements/
      2024/
        TCSH_2024_Balance_Sheet.pdf
        TCSH_2024_Income_Statement.pdf
    rent-rolls/
      2025/
        TCSH_Rent_Roll_April_2025.pdf
```

---

## API Endpoints

### Upload Document

**Endpoint:** `POST /api/documents/upload`

**Parameters:**
- `file` (required): Document file (PDF, Excel, CSV)
- `property_id` (required): Property ID
- `document_type` (required): Type of document
- `property_name` (optional): Auto-extracted from filename
- `document_year` (optional): Auto-extracted from filename
- `document_period` (optional): Auto-extracted from filename

**Response:**
```json
{
  "success": true,
  "data": {
    "document_id": "abc-123-def-456",
    "status": "queued",
    "file_name": "Hammond_Aire_2024_Balance_Sheet.pdf",
    "file_size": 8387,
    "property_name": "Hammond Aire",
    "document_year": 2024,
    "document_type": "financial_statement"
  }
}
```

### Download Document

**Endpoint:** `GET /api/documents/{document_id}/download`

Returns the file as an attachment for download.

### View Document

**Endpoint:** `GET /api/documents/{document_id}/view`

Returns the file inline for viewing in browser (for PDFs).

---

## Database Schema

### financial_documents Table

```sql
CREATE TABLE financial_documents (
    id TEXT PRIMARY KEY,
    property_id TEXT,
    file_path TEXT,
    file_name TEXT,
    document_type TEXT,
    property_name VARCHAR(255),
    document_year INTEGER,
    document_period VARCHAR(50),
    status TEXT,
    upload_date TIMESTAMP,
    processing_date TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP
);
```

### documents Table

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    document_id VARCHAR,
    original_filename VARCHAR,
    stored_filename VARCHAR,
    property_id VARCHAR,
    file_size INTEGER,
    content_type VARCHAR,
    file_path VARCHAR,
    upload_timestamp DATETIME,
    status VARCHAR,
    minio_bucket TEXT,
    minio_object_name TEXT,
    minio_url TEXT,
    storage_type TEXT,
    property_name VARCHAR(255),
    document_year INTEGER,
    document_type VARCHAR(100),
    document_period VARCHAR(50)
);
```

---

## Common Queries

### Get all documents for a property

```sql
SELECT * FROM financial_documents
WHERE property_id = '3'
ORDER BY document_year DESC, upload_date DESC;
```

### Get documents by year

```sql
SELECT * FROM financial_documents
WHERE document_year = 2024
AND document_type = 'rent_roll'
ORDER BY property_name, document_period;
```

### Check document sync status

```sql
SELECT 
    fd.id,
    fd.property_name,
    fd.file_name,
    CASE 
        WHEN d.document_id IS NOT NULL THEN 'Synced'
        ELSE 'Not Synced'
    END as sync_status
FROM financial_documents fd
LEFT JOIN documents d ON fd.id = d.document_id;
```

---

## Validation

### Path Pattern Validation

Use regex to validate paths:
```python
import re
pattern = r'^properties/[\w-]+/(financial-statements|rent-rolls|offering-memos|lease-agreements|maintenance-records|other)/\d{4}/.+$'
is_valid = re.match(pattern, file_path) is not None
```

### File Accessibility Test

```python
from minio import Minio

minio_client = Minio(...)
try:
    stat = minio_client.stat_object("reims-files", file_path)
    print(f"File accessible: {stat.size} bytes")
except:
    print("File not accessible")
```

---

## Best Practices

### DO ✅

- Always use the standardized path structure
- Include year in the path
- Write to both database tables
- Use descriptive filenames with property name and year
- Validate file type and size before upload
- Log upload operations

### DON'T ❌

- Don't hardcode bucket names (use config)
- Don't skip database synchronization
- Don't upload without property association
- Don't delete old files immediately (keep backups)
- Don't bypass filename parsing

---

## Troubleshooting

### Document not found in MinIO

1. Check database for file_path
2. Verify bucket name is "reims-files"
3. Check if path follows standard pattern
4. Verify MinIO connection

### Upload fails

1. Check MinIO service is running
2. Verify bucket exists
3. Check file size < 50MB
4. Verify file type is allowed
5. Check property_id exists

### Database sync issues

1. Check both tables have records
2. Verify document_id matches
3. Check file_path is consistent
4. Verify foreign key constraints

---

## Maintenance

### Cleanup Old Files

After verifying migration:

```python
# Delete old files from reims-documents bucket
minio_client.remove_object("reims-documents", old_path)

# Delete old path files from reims-files
minio_client.remove_object("reims-files", old_path)
```

### Audit Storage

Run audit script periodically:
```bash
python audit_storage_structure.py
```

### Verify Integrity

Run verification script:
```bash
python verify_storage_migration.py
```

---

## Implementation Files

| File | Purpose |
|------|---------|
| `backend/api/routes/documents.py` | Primary upload endpoint with standardization |
| `backend/api/upload.py` | Alternate upload endpoint (legacy) |
| `backend/utils/filename_parser.py` | Filename metadata extraction |
| `audit_storage_structure.py` | Audit current storage state |
| `migrate_minio_structure.py` | Migration script |
| `verify_storage_migration.py` | Verification script |
| `DOCUMENT_STORAGE_STANDARD.md` | This documentation |

---

## Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-19 | 1.0 | Initial standardization implemented |

---

## Support

For issues or questions:
1. Check verification report
2. Review audit logs
3. Check MinIO console at http://localhost:9001
4. Review database records

---

**Last Updated:** October 19, 2025  
**Maintained By:** REIMS Development Team

