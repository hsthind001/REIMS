# Validation Usage Examples

**Version:** 1.0  
**Date:** October 20, 2025  
**Purpose:** Practical examples for using the validation system

---

## Overview

This guide provides practical examples of how to use the REIMS validation system to ensure data imports are accurate.

---

## Example 1: Validate Rent Roll Import

### Scenario
You've just imported Hammond Aire's rent roll from MinIO into the database. You want to verify that all 39 units were imported correctly.

### Using CLI Tool

```bash
python validate_import.py \
  --property-id 3 \
  --document-type rent_roll \
  --file "Financial Statements/2025/Rent Rolls/Hammond Rent Roll April 2025.pdf"
```

### Expected Output

```
================================================================================
RENT ROLL VALIDATION
Property ID: 3
File: Financial Statements/2025/Rent Rolls/Hammond Rent Roll April 2025.pdf
================================================================================

✅ total_units count: expected 39, got 39
✅ occupied_units count: expected 33, got 33
✅ Occupancy rate: stored 84.6%, calculated 84.6%
✅ unit_numbers completeness: 39/39 present

✅ ALL VALIDATIONS PASSED

================================================================================
VALIDATION SUMMARY
================================================================================
Status: ✅ PASS
Validations run: 4
Passed: 4
Failed: 0
Errors: 0
Warnings: 0
================================================================================

✅ VALIDATION PASSED - Import is accurate
```

### Using Python API

```python
from backend.utils.rentroll_validator import RentRollValidator

# Create validator
validator = RentRollValidator(
    minio_file_path="Financial Statements/2025/Rent Rolls/Hammond Rent Roll April 2025.pdf",
    property_id=3
)

# Run validation
report = validator.validate_all()

# Check results
if report.passed:
    print("✅ Validation passed!")
else:
    print("❌ Validation failed!")
    for error in report.errors:
        print(f"  Error: {error}")

# Save report
validator.save_report("validation_report_hammond.json")
```

---

## Example 2: Detect Missing Units

### Scenario
After importing a rent roll, you suspect some units might be missing from the database.

### Code

```python
from backend.utils.rentroll_validator import RentRollValidator

validator = RentRollValidator(
    minio_file_path="Financial Statements/2025/Rent Rolls/Property Rent Roll.pdf",
    property_id=5
)

# Check for missing units specifically
missing_units = validator.check_missing_units()

if missing_units:
    print(f"❌ Missing {len(missing_units)} units in database:")
    for unit in missing_units:
        print(f"  - Unit {unit}")
else:
    print("✅ All units present in database")
```

### Output

```
❌ Missing 7 units in database:
  - Unit 009-A
  - Unit 015
  - Unit 0B
  - Unit 0C
  - Unit 0D
  - Unit 0F
  - Unit 0G
```

---

## Example 3: Validate Financial Statement

### Scenario
You've uploaded a balance sheet and want to verify the metadata was extracted correctly.

### Using CLI Tool

```bash
python validate_import.py \
  --property-id 3 \
  --document-type financial_statement \
  --file "Financial Statements/2024/Balance Sheets/Hammond Aire 2024 Balance Sheet.pdf" \
  --output "balance_sheet_validation.json"
```

### Using Python API

```python
from backend.utils.document_validator import DocumentValidator

validator = DocumentValidator(
    minio_file_path="Financial Statements/2024/Balance Sheets/Hammond Aire 2024 Balance Sheet.pdf",
    property_id=3
)

# Define expected metadata
expected_metadata = {
    'property_id': 3,
    'document_year': 2024,
    'document_type': 'financial_statement',
    'property_name': 'Hammond Aire'
}

# Run validation with metadata check
report = validator.validate_all(expected_metadata=expected_metadata)

if report.passed:
    print("✅ Document metadata correct")
else:
    print("❌ Document metadata issues found")
```

---

## Example 4: Batch Validation

### Scenario
You want to validate all rent rolls for all properties in the database.

### Code

