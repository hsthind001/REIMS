# Database Schema Analysis - Property Name & Year

**Date:** October 13, 2025  
**Status:** ❌ **NOT IMPLEMENTED** - Critical metadata missing

---

## Current Database Schema

### ✅ Documents Table (EXISTS)
```
Column Name              Type            
------------------------  ---------------
id                       UUID (PK)
document_id              VARCHAR
original_filename        VARCHAR         ✅ Has filename like "ESP 2024 Income Statement.pdf"
stored_filename          VARCHAR
property_id              VARCHAR         ❌ Only has UUID/random ID, not actual name
file_size                INTEGER
content_type             VARCHAR
file_path                VARCHAR
upload_timestamp         DATETIME
status                   VARCHAR
minio_bucket             TEXT
minio_object_name        TEXT
minio_url                TEXT
storage_type             TEXT
minio_upload_timestamp   DATETIME
```

**Missing Columns:**
- ❌ `property_name` - Actual property name (e.g., "Empire State Plaza")
- ❌ `document_year` - Year of financial data (e.g., 2024)
- ❌ `document_type` - Type classification (Income Statement, Balance Sheet, etc.)
- ❌ `document_period` - Period (Annual, Q1, Q2, etc.)

### ✅ Financial_Documents Table (EXISTS)
```
Column Name              Type            
------------------------  ---------------
id                       TEXT (PK)
property_id              TEXT            ❌ Only UUID, not property name
file_path                TEXT
file_name                TEXT            ✅ Has filename
document_type            TEXT            ✅ HAS DOCUMENT TYPE! (But not populated)
status                   TEXT
upload_date              TIMESTAMP
processing_date          TIMESTAMP
error_message            TEXT
created_at               TIMESTAMP
processing_status        TEXT
```

**Good News:**
- ✅ Has `document_type` column already!

**Still Missing:**
- ❌ `property_name` - Actual property name
- ❌ `document_year` - Year of financial data
- ❌ `document_period` - Period specification

### ✅ Properties Table (EXISTS)
```python
class Property(Base):
    property_id = Column(String)      # UUID or code
    address = Column(String)          # Could store address
    property_type = Column(String)    # residential, commercial
    value = Column(Float)
    property_metadata = Column(JSON)  # Could store additional data
```

**Issue:** Not linked to documents! No property NAME field.

---

## What's Missing vs What We Have

### Metadata We NEED for ESP Files:
```
ESP 2024 Income Statement.pdf
├── property_name: "Empire State Plaza" or "ESP"
├── document_year: 2024
├── document_type: "Income Statement"
└── document_period: "Annual"
```

### What's CURRENTLY Stored:
```
✅ original_filename: "ESP 2024 Income Statement.pdf"
✅ document_type: (column exists in financial_documents, but NULL)
❌ property_name: (not captured at all)
❌ document_year: (not captured at all)
❌ document_period: (not captured at all)
```

---

## Required Database Changes

### Option 1: Update `documents` Table (Recommended)
```sql
-- Add missing columns to documents table
ALTER TABLE documents 
ADD COLUMN property_name VARCHAR(255),
ADD COLUMN document_year INTEGER,
ADD COLUMN document_type VARCHAR(100),
ADD COLUMN document_period VARCHAR(50) DEFAULT 'Annual';

-- Create indexes for fast filtering
CREATE INDEX idx_documents_property_name ON documents(property_name);
CREATE INDEX idx_documents_year ON documents(document_year);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_prop_year ON documents(property_name, document_year);
```

### Option 2: Update `financial_documents` Table (Alternative)
```sql
-- Add missing columns to financial_documents table
ALTER TABLE financial_documents 
ADD COLUMN property_name VARCHAR(255),
ADD COLUMN document_year INTEGER,
ADD COLUMN document_period VARCHAR(50) DEFAULT 'Annual';

-- Update existing document_type column usage
-- Create indexes
CREATE INDEX idx_fin_docs_property_name ON financial_documents(property_name);
CREATE INDEX idx_fin_docs_year ON financial_documents(document_year);
CREATE INDEX idx_fin_docs_prop_year ON financial_documents(property_name, document_year);
```

