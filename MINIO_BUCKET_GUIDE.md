# MinIO Bucket Structure Guide

## Overview

REIMS uses a **multi-bucket architecture** in MinIO to organize different types of documents and data. This provides better organization, security, and performance.

**Total Buckets:** 8 specialized buckets  
**Status:** ✅ All buckets created and operational  
**Endpoint:** localhost:9000

---

## 📦 Bucket Structure

```
MinIO Server (localhost:9000)
│
├── 📂 reims-documents          ← Primary document storage
├── 💰 reims-financial          ← Financial documents (sensitive)
├── 📷 reims-property-photos    ← Property images and media
├── 🤖 reims-processed          ← AI-processed data
├── 📚 reims-archives           ← Historical documents
├── 💾 reims-backups            ← System backups
├── ⏳ reims-temp               ← Temporary workspace
└── 📊 reims-reports            ← Generated reports
```

---

## Bucket Descriptions

### 1. `reims-documents` (Primary)
**Purpose:** General document uploads  
**Use Cases:**
- Property leases
- Legal documents
- Contracts
- PDF reports
- General paperwork

**Document Types:**
- `.pdf` - Property documents, reports
- `.doc`, `.docx` - Word documents
- `.txt` - Text files

**Access:** Standard upload endpoint  
**Retention:** Permanent  
**Status:** ✅ Active (1 object)

---

### 2. `reims-financial` (Sensitive)
**Purpose:** Financial documents requiring special access  
**Use Cases:**
- Financial statements
- Offering memorandums
- Investment reports
- Bank statements
- Tax documents
- Balance sheets
- Income statements

**Document Types:**
- `.pdf` - Financial PDFs
- `.xlsx` - Financial spreadsheets
- `.csv` - Financial data exports

**Access:** Restricted (requires financial document permissions)  
**Retention:** 7 years (compliance)  
**Security:** Enhanced access controls  
**Status:** ✅ Ready

---

### 3. `reims-property-photos` (Media)
**Purpose:** Property images and visual assets  
**Use Cases:**
- Property photos
- Interior/exterior shots
- Before/after images
- Property condition documentation
- Marketing materials

**File Types:**
- `.jpg`, `.jpeg` - Photos
- `.png` - Images with transparency
- `.webp` - Modern image format
- `.heic` - iPhone photos

**Access:** Public read (for marketing)  
**Retention:** Permanent  
**CDN:** Can be configured for fast delivery  
**Status:** ✅ Ready

---

### 4. `reims-processed` (AI Output)
**Purpose:** Processed documents and extracted data  
**Use Cases:**
- AI-extracted data JSON files
- Processed CSV outputs
- OCR results
- Text extraction results
- Structured data from documents

**File Types:**
- `.json` - Structured data
- `.csv` - Extracted tabular data
- `.txt` - Extracted text

**Access:** System-generated  
**Retention:** Link to source document  
**Status:** ✅ Ready

---

### 5. `reims-archives` (Long-term Storage)
**Purpose:** Historical and archived documents  
**Use Cases:**
- Expired leases
- Closed properties
- Historical financial records
- Compliance archives
- Old property documentation

**Access:** Read-only (archive mode)  
**Retention:** 10+ years  
**Storage Class:** Can use cold storage tier  
**Status:** ✅ Ready

---

### 6. `reims-backups` (Disaster Recovery)
**Purpose:** System backups and redundancy  
**Use Cases:**
- Database backups
- Configuration backups
- Full system snapshots
- Disaster recovery files

**File Types:**
- `.sql` - Database dumps
- `.tar.gz` - Compressed backups
- `.zip` - Backup archives

**Access:** System only  
**Retention:** Rolling (30 days)  
**Automation:** Scheduled via cron/PowerShell  
**Status:** ✅ Ready

---

### 7. `reims-temp` (Processing Workspace)
**Purpose:** Temporary files during processing  
**Use Cases:**
- File conversions
- Processing intermediates
- Upload staging
- Thumbnail generation
- Format conversions

