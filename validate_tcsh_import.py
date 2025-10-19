#!/usr/bin/env python3
"""
Validate TCSH Import - Verify Data Matches Rent Roll
Checks that the import was successful and accurate
"""

import sqlite3
from datetime import datetime

DB_PATH = "reims.db"

def validate_import():
    """Validate TCSH data import"""
    print("\n" + "="*80)
    print("✅ TCSH IMPORT VALIDATION")
    print("="*80)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    all_pass = True
    
    # Test 1: Unit Count
    print("\n📊 Test 1: Unit Count")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) as count FROM stores WHERE property_id = 6")
    unit_count = cursor.fetchone()['count']
    print(f"  Expected: 37 units")
    print(f"  Actual: {unit_count} units")
    if unit_count == 37:
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL")
        all_pass = False
    
    # Test 2: All Units Occupied
    print("\n📊 Test 2: Occupancy Status")
    print("-" * 80)
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'occupied' THEN 1 ELSE 0 END) as occupied,
            SUM(CASE WHEN status = 'vacant' THEN 1 ELSE 0 END) as vacant
        FROM stores
        WHERE property_id = 6
    """)
    result = cursor.fetchone()
    print(f"  Total Units: {result['total']}")
    print(f"  Occupied: {result['occupied']}")
    print(f"  Vacant: {result['vacant']}")
    print(f"  Expected: All 37 occupied, 0 vacant")
    if result['occupied'] == 37 and result['vacant'] == 0:
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL")
        all_pass = False
    
    # Test 3: Occupancy Rate
    print("\n📊 Test 3: Property Occupancy Rate")
    print("-" * 80)
    cursor.execute("""
        SELECT 
            total_units,
            occupied_units,
            occupancy_rate
        FROM properties
        WHERE id = 6
    """)
    prop = cursor.fetchone()
    print(f"  Total Units: {prop['total_units']}")
    print(f"  Occupied Units: {prop['occupied_units']}")
    print(f"  Occupancy Rate: {prop['occupancy_rate']:.2f}%")
    print(f"  Expected: 100%")
    if prop['occupancy_rate'] >= 99.9:  # Allow for rounding
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL")
        all_pass = False
    
    # Test 4: Total Square Footage
    print("\n📊 Test 4: Total Square Footage")
    print("-" * 80)
    cursor.execute("""
        SELECT SUM(sqft) as total_sqft
        FROM stores
        WHERE property_id = 6
    """)
    sqft = cursor.fetchone()['total_sqft']
    print(f"  Expected: 219,905 sqft (from rent roll)")
    print(f"  Actual: {sqft:,.0f} sqft")
    # Allow 1% variance
    if abs(sqft - 219905) / 219905 < 0.01:
        print("  ✅ PASS")
    else:
        print("  ⚠️  WARNING: Square footage doesn't match rent roll total")
        print(f"     Difference: {abs(sqft - 219905):,.0f} sqft")
    
    # Test 5: Real Tenant Names (no demo data)
    print("\n📊 Test 5: Real Tenant Names (No Demo Data)")
    print("-" * 80)
    cursor.execute("""
        SELECT COUNT(*) as demo_count
        FROM stores
        WHERE property_id = 6
        AND (
            tenant_name LIKE '%Acme%'
            OR tenant_name LIKE '%Global Tech%'
            OR tenant_name LIKE '%Metro Coffee%'
            OR unit_number LIKE 'Suite %'
            OR unit_number LIKE 'Space %'
        )
    """)
    demo_count = cursor.fetchone()['demo_count']
    print(f"  Demo/Generic Names Found: {demo_count}")
    print(f"  Expected: 0")
    if demo_count == 0:
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL - Still has demo data")
        all_pass = False
    
    # Test 6: Sample of Real Tenants
    print("\n📊 Test 6: Sample Real Tenants")
    print("-" * 80)
    expected_tenants = [
        'Ross Dress For Less',
        'Dollar Tree',
        'Old Navy',
        'PetSmart',
        'HomeGoods',
        'Buffalo Wild Wings'
    ]
    
    cursor.execute("""
        SELECT tenant_name
        FROM stores
        WHERE property_id = 6
    """)
    all_tenants = [row['tenant_name'] for row in cursor.fetchall()]
    
    found_count = 0
    for expected in expected_tenants:
        found = any(expected.lower() in tenant.lower() for tenant in all_tenants)
        status = "✓" if found else "✗"
        print(f"  {status} {expected}")
        if found:
            found_count += 1
    
    if found_count >= 5:  # At least 5 of 6 major tenants
        print(f"  ✅ PASS ({found_count}/6 major tenants found)")
    else:
        print(f"  ❌ FAIL (Only {found_count}/6 major tenants found)")
        all_pass = False
    
    # Test 7: Unit Numbers
    print("\n📊 Test 7: Unit Numbers")
    print("-" * 80)
    cursor.execute("""
        SELECT unit_number
        FROM stores
        WHERE property_id = 6
        ORDER BY unit_number
    """)
    units = [row['unit_number'] for row in cursor.fetchall()]
    
    print(f"  Sample Units: {', '.join(units[:5])}...")
    
    # Check for expected unit patterns
    has_target = any('target' in u.lower() for u in units)
    has_1000s = any(u.startswith('1') and u[1:].replace('B', '').replace('C', '').replace('/', '').isdigit() for u in units)
    has_2000s = any(u.startswith('2') and u[1:].isdigit() for u in units)
    
    print(f"  Has Target unit: {has_target} (NOTE: Correctly excluded - NAP-Exp Only)")
    print(f"  Has 1000-series units: {has_1000s}")
    print(f"  Has 2000-series units: {has_2000s}")
    
    # Target should NOT be present (it's an expense allocation, not a lease)
    if not has_target and has_1000s and has_2000s:
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL - Missing expected unit number patterns or has Target")
        all_pass = False
    
    # Summary
    print("\n" + "="*80)
    if all_pass:
        print("✅ ALL TESTS PASSED")
        print("="*80)
        print("\n🎉 TCSH data has been successfully imported!")
        print("   • 37 units imported")
        print("   • 100% occupancy")
        print("   • Real tenant data")
        print("   • Demo data removed")
        print("\n👉 View in dashboard: http://localhost:3001/property/6")
    else:
        print("❌ SOME TESTS FAILED")
        print("="*80)
        print("\n⚠️  Please review the failed tests above")
        print("   Run 'python fix_tcsh_data.py' again if needed")
    print("\n" + "="*80)
    
    conn.close()
    
    return all_pass


if __name__ == "__main__":
    validate_import()

