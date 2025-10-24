# Data Import & Validation Standard Operating Procedure

**Version:** 1.0  
**Date:** October 20, 2025  
**Purpose:** Ensure first-time accuracy for all data imports from MinIO to database

---

## Overview

This procedure ensures that all data imported from MinIO files into the REIMS database is accurate, complete, and validated before being considered "complete". This prevents issues like the Hammond Aire discrepancy (32 vs 39 units).

---

## Pre-Import Checklist

Before importing any data from a MinIO file, verify:

### 1. File Validation
- [ ] File exists in MinIO at expected path
- [ ] File is not corrupted (can be opened/read)
- [ ] File size is reasonable (not 0 bytes or suspiciously large)
- [ ] File format matches expected type (PDF, Excel, CSV, etc.)

### 2. Property Setup
- [ ] Property exists in database with valid ID
- [ ] Property has correct name and address
- [ ] Property type is set correctly
- [ ] No duplicate property records exist

### 3. Document Metadata
- [ ] Document year is identified
- [ ] Document type is classified correctly
- [ ] Document period (month/quarter) is known
- [ ] Property ID is confirmed

### 4. Database State
- [ ] Check for existing data that will be replaced
- [ ] Backup current data if overwriting
- [ ] Database has capacity for new records
- [ ] No database locks or ongoing transactions

---

## Import Process

### Step 1: Extract Data from MinIO File

**For Rent Rolls:**
```python
1. Download PDF from MinIO
2. Extract all text using PyPDF2
3. Parse unit entries using regex patterns
4. Extract for each unit:
   - Unit number (ALL variations: 001, 002-A, 0B, etc.)
   - Tenant name (if occupied)
   - Square footage
   - Lease dates (start/end)
   - Monthly rent
   - Status (occupied/vacant)
5. Count total unique units
6. Count occupied units (with tenant IDs)
7. Count vacant units
```

**For Financial Statements:**
```python
1. Download file from MinIO
2. Extract financial data
3. Parse key metrics
4. Validate calculations
5. Extract metadata (year, period, property)
```

### Step 2: Prepare Database Records

```python
1. Generate UUIDs for new records
2. Format dates to ISO format (YYYY-MM-DD)
3. Handle NULL values appropriately
4. Set default values for missing optional fields
5. Validate foreign keys (property_id exists)
```

### Step 3: Insert into Database

```python
1. Begin transaction
2. Insert all records
3. DO NOT commit yet - validation first
4. Keep transaction open for rollback if needed
```

### Step 4: Validate Import (MANDATORY)

**This step is CRITICAL and must not be skipped.**

```python
1. Run validation against source file
2. Compare counts (units, tenants, etc.)
3. Verify all source records in database
4. Check for missing records
5. Validate field accuracy
6. Generate validation report
```

### Step 5: Review Validation Results

**If validation PASSES:**
```python
1. Commit transaction
2. Update property-level aggregates
3. Log successful import
4. Save validation report
5. Proceed to next step
```

**If validation FAILS:**
```python
1. Rollback transaction
2. Log all discrepancies
3. Investigate parsing issues
4. Fix extraction logic
5. Start over from Step 1
6. DO NOT proceed with bad data
```

### Step 6: Update Property Aggregates

```python
1. Count total units from stores table
2. Count occupied units
3. Calculate occupancy rate
4. Update properties table
5. Set updated_at timestamp
```

### Step 7: Final Verification

```python
1. Query property record
2. Verify totals match imported data
3. Spot-check random records
4. Confirm no data loss
```

---

## Validation Requirements

### Mandatory Validations

Every import MUST validate:

1. **Count Validation**
   - Total records in source vs database
   - Example: 39 units in PDF = 39 records in stores table
   
2. **Completeness Validation**
   - All source identifiers present in database
   - Example: All unit numbers from PDF exist in stores

3. **Accuracy Validation**
   - Sample random records and compare field values
   - Tenant names, sqft, dates match source

4. **Aggregate Validation**
   - Property-level totals match detail records
   - Occupancy rate calculation correct

### Validation Thresholds

- **100% count match required** - No tolerance for missing records
- **100% identifier match required** - All IDs must be present
- **95% field accuracy required** - Allow minor parsing variations
- **100% aggregate match required** - Totals must be exact

---

## Error Handling

### Common Errors and Solutions

