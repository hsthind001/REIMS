# 🚨 Occupancy Discrepancy Report
**Property:** The Crossings of Spring Hill (TCSH)  
**Date:** October 19, 2025  
**Issue:** Database occupancy (81.8%) does not match source document (100%)

---

## 📊 The Discrepancy

### **Source Document: TCSH Rent Roll April 2025.pdf**
- **Total Units:** 37 leased spaces
- **Occupied Units:** 37 (all units have active tenants)
- **Vacant Units:** 0
- **Occupancy Rate:** **100.00%**
- **Total Area:** 219,905 sqft

### **REIMS Database (Current State)**
- **Total Units:** 22 units
- **Occupied Units:** 18
- **Vacant Units:** 4
- **Occupancy Rate:** **81.82%** ❌

---

## 🔍 Root Cause Analysis

### **Problem #1: Missing Units (15 units not imported)**

The rent roll lists **37 active leases**, but only **22 units** were imported into the database.

**Units in Rent Roll (37 total):**
1. Target #-2362 (NAP)
2. Units 1000-1019 (20 units)
3. Unit 1021 (skipped 1020)
4. Units 1022-1030 (9 units)
5. Units 1036A, 1036B/1036C (3 units combined)
6. Units 1037-1041 (5 units)
7. Units 2000, 2008, 2020 (3 outparcels)

**Units in Database (22 total):**
- Space 1, Space 2
- Suite 101-105
- Suite 201-205
- Suite 301-305
- Unit A, B, C, D, E

❌ **The database has GENERIC unit names (Suite 101, Space 1) instead of the ACTUAL unit numbers from the rent roll (1000, 1001, etc.)**

### **Problem #2: Incorrect Vacancy Data**

The rent roll shows **0 vacant units** (100% occupancy), but the database shows **4 vacant units**:
- Space 1 (vacant)
- Space 2 (vacant)
- Unit D (vacant)
- Unit E (vacant)

These appear to be **sample/demo data** that was never replaced with actual rent roll data.

### **Problem #3: Incorrect Tenant Names**

The database shows generic tenant names like:
- "Acme Corporation"
- "Global Tech Solutions"
- "Metro Coffee Co"

But the rent roll shows actual tenants like:
- "ISP Corporation/Firehouse Subs"
- "Moe's / Cannon Restaurant Management, LLC"
- "Ascend Federal Credit Union"
- "Buffalo Wild Wings #0222/IRB Holding"
- "Ross Dress For Less, Inc. #1268"
- "Dollar Tree Stores, Inc."
- "Ulta Salon, Cosmetics & Fragrance"
- "HomeGoods Inc/TJX companies Inc"
- "Old Navy #9736/GAP"
- "PetSmart, Inc."

---

## 🛠️ Why This Happened

### **Document Processing Pipeline Failed**

The REIMS document processing workflow has these stages:
1. ✅ **Upload:** PDF was successfully uploaded
2. ✅ **Text Extraction:** PDF text was extracted correctly
3. ❌ **Data Parsing:** Failed to properly parse unit data from rent roll
4. ❌ **Data Import:** Failed to import parsed data into `stores` table
5. ❌ **Validation:** No validation to check if imported data matches source totals

**Evidence:**
- The processed JSON file contains the full rent roll text
- All 37 leases are visible in the extracted text
- But the `stores` table only has 22 generic demo units
- The property was likely created with sample data that was never replaced

---

## 📝 What Should Have Been Imported

Here are some examples of actual units from the rent roll:

