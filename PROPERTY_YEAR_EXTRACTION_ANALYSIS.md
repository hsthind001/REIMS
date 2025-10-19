# Property Name and Year Extraction - Gap Analysis

**Date:** October 13, 2025  
**Issue:** Files uploaded contain property name and year in filename, but we're not extracting or storing this metadata

---

## Current Workflow

### 1. Frontend Upload
```javascript
// SimpleDashboard.jsx line 56
formData.append('property_id', 'PROP-' + Math.floor(Math.random() * 1000));
```

**Problem:** Random property ID generated, doesn't capture actual property name!

```javascript
// ProfessionalExecutiveApp.jsx line 813
formData.append('property_id', propertyId.trim());
```

**Problem:** User manually enters property_id, but no field for:
- Property Name
- Year of Financial Data

### 2. Backend Upload Processing
```python
# backend/api/upload.py line 37-40
async def upload_document(
    file: UploadFile = File(...), 
    property_id: str = Form(...),
    db: Session = Depends(get_db)
):
```

**Problem:** Only captures `property_id`, not property name or year!

### 3. Database Schema
```python
# backend/database.py - Document model
class Document(Base):
    document_id = Column(String, primary_key=True)
    original_filename = Column(String, nullable=False)  # ESP 2024 Income Statement.pdf
    property_id = Column(String, nullable=False)        # Random ID or user input
    # ... other fields
```

**Missing Fields:**
- `property_name` - Actual property name (e.g., "Empire State Plaza")
- `document_year` - Year the financial data represents (e.g., 2024)
- `document_period` - Period type (annual, quarterly, monthly)

### 4. Document Processor
```python
# queue_service/document_processor.py
def process_csv(self, file_path: str, metadata: dict) -> dict:
    # Processes file content
    # Does NOT extract property name or year from filename
```

**Problem:** No logic to parse filename for property name and year!

---

## Example Files Analysis

### ESP 2024 Income Statement.pdf
- **Property Name:** ESP (Empire State Plaza - assumed)
- **Year:** 2024
- **Document Type:** Income Statement
- **Period:** Annual (assumed)

### ESP 2024 Cash Flow Statement.pdf
- **Property Name:** ESP  
- **Year:** 2024
- **Document Type:** Cash Flow Statement
- **Period:** Annual

### ESP 2024 Balance Sheet.pdf
- **Property Name:** ESP
- **Year:** 2024  
- **Document Type:** Balance Sheet
- **Period:** Annual

---

## What We're Missing

### 1. **Frontend Upload Form** ❌
No fields for:
- Property Name (text input)
- Document Year (number/dropdown: 2020-2025)
- Document Period (dropdown: Annual/Q1/Q2/Q3/Q4/Monthly)
- Document Type (dropdown: Income Statement/Balance Sheet/Cash Flow)

### 2. **Filename Parsing Logic** ❌
No automatic extraction of:
```
"ESP 2024 Income Statement.pdf" →
{
  property_name: "ESP",
  document_year: 2024,
  document_type: "Income Statement"
}
```

### 3. **Database Storage** ❌
Missing columns in `documents` or `financial_documents` table:
- `property_name VARCHAR(255)`
- `document_year INTEGER`
- `document_period VARCHAR(50)` (Annual/Q1/Q2/Q3/Q4/Jan-Dec)
- `document_type VARCHAR(100)` (Income Statement, Balance Sheet, etc.)

### 4. **KPI Filtering** ❌
Cannot query data by:
```sql
SELECT * FROM financial_data 
WHERE property_name = 'ESP' 
AND document_year = 2024
AND document_type = 'Income Statement'
```

---

## Impact on Frontend

### Current Dashboard Display
```javascript
// Cannot filter by property or year!
const kpiData = await fetch('/api/kpis/financial');

// Shows aggregate data from ALL properties and ALL years mixed together
```

### What Users Need
```javascript
// Filter by specific property and year
const kpiData = await fetch('/api/kpis/financial?property=ESP&year=2024');

// Show year-over-year comparison
const comparison = await fetch('/api/kpis/comparison?property=ESP&years=2023,2024');

// Filter by document type
const incomeStatements = await fetch('/api/documents?type=Income Statement&year=2024');
```

---

## Recommended Solution

### Option 1: Enhanced Upload Form (RECOMMENDED)

**Frontend Changes:**
```jsx
<form onSubmit={handleUpload}>
  {/* File Selection */}
  <input type="file" onChange={handleFileSelect} />
  
  {/* NEW FIELDS */}
  <input 
    type="text" 
    placeholder="Property Name (e.g., Empire State Plaza)"
    value={propertyName}
    onChange={(e) => setPropertyName(e.target.value)}
    required
  />
  
  <select value={documentYear} onChange={(e) => setDocumentYear(e.target.value)}>
    <option value="">Select Year</option>
    <option value="2024">2024</option>
    <option value="2023">2023</option>
    <option value="2022">2022</option>
  </select>
  
  <select value={documentType} onChange={(e) => setDocumentType(e.target.value)}>
    <option value="">Select Document Type</option>
    <option value="Income Statement">Income Statement</option>
    <option value="Balance Sheet">Balance Sheet</option>
    <option value="Cash Flow Statement">Cash Flow Statement</option>
    <option value="Offering Memorandum">Offering Memorandum</option>
  </select>
  
  <select value={documentPeriod} onChange={(e) => setDocumentPeriod(e.target.value)}>
    <option value="Annual">Annual</option>
    <option value="Q1">Q1</option>
    <option value="Q2">Q2</option>
    <option value="Q3">Q3</option>
    <option value="Q4">Q4</option>
  </select>
  
  <button type="submit">Upload</button>
</form>
```

