# Import Template Guide

**Version:** 1.0  
**Date:** October 20, 2025  
**Purpose:** Standard templates for importing different document types

---

## Overview

This guide provides tested templates for importing common document types into REIMS. Each template includes parsing patterns, validation criteria, and success metrics.

---

## Template 1: Rent Roll Import

### Document Type
Commercial property rent roll (PDF format)

### Expected Data Fields

| Field | Type | Required | Example |
|-------|------|----------|---------|
| `unit_number` | VARCHAR(50) | Yes | "001", "002-A", "0B" |
| `tenant_name` | VARCHAR(255) | If occupied | "Foot Locker Retail Inc" |
| `sqft` | DECIMAL(10,2) | Yes | 1312.00 |
| `lease_start` | DATE | No | "2024-01-15" |
| `lease_end` | DATE | No | "2027-01-15" |
| `monthly_rent` | DECIMAL(10,2) | No | 4536.00 |
| `status` | VARCHAR(20) | Yes | "occupied" or "vacant" |

### Parsing Patterns

**Unit Number Pattern:**
```python
# Matches: 001, 002-A, 002-B, 0B, 0C, 099, etc.
unit_pattern = r'(?:Property Name|Hammond Aire Plaza)\s+\(property_code\)(\d+[A-Z-]*)'
```

**Tenant Name Pattern:**
```python
# Tenant name appears between unit number and tenant ID
tenant_pattern = r'\(property_code\)' + unit_num + r'\s+(.+?)\s+\(t\d{7}\)'
```

**Square Footage Pattern:**
```python
# Follows "Retail NNN" or just "Retail"
sqft_pattern = r'(?:NNN|Retail)\s+(\d{1,5}(?:,\d{3})?\.?\d{0,2})'
```

**Lease Date Pattern:**
```python
# Format: MM/DD/YYYY
date_pattern = r'(\d{2}/\d{2}/\d{4})'
```

**Monthly Rent Pattern:**
```python
# Look for currency amount after area and dates
rent_pattern = r'(?:Years|Tenancy)\s*([\d,]+\.\d{2})'
```

### Validation Criteria

**Unit Count Validation:**
```python
pdf_units = len(set(re.findall(unit_pattern, full_text)))
db_units = cursor.execute("SELECT COUNT(*) FROM stores WHERE property_id = ?", (property_id,)).fetchone()[0]

assert pdf_units == db_units, f"Unit count mismatch: {pdf_units} (PDF) vs {db_units} (DB)"
```

**Tenant Name Validation:**
```python
occupied_in_pdf = len(re.findall(r'\(t\d{7}\)', full_text))
occupied_in_db = cursor.execute("SELECT COUNT(*) FROM stores WHERE property_id = ? AND status = 'occupied'", (property_id,)).fetchone()[0]

assert occupied_in_pdf == occupied_in_db, f"Occupied count mismatch"
```

**Unit Number Completeness:**
```python
pdf_unit_numbers = set(re.findall(unit_pattern, full_text))
db_unit_numbers = set([row[0] for row in cursor.execute("SELECT unit_number FROM stores WHERE property_id = ?", (property_id,))])

missing = pdf_unit_numbers - db_unit_numbers
assert len(missing) == 0, f"Missing units in DB: {missing}"
```

### Success Metrics

- ✅ **100%** unit count match (39/39 units)
- ✅ **100%** unit number match (all IDs present)
- ✅ **95%+** tenant name accuracy
- ✅ **90%+** sqft data captured
- ✅ **80%+** lease date captured
- ✅ **100%** occupancy rate calculation correct

### Code Template

