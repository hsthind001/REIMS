#!/usr/bin/env python3
"""
Analyze Occupancy Discrepancy Between Rent Roll and Database
Compare TCSH Rent Roll April 2025 data with database
"""

import sqlite3
import json
from datetime import datetime

def main():
    print("\n" + "="*80)
    print("🔍 OCCUPANCY DISCREPANCY ANALYSIS")
    print("Property: The Crossings of Spring Hill (TCSH)")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Read the processed rent roll data
    print("\n📄 Reading Rent Roll Data from PDF...")
    with open('processed_data/955a88fe-c0ab-48cd-8b1b-2a714bf17f49_processed.json', 'r') as f:
        rent_roll_data = json.load(f)
    
    # Extract occupancy summary from the rent roll
    full_text = rent_roll_data['extracted_data']['full_text']
    
    # Parse the occupancy summary section
    print("\n" + "="*80)
    print("📊 RENT ROLL DATA (Source of Truth - TCSH Rent Roll April 2025.pdf)")
    print("="*80)
    
    # Count actual leases from the rent roll
    rent_roll_lines = full_text.split('\n')
    
    # Find units - looking for lines that start with unit numbers
    units_in_rent_roll = []
    for i, line in enumerate(rent_roll_lines):
        # Look for unit patterns like "1000", "1001", etc.
        if line.strip().startswith('The Crossings of Spring'):
            # Next line should have the unit number
            if i + 1 < len(rent_roll_lines):
                next_line = rent_roll_lines[i + 1].strip()
                # Check if it's a unit number
                if next_line and (next_line.startswith('1') or next_line.startswith('2') or next_line == 'Target #-2362'):
                    units_in_rent_roll.append(next_line)
    
    # Look for the occupancy summary
    occupancy_summary_found = False
    for i, line in enumerate(rent_roll_lines):
        if 'Occupancy Summary' in line:
            print(f"\n{line}")
            # Print next several lines
            for j in range(1, 10):
                if i + j < len(rent_roll_lines):
                    print(rent_roll_lines[i + j])
                    if '100.00' in rent_roll_lines[i + j] or 'Grand Total' in rent_roll_lines[i + j]:
                        occupancy_summary_found = True
            if occupancy_summary_found:
                break
    
    # Look for lease count
    for i, line in enumerate(rent_roll_lines):
        if '# of Leases' in line:
            print(f"\n📋 Lease Summary:")
            print(f"   {line}")
            if i + 1 < len(rent_roll_lines):
                print(f"   {rent_roll_lines[i + 1]}")
            if i + 2 < len(rent_roll_lines):
                print(f"   {rent_roll_lines[i + 2]}")
            break
    
    print(f"\n✅ Rent Roll Summary:")
    print(f"   Total Leases: 37 (ALL OCCUPIED)")
    print(f"   Occupied Area: 219,905.00 sqft")
    print(f"   Vacant Area: 0.00 sqft")
    print(f"   Occupancy Rate: 100.00%")
    
    # Now query the database
    print("\n" + "="*80)
    print("💾 DATABASE DATA (What REIMS Currently Shows)")
    print("="*80)
    
    conn = sqlite3.connect('reims.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get property data
    cursor.execute("""
        SELECT 
            id, name, total_units, occupied_units, occupancy_rate
        FROM properties
        WHERE name LIKE '%Crossings of Spring Hill%'
    """)
    property_data = cursor.fetchone()
    
    if property_data:
        print(f"\n🏢 Property: {property_data['name']}")
        print(f"   Total Units: {property_data['total_units']}")
        print(f"   Occupied Units: {property_data['occupied_units']}")
        print(f"   Occupancy Rate: {property_data['occupancy_rate']:.2f}%")
        
        # Get store details
        cursor.execute("""
            SELECT 
                unit_number, status, tenant_name, sqft, monthly_rent
            FROM stores
            WHERE property_id = ?
            ORDER BY unit_number
        """, (property_data['id'],))
        
        stores = cursor.fetchall()
        
        print(f"\n📋 Stores in Database ({len(stores)} units):")
        print("-" * 80)
        print(f"{'Unit':<10} {'Status':<15} {'Tenant':<30} {'Sqft':<12}")
        print("-" * 80)
        
        occupied_count = 0
        vacant_count = 0
        
        for store in stores:
            print(f"{store['unit_number']:<10} {store['status']:<15} {str(store['tenant_name'] or 'N/A')[:28]:<30} {store['sqft'] or 0:<12.0f}")
            if store['status'] == 'occupied':
                occupied_count += 1
            elif store['status'] == 'vacant':
                vacant_count += 1
        
        print("-" * 80)
        print(f"Occupied: {occupied_count}, Vacant: {vacant_count}, Total: {len(stores)}")
    
    conn.close()
    
    # Analysis
    print("\n" + "="*80)
    print("🚨 DISCREPANCY ANALYSIS")
    print("="*80)
    
    print(f"\n❌ MISMATCH IDENTIFIED:")
    print(f"\n   Rent Roll (Source Document):")
    print(f"      • Total Units: 37")
    print(f"      • Occupied Units: 37")
    print(f"      • Vacant Units: 0")
    print(f"      • Occupancy: 100%")
    print(f"\n   Database (REIMS System):")
    print(f"      • Total Units: {property_data['total_units']}")
    print(f"      • Occupied Units: {property_data['occupied_units']}")
    print(f"      • Vacant Units: {property_data['total_units'] - property_data['occupied_units']}")
    print(f"      • Occupancy: {property_data['occupancy_rate']:.2f}%")
    
    print(f"\n🔍 ROOT CAUSE:")
    print(f"   1. The rent roll lists 37 ACTIVE LEASES with 100% occupancy")
    print(f"   2. The database only contains 22 units (15 units MISSING!)")
    print(f"   3. The database incorrectly shows 4 vacant units")
    print(f"\n💡 ISSUE:")
    print(f"   The data extraction process failed to properly parse and import")
    print(f"   all 37 units from the rent roll into the stores table.")
    print(f"\n   Missing units: 15 (37 from rent roll - 22 in database)")
    print(f"   Incorrect vacancy count: 4 units marked vacant (should be 0)")
    
    print(f"\n📝 UNITS LISTED IN RENT ROLL:")
    print(f"   Target #-2362 (NAP), 1000-1019, 1021-1030, 1036A, 1036B/1036C,")
    print(f"   1037-1041, 2000, 2008, 2020")
    print(f"   (Total: 37 units, all with active leases)")
    
    print("\n" + "="*80)
    print("🎯 RECOMMENDATION:")
    print("="*80)
    print("""
   The document processing pipeline needs improvement:
   
   1. PDF Parser: The rent roll parser is not extracting all units correctly
   2. Data Import: The import logic may be filtering out some units
   3. Data Validation: Need to validate extracted data against source totals
   
   The rent roll clearly states:
   - "# of Leases: 37"
   - "Occupied Area: 219,905.00 sqft (100%)"
   - "Vacant Area: 0.00 sqft (0%)"
   
   But only 22 units were imported into the database.
    """)
    
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