**File Types:** All (temporary)

**Access:** System only  
**Retention:** Auto-delete after 24 hours  
**Cleanup:** Automated cleanup job  
**Status:** ✅ Ready

---

### 8. `reims-reports` (Generated Reports)
**Purpose:** User-generated reports and analytics  
**Use Cases:**
- Dashboard exports
- Custom reports
- Analytics PDFs
- Excel exports
- Data exports

**File Types:**
- `.pdf` - Report PDFs
- `.xlsx` - Excel reports
- `.csv` - Data exports
- `.json` - API exports

**Access:** User-specific  
**Retention:** 90 days  
**Status:** ✅ Ready

---

## Bucket Selection Logic

### Upload Routing
Documents are automatically routed to the appropriate bucket based on type:

```python
def get_bucket_for_document(document_type, content_type):
    """Determine which bucket to use"""
    
    # Financial documents
    if document_type in ['financial_statement', 'offering_memorandum', 'bank_statement']:
        return 'reims-financial'
    
    # Images
    if content_type.startswith('image/'):
        return 'reims-property-photos'
    
    # Processed data
    if document_type == 'processed' or content_type == 'application/json':
        return 'reims-processed'
    
    # Archives
    if document_type == 'archive':
        return 'reims-archives'
    
    # Reports
    if document_type == 'report':
        return 'reims-reports'
    
    # Default: general documents
    return 'reims-documents'
```

---

## Access Patterns

### By Document Type

| Document Type | Bucket | Access Level |
|---------------|--------|--------------|
| Lease Agreement | reims-documents | Standard |
| Financial Statement | reims-financial | Restricted |
| Property Photo | reims-property-photos | Public Read |
| Inspection Report | reims-documents | Standard |
| Tax Document | reims-financial | Restricted |
| AI Extracted Data | reims-processed | System |
| Historical Lease | reims-archives | Read-only |
| User Report | reims-reports | User-specific |

### By User Role

| Role | Access |
|------|--------|
| **Admin** | All buckets (read/write) |
| **Property Manager** | documents, photos, reports (read/write) |
| **Accountant** | financial, documents (read/write) |
| **Tenant** | documents (read-only assigned docs) |
| **System** | All buckets (read/write) |

---

## Storage Policies

### Lifecycle Rules

```
reims-temp:        Delete after 24 hours
reims-reports:     Delete after 90 days
reims-backups:     Keep last 30 days
reims-documents:   Permanent
reims-financial:   7 years retention
reims-archives:    10+ years retention
```

### Versioning

```
reims-financial:   ✅ Enabled (audit trail)
reims-documents:   ✅ Enabled (track changes)
reims-backups:     ✅ Enabled (safety)
reims-temp:        ❌ Disabled (temporary)
reims-reports:     ❌ Disabled (regeneratable)
```

---

## Environment Configuration

### `.env` Setup

```bash
# MinIO Buckets
MINIO_BUCKET_DOCUMENTS=reims-documents
MINIO_BUCKET_FINANCIAL=reims-financial
MINIO_BUCKET_PHOTOS=reims-property-photos
MINIO_BUCKET_PROCESSED=reims-processed
MINIO_BUCKET_ARCHIVES=reims-archives
MINIO_BUCKET_BACKUPS=reims-backups
MINIO_BUCKET_TEMP=reims-temp
MINIO_BUCKET_REPORTS=reims-reports
```

### Python Usage

```python
import os
from minio import Minio

# Get bucket based on document type
financial_bucket = os.getenv('MINIO_BUCKET_FINANCIAL', 'reims-financial')

# Upload financial document
client.put_object(
    financial_bucket,
    object_name,
    data,
    length
)
```

---

## Management Commands

### Create All Buckets
```bash
python setup_minio_buckets.py
```