```python
import sqlite3
from backend.utils.rentroll_validator import RentRollValidator

# Get all properties with rent rolls
conn = sqlite3.connect('reims.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT DISTINCT property_id, file_path 
    FROM financial_documents
    WHERE file_path LIKE '%Rent Roll%'
""")

properties = cursor.fetchall()
conn.close()

# Validate each one
results = []
for prop_id, file_path in properties:
    print(f"\nValidating property {prop_id}...")
    
    validator = RentRollValidator(
        minio_file_path=file_path,
        property_id=prop_id
    )
    
    report = validator.validate_all()
    results.append({
        'property_id': prop_id,
        'file_path': file_path,
        'passed': report.passed,
        'errors': len(report.errors)
    })

# Summary
print("\n" + "="*80)
print("BATCH VALIDATION SUMMARY")
print("="*80)
for result in results:
    status = "✅ PASS" if result['passed'] else "❌ FAIL"
    print(f"Property {result['property_id']}: {status} ({result['errors']} errors)")
```

---

## Example 5: Validate During Import

### Scenario
You're writing an import script and want to validate immediately after importing data.

### Code

```python
from backend.utils.rentroll_validator import RentRollValidator
import sqlite3

def import_rent_roll(property_id, minio_file_path):
    """
    Import rent roll with automatic validation
    """
    conn = sqlite3.connect('reims.db')
    
    try:
        # Begin transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Import data (your import logic here)
        # ... import units, tenants, etc ...
        
        # VALIDATE BEFORE COMMITTING
        validator = RentRollValidator(minio_file_path, property_id)
        report = validator.validate_all()
        
        if report.passed:
            # Validation passed - commit
            conn.commit()
            print("✅ Import successful and validated")
            return True
        else:
            # Validation failed - rollback
            conn.rollback()
            print("❌ Import validation failed - rolled back")
            print(f"Errors: {report.errors}")
            return False
            
    except Exception as e:
        conn.rollback()
        print(f"❌ Import failed: {e}")
        return False
    finally:
        conn.close()

# Use it
success = import_rent_roll(
    property_id=3,
    minio_file_path="Financial Statements/2025/Rent Rolls/Hammond Rent Roll April 2025.pdf"
)
```

---

## Example 6: Interpret Validation Reports

### Scenario
You ran a validation and it failed. You need to understand what went wrong.

### Reading the Report

```python
from backend.utils.rentroll_validator import RentRollValidator

validator = RentRollValidator(
    minio_file_path="Financial Statements/2025/Rent Rolls/Property Rent Roll.pdf",
    property_id=5
)

report = validator.validate_all()

# Check overall status
print(f"Status: {report.status}")  # PASS, FAIL, or WARN
print(f"Passed: {report.passed}")  # True or False

# Look at specific validations
for validation in report.validations:
    if not validation.passed:
        print(f"\n❌ {validation.entity_type}:")
        print(f"   Expected: {validation.expected}")
        print(f"   Actual: {validation.actual}")
        print(f"   Message: {validation.message}")

# Check errors
if report.errors:
    print("\n Errors:")
    for error in report.errors:
        print(f"  - {error}")

# Check warnings
if report.warnings:
    print("\n⚠️  Warnings:")
    for warning in report.warnings:
        print(f"  - {warning}")

# Get JSON representation
report_dict = report.to_dict()
print(f"\nJSON: {report_dict}")
```

### Sample Failed Report

```
Status: FAIL
Passed: False

❌ total_units:
   Expected: 39
   Actual: 32
   Message: total_units count: expected 39, got 32 - MISMATCH (7 difference)

❌ unit_numbers:
   Expected: 39
   Actual: 32
   Message: unit_numbers completeness: 32/39 present - Missing: ['009-A', '015', '0B', '0C', '0D', '0F', '0G']

Errors:
  - total_units count: expected 39, got 32 - MISMATCH (7 difference)
  - Missing unit_numbers: {'009-A', '015', '0B', '0C', '0D', '0F', '0G'}

⚠️  Warnings:
  - Missing units in database: ['009-A', '015', '0B', '0C', '0D', '0F', '0G']
```

---

## Example 7: Fix Validation Failures

### Scenario
Validation revealed 7 missing units. You need to fix the database.

### Step 1: Identify the Problem

```python
validator = RentRollValidator(minio_file_path="...", property_id=3)
missing_units = validator.check_missing_units()

print(f"Missing units: {missing_units}")
# Output: ['009-A', '015', '0B', '0C', '0D', '0F', '0G']
```

### Step 2: Re-import Missing Units