```python
def import_rent_roll(property_id, minio_file_path):
    """
    Import rent roll from MinIO PDF to database
    """
    # 1. Download from MinIO
    pdf_data = download_from_minio(minio_file_path)
    
    # 2. Extract text
    full_text = extract_pdf_text(pdf_data)
    
    # 3. Parse units
    units = []
    unit_pattern = r'Property Name\s+\(code\)(\d+[A-Z-]*)\s+(.+?)(?=Property Name|$)'
    
    for unit_num, content in re.findall(unit_pattern, full_text, re.DOTALL):
        # Parse tenant data
        tenant = parse_tenant_data(unit_num, content)
        units.append(tenant)
    
    # 4. Begin transaction
    conn.begin()
    
    # 5. Insert into database
    for unit in units:
        insert_store_record(property_id, unit)
    
    # 6. Validate BEFORE committing
    validator = RentRollValidator(minio_file_path, property_id)
    validation = validator.validate_all()
    
    if not validation.passed:
        conn.rollback()
        raise ValidationError(f"Validation failed: {validation.errors}")
    
    # 7. Commit
    conn.commit()
    
    # 8. Update property aggregates
    update_property_occupancy(property_id)
    
    return validation.report
```

---

## Template 2: Financial Statement Import

### Document Type
Balance Sheet, Income Statement, Cash Flow Statement (PDF or Excel)

### Expected Data Fields

| Field | Type | Required | Example |
|-------|------|----------|---------|
| `property_id` | INTEGER | Yes | 3 |
| `document_year` | INTEGER | Yes | 2024 |
| `document_type` | VARCHAR(50) | Yes | "balance_sheet" |
| `file_path` | TEXT | Yes | "Financial Statements/2024/..." |
| `total_assets` | DECIMAL(12,2) | No | 5000000.00 |
| `total_liabilities` | DECIMAL(12,2) | No | 2000000.00 |
| `net_income` | DECIMAL(12,2) | No | 500000.00 |

### Parsing Patterns

**Year Pattern:**
```python
# Look for 4-digit year
year_pattern = r'20(2[0-9])'
year = int(re.search(year_pattern, filename).group(0))
```

**Property Name Pattern:**
```python
# Extract property name from document
property_pattern = r'Property:?\s+(.+?)(?:\n|$)'
```

**Financial Figures Pattern:**
```python
# Currency amounts
amount_pattern = r'\$?\s*([\d,]+\.?\d{0,2})'
```

### Validation Criteria

**Metadata Validation:**
```python
assert document_year >= 2020 and document_year <= 2030, "Invalid year"
assert property_id in valid_property_ids, "Unknown property"
assert document_type in ['balance_sheet', 'income_statement', 'cash_flow'], "Invalid type"
```

**Storage Path Validation:**
```python
expected_path = f"Financial Statements/{year}/{doc_type}/{filename}"
assert file_path == expected_path, f"Path mismatch: {file_path} vs {expected_path}"
```

### Success Metrics

- ✅ **100%** metadata extraction (year, property, type)
- ✅ **100%** file stored in correct MinIO location
- ✅ **100%** database record created
- ✅ **80%+** financial figures extracted (optional)

---

## Template 3: Lease Agreement Import

### Document Type
Individual tenant lease agreement (PDF)

### Expected Data Fields

| Field | Type | Required | Example |
|-------|------|----------|---------|
| `property_id` | INTEGER | Yes | 3 |
| `tenant_id` | INTEGER | Yes | 42 |
| `start_date` | DATE | Yes | "2024-01-01" |
| `end_date` | DATE | Yes | "2027-01-01" |
| `monthly_rent` | DECIMAL(10,2) | Yes | 3500.00 |
| `security_deposit` | DECIMAL(10,2) | No | 7000.00 |

### Parsing Patterns

**Date Pattern:**
```python
# Various date formats
date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})'
```

**Rent Amount Pattern:**
```python
# Look for "monthly rent" or "base rent"
rent_pattern = r'(?:monthly|base)\s+rent:?\s*\$?([\d,]+\.?\d{0,2})'
```

**Tenant Name Pattern:**
```python
# Usually at beginning of lease
tenant_pattern = r'(?:Tenant|Lessee):?\s+(.+?)(?:\n|$)'
```

### Validation Criteria

**Date Logic Validation:**
```python
assert end_date > start_date, "End date must be after start date"
assert start_date <= datetime.now(), "Start date cannot be in future"
```

**Financial Validation:**
```python
assert monthly_rent > 0, "Monthly rent must be positive"
assert security_deposit >= 0, "Security deposit cannot be negative"
```