### Option 3: New `document_metadata` Table (Over-engineered)
```sql
-- Create separate metadata table
CREATE TABLE document_metadata (
    id UUID PRIMARY KEY,
    document_id VARCHAR REFERENCES documents(document_id),
    property_name VARCHAR(255),
    property_full_name VARCHAR(500),
    document_year INTEGER,
    document_type VARCHAR(100),
    document_period VARCHAR(50),
    fiscal_year_start DATE,
    fiscal_year_end DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Backend ORM Model Changes

### Update Document Model (database.py)
```python
class Document(Base):
    __tablename__ = "documents"
    
    # ... existing fields ...
    
    # NEW FIELDS
    property_name = Column(String(255), index=True, nullable=True)
    document_year = Column(Integer, index=True, nullable=True)
    document_type = Column(String(100), nullable=True)
    document_period = Column(String(50), default="Annual")
```

---

## MinIO Structure

### Current MinIO Path:
```
bucket: reims-documents
path: {property_id}/{safe_filename}
example: reims-documents/550e8400-e29b-41d4/abc123_ESP 2024 Income Statement.pdf
```

### Recommended MinIO Path (After Implementation):
```
bucket: reims-documents
path: {property_name}/{year}/{document_type}/{safe_filename}
example: reims-documents/ESP/2024/Income_Statement/abc123_ESP_2024_Income_Statement.pdf
```

**Benefits:**
- Easy to browse by property
- Easy to browse by year
- Easy to browse by document type
- Better organization
- Better for backup/archival

---

## Impact Analysis

### What CANNOT Be Done Currently:

1. ❌ **Filter KPIs by Property**
   ```javascript
   // CANNOT DO THIS:
   fetch('/api/kpis/financial?property=ESP&year=2024')
   ```

2. ❌ **Year-over-Year Comparison**
   ```javascript
   // CANNOT DO THIS:
   fetch('/api/kpis/comparison?property=ESP&years=2023,2024')
   ```

3. ❌ **Property-Specific Dashboard**
   ```javascript
   // CANNOT DO THIS:
   const espData = documents.filter(d => d.property_name === 'ESP')
   ```

4. ❌ **Financial Reporting**
   ```sql
   -- CANNOT DO THIS:
   SELECT * FROM extracted_data 
   WHERE property_name = 'ESP' 
   AND document_year = 2024
   AND document_type = 'Income Statement'
   ```

### What Happens Instead:

✅ Files are uploaded
✅ Files are stored in MinIO
✅ Metadata saved to database
❌ **But all data is MIXED together!**
- ESP 2024 data + ESP 2023 data + Other property data = One big mess
- No way to separate "ESP 2024" from "Other Property 2023"
- KPIs show aggregate of ALL properties and ALL years

---

## Recommendation

### Implement Option 1: Update `documents` Table

**Why:**
1. `documents` table is the primary source of truth
2. Already has relationships to `processing_jobs` and `extracted_data`
3. Simpler than creating new table
4. Maintains existing architecture

**Steps:**
1. ✅ Create database migration script
2. ✅ Update ORM model (`backend/database.py`)
3. ✅ Update upload endpoint to accept new fields
4. ✅ Update frontend form to capture new fields
5. ✅ Add filename parsing as fallback/suggestion
6. ✅ Update KPI endpoints to filter by property/year

---

## Current Status

### Database Schema:
- ❌ **NOT READY** for property name and year tracking
- ✅ Has `document_type` in `financial_documents` (but unused)
- ❌ Missing `property_name` column
- ❌ Missing `document_year` column
- ❌ Missing `document_period` column

### MinIO Structure:
- ❌ **NOT OPTIMIZED** for property/year organization
- Current: `{property_id}/{filename}`
- Needed: `{property_name}/{year}/{type}/{filename}`

### Impact:
- **HIGH** - Cannot meaningfully analyze financial data without property and year context
- All uploaded data gets mixed together
- No way to generate property-specific or year-specific reports
- KPIs are meaningless aggregates

---

## Summary

**Question:** Is this implemented in database and MinIO?

**Answer:** ❌ **NO**

**Details:**
1. Database has `document_type` column but **NOT** `property_name` or `document_year`
2. MinIO path structure does not organize by property name or year
3. Cannot filter or separate data by property or year
4. Critical gap for financial analysis

**Required:** Implement database schema changes + update upload workflow

---

**Status:** ❌ Gap Identified - Implementation Required  
**Priority:** 🔴 HIGH - Blocking meaningful financial analysis  
**Estimated Effort:** 6-8 hours (full implementation)



