# Document-Type-First Storage Structure

**Version:** 2.0 (Revised Structure)  
**Date:** October 19, 2025  
**Status:** ✅ Implemented and Migrated

---

## Overview

REIMS now uses a **document-type-first organization** where files are categorized by their type and year, with **original filenames preserved**.

## Storage Structure

### MinIO Path Pattern

```
reims-files/Financial Statements/{year}/{document_subtype}/{original_filename}
```

### Document Subtypes

| Subtype | Example Files |
|---------|---------------|
| **Balance Sheets** | `Hammond Aire 2024 Balance Sheet.pdf` |
| **Cash Flow Statements** | `TCSH 2024 Cash Flow Statement.pdf` |
| **Income Statements** | `ESP 2024 Income Statement.pdf` |
| **Rent Rolls** | `Hammond Rent Roll April 2025.pdf` |
| **Other Financial Documents** | Any other financial documents |

### Example Structure

```
reims-files/
  Financial Statements/
    2024/
      Balance Sheets/
        Hammond Aire 2024 Balance Sheet.pdf
        TCSH 2024 Balance Sheet.pdf
        ESP 2024 Balance Sheet.pdf
      Cash Flow Statements/
        Hammond Aire 2024 Cash Flow Statement.pdf
        TCSH 2024 Cash Flow Statement.pdf
      Income Statements/
        Hammond Aire 2024 Income Statement.pdf
        TCSH 2024 Income Statement.pdf
    2025/
      Rent Rolls/
        Hammond Rent Roll April 2025.pdf
        TCSH Rent Roll April 2025.pdf
      Balance Sheets/
        Hammond Aire 2025 Balance Sheet.pdf
```

---

## Key Features

### ✅ Original Filenames Preserved

Files are stored with their **exact original names** - no UUID prefixes or modifications.

- ✅ `Hammond Aire 2024 Balance Sheet.pdf`
- ❌ ~~`abc123_Hammond_Aire_2024_Balance_Sheet.pdf`~~

### ✅ Automatic Subtype Detection

The system analyzes filenames to automatically determine the correct subtype folder:

```python
# Balance Sheet detection
if 'balance' in filename and 'sheet' in filename:
    → Balance Sheets/

# Cash Flow detection  
if 'cash' in filename and 'flow' in filename:
    → Cash Flow Statements/

# Income Statement detection
if 'income' in filename and 'statement' in filename:
    → Income Statements/

# Rent Roll detection
if 'rent' in filename and 'roll' in filename:
    → Rent Rolls/
```

### ✅ Year-Based Organization

Files are automatically organized by the year extracted from:
1. Filename (e.g., "2024" in filename)
2. Metadata provided during upload
3. Current year (fallback)

---

## Upload Process

### Frontend Upload

When uploading through the frontend:

1. User selects file: `Hammond Aire 2025 Balance Sheet.pdf`
2. System extracts:
   - Year: **2025**
   - Document type: **Balance Sheets**
   - Property: Hammond Aire
3. File stored at: `Financial Statements/2025/Balance Sheets/Hammond Aire 2025 Balance Sheet.pdf`
4. Database updated with file location

### API Upload

```bash
curl -X POST http://localhost:8001/api/documents/upload \
  -F "file=@Hammond_Aire_2024_Balance_Sheet.pdf" \
  -F "property_id=3" \
  -F "document_type=financial_statement"
```

Result:
```
reims-files/Financial Statements/2024/Balance Sheets/Hammond Aire 2024 Balance Sheet.pdf
```

---

## Migration Results

### Statistics

- **Total files processed:** 30
- **Files migrated:** 11
- **Files skipped:** 19 (already in correct location)
- **Migration errors:** 0

### What Changed

**Before:**
```
reims-files/properties/3/abc123_Hammond_Aire_2024_Balance_Sheet.pdf
reims-documents/financial-statements/balance-sheets/TCSH_2024_Balance_Sheet.pdf
```

