# Wendover Commons Data Sources - Complete Explanation

**Property:** Wendover Commons  
**URL:** http://localhost:3001/property/2  
**Date:** October 18, 2025

---

## 🎯 Quick Answer

**The data displayed for Wendover Commons is NOT coming from the uploaded financial documents.**

Instead, all data comes from:
1. The `properties` table in the SQLite database
2. Calculations based on those base values
3. Synthetically generated chart data using algorithms

---

## 📊 Detailed Data Source Breakdown

### 1. Property Details Section

**What You See:**
- Property Type: Commercial
- Year Built: 1995  
- Square Footage: 150,000
- Monthly Rent: $180K
- Status: healthy

**Data Source:**
```
Database Table: properties
Database File: reims.db
Record ID: 2
```

**Specific Fields:**
- `property_type` = "Commercial"
- `year_built` = 1995
- `square_footage` = 150000
- `monthly_rent` = 180000
- `purchase_price` = 22000000
- `current_market_value` = 25000000
- `status` = "active"

**NOT from uploaded files:**
❌ Balance Sheet.pdf
❌ Cash Flow Statement.pdf
❌ Income Statement.pdf

---

### 2. KPI Cards (Top of Page)

#### **Market Value: $25.0M**
- **Source:** `properties.current_market_value`
- **Value:** 25,000,000
- **File:** SQLite database `reims.db`, table `properties`, column `current_market_value`
- **NOT from:** Uploaded financial statements

#### **Annual NOI: $2.16M**
- **Source:** Calculated from `properties.monthly_rent`
- **Formula:** `monthly_rent * 12`
- **Calculation:** $180,000 × 12 = $2,160,000
- **Code Location:** `backend/api/routes/properties.py` (line ~113)
  ```python
  COALESCE(p.monthly_rent * 12, 0) as noi
  ```
- **NOT from:** Uploaded financial statements

#### **Cap Rate: 8.6%**
- **Source:** Calculated from NOI and Market Value
- **Formula:** `(Annual NOI / Current Market Value) × 100`
- **Calculation:** ($2,160,000 / $25,000,000) × 100 = 8.6%
- **Code Location:** `frontend/src/components/PropertyDetailPage.jsx` (lines 52-57)
  ```javascript
  const calculateYearlyReturn = () => {
    const annualNOI = propertyData.noi || 0;
    const propertyValue = propertyData.current_market_value || 1;
    return ((annualNOI / propertyValue) * 100).toFixed(1);
  };
  ```
- **NOT from:** Uploaded financial statements

#### **Occupancy: 95.0%**
- **Source:** Hardcoded in backend
- **Value:** 0.95 (95%)
- **Code Location:** `backend/api/routes/properties.py` (line ~202)
  ```python
  0.95 as occupancy_rate
  ```
- **NOT from:** Uploaded financial statements or actual occupancy data

---

### 3. Net Operating Income Chart (Line Chart)

**What You See:**
- 12 months of data (Jan-Dec)
- Blue line showing NOI trends
- Values around $180K/month with variations
- Green dashed target line

**Data Source:**
- **NOT from uploaded financial statements**
- **Synthetically generated** by frontend algorithm

**How It's Generated:**

**File:** `frontend/src/components/charts/PropertyNOIChart.jsx`

**Algorithm:**
1. Takes base value from `propertyData.monthly_rent` ($180,000)
2. Calculates average monthly: `annualNOI / 12`
3. Applies seasonal factors:
   - Q1 (Jan-Mar): 95% (winter dip)
   - Q2-Q3: 100-102% (normal/slight increase)
   - Q4 (Oct-Dec): 108% (year-end boost)
4. Adds deterministic variations using property ID as seed:
   ```javascript
   const seed = (propertyId * 1000) + (i * 100);
   const variation = 1 + (Math.sin(seed) * 0.08);
   ```
5. Creates 12 data points with realistic-looking trends

**Result:** Chart shows **simulated** NOI data that looks realistic but is **not real data** from uploaded PDFs.

---

### 4. Revenue Analysis Chart (Area Chart)

**What You See:**
- 12 months of data (Jan-Dec)
- Teal area (revenue)
- Red area (expenses)
- Total height shows combined revenue/expenses

**Data Source:**
- **NOT from uploaded financial statements**
- **Synthetically generated** by frontend algorithm

**How It's Generated:**

**File:** `frontend/src/components/charts/PropertyRevenueChart.jsx`

**Algorithm:**
1. **Revenue Generation:**
   - Base: `propertyData.monthly_rent` ($180,000)
   - Seasonal factors applied (Q4 boost, Q1 dip)
   - Deterministic variations using property ID

2. **Expense Generation:**
   - Base: `monthly_rent * 0.6` (assumes 60% expense ratio)
   - Result: $108,000/month average expenses
   - Variations applied independently

3. **Profit Calculation:**
   - `profit = revenue - expenses`
   - Approximately $72,000/month

**Result:** Chart shows **simulated** revenue/expense data that looks realistic but is **not real data** from uploaded PDFs.

---

