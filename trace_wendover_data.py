"""
Trace Wendover Commons Data Sources
Shows which uploaded files are used for charts and KPIs
"""

import sqlite3
import json

conn = sqlite3.connect('reims.db')
cursor = conn.cursor()

print("\n" + "="*70)
print("WENDOVER COMMONS DATA SOURCE TRACING")
print("="*70)

# 1. Property Base Data
print("\n📊 PROPERTY BASE DATA (from 'properties' table):")
print("-" * 70)
cursor.execute("""
    SELECT 
        name, 
        monthly_rent,
        purchase_price,
        current_market_value,
        square_footage,
        property_type,
        year_built,
        created_at
    FROM properties 
    WHERE id = 2
""")
row = cursor.fetchone()
if row:
    print(f"Property Name: {row[0]}")
    print(f"Monthly Rent: ${row[1]:,.2f}")
    print(f"Purchase Price: ${row[2]:,.2f}")
    print(f"Current Market Value: ${row[3]:,.2f}")
    print(f"Square Footage: {row[4]:,.0f}")
    print(f"Property Type: {row[5]}")
    print(f"Year Built: {row[6]}")
    print(f"Created: {row[7]}")
    
    monthly_rent = row[1]
    current_value = row[3]

# 2. Calculated KPIs
print("\n💰 CALCULATED KPIs (derived from properties table):")
print("-" * 70)
annual_noi = monthly_rent * 12
cap_rate = (annual_noi / current_value * 100) if current_value > 0 else 0
occupancy = 0.95  # Hardcoded in backend

print(f"Annual NOI: ${annual_noi:,.2f}")
print(f"  ├─ Formula: monthly_rent * 12")
print(f"  ├─ Calculation: ${monthly_rent:,.2f} * 12")
print(f"  └─ Source: properties.monthly_rent")
print()
print(f"Cap Rate: {cap_rate:.1f}%")
print(f"  ├─ Formula: (annual_noi / current_market_value) * 100")
print(f"  ├─ Calculation: (${annual_noi:,.2f} / ${current_value:,.2f}) * 100")
print(f"  └─ Source: properties.monthly_rent, properties.current_market_value")
print()
print(f"Occupancy Rate: {occupancy*100:.1f}%")
print(f"  ├─ Value: Hardcoded at 0.95 (95%)")
print(f"  └─ Source: backend/api/routes/properties.py (line ~202)")

# 3. Chart Data Generation
print("\n📈 CHART DATA GENERATION (synthetic, not from uploaded files):")
print("-" * 70)
print("NOI Chart:")
print(f"  ├─ Data Points: 12 months (Jan-Dec)")
print(f"  ├─ Base Value: ${monthly_rent:,.2f}/month")
print(f"  ├─ Generation: Seasonal variations applied")
print(f"  ├─ Algorithm: PropertyNOIChart.jsx generateNOIData()")
print(f"  └─ Source File: frontend/src/components/charts/PropertyNOIChart.jsx")
print()
print("Revenue Analysis Chart:")
print(f"  ├─ Revenue: ${monthly_rent:,.2f}/month (with variations)")
print(f"  ├─ Expenses: ${monthly_rent * 0.6:,.2f}/month (60% of revenue)")
print(f"  ├─ Generation: Seasonal + deterministic variations")
print(f"  ├─ Algorithm: PropertyRevenueChart.jsx generateRevenueData()")
print(f"  └─ Source File: frontend/src/components/charts/PropertyRevenueChart.jsx")

# 4. Check for uploaded documents
print("\n📄 UPLOADED FINANCIAL DOCUMENTS:")
print("-" * 70)
cursor.execute("""
    SELECT 
        file_name,
        document_type,
        property_name,
        status,
        upload_date
    FROM financial_documents 
    WHERE property_name = 'Wendover Commons'
    ORDER BY upload_date DESC
""")
docs = cursor.fetchall()
if docs:
    for doc in docs:
        print(f"File: {doc[0]}")
        print(f"  ├─ Type: {doc[1]}")
        print(f"  ├─ Status: {doc[3]}")
        print(f"  ├─ Uploaded: {doc[4]}")
        print(f"  └─ Usage: Document uploaded but NOT used for charts/KPIs")
        print()
else:
    print("⚠️  NO DOCUMENTS UPLOADED for Wendover Commons")
    print()

# 5. Check processed data table
print("\n🔍 PROCESSED/EXTRACTED DATA:")
print("-" * 70)
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND (name LIKE '%extract%' OR name LIKE '%process%')
""")
tables = cursor.fetchall()
if tables:
    print(f"Found tables: {[t[0] for t in tables]}")
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]} WHERE property_name = 'Wendover Commons'")
            count = cursor.fetchone()[0]
            print(f"  └─ {table[0]}: {count} records for Wendover Commons")
        except sqlite3.OperationalError:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  └─ {table[0]}: {count} total records (no property_name column)")
else:
    print("⚠️  NO processed data tables found")

print("\n" + "="*70)
print("DATA SOURCE SUMMARY")
print("="*70)
print("""
🎯 DATA FLOW for Wendover Commons Property Detail Page:

1. Property Details Section:
   ├─ Source: `properties` table in SQLite database
   ├─ Data: Name, address, type, year, square footage, etc.
   └─ NOT from uploaded files

2. KPI Cards (Market Value, NOI, Cap Rate, Occupancy):
   ├─ Source: `properties` table fields
   ├─ Monthly Rent: properties.monthly_rent ($180,000)
   ├─ Market Value: properties.current_market_value ($25,000,000)
   ├─ Annual NOI: Calculated as monthly_rent * 12
   ├─ Cap Rate: Calculated as (NOI / market_value) * 100
   ├─ Occupancy: Hardcoded at 95% in backend
   └─ NOT from uploaded financial documents

3. NOI Chart (12 months line graph):
   ├─ Source: Synthetic data generated in frontend
   ├─ Base Value: properties.monthly_rent
   ├─ Algorithm: Seasonal variations + deterministic patterns
   ├─ File: frontend/src/components/charts/PropertyNOIChart.jsx
   └─ NOT from uploaded financial statements

4. Revenue Analysis Chart (area chart):
   ├─ Source: Synthetic data generated in frontend
   ├─ Base Value: properties.monthly_rent
   ├─ Revenue: Monthly rent with variations
   ├─ Expenses: 60% of revenue with variations
   ├─ File: frontend/src/components/charts/PropertyRevenueChart.jsx
   └─ NOT from uploaded financial statements

⚠️  IMPORTANT FINDINGS:
   • The charts show CALCULATED/SYNTHETIC data
   • They are NOT extracted from uploaded PDF financial statements
   • Uploaded documents (if any) are stored but NOT processed for charts
   • All displayed data comes from the `properties` table base fields
   • Charts generate realistic-looking trends algorithmically

💡 TO USE UPLOADED FINANCIAL DOCUMENTS:
   • You would need to implement document parsing/extraction
   • Extract actual NOI, revenue, expenses from PDFs
   • Store extracted data in database
   • Modify charts to use real extracted data instead of synthetic data
""")

print("="*70)
print()

conn.close()

                                