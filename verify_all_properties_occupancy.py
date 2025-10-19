#!/usr/bin/env python3
"""
Verify Occupancy for All Properties
Check if occupancy rates match actual unit data
"""

import sqlite3
from datetime import datetime

DB_PATH = "reims.db"

def verify_all_properties():
    """Check occupancy accuracy for all properties"""
    print("\n" + "="*100)
    print("🏢 VERIFYING OCCUPANCY FOR ALL PROPERTIES")
    print("="*100)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all properties
    cursor.execute("""
        SELECT 
            id, name, total_units, occupied_units, occupancy_rate, square_footage
        FROM properties
        ORDER BY id
    """)
    
    properties = cursor.fetchall()
    
    if not properties:
        print("❌ No properties found in database")
        conn.close()
        return
    
    print(f"Found {len(properties)} properties\n")
    print("="*100)
    
    issues_found = []
    correct_count = 0
    
    for prop in properties:
        property_id = prop['id']
        property_name = prop['name']
        stored_total = prop['total_units']
        stored_occupied = prop['occupied_units']
        stored_rate = prop['occupancy_rate']
        stored_sqft = prop['square_footage']
        
        print(f"\n📋 Property ID: {property_id}")
        print(f"   Name: {property_name}")
        print("-" * 100)
        
        # Get actual unit data from stores table
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'occupied' THEN 1 ELSE 0 END) as occupied,
                SUM(CASE WHEN status = 'vacant' THEN 1 ELSE 0 END) as vacant,
                SUM(sqft) as total_sqft
            FROM stores
            WHERE property_id = ?
        """, (property_id,))
        
        stores_data = cursor.fetchone()
        actual_total = stores_data['total'] or 0
        actual_occupied = stores_data['occupied'] or 0
        actual_vacant = stores_data['vacant'] or 0
        actual_sqft = stores_data['total_sqft'] or 0
        
        # Calculate actual occupancy rate
        actual_rate = (actual_occupied / actual_total * 100) if actual_total > 0 else 0
        
        # Display comparison
        print(f"\n   📊 STORED IN PROPERTIES TABLE:")
        print(f"      Total Units: {stored_total or 'NULL'}")
        print(f"      Occupied Units: {stored_occupied or 'NULL'}")
        print(f"      Occupancy Rate: {stored_rate:.2f}%" if stored_rate is not None else "      Occupancy Rate: NULL")
        print(f"      Square Footage: {stored_sqft:,.0f}" if stored_sqft else "      Square Footage: NULL")
        
        print(f"\n   📊 ACTUAL FROM STORES TABLE:")
        print(f"      Total Units: {actual_total}")
        print(f"      Occupied: {actual_occupied}")
        print(f"      Vacant: {actual_vacant}")
        print(f"      Calculated Occupancy: {actual_rate:.2f}%")
        print(f"      Total Sqft: {actual_sqft:,.0f}" if actual_sqft > 0 else "      Total Sqft: 0")
        
        # Check for discrepancies
        has_issues = False
        issues = []
        
        # Check if property has units in stores table
        if actual_total == 0:
            issues.append("⚠️  NO UNITS in stores table (property has no unit data)")
            has_issues = True
        
        # Check unit count mismatch
        if stored_total != actual_total:
            issues.append(f"❌ Unit count mismatch: stored={stored_total}, actual={actual_total}")
            has_issues = True
        
        # Check occupied count mismatch
        if stored_occupied != actual_occupied:
            issues.append(f"❌ Occupied count mismatch: stored={stored_occupied}, actual={actual_occupied}")
            has_issues = True
        
        # Check occupancy rate mismatch (allow 0.1% tolerance for rounding)
        if stored_rate is not None and abs(stored_rate - actual_rate) > 0.1:
            issues.append(f"❌ Occupancy rate mismatch: stored={stored_rate:.2f}%, actual={actual_rate:.2f}%")
            has_issues = True
        
        # Check square footage mismatch (allow 1% variance)
        if stored_sqft and actual_sqft > 0:
            variance = abs(stored_sqft - actual_sqft) / actual_sqft if actual_sqft > 0 else 1
            if variance > 0.01:
                issues.append(f"⚠️  Square footage mismatch: stored={stored_sqft:,.0f}, actual={actual_sqft:,.0f}")
        
        # Display status
        print(f"\n   🔍 VERIFICATION STATUS:")
        if has_issues:
            print("      ❌ ISSUES FOUND:")
            for issue in issues:
                print(f"         {issue}")
            issues_found.append({
                'property_id': property_id,
                'property_name': property_name,
                'issues': issues
            })
        else:
            if actual_total > 0:
                print("      ✅ CORRECT - Data matches stores table")
                correct_count += 1
            else:
                print("      ⚠️  NO UNIT DATA - Property exists but has no units in stores table")
                issues_found.append({
                    'property_id': property_id,
                    'property_name': property_name,
                    'issues': ["No units in stores table"]
                })
        
        print("-" * 100)
    
    # Summary
    print("\n" + "="*100)
    print("📊 VERIFICATION SUMMARY")
    print("="*100)
    print(f"\n  Total Properties: {len(properties)}")
    print(f"  ✅ Correct: {correct_count}")
    print(f"  ❌ With Issues: {len(issues_found)}")
    
    if issues_found:
        print(f"\n  🔍 PROPERTIES WITH ISSUES:")
        for item in issues_found:
            print(f"\n     Property ID {item['property_id']}: {item['property_name']}")
            for issue in item['issues']:
                print(f"        • {issue}")
    else:
        print(f"\n  🎉 ALL PROPERTIES HAVE CORRECT OCCUPANCY DATA!")
    
    print("\n" + "="*100)
    
    # Recommendations
    if issues_found:
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 100)
        
        no_units = [p for p in issues_found if any('NO UNITS' in i for i in p['issues'])]
        mismatches = [p for p in issues_found if not any('NO UNITS' in i for i in p['issues'])]
        
        if no_units:
            print(f"\n  📋 {len(no_units)} properties have no unit data:")
            print("     → These properties need rent roll data to be uploaded and imported")
            print("     → Or they may be properties without unit-level tracking")
        
        if mismatches:
            print(f"\n  ⚠️  {len(mismatches)} properties have data mismatches:")
            print("     → Run update script to sync properties table with stores table")
            print("     → Script: python sync_property_occupancy.py")
        
        print("\n" + "-" * 100)
    
    print("\n")
    conn.close()


if __name__ == "__main__":
    verify_all_properties()