### Success Metrics

- ✅ **100%** tenant identification
- ✅ **100%** lease dates extracted
- ✅ **100%** monthly rent captured
- ✅ **80%+** additional terms extracted

---

## Template 4: Property Document Import

### Document Type
General property documents (offering memo, inspection report, etc.)

### Expected Data Fields

| Field | Type | Required | Example |
|-------|------|----------|---------|
| `property_id` | INTEGER | Yes | 3 |
| `document_type` | VARCHAR(50) | Yes | "offering_memo" |
| `document_year` | INTEGER | No | 2024 |
| `file_path` | TEXT | Yes | "Financial Statements/..." |
| `original_filename` | VARCHAR(255) | Yes | "Hammond Aire Offering.pdf" |

### Parsing Patterns

**Property Identification:**
```python
# From filename or document content
property_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
```

**Document Type Classification:**
```python
# Keyword-based classification
if 'offering' in filename.lower():
    doc_type = 'offering_memo'
elif 'inspection' in filename.lower():
    doc_type = 'inspection_report'
```

### Validation Criteria

**File Accessibility:**
```python
assert file_exists_in_minio(file_path), "File not accessible"
assert file_size > 0, "File is empty"
```

**Metadata Completeness:**
```python
assert property_id is not None, "Property ID required"
assert document_type != '', "Document type required"
```

### Success Metrics

- ✅ **100%** file stored successfully
- ✅ **100%** metadata recorded
- ✅ **100%** file accessible after storage

---

## Common Parsing Utilities

### Text Cleaning
```python
def clean_text(text):
    """Remove excessive whitespace and normalize"""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text
```

### Date Parsing
```python
def parse_date(date_str):
    """Parse various date formats to YYYY-MM-DD"""
    formats = ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except:
            continue
    return None
```

### Currency Parsing
```python
def parse_currency(amount_str):
    """Parse currency string to decimal"""
    # Remove $ and commas
    amount_str = amount_str.replace('$', '').replace(',', '')
    try:
        return float(amount_str)
    except:
        return None
```

---

## Validation Helper Functions

### Count Validator
```python
def validate_count(expected, actual, entity_type):
    """Validate record counts match"""
    if expected != actual:
        raise ValidationError(
            f"{entity_type} count mismatch: "
            f"expected {expected}, got {actual}"
        )
    return True
```

### Completeness Validator
```python
def validate_completeness(source_ids, db_ids, entity_type):
    """Check all source IDs present in database"""
    missing = source_ids - db_ids
    if missing:
        raise ValidationError(
            f"Missing {entity_type} in database: {missing}"
        )
    return True
```

### Field Accuracy Validator
```python
def validate_field_accuracy(source_record, db_record, fields):
    """Validate specific fields match"""
    for field in fields:
        source_val = source_record.get(field)
        db_val = db_record.get(field)
        if source_val != db_val:
            logger.warning(
                f"Field mismatch: {field} "
                f"source={source_val}, db={db_val}"
            )
    return True
```

---

## Testing Your Import

### Test Checklist

Before deploying a new import:

1. **Unit Test Parsing**
   - [ ] Test with sample file
   - [ ] Verify all expected fields extracted
   - [ ] Handle edge cases

2. **Integration Test**
   - [ ] Import to test database
   - [ ] Run validation
   - [ ] Verify counts match

3. **Regression Test**
   - [ ] Re-import same file
   - [ ] Verify same results
   - [ ] No duplicates created

4. **Error Test**
   - [ ] Test with malformed file
   - [ ] Verify graceful error handling
   - [ ] Verify rollback works

---

## Best Practices Summary

1. **Always validate after import** - No exceptions
2. **Use regex carefully** - Test patterns thoroughly
3. **Handle NULL values** - Don't crash on missing data
4. **Log everything** - Debug issues faster
5. **Test with real data** - Sample files may not have all edge cases
6. **Document special cases** - Help future maintainers

---

**Remember**: These templates are starting points. Adjust parsing patterns based on your specific document formats while maintaining validation rigor.

