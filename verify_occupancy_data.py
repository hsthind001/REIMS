#!/usr/bin/env python3
"""
Verify Occupancy Calculation for The Crossings of Spring Hill
This script runs SQL queries to show exactly how 81.8% was calculated
"""

import sqlite3
from datetime import datetime
from decimal import Decimal

def connect_to_db():
    """Connect to SQLite database"""
    try:
        conn = sqlite3.connect('reims.db')
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def run_query(conn, query_name, query, params=None):
    """Execute query and display results"""
    print(f"\n{'='*80}")
    print(f"📊 {query_name}")
    print(f"{'='*80}")
    print(f"\n🔍 Query:\n{query}\n")
    
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        
        if not results:
            print("⚠️  No results found")
            return None
        
        # Print column headers
        columns = [description[0] for description in cursor.description]
        print("📋 Results:")
        print("-" * 80)
        header = " | ".join(f"{col:20}" for col in columns)
        print(header)
        print("-" * 80)
        
        # Print rows
        for row in results:
            row_data = " | ".join(f"{str(val):20}" for val in row)
            print(row_data)
        
        print("-" * 80)
        print(f"✅ Total rows: {len(results)}\n")
        
        return results
        
    except Exception as e:
        print(f"❌ Error executing query: {e}\n")
        return None

def main():
    print("\n" + "="*80)
    print("🏢 REIMS OCCUPANCY VERIFICATION TOOL")
    print("Property: The Crossings of Spring Hill")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    conn = connect_to_db()
    if not conn:
        return
    
    # Query 1: Find the property
    query1 = """
        SELECT 
            id,
            name,
            address,
            city,
            state,
            total_units,
            occupied_units,
            occupancy_rate
        FROM properties
        WHERE name LIKE '%Crossings of Spring Hill%'
    """
    results1 = run_query(conn, "Query 1: Find Property Details", query1)
    
    if not results1:
        print("\n❌ Property not found in database!")
        conn.close()
        return
    
    property_id = results1[0]['id']
    stored_occupancy = results1[0]['occupancy_rate']
    
    # Query 2: Count stores by status
    query2 = """
        SELECT 
            status,
            COUNT(*) as unit_count
        FROM stores
        WHERE property_id = ?
        GROUP BY status
        ORDER BY status
    """
    run_query(conn, "Query 2: Count Units by Status", query2, (property_id,))
    
    # Query 3: Calculate occupancy rate
    query3 = """
        SELECT 
            p.name as property_name,
            COUNT(s.id) as total_units,
            SUM(CASE WHEN s.status = 'occupied' THEN 1 ELSE 0 END) as occupied_units,
            SUM(CASE WHEN s.status = 'vacant' THEN 1 ELSE 0 END) as vacant_units,
            SUM(CASE WHEN s.status = 'under_lease' THEN 1 ELSE 0 END) as under_lease_units,
            SUM(CASE WHEN s.status = 'maintenance' THEN 1 ELSE 0 END) as maintenance_units,
            ROUND(
                (SUM(CASE WHEN s.status = 'occupied' THEN 1 ELSE 0 END) * 100.0) / COUNT(s.id),
                2
            ) as calculated_occupancy_rate,
            p.occupancy_rate as stored_occupancy_rate
        FROM properties p
        LEFT JOIN stores s ON p.id = s.property_id
        WHERE p.id = ?
        GROUP BY p.id, p.name, p.occupancy_rate
    """
    results3 = run_query(conn, "Query 3: Calculate Occupancy Rate", query3, (property_id,))
    
    # Query 4: Sample of units (first 10)
    query4 = """
        SELECT 
            unit_number,
            status,
            tenant_name,
            sqft,
            monthly_rent,
            lease_end_date
        FROM stores
        WHERE property_id = ?
        ORDER BY unit_number
        LIMIT 10
    """
    run_query(conn, "Query 4: Sample Units (First 10)", query4, (property_id,))
    
    # Query 5: Verification
    query5 = """
        SELECT 
            p.name,
            p.occupancy_rate as stored_rate,
            ROUND(
                (CAST(SUM(CASE WHEN s.status = 'occupied' THEN 1 ELSE 0 END) AS FLOAT) * 100.0) / COUNT(s.id),
                2
            ) as calculated_rate,
            CASE 
                WHEN ABS(p.occupancy_rate - ROUND(
                    (CAST(SUM(CASE WHEN s.status = 'occupied' THEN 1 ELSE 0 END) AS FLOAT) * 100.0) / COUNT(s.id),
                    2
                )) < 0.01 THEN 'MATCH ✅'
                ELSE 'MISMATCH ❌'
            END as verification
        FROM properties p
        LEFT JOIN stores s ON p.id = s.property_id
        WHERE p.id = ?
        GROUP BY p.id, p.name, p.occupancy_rate
    """
    results5 = run_query(conn, "Query 5: Verification Check", query5, (property_id,))
    
    # Summary
    print("\n" + "="*80)
    print("📊 VERIFICATION SUMMARY")
    print("="*80)
    
    if results3 and results5:
        result = results3[0]
        verification = results5[0]
        
        print(f"\n🏢 Property: {result['property_name']}")
        print(f"\n📈 Occupancy Calculation:")
        print(f"   Total Units:        {result['total_units']}")
        print(f"   Occupied Units:     {result['occupied_units']}")
        print(f"   Vacant Units:       {result['vacant_units']}")
        print(f"   Under Lease:        {result['under_lease_units']}")
        print(f"   Maintenance:        {result['maintenance_units']}")
        print(f"\n🧮 Calculation Formula:")
        print(f"   ({result['occupied_units']} occupied / {result['total_units']} total) × 100")
        print(f"   = {result['calculated_occupancy_rate']}%")
        print(f"\n💾 Stored in Database:  {result['stored_occupancy_rate']}%")
        print(f"🔢 Calculated from Data: {result['calculated_occupancy_rate']}%")
        print(f"\n✅ Verification Status:  {verification['verification']}")
    
    print("\n" + "="*80 + "\n")
    
    conn.close()

if __name__ == "__main__":
    main()