#### Error: Unit Count Mismatch
```
PDF shows 39 units, database has 32 units
```

**Solution:**
1. Re-parse PDF with verbose logging
2. Check for units with non-standard formats (0B, 0C, etc.)
3. Look for units on summary pages
4. Update parser to handle all formats
5. Re-run import
6. Validate count matches

#### Error: Missing Tenant Data
```
Tenant name not extracted for occupied unit
```

**Solution:**
1. Review PDF text extraction
2. Check for multi-line tenant names
3. Verify regex patterns capture all formats
4. Add special case handling
5. Re-import affected records

#### Error: Date Format Issues
```
Lease dates not parsing correctly
```

**Solution:**
1. Identify source date format (MM/DD/YYYY vs DD/MM/YYYY)
2. Add date parsing logic with format detection
3. Handle missing dates gracefully
4. Set NULL for unparseable dates with warning

#### Error: Duplicate Records
```
Unit already exists in database
```

**Solution:**
1. Check if this is a re-import or update
2. Delete old records if intentional re-import
3. Update existing records if refresh
4. Prevent accidental duplicates

---

## Rollback Procedures

### When to Rollback

Rollback immediately if:
- Validation fails
- Count mismatch detected
- Critical data missing
- Database constraint violations
- Unexpected errors during import

### How to Rollback

**Within Transaction:**
```python
try:
    # Import data
    # Validate
    if not validation.passed:
        raise ValidationError("Import validation failed")
    conn.commit()
except:
    conn.rollback()
    logger.error("Import rolled back")
```

**After Commit (Emergency):**
```python
1. Restore from backup
2. Or delete by timestamp:
   DELETE FROM stores 
   WHERE property_id = X 
   AND created_at > 'import_start_time'
   
3. Reset property aggregates
4. Investigate and fix issue
5. Re-import correctly
```

---

## Quality Assurance

### Before Declaring Import "Complete"

Verify ALL of the following:

- [ ] Validation report shows 100% PASS
- [ ] All counts match source file
- [ ] Random spot-checks pass
- [ ] Property aggregates updated
- [ ] No error logs generated
- [ ] Validation report saved
- [ ] Import logged in audit trail

### Documentation Requirements

For each import, document:

1. **Source file**: MinIO path
2. **Import date/time**: When performed
3. **Records imported**: Count by type
4. **Validation results**: Pass/Fail with details
5. **Any issues**: Problems encountered and resolved
6. **Performed by**: User/script that ran import

---

## Best Practices

### DO:
- ✅ Always validate after import
- ✅ Test parser on sample data first
- ✅ Use verbose logging during development
- ✅ Keep validation reports for audit
- ✅ Document any parser customizations
- ✅ Handle edge cases explicitly
- ✅ Use transactions for atomicity

### DON'T:
- ❌ Skip validation "just this once"
- ❌ Commit without verifying counts
- ❌ Ignore parsing warnings
- ❌ Proceed with known discrepancies
- ❌ Delete validation reports
- ❌ Use hard-coded values
- ❌ Assume all files have same format

---

## Audit Trail

### What to Log

```python
{
    "import_id": "uuid",
    "timestamp": "2025-10-20T12:00:00Z",
    "property_id": 3,
    "property_name": "Hammond Aire",
    "file_path": "Financial Statements/2025/Rent Rolls/Hammond Rent Roll April 2025.pdf",
    "document_type": "rent_roll",
    "records_imported": 39,
    "validation_status": "PASS",
    "discrepancies": [],
    "import_duration": "3.2 seconds",
    "performed_by": "auto_import_service"
}
```

### Where to Store

- Database table: `import_audit_log`
- File system: `logs/imports/YYYY-MM-DD_import_log.json`
- Both for redundancy

---

## Success Metrics

Track these metrics for all imports:

- **First-time success rate**: % of imports that pass validation first try
- **Average discrepancy count**: How many issues per import
- **Validation pass rate**: % that pass validation overall
- **Time to validate**: How long validation takes
- **Rollback frequency**: How often we need to rollback

**Target**: 95% first-time success rate within 3 months

---

## Contact & Support

If validation fails repeatedly:

1. Review parser logic
2. Check PDF format variations
3. Consult this procedure
4. Review validation logs
5. Update parser for new edge cases
6. Document solution for future reference

---

**Remember**: The goal is accuracy on first import. Take time to validate properly rather than fix issues later.