```python
import sqlite3
import uuid

# Add missing units to database
conn = sqlite3.connect('reims.db')
cursor = conn.cursor()

missing_units_data = [
    {'unit': '009-A', 'tenant': 'Jimmy Jazz', 'sqft': 5500},
    {'unit': '015', 'tenant': 'T-Mobile', 'sqft': 1200},
    # ... etc
]

for unit_data in missing_units_data:
    cursor.execute("""
        INSERT INTO stores (id, property_id, unit_number, sqft, status, tenant_name)
        VALUES (?, 3, ?, ?, 'occupied', ?)
    """, (str(uuid.uuid4()), unit_data['unit'], unit_data['sqft'], unit_data['tenant']))

conn.commit()
conn.close()
```

### Step 3: Re-validate

```python
validator = RentRollValidator(minio_file_path="...", property_id=3)
report = validator.validate_all()

if report.passed:
    print("✅ All issues fixed!")
else:
    print("❌ Still have issues:", report.errors)
```

---

## Example 8: Custom Validation

### Scenario
You want to add custom validation logic specific to your needs.

### Code

```python
from backend.utils.rentroll_validator import RentRollValidator

class CustomRentRollValidator(RentRollValidator):
    """Extended validator with custom checks"""
    
    def validate_rent_amounts(self):
        """Custom validation: check if all rents are > 0"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM stores
            WHERE property_id = ? 
            AND status = 'occupied'
            AND (monthly_rent IS NULL OR monthly_rent <= 0)
        """, (self.property_id,))
        
        invalid_count = cursor.fetchone()['count']
        conn.close()
        
        passed = invalid_count == 0
        message = f"Rent amounts: {invalid_count} invalid rents found"
        
        if not passed:
            self.report.errors.append(message)
        
        from backend.utils.import_validator import ValidationResult
        result = ValidationResult(
            passed=passed,
            entity_type="rent_amounts",
            expected=0,
            actual=invalid_count,
            message=message
        )
        
        self.report.validations.append(result)
        return result
    
    def validate_all(self):
        """Override to add custom validation"""
        # Run standard validations
        super().validate_all()
        
        # Add custom validations
        self.validate_rent_amounts()
        
        return self.report

# Use custom validator
validator = CustomRentRollValidator(
    minio_file_path="...",
    property_id=3
)

report = validator.validate_all()
```

---

## Common Issues and Solutions

### Issue: "File not found in MinIO"

**Problem:** Validation can't find the source file

**Solution:**
```python
# Check file path format
file_path = "Financial Statements/2025/Rent Rolls/file.pdf"  # Correct
# NOT: "reims-files/Financial Statements/..."  # Wrong - don't include bucket

# Verify file exists
from minio import Minio
client = Minio('localhost:9000', 'minioadmin', 'minioadmin', secure=False)
exists = client.bucket_exists("reims-files")
print(f"Bucket exists: {exists}")
```

### Issue: "Unit count mismatch"

**Problem:** Parser didn't extract all units from PDF

**Solution:**
1. Check PDF format - units may have non-standard naming
2. Update regex patterns in validator
3. Use verbose logging to see what's being extracted
4. Manually verify unit count in PDF

### Issue: "Validation passes but data looks wrong"

**Problem:** Validation is too lenient

**Solution:**
1. Add more specific validation checks
2. Reduce tolerance thresholds
3. Add field-level accuracy checks
4. Implement custom validators

---

## Best Practices

### DO:
- ✅ Always validate immediately after import
- ✅ Save validation reports for audit trail
- ✅ Fix issues and re-validate
- ✅ Use batch validation for bulk imports
- ✅ Customize validators for specific needs

### DON'T:
- ❌ Skip validation to save time
- ❌ Ignore validation warnings
- ❌ Proceed with failed validation
- ❌ Delete validation reports
- ❌ Assume validation will always pass

---

## Getting Help

### Validation Fails Repeatedly

1. Check PDF format - may need parser updates
2. Review regex patterns in validator
3. Consult `DATA_IMPORT_VALIDATION_PROCEDURE.md`
4. Check validation logs for patterns
5. Consider custom validator for special cases

### Custom Validation Needed

1. Extend base `ImportValidator` class
2. Add custom validation methods
3. Override `validate_all()` to include them
4. Document custom logic for future reference

---

**Remember:** Validation is your safety net. Use it consistently to ensure data quality!