**After:**
```
reims-files/Financial Statements/2024/Balance Sheets/Hammond Aire 2024 Balance Sheet.pdf
reims-files/Financial Statements/2024/Balance Sheets/TCSH 2024 Balance Sheet.pdf
```

---

## Benefits

### 1. **Intuitive Organization**
   - Documents grouped by type, then year
   - Easy to browse and find specific document types
   - Logical hierarchy that matches how users think

### 2. **Clean Filenames**
   - Original filenames preserved
   - No system-generated prefixes
   - Professional appearance in MinIO console

### 3. **Automatic Categorization**
   - System detects document type from filename
   - No manual folder selection needed
   - Consistent organization rules

### 4. **Year-Based Versioning**
   - Easy to compare documents across years
   - Clear temporal organization
   - Simple archival structure

---

## Database Schema

Both tables store the full MinIO path:

### financial_documents Table
```sql
file_path: "Financial Statements/2024/Balance Sheets/Hammond Aire 2024 Balance Sheet.pdf"
file_name: "Hammond Aire 2024 Balance Sheet.pdf"
document_year: 2024
document_type: "financial_statement"
```

### documents Table
```sql
minio_bucket: "reims-files"
minio_object_name: "Financial Statements/2024/Balance Sheets/Hammond Aire 2024 Balance Sheet.pdf"
original_filename: "Hammond Aire 2024 Balance Sheet.pdf"
stored_filename: "Hammond Aire 2024 Balance Sheet.pdf"
```

---

## Browsing Structure

### MinIO Console

Navigate to: `http://localhost:9001`

Browse:
```
reims-files/
  └─ Financial Statements/
       ├─ 2024/
       │    ├─ Balance Sheets/
       │    ├─ Cash Flow Statements/
       │    ├─ Income Statements/
       │    └─ Other Financial Documents/
       └─ 2025/
            ├─ Rent Rolls/
            └─ Balance Sheets/
```

### API Access

**List all Balance Sheets for 2024:**
```python
objects = minio_client.list_objects(
    "reims-files", 
    prefix="Financial Statements/2024/Balance Sheets/",
    recursive=True
)
```

**Download specific file:**
```python
minio_client.fget_object(
    "reims-files",
    "Financial Statements/2024/Balance Sheets/Hammond Aire 2024 Balance Sheet.pdf",
    "local_file.pdf"
)
```

---

## Current Files

### 2024 Documents

**Balance Sheets:**
- Hammond Aire 2024 Balance Sheet.pdf
- TCSH 2024 Balance Sheet.pdf

**Cash Flow Statements:**
- Hammond Aire 2024 Cash Flow Statement.pdf
- TCSH 2024 Cash Flow Statement.pdf

**Income Statements:**
- Hammond Aire 2024 Income Statement.pdf
- TCSH 2024 Income Statement.pdf

### 2025 Documents

**Rent Rolls:**
- Hammond Rent Roll April 2025.pdf
- TCSH Rent Roll April 2025.pdf

---

## Filename Correction

The system will automatically correct filenames if analysis shows they're wrong:

### Example Scenarios

1. **Misnamed File**
   - Uploaded as: `Document1.pdf`
   - Content analysis: Balance sheet for Hammond Aire 2024
   - Corrected to: `Hammond Aire 2024 Balance Sheet.pdf`

2. **Wrong Year**
   - Uploaded as: `Hammond Aire 2023 Balance Sheet.pdf`
   - Content analysis: Actually 2024 data
   - Corrected to: `Hammond Aire 2024 Balance Sheet.pdf`

3. **Wrong Type**
   - Uploaded as: `Hammond Report.pdf`
   - Content analysis: Income statement
   - Corrected to: `Hammond Aire 2024 Income Statement.pdf`

*Note: Filename correction requires content analysis implementation (future enhancement)*

---

## Queries

### Find all documents for a property

```sql
SELECT * FROM financial_documents
WHERE file_name LIKE '%Hammond Aire%'
ORDER BY document_year DESC, file_name;
```

### Get all Balance Sheets

```sql
SELECT * FROM financial_documents
WHERE file_path LIKE '%Balance Sheets%'
ORDER BY document_year DESC;
```