## 📄 What About the Uploaded Documents?

### Files Found for Wendover Commons:

1. **Wendover Commons 2024 Balance Sheet.pdf**
   - Uploaded: October 17, 2025
   - Status: completed
   - **Usage: NONE - Not used for any displayed data**

2. **Wendover Commons 2024 Cash Flow Statement.pdf**
   - Uploaded: October 17, 2025
   - Status: completed
   - **Usage: NONE - Not used for any displayed data**

3. **Wendover Commons 2024 Income Statement.pdf**
   - Uploaded: October 17, 2025
   - Status: completed
   - **Usage: NONE - Not used for any displayed data**

### Why Aren't They Used?

The uploaded financial documents are:
- ✅ Stored in the database (`financial_documents` table)
- ✅ Marked as "completed" status
- ❌ **NOT parsed or extracted** for actual financial data
- ❌ **NOT used** in any calculations or charts
- ❌ **NOT displayed** on the property detail page

The system currently has document **storage** but not document **processing/extraction**.

---

## 🔍 Data Flow Diagram

```
User Views Property Detail Page
         ↓
Frontend fetches: GET /api/properties/2
         ↓
Backend queries: properties table in SQLite
         ↓
Returns JSON with base fields:
  - monthly_rent: 180000
  - current_market_value: 25000000
  - year_built: 1995
  - etc.
         ↓
Frontend receives data
         ↓
├─ Property Details: Display as-is
├─ KPIs: Calculate (NOI = rent * 12, Cap Rate = NOI/Value)
├─ NOI Chart: Generate synthetic data using monthly_rent as base
└─ Revenue Chart: Generate synthetic data using monthly_rent as base
         ↓
User sees complete page
(but data is NOT from uploaded PDFs)
```

---

## ⚠️ Important Implications

### What This Means:

1. **The charts look realistic but are simulated**
   - They show trends and patterns
   - But they're algorithmically generated
   - Not based on actual financial statement data

2. **KPIs are calculated, not extracted**
   - Annual NOI = monthly rent × 12 (simple multiplication)
   - Actual NOI from financial statements may differ
   - Occupancy rate is hardcoded at 95%

3. **Uploaded documents are not processed**
   - PDFs are stored in the database
   - But their content is not extracted
   - No OCR or text parsing is performed
   - Charts don't use actual statement data

---

## 💡 To Use Real Financial Document Data

If you want the charts to show **actual data from uploaded PDFs**, you would need to:

### 1. Implement Document Processing
- Extract text from PDFs (OCR or text extraction)
- Parse financial statement formats
- Identify key metrics (revenue, expenses, NOI)
- Handle different document layouts

### 2. Store Extracted Data
- Create tables for extracted metrics
- Store monthly revenue/expense data
- Link to specific documents
- Track extraction date and confidence

### 3. Modify Charts to Use Real Data
- Query extracted data instead of generating synthetic data
- Display actual monthly values from statements
- Show document source and date
- Handle missing months or incomplete data

### 4. Example Implementation

**Backend:**
```python
# Extract from PDF
def extract_financial_data(pdf_file):
    # Parse PDF
    # Extract revenue, expenses, NOI by month
    # Return structured data
    
# Store in database
INSERT INTO extracted_financial_data 
(property_id, document_id, month, year, revenue, expenses, noi)
VALUES (2, 'doc_id', 1, 2024, 185000, 110000, 75000)
```

**Frontend:**
```javascript
// Fetch real data instead of generating
const response = await fetch(`/api/properties/2/financial-data?year=2024`);
const realData = await response.json();
// Use realData in charts instead of generateNOIData()
```

---

## 📊 Current vs. Desired State

### Current State (As-Is):
```
Upload PDFs → Store in database → [Nothing happens]
Charts show synthetic data based on monthly_rent field
```

### Desired State (To-Be):
```
Upload PDFs → Extract data → Store metrics → Charts use real data
Charts show actual revenue/expenses from financial statements
```

---

## ✅ Summary

**For Wendover Commons property detail page:**

| Component | Data Source | Real or Synthetic |
|-----------|-------------|-------------------|
| Property Details | `properties` table | Real (manually entered) |
| Market Value KPI | `properties.current_market_value` | Real (manually entered) |
| Annual NOI KPI | Calculated: `monthly_rent * 12` | Calculated |
| Cap Rate KPI | Calculated: `(NOI / Value) * 100` | Calculated |
| Occupancy KPI | Hardcoded at 95% | Synthetic (fixed) |
| NOI Chart | Algorithm using `monthly_rent` | **Synthetic** |
| Revenue Chart | Algorithm using `monthly_rent` | **Synthetic** |
| Uploaded PDFs | Stored in database | **Not Used** |

**Key Takeaway:** The data looks professional and realistic, but **charts are generated algorithmically** and **do not reflect actual data from uploaded financial statements**. The uploaded PDFs are stored but not processed or used for any visualizations.

---

**Generated:** October 18, 2025  
**Database:** reims.db (SQLite)  
**Property ID:** 2 (Wendover Commons)

