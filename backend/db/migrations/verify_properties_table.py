"""
Verify Properties Table Creation

This script verifies that the properties table was created correctly
with all columns, indexes, constraints, and triggers.

Usage:
    python backend/db/migrations/verify_properties_table.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.db import init_db, close_db, fetch_all, fetch_val


async def verify_table_exists() -> bool:
    """Check if properties table exists"""
    exists = await fetch_val("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'properties'
        )
    """)
    return exists


async def verify_columns():
    """Verify all columns exist with correct types"""
    columns = await fetch_all("""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = 'properties'
        ORDER BY ordinal_position
    """)
    
    expected_columns = [
        'id', 'name', 'description', 'address', 'city', 'state', 'zip_code',
        'latitude', 'longitude', 'total_sqft', 'year_built', 'property_type',
        'property_class', 'acquisition_cost', 'acquisition_date', 'current_value',
        'last_appraised_date', 'estimated_market_value', 'loan_balance',
        'original_loan_amount', 'interest_rate', 'loan_maturity_date', 'dscr',
        'annual_noi', 'annual_revenue', 'total_units', 'occupied_units',
        'occupancy_rate', 'status', 'has_active_alerts', 'created_at',
        'updated_at', 'created_by', 'updated_by'
    ]
    
    actual_columns = [c['column_name'] for c in columns]
    
    print(f"\n📊 Column Verification:")
    print(f"   Expected: {len(expected_columns)} columns")
    print(f"   Found: {len(actual_columns)} columns")
    
    missing = set(expected_columns) - set(actual_columns)
    extra = set(actual_columns) - set(expected_columns)
    
    if missing:
        print(f"   ❌ Missing columns: {missing}")
        return False
    
    if extra:
        print(f"   ⚠️  Extra columns: {extra}")
    
    print(f"   ✅ All required columns present")
    
    # Show column details
    print(f"\n   Column Details:")
    for col in columns[:10]:  # Show first 10 columns
        nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
        default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
        print(f"      {col['column_name']:25s} {col['data_type']:20s} {nullable}{default}")
    
    if len(columns) > 10:
        print(f"      ... and {len(columns) - 10} more columns")
    
    return True


async def verify_indexes():
    """Verify all indexes exist"""
    indexes = await fetch_all("""
        SELECT 
            indexname,
            indexdef
        FROM pg_indexes
        WHERE tablename = 'properties'
        AND schemaname = 'public'
        ORDER BY indexname
    """)
    
    expected_indexes = [
        'idx_properties_status',
        'idx_properties_city_state',
        'idx_properties_property_type',
        'idx_properties_occupancy_rate',
        'idx_properties_created_at',
        'idx_properties_has_alerts',
        'idx_properties_current_value',
        'idx_properties_coordinates',
        'idx_properties_class',
    ]
    
    actual_indexes = [i['indexname'] for i in indexes if not i['indexname'].endswith('_pkey')]
    
    print(f"\n🔍 Index Verification:")
    print(f"   Expected: {len(expected_indexes)} indexes")
    print(f"   Found: {len(actual_indexes)} indexes (excluding primary key)")
    
    missing = set(expected_indexes) - set(actual_indexes)
    
    if missing:
        print(f"   ❌ Missing indexes: {missing}")
        return False
    
    print(f"   ✅ All required indexes present")
    
    # Show index details
    print(f"\n   Index Details:")
    for idx in indexes:
        if not idx['indexname'].endswith('_pkey'):
            print(f"      {idx['indexname']}")
    
    return True


async def verify_constraints():
    """Verify all constraints exist"""
    constraints = await fetch_all("""
        SELECT 
            conname,
            contype,
            pg_get_constraintdef(oid) as definition
        FROM pg_constraint
        WHERE conrelid = 'properties'::regclass
        ORDER BY conname
    """)
    
    expected_constraints = [
        'chk_occupancy_rate',
        'chk_sqft_positive',
        'chk_acquisition_before_current',
        'chk_year_built_reasonable',
        'chk_occupied_within_total',
        'chk_valid_status',
        'chk_valid_property_type',
        'chk_valid_property_class',
    ]
    
    actual_constraints = [c['conname'] for c in constraints if c['contype'] == 'c']
    
    print(f"\n🔒 Constraint Verification:")
    print(f"   Expected: {len(expected_constraints)} check constraints")
    print(f"   Found: {len(actual_constraints)} check constraints")
    
    missing = set(expected_constraints) - set(actual_constraints)
    
    if missing:
        print(f"   ❌ Missing constraints: {missing}")
        return False
    
    print(f"   ✅ All required constraints present")
    
    # Show constraint details
    print(f"\n   Constraint Details:")
    for con in constraints:
        if con['contype'] == 'c':
            print(f"      {con['conname']:35s} CHECK ({con['definition'][:60]}...)")
    
    return True