**Backend Changes:**
```python
@router.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...), 
    property_id: str = Form(...),
    property_name: str = Form(...),        # NEW
    document_year: int = Form(...),        # NEW
    document_type: str = Form(...),        # NEW
    document_period: str = Form("Annual"), # NEW
    db: Session = Depends(get_db)
):
    # Save all metadata to database
    db_document = Document(
        document_id=doc_id,
        original_filename=file.filename,
        property_id=property_id,
        property_name=property_name,         # NEW
        document_year=document_year,         # NEW
        document_type=document_type,         # NEW
        document_period=document_period,     # NEW
        # ... other fields
    )
```

**Database Migration:**
```sql
-- Add new columns to documents table
ALTER TABLE documents 
ADD COLUMN property_name VARCHAR(255),
ADD COLUMN document_year INTEGER,
ADD COLUMN document_type VARCHAR(100),
ADD COLUMN document_period VARCHAR(50) DEFAULT 'Annual';

-- Create index for fast filtering
CREATE INDEX idx_documents_property_year ON documents(property_name, document_year);
CREATE INDEX idx_documents_type ON documents(document_type);
```

### Option 2: Automatic Filename Parsing

**Filename Parser:**
```python
import re
from typing import Dict, Optional

def parse_filename(filename: str) -> Dict[str, any]:
    """
    Parse financial document filename for metadata
    
    Examples:
        "ESP 2024 Income Statement.pdf" → {property: "ESP", year: 2024, type: "Income Statement"}
        "Empire State 2023 Q1 Balance Sheet.xlsx" → {property: "Empire State", year: 2023, period: "Q1", type: "Balance Sheet"}
    """
    result = {
        "property_name": None,
        "document_year": None,
        "document_type": None,
        "document_period": "Annual"
    }
    
    # Extract year (4-digit number)
    year_match = re.search(r'\b(20\d{2})\b', filename)
    if year_match:
        result["document_year"] = int(year_match.group(1))
    
    # Extract period (Q1, Q2, Q3, Q4, or month names)
    period_match = re.search(r'\b(Q[1-4]|January|February|March|April|May|June|July|August|September|October|November|December)\b', filename, re.IGNORECASE)
    if period_match:
        result["document_period"] = period_match.group(1)
    
    # Extract document type
    doc_types = [
        "Income Statement", "Balance Sheet", "Cash Flow Statement",
        "Offering Memorandum", "Rent Roll", "Operating Statement",
        "P&L", "Profit and Loss"
    ]
    for doc_type in doc_types:
        if doc_type.lower() in filename.lower():
            result["document_type"] = doc_type
            break
    
    # Extract property name (everything before the year)
    if year_match:
        property_part = filename[:year_match.start()].strip()
        # Remove file extension if present
        property_part = re.sub(r'\.(pdf|xlsx?|csv)$', '', property_part, flags=re.IGNORECASE)
        result["property_name"] = property_part
    
    return result

# Usage in upload endpoint:
def upload_document(file: UploadFile, ...):
    # Auto-parse filename
    parsed = parse_filename(file.filename)
    
    # Use parsed data as defaults, can be overridden by form data
    property_name = property_name_form or parsed["property_name"]
    document_year = document_year_form or parsed["document_year"]
    document_type = document_type_form or parsed["document_type"]
```

### Option 3: Hybrid Approach (BEST)

1. **Parse filename** automatically for suggestions
2. **Show parsed values** in upload form for user to confirm/edit
3. **Require user confirmation** before saving
4. **Learn from corrections** to improve parsing

---

## Implementation Priority

### Phase 1: Database Schema (Required First)
1. Add new columns to `documents` table
2. Create migration script
3. Update ORM models

### Phase 2: Backend API (Required Second)
1. Update upload endpoint to accept new fields
2. Add filename parsing logic
3. Update validation rules

### Phase 3: Frontend Form (Required Third)
1. Add input fields for metadata
2. Implement auto-fill from filename parsing
3. Add validation

### Phase 4: KPI Filtering (Enhancement)
1. Update KPI endpoints to filter by property/year
2. Add comparison endpoints
3. Update dashboard to use filters

---

## Immediate Action Required

To process the ESP 2024 files correctly, you need to:

1. **Add form fields** to capture:
   - Property Name: "Empire State Plaza" (or "ESP")
   - Document Year: 2024
   - Document Type: "Income Statement" / "Cash Flow Statement" / "Balance Sheet"

2. **Store this metadata** in the database so KPIs can filter by:
   - Property: ESP
   - Year: 2024
   - Type: Income Statement

3. **Update frontend dashboards** to show:
   - "ESP 2024 Income Statement Data"
   - "ESP 2024 vs 2023 Comparison"
   - "All Properties 2024 Summary"

---

## Current State Summary

✅ **What Works:**
- File upload to MinIO
- Document processing (reading PDF/CSV/Excel)
- Data extraction to database

❌ **What's Missing:**
- Property name capture
- Document year capture
- Document type classification
- Period identification
- Ability to filter KPIs by property/year
- Year-over-year comparisons

---

**Status:** Gap Identified - Needs Implementation  
**Priority:** HIGH - Critical for meaningful financial analysis  
**Estimated Effort:** 4-6 hours (database + backend + frontend changes)