### List documents by year

```sql
SELECT 
    document_year,
    COUNT(*) as count,
    GROUP_CONCAT(file_name) as files
FROM financial_documents
WHERE file_path LIKE 'Financial Statements/%'
GROUP BY document_year
ORDER BY document_year DESC;
```

---

## Best Practices

### DO ✅

- Use descriptive filenames with property name and year
- Include document type keywords in filename
- Use original document names when possible
- Verify year in filename matches content
- Include period (Q1, April, etc.) for rent rolls

### DON'T ❌

- Don't use generic names like "Document1.pdf"
- Don't include special characters in filenames
- Don't use ambiguous abbreviations
- Don't omit year from filename
- Don't mix document types in same file

### Recommended Filename Format

```
{Property Name} {Year} {Document Type} [{Period}].{ext}
```

**Examples:**
- `Hammond Aire 2024 Balance Sheet.pdf` ✅
- `TCSH Rent Roll April 2025.pdf` ✅
- `ESP 2025 Q1 Income Statement.pdf` ✅
- `Document.pdf` ❌
- `BS_2024.pdf` ❌

---

## Troubleshooting

### File Not Found

**Problem:** Cannot locate uploaded file

**Solution:**
1. Check MinIO console: `http://localhost:9001`
2. Navigate to: `Financial Statements/{year}/{type}/`
3. Verify filename matches original
4. Check database `file_path` field

### Wrong Folder

**Problem:** File uploaded to wrong subtype folder

**Solution:**
1. Filename may not contain expected keywords
2. Manually move in MinIO console
3. Update database `file_path` field
4. Or re-upload with corrected filename

### Duplicate Filenames

**Problem:** Same filename already exists

**Solution:**
1. Add distinguishing information to filename
2. Example: `Hammond Aire 2024 Balance Sheet v2.pdf`
3. Or include property identifier

---

## Implementation Files

| File | Purpose |
|------|---------|
| `backend/api/routes/documents.py` | Upload endpoint with new structure |
| `backend/api/upload.py` | Alternate upload endpoint |
| `migrate_to_doctype_first.py` | Migration script |
| `DOCUMENT_TYPE_FIRST_STRUCTURE.md` | This documentation |

---

## Comparison: Old vs New

| Aspect | Old Structure | New Structure |
|--------|--------------|---------------|
| **Organization** | Property-first | Document-type-first |
| **Path** | `properties/{id}/{type}/{year}/` | `Financial Statements/{year}/{type}/` |
| **Filename** | `{uuid}_{filename}` | `{original_filename}` |
| **Browsing** | Grouped by property | Grouped by document type |
| **Year Location** | End of path | Middle of path |
| **Use Case** | Property-centric analysis | Document-type comparison |

---

## Future Enhancements

### Planned Features

1. **Content Analysis**
   - Automatic filename correction
   - Property name extraction from PDF content
   - Year validation against document content

2. **Additional Categories**
   - Leases
   - Maintenance Records
   - Offering Memorandums
   - Reports

3. **Version Control**
   - Automatic versioning for duplicate uploads
   - Revision history
   - Comparison tools

4. **Search Features**
   - Full-text search across documents
   - Filter by property, year, type
   - Advanced query builder

---

## Support

### Tools

- **MinIO Console:** http://localhost:9001
- **Migration Script:** `python migrate_to_doctype_first.py`
- **API Docs:** http://localhost:8001/docs

### Common Operations

**Upload new document:**
```bash
curl -X POST http://localhost:8001/api/documents/upload \
  -F "file=@{filename}" \
  -F "property_id={id}" \
  -F "document_type=financial_statement"
```

**List all files:**
```python
from minio import Minio
client = Minio('localhost:9000', 'minioadmin', 'minioadmin', secure=False)
for obj in client.list_objects('reims-files', prefix='Financial Statements/', recursive=True):
    print(obj.object_name)
```

---

**Last Updated:** October 19, 2025  
**Structure Version:** 2.0  
**Status:** ✅ Production Ready