### List All Buckets
```bash
# PowerShell
curl http://localhost:9000

# Python
python -c "from minio import Minio; c=Minio('localhost:9000','minioadmin','minioadmin',secure=False); print([b.name for b in c.list_buckets()])"
```

### Check Bucket Contents
```python
python -c "
from minio import Minio
c = Minio('localhost:9000', 'minioadmin', 'minioadmin', secure=False)
for bucket in c.list_buckets():
    objects = list(c.list_objects(bucket.name, recursive=True))
    print(f'{bucket.name}: {len(objects)} objects')
"
```

### Bucket Statistics
```bash
python -c "
from minio import Minio
c = Minio('localhost:9000', 'minioadmin', 'minioadmin', secure=False)
for bucket in c.list_buckets():
    objects = list(c.list_objects(bucket.name, recursive=True))
    total_size = sum(obj.size for obj in objects)
    print(f'{bucket.name}:')
    print(f'  Objects: {len(objects)}')
    print(f'  Size: {total_size / 1024 / 1024:.2f} MB')
"
```

---

## Best Practices

### 1. Use Correct Bucket
- Always route documents to the appropriate bucket
- Don't mix document types in wrong buckets
- Use temp bucket for processing intermediates

### 2. Security
- Financial documents require additional access controls
- Use bucket policies for public/private access
- Implement role-based access control (RBAC)

### 3. Performance
- Use appropriate bucket for access patterns
- Leverage CDN for property photos
- Use temp bucket for frequent read/write operations

### 4. Maintenance
- Regular cleanup of temp bucket
- Monitor storage usage
- Archive old documents to archives bucket
- Implement lifecycle policies

---

## Monitoring

### Health Check
```bash
python -c "
from minio import Minio
c = Minio('localhost:9000', 'minioadmin', 'minioadmin', secure=False)
try:
    buckets = c.list_buckets()
    print(f'✅ MinIO healthy: {len(buckets)} buckets')
except Exception as e:
    print(f'❌ MinIO error: {e}')
"
```

### Storage Usage Dashboard
Access MinIO Console: http://localhost:9000  
Login: minioadmin / minioadmin

---

## Troubleshooting

### Bucket Not Found
```bash
# Recreate bucket
python setup_minio_buckets.py
```

### Permission Denied
```bash
# Check MinIO credentials in .env
# Verify MINIO_ACCESS_KEY and MINIO_SECRET_KEY
```

### Slow Performance
- Check if using correct bucket for access pattern
- Consider using CDN for photos
- Verify network connection

---

## Migration Guide

### From Single Bucket to Multi-Bucket

```python
# migrate_to_multi_bucket.py
from minio import Minio
import os

client = Minio('localhost:9000', 'minioadmin', 'minioadmin', secure=False)

# Get all objects from old bucket
old_bucket = 'reims-documents'
objects = client.list_objects(old_bucket, recursive=True)

for obj in objects:
    # Determine new bucket based on filename/type
    if 'financial' in obj.object_name:
        new_bucket = 'reims-financial'
    elif any(ext in obj.object_name for ext in ['.jpg', '.png']):
        new_bucket = 'reims-property-photos'
    else:
        new_bucket = 'reims-documents'
    
    # Copy to new bucket if different
    if new_bucket != old_bucket:
        client.copy_object(
            new_bucket,
            obj.object_name,
            f"{old_bucket}/{obj.object_name}"
        )
        print(f"Moved {obj.object_name} to {new_bucket}")
```

---

## Summary

✅ **8 specialized buckets** for organized document management  
✅ **Automatic routing** based on document type  
✅ **Security policies** for sensitive financial data  
✅ **Performance optimization** with appropriate bucket selection  
✅ **Lifecycle management** for automated cleanup  
✅ **Ready for production** use

**All buckets created and operational!**

---

**Last Updated:** October 11, 2025  
**Created By:** `setup_minio_buckets.py`  
**Status:** ✅ Production Ready

















