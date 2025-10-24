# Hammond Aire Occupancy Validation Report

**Date:** October 19, 2025  
**Property:** Hammond Aire  
**Location:** Albany, NY

---

## Executive Summary

Validation of Hammond Aire property occupancy revealed a **discrepancy between the uploaded rent roll document and the current database records**. The actual rent roll shows significantly different data than what is stored in the system.

---

## Database Records (Current)

**Property ID:** 3  
**Property Name:** Hammond Aire  
**Location:** Hammond Aire Drive, Albany, NY  
**Size:** 14,400 sq ft

### Occupancy Summary
- **Total Units:** 8
- **Occupied:** 6 units
- **Vacant:** 2 units
- **Occupancy Rate:** 75.0%

### Unit Details (Database)

| Unit | Status | Size (sq ft) | Tenant | Monthly Rent |
|------|--------|--------------|--------|--------------|
| Suite 101 | 🟢 Occupied | 800 | Acme Corporation | $2,500.00 |
| Suite 102 | 🟢 Occupied | 1,100 | Global Tech Solutions | $3,200.00 |
| Suite 103 | 🟢 Occupied | 1,400 | Metro Coffee Co | $3,900.00 |
| Suite 104 | 🟢 Occupied | 1,400 | Premier Dental | $4,600.00 |
| Suite 105 | 🟢 Occupied | 1,700 | Fitness First | $4,500.00 |
| Suite 201 | 🟢 Occupied | 2,000 | Creative Marketing | $5,200.00 |
| Suite 202 | 🔴 Vacant | 2,000 | - | - |
| Suite 203 | 🔴 Vacant | 2,300 | - | - |

**Total Monthly Revenue:** $23,900.00

---

## Uploaded Rent Roll Document (Actual)

**Document:** Hammond Rent Roll April 2025.pdf  
**Upload Date:** October 20, 2025  
**File Size:** 60,419 bytes  
**Location:** `reims-files/properties/7/financial-statements/2025/5471be30-1e71-4066-86b0-ab88de352409_Hammond Rent Roll April 2025.pdf`

### Actual Occupancy (from PDF)

**Property:** Hammond Aire Plaza

- **Occupied Area:** 326,695 sq ft
- **Vacant Area:** 22,965 sq ft
- **Total Area:** 349,660 sq ft
- **Occupancy Rate:** **93.43%**

### Actual Tenants (from PDF)

| Unit | Tenant | Type | Area (sq ft) | Monthly Rent | Annual Rent |
|------|--------|------|--------------|--------------|-------------|
| (hmnd)001 | Elite Nails | Retail NNN | 703 | $2,167.58 | $26,010.96 |
| (hmnd)002-A | Subway Real Estate, LLC | Retail NNN | 1,312 | $4,536.00 | $54,432.00 |
| (hmnd)002-B | SprintCom, Inc | Retail NNN | 1,590 | $4,591.13 | $55,093.56 |
| (hmnd)003 | Hi-Tech Cuts | Retail NNN | 1,410 | $4,133.00 | $49,596.00 |
| (hmnd)004 | DC Labs, LLC / Billedeaux Centers LLC | Retail NNN | 1,023 | $2,898.50 | $34,782.00 |
| (hmnd)005 | Regional Finance Company of Louisiana, LLC | Retail NNN | 4,200 | $5,250.00 | $63,000.00 |
| (hmnd)006 | Foot Locker Retail Inc #7837 | Retail NNN | 10,494 | $13,117.50 | $157,410.00 |

**Vacant Units (from PDF):**
- (hmnd)020 - 1,149 sq ft
- (hmnd)042 - 6,087 sq ft
- (hmnd)055 - 5,853 sq ft
- (hmnd)064 - 810 sq ft
- (hmnd)0B0 - 3,449 sq ft
- (hmnd)0C0 - 2,550 sq ft
- (hmnd)0F0 - 3,067 sq ft

---

## Discrepancy Analysis

### Key Differences

1. **Property Scale:**
   - Database: 14,400 sq ft (8 units)
   - Actual: 349,660 sq ft (multiple units)
   - **Difference:** Actual property is **24x larger** than database records

2. **Occupancy Rate:**
   - Database: 75.0%
   - Actual: 93.43%
   - **Difference:** Actual occupancy is **18.43% higher**