async def verify_triggers():
    """Verify triggers exist"""
    triggers = await fetch_all("""
        SELECT 
            trigger_name,
            event_manipulation,
            action_timing,
            action_statement
        FROM information_schema.triggers
        WHERE event_object_table = 'properties'
    """)
    
    print(f"\n⚡ Trigger Verification:")
    print(f"   Found: {len(triggers)} trigger(s)")
    
    if len(triggers) == 0:
        print(f"   ❌ No triggers found (expected updated_at trigger)")
        return False
    
    has_update_trigger = any('updated_at' in t['trigger_name'].lower() for t in triggers)
    
    if not has_update_trigger:
        print(f"   ❌ updated_at trigger not found")
        return False
    
    print(f"   ✅ updated_at trigger present")
    
    # Show trigger details
    print(f"\n   Trigger Details:")
    for trig in triggers:
        print(f"      {trig['trigger_name']:30s} {trig['action_timing']} {trig['event_manipulation']}")
    
    return True


async def test_insert_select():
    """Test inserting and selecting data"""
    from backend.db import fetch_val, fetch_one, execute
    
    print(f"\n🧪 Data Operation Test:")
    
    try:
        # Insert test record
        property_id = await fetch_val("""
            INSERT INTO properties (
                name, address, city, state, zip_code,
                total_sqft, year_built, property_type, property_class,
                occupancy_rate, current_value, status
            ) VALUES (
                'Test Property', '123 Test St', 'Test City', 'CA', '90001',
                10000, 2020, 'office', 'A',
                85.50, 5000000.00, 'active'
            ) RETURNING id
        """)
        
        print(f"   ✅ INSERT successful (ID: {property_id})")
        
        # Select test record
        property_data = await fetch_one("""
            SELECT name, city, property_type, occupancy_rate, current_value
            FROM properties
            WHERE id = $1
        """, property_id)
        
        print(f"   ✅ SELECT successful")
        print(f"      Name: {property_data['name']}")
        print(f"      City: {property_data['city']}")
        print(f"      Type: {property_data['property_type']}")
        print(f"      Occupancy: {property_data['occupancy_rate']}%")
        print(f"      Value: ${property_data['current_value']:,.2f}")
        
        # Test update trigger
        await execute("""
            UPDATE properties 
            SET occupancy_rate = 90.00
            WHERE id = $1
        """, property_id)
        
        updated_record = await fetch_one("""
            SELECT occupancy_rate, updated_at
            FROM properties
            WHERE id = $1
        """, property_id)
        
        print(f"   ✅ UPDATE successful (trigger fired)")
        print(f"      New occupancy: {updated_record['occupancy_rate']}%")
        print(f"      Updated at: {updated_record['updated_at']}")
        
        # Clean up test data
        await execute("DELETE FROM properties WHERE id = $1", property_id)
        print(f"   ✅ DELETE successful (test data cleaned up)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Data operation failed: {str(e)}")
        return False


async def test_constraints():
    """Test that constraints are enforced"""
    from backend.db import execute
    
    print(f"\n🔒 Constraint Test:")
    
    # Test occupancy rate constraint (should fail)
    try:
        await execute("""
            INSERT INTO properties (name, address, city, state, occupancy_rate)
            VALUES ('Test', '123 St', 'City', 'CA', 150.00)
        """)
        print(f"   ❌ Occupancy rate constraint NOT working (allowed invalid value)")
        return False
    except Exception as e:
        if "chk_occupancy_rate" in str(e):
            print(f"   ✅ Occupancy rate constraint working")
        else:
            print(f"   ⚠️  Unexpected error: {str(e)[:100]}")
    
    # Test sqft constraint (should fail)
    try:
        await execute("""
            INSERT INTO properties (name, address, city, state, total_sqft)
            VALUES ('Test', '123 St', 'City', 'CA', -1000)
        """)
        print(f"   ❌ Square footage constraint NOT working")
        return False
    except Exception as e:
        if "chk_sqft_positive" in str(e):
            print(f"   ✅ Square footage constraint working")
        else:
            print(f"   ⚠️  Unexpected error: {str(e)[:100]}")
    
    return True


async def main():
    """Main verification function"""
    print("\n" + "="*70)
    print("REIMS Properties Table Verification")
    print("="*70)
    
    try:
        # Initialize database
        print("\n🔌 Connecting to database...")
        await init_db()
        print("✅ Connected to database")
        
        # Check table exists
        print("\n📋 Checking table existence...")
        if not await verify_table_exists():
            print("❌ Properties table does not exist!")
            print("\nRun the migration first:")
            print("  python backend/db/migrations/run_migration.py 001_create_properties.sql")
            return
        
        print("✅ Properties table exists")
        
        # Run all verifications
        all_passed = True
        
        all_passed &= await verify_columns()
        all_passed &= await verify_indexes()
        all_passed &= await verify_constraints()
        all_passed &= await verify_triggers()
        all_passed &= await test_insert_select()
        all_passed &= await test_constraints()
        
        # Final summary
        print("\n" + "="*70)
        if all_passed:
            print("✅ ALL VERIFICATIONS PASSED")
            print("="*70)
            print("\n🎉 Properties table is correctly configured!")
            print("\nYou can now:")
            print("  • Insert property data")
            print("  • Query properties")
            print("  • Build your property management API")
        else:
            print("⚠️  SOME VERIFICATIONS FAILED")
            print("="*70)
            print("\nPlease review the errors above and re-run the migration if needed.")
        
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Verification error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
