| Unit | Tenant | Status | Sqft | Monthly Rent |
|------|--------|--------|------|--------------|
| Target #-2362 | Target (NAP-Exp Only) | Occupied | 0 | $0.00 |
| 1000 | ISP Corporation/Firehouse Subs | Occupied | 2,261 | $6,307.25 |
| 1001 | Moe's / Cannon Restaurant Mgmt | Occupied | 2,400 | $5,688.00 |
| 1002 | Ascend Federal Credit Union | Occupied | 1,790 | $4,036.45 |
| 1005 | CeCe's Yogurt / Sherwin 627, LLC | Occupied | 1,200 | $3,118.27 |
| 1006 | Ascend Fitness, Inc. | Occupied | 4,786 | $10,768.50 |
| 1022 | Ross Dress For Less, Inc. #1268 | Occupied | 24,911 | $25,948.96 |
| 1024 | Dollar Tree Stores, Inc. | Occupied | 7,500 | $8,406.25 |
| 1028 | Ulta Salon, Cosmetics & Fragrance | Occupied | 8,027 | $12,475.30 |
| 1030 | HomeGoods Inc/TJX companies Inc | Occupied | 23,391 | $24,658.01 |
| 1038 | PetSmart, Inc. | Occupied | 18,471 | $21,472.54 |
| 1040 | Old Navy #9736/GAP | Occupied | 15,500 | $19,375.00 |
| 1041 | The Electronic Express, Inc. | Occupied | 20,331 | $21,449.20 |
| 2000 | Chili's, Inc / Brinker Interntl | Occupied | 6,387 | $10,833.33 |
| 2008 | Logan's Roadhouse #471 | Occupied | 7,290 | $13,291.67 |
| 2020 | Cracker Barrel Old Country Store | Occupied | 10,160 | $13,867.00 |

**ALL 37 UNITS HAVE ACTIVE LEASES = 100% OCCUPANCY**

---

## 🎯 Impact

### **Incorrect Reporting**
- Dashboard shows 81.8% occupancy instead of 100%
- Financial projections based on 18 occupied units instead of 37
- Missing revenue from 19 units not in the system

### **Business Impact**
- Underreporting property performance
- Incorrect valuation calculations
- Misleading analytics and KPIs

---

## ✅ Solution

### **Immediate Actions Needed:**

1. **Clear Existing Demo Data**
   - Delete the 22 generic units in the database for this property
   
2. **Implement Rent Roll Parser**
   - Create a dedicated rent roll parser that can extract:
     - Unit numbers
     - Tenant names
     - Lease dates (start/end)
     - Square footage
     - Monthly rent
     - Lease status
   
3. **Import Actual Data**
   - Parse all 37 units from the rent roll
   - Import into `stores` table with correct data
   - Link to property ID
   
4. **Validate Import**
   - Verify 37 units imported
   - Verify all marked as 'occupied'
   - Verify occupancy rate = 100%
   - Verify total sqft = 219,905

5. **Add Data Validation**
   - Check imported unit count against source document totals
   - Validate occupancy percentages
   - Flag discrepancies for manual review

---

## 🔧 Technical Details

### **Database Schema**
```sql
-- stores table structure
CREATE TABLE stores (
    id UUID PRIMARY KEY,
    property_id UUID REFERENCES properties(id),
    unit_number VARCHAR(50),  -- Should be "1000", "1001", not "Suite 101"
    tenant_name VARCHAR(255),  -- Should be actual tenant names
    status VARCHAR(20),        -- Should be 'occupied' for all 37 units
    sqft DECIMAL(10,2),
    monthly_rent DECIMAL(12,2),
    lease_start_date DATE,
    lease_end_date DATE,
    -- ... other fields
);
```

### **Files Involved**
- **Source:** `storage/955a88fe-c0ab-48cd-8b1b-2a714bf17f49_TCSH Rent Roll April 2025.pdf`
- **Processed:** `processed_data/955a88fe-c0ab-48cd-8b1b-2a714bf17f49_processed.json`
- **Database:** `reims.db` → `stores` table

---

## 📌 Conclusion

**The 81.8% occupancy figure is INCORRECT.**

The actual occupancy rate from the source rent roll document is **100%** with all 37 units occupied by active tenants. The database contains outdated sample/demo data that was never replaced with the actual rent roll information.

**To fix this, the rent roll data needs to be properly parsed and imported into the `stores` table, replacing the current demo data.**

---

## 📂 Verification Files Created

1. `verify_occupancy_calculation.sql` - SQL queries to verify data
2. `verify_occupancy_data.py` - Python script to check current database state
3. `analyze_occupancy_discrepancy.py` - Full discrepancy analysis
4. `OCCUPANCY_DISCREPANCY_REPORT.md` - This report

Run `python analyze_occupancy_discrepancy.py` to see the full comparison.