3. **Tenants:**
   - Database: Generic tenant names (Acme Corporation, Global Tech Solutions, etc.)
   - Actual: Real tenant names (Elite Nails, Subway, Sprint, Foot Locker, etc.)
   - **Conclusion:** Database contains **sample/demo data**

4. **Revenue:**
   - Database: $23,900/month
   - Actual: Significantly higher (specific units show $36,693.71/month minimum)

---

## Findings

### ✅ Positive Findings

1. **Document Upload Successful:** Rent roll PDF was successfully uploaded to MinIO
2. **File Accessible:** Document is retrievable and readable
3. **Storage Standardized:** File is stored in the correct standardized path
4. **Metadata Captured:** Document year, period, and property information properly extracted

### ⚠️ Issues Identified

1. **Sample Data in Database:** Current database records appear to be sample/demo data, not actual property information
2. **Property ID Mismatch:** Rent roll uploaded to property ID 7, but database shows Hammond Aire as property ID 3
3. **Scale Mismatch:** Actual property is much larger than database indicates
4. **Data Not Synchronized:** Rent roll data has not been parsed and loaded into the database

---

## Recommendations

### Immediate Actions

1. **Replace Sample Data:** Update database with actual tenant and occupancy information from the rent roll
2. **Correct Property Records:**
   - Update property size to reflect actual 349,660 sq ft
   - Update unit count to reflect actual number of leasable units
   - Update tenant names with actual tenants
3. **Implement Rent Roll Parser:** Create automated parser to extract tenant data from rent roll PDFs
4. **Data Validation:** Establish process to validate uploaded documents against database records

### Long-Term Improvements

1. **Automated Extraction:** Implement OCR/parsing for rent roll PDFs to auto-populate database
2. **Data Reconciliation:** Monthly reconciliation process between uploaded documents and database
3. **Validation Alerts:** Alert users when uploaded documents show significant discrepancies
4. **Historical Tracking:** Track occupancy changes over time from uploaded rent rolls

---

## Technical Details

### Document Location

```
MinIO Bucket: reims-files
Path: properties/7/financial-statements/2025/5471be30-1e71-4066-86b0-ab88de352409_Hammond Rent Roll April 2025.pdf
```

### Database Queries Used

```sql
-- Get current database occupancy
SELECT 
    COUNT(*) as total_units,
    SUM(CASE WHEN status = 'occupied' THEN 1 ELSE 0 END) as occupied_units,
    SUM(CASE WHEN status = 'vacant' THEN 1 ELSE 0 END) as vacant_units
FROM stores 
WHERE property_id = '3';

-- Get unit details
SELECT unit_number, status, tenant_name, monthly_rent, sqft
FROM stores 
WHERE property_id = '3'
ORDER BY unit_number;
```

### PDF Extraction Method

- Tool: PyPDF2
- Pages: 6
- Characters extracted: 10,475
- Manual review required for detailed parsing

---

## Validation Checklist

- [x] Rent roll document uploaded successfully
- [x] Document stored in standardized MinIO path
- [x] Document accessible and downloadable
- [x] Database records exist for property
- [x] Occupancy data extracted from PDF
- [x] Discrepancy identified and documented
- [ ] Database updated with actual property data
- [ ] Rent roll data parsed and loaded
- [ ] Automated parser implemented
- [ ] Reconciliation process established

---

## Next Steps

1. ✅ **Completed:** Document upload and storage standardization
2. ✅ **Completed:** Validation and discrepancy identification
3. **Pending:** Update database with actual property information
4. **Pending:** Implement rent roll parsing automation
5. **Pending:** Establish ongoing data validation process

---

## Conclusion

The document storage standardization and migration were **successfully completed**. The Hammond Aire rent roll document is properly stored and accessible. However, the validation revealed that the **database contains sample data**, not the actual property information from the rent roll. 

**The uploaded rent roll shows the actual property has:**
- **93.43% occupancy rate** (vs. 75% in database)
- **349,660 sq ft** (vs. 14,400 sq ft in database)
- **Real tenants** including Subway, Foot Locker, Sprint, etc. (vs. generic sample tenants in database)

---

**Report Generated:** October 19, 2025  
**Validated By:** Storage Migration Verification System  
**Status:** ⚠️ Data Discrepancy Identified - Manual Review Required

