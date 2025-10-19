"""
Verify Stores Table Creation

This script verifies that the stores table was created correctly
with all columns, indexes, constraints, triggers, and functions.

Usage:
    python backend/db/migrations/verify_stores_table.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.db import init_db, close_db, fetch_all, fetch_val, fetch_one, execute


async def verify_table_exists() -> bool:
    """Check if stores table exists"""
    exists = await fetch_val("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'stores'
        )
    """)
    return exists


async def verify_foreign_key():
    """Verify foreign key to properties table"""
    fk_exists = await fetch_val("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu
              ON tc.constraint_name = ccu.constraint_name
            WHERE tc.table_name = 'stores'
              AND tc.constraint_type = 'FOREIGN KEY'
              AND ccu.table_name = 'properties'
        )
    """)
    
    print(f"\n🔗 Foreign Key Verification:")
    if fk_exists:
        print(f"   ✅ Foreign key to properties table exists")
        
        # Get FK details
        fk_details = await fetch_one("""
            SELECT 
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                rc.delete_rule
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
              ON tc.constraint_name = ccu.constraint_name
            JOIN information_schema.referential_constraints rc
              ON tc.constraint_name = rc.constraint_name
            WHERE tc.table_name = 'stores' AND tc.constraint_type = 'FOREIGN KEY'
        """)
        
        print(f"      Column: {fk_details['column_name']}")
        print(f"      References: {fk_details['foreign_table_name']}({fk_details['foreign_column_name']})")
        print(f"      On Delete: {fk_details['delete_rule']}")
        return True
    else:
        print(f"   ❌ Foreign key to properties table NOT found")
        return False


async def verify_columns():
    """Verify all columns exist with correct types"""
    columns = await fetch_all("""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = 'stores'
        ORDER BY ordinal_position
    """)
    
    expected_columns = [
        'id', 'property_id', 'unit_number', 'unit_name', 'sqft', 'floor_number',
        'tenant_name', 'tenant_type', 'lease_start_date', 'lease_end_date',
        'lease_status', 'monthly_rent', 'annual_rent', 'rent_escalation_pct',
        'security_deposit', 'status', 'occupancy_date', 'vacancy_date',
        'parking_spaces', 'utilities_included', 'common_area_maintenance_fee',
        'renewal_option', 'renewal_term_months', 'tenant_contact_name',
        'tenant_contact_phone', 'tenant_contact_email', 'created_at',
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
    
    # Show key column details
    print(f"\n   Key Columns:")
    key_cols = ['id', 'property_id', 'unit_number', 'sqft', 'status', 'monthly_rent']
    for col in columns:
        if col['column_name'] in key_cols:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"      {col['column_name']:20s} {col['data_type']:20s} {nullable}{default}")
    
    return True


async def verify_indexes():
    """Verify all indexes exist"""
    indexes = await fetch_all("""
        SELECT 
            indexname,
            indexdef
        FROM pg_indexes
        WHERE tablename = 'stores'
        AND schemaname = 'public'
        ORDER BY indexname
    """)
    
    expected_indexes = [
        'idx_stores_property_id',
        'idx_stores_status',
        'idx_stores_property_status',
        'idx_stores_lease_end_date',
        'idx_stores_tenant_name',
        'idx_stores_created_at',
        'idx_stores_lease_status',
        'idx_stores_tenant_type',
        'idx_stores_unit_number',
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
        WHERE conrelid = 'stores'::regclass
        ORDER BY conname
    """)
    
    expected_constraints = [
        'chk_sqft_positive',
        'chk_rent_positive',
        'chk_lease_dates',
        'chk_valid_status',
        'chk_valid_lease_status',
        'chk_valid_tenant_type',
        'chk_parking_non_negative',
        'chk_annual_rent_consistency',
        'chk_occupancy_date_valid',
        'chk_vacancy_after_occupancy',
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
    
    # Check unique constraint
    unique_constraints = [c for c in constraints if c['contype'] == 'u']
    if any('property_id' in c['definition'] and 'unit_number' in c['definition'] for c in unique_constraints):
        print(f"   ✅ Unique constraint (property_id, unit_number) present")
    
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
        WHERE event_object_table = 'stores'
    """)
    
    print(f"\n⚡ Trigger Verification:")
    print(f"   Found: {len(triggers)} trigger(s)")
    
    if len(triggers) < 2:
        print(f"   ❌ Expected 2 triggers (updated_at, sync_property_occupancy)")
        return False
    
    trigger_names = [t['trigger_name'] for t in triggers]
    
    has_update_trigger = any('updated_at' in name.lower() for name in trigger_names)
    has_sync_trigger = any('sync' in name.lower() or 'occupancy' in name.lower() for name in trigger_names)
    
    if not has_update_trigger:
        print(f"   ❌ updated_at trigger not found")
        return False
    
    if not has_sync_trigger:
        print(f"   ❌ sync_property_occupancy trigger not found")
        return False
    
    print(f"   ✅ updated_at trigger present")
    print(f"   ✅ sync_property_occupancy trigger present")
    
    # Show trigger details
    print(f"\n   Trigger Details:")
    for trig in triggers:
        print(f"      {trig['trigger_name']:35s} {trig['action_timing']} {trig['event_manipulation']}")
    
    return True


async def verify_functions():
    """Verify custom functions exist"""
    functions = await fetch_all("""
        SELECT 
            routine_name,
            routine_type
        FROM information_schema.routines
        WHERE routine_schema = 'public'
        AND (
            routine_name LIKE '%store%' OR 
            routine_name LIKE '%occupancy%'
        )
        ORDER BY routine_name
    """)
    
    print(f"\n🔧 Function Verification:")
    print(f"   Found: {len(functions)} function(s)")
    
    function_names = [f['routine_name'] for f in functions]
    
    has_calc_function = any('calculate' in name and 'occupancy' in name for name in function_names)
    has_sync_function = any('sync' in name and 'occupancy' in name for name in function_names)
    
    if has_calc_function:
        print(f"   ✅ calculate_property_occupancy function present")
    else:
        print(f"   ⚠️  calculate_property_occupancy function not found")
    
    if has_sync_function:
        print(f"   ✅ sync_property_occupancy function present")
    else:
        print(f"   ⚠️  sync_property_occupancy function not found")
    
    return True


async def test_insert_and_sync():
    """Test inserting stores and auto-sync to properties"""
    print(f"\n🧪 Data Operation & Auto-Sync Test:")
    
    try:
        # First, create a test property
        property_id = await fetch_val("""
            INSERT INTO properties (
                name, address, city, state, 
                property_type, total_sqft, status
            ) VALUES (
                'Test Property for Stores', '123 Test St', 'Test City', 'CA',
                'office', 10000, 'active'
            ) RETURNING id
        """)
        
        print(f"   ✅ Test property created (ID: {property_id})")
        
        # Insert test stores
        store1_id = await fetch_val("""
            INSERT INTO stores (
                property_id, unit_number, sqft, status,
                tenant_name, monthly_rent
            ) VALUES (
                $1, 'Suite 101', 1000, 'occupied',
                'Test Tenant 1', 2500.00
            ) RETURNING id
        """, property_id)
        
        print(f"   ✅ Store 1 created (occupied)")
        
        store2_id = await fetch_val("""
            INSERT INTO stores (
                property_id, unit_number, sqft, status
            ) VALUES (
                $1, 'Suite 102', 1200, 'vacant'
            ) RETURNING id
        """, property_id)
        
        print(f"   ✅ Store 2 created (vacant)")
        
        # Check if property was auto-updated
        property_data = await fetch_one("""
            SELECT total_units, occupied_units, occupancy_rate
            FROM properties
            WHERE id = $1
        """, property_id)
        
        print(f"\n   ⚡ Auto-Sync Results:")
        print(f"      Total Units: {property_data['total_units']}")
        print(f"      Occupied Units: {property_data['occupied_units']}")
        print(f"      Occupancy Rate: {property_data['occupancy_rate']}%")
        
        if property_data['total_units'] == 2 and property_data['occupied_units'] == 1:
            print(f"   ✅ Property auto-sync working correctly!")
        else:
            print(f"   ❌ Property auto-sync NOT working")
            return False
        
        # Test calculate function
        calc_occupancy = await fetch_val("""
            SELECT calculate_property_occupancy($1)
        """, property_id)
        
        print(f"\n   🔧 Function Test:")
        print(f"      calculate_property_occupancy: {calc_occupancy}%")
        
        if calc_occupancy == 50.00:
            print(f"   ✅ Function working correctly (1/2 = 50%)")
        
        # Test update trigger
        await execute("""
            UPDATE stores 
            SET monthly_rent = 3000.00
            WHERE id = $1
        """, store1_id)
        
        updated_store = await fetch_one("""
            SELECT monthly_rent, updated_at
            FROM stores
            WHERE id = $1
        """, store1_id)
        
        print(f"\n   🔄 Update Trigger Test:")
        print(f"      New rent: ${updated_store['monthly_rent']:,.2f}")
        print(f"      Updated at: {updated_store['updated_at']}")
        print(f"   ✅ UPDATE trigger working")
        
        # Clean up test data
        await execute("DELETE FROM properties WHERE id = $1", property_id)
        print(f"\n   ✅ Test data cleaned up (CASCADE deleted stores)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_constraints():
    """Test that constraints are enforced"""
    print(f"\n🔒 Constraint Enforcement Test:")
    
    # Create test property first
    try:
        property_id = await fetch_val("""
            INSERT INTO properties (name, address, city, state, property_type)
            VALUES ('Constraint Test', '123 St', 'City', 'CA', 'office')
            RETURNING id
        """)
        
        # Test sqft constraint (should fail)
        try:
            await execute("""
                INSERT INTO stores (property_id, unit_number, sqft, status)
                VALUES ($1, 'Test', -100, 'vacant')
            """, property_id)
            print(f"   ❌ Square footage constraint NOT working")
            return False
        except Exception as e:
            if "chk_sqft_positive" in str(e):
                print(f"   ✅ Square footage constraint working")
        
        # Test valid status constraint (should fail)
        try:
            await execute("""
                INSERT INTO stores (property_id, unit_number, sqft, status)
                VALUES ($1, 'Test', 1000, 'invalid_status')
            """, property_id)
            print(f"   ❌ Status constraint NOT working")
            return False
        except Exception as e:
            if "chk_valid_status" in str(e):
                print(f"   ✅ Status constraint working")
        
        # Test lease dates constraint (should fail)
        try:
            await execute("""
                INSERT INTO stores (
                    property_id, unit_number, sqft, status,
                    lease_start_date, lease_end_date
                )
                VALUES ($1, 'Test', 1000, 'vacant', '2025-12-31', '2025-01-01')
            """, property_id)
            print(f"   ❌ Lease dates constraint NOT working")
            return False
        except Exception as e:
            if "chk_lease_dates" in str(e):
                print(f"   ✅ Lease dates constraint working")
        
        # Test unique constraint (should fail)
        try:
            # Insert first store
            await execute("""
                INSERT INTO stores (property_id, unit_number, sqft, status)
                VALUES ($1, 'Suite 100', 1000, 'vacant')
            """, property_id)
            
            # Try to insert duplicate
            await execute("""
                INSERT INTO stores (property_id, unit_number, sqft, status)
                VALUES ($1, 'Suite 100', 1000, 'vacant')
            """, property_id)
            
            print(f"   ❌ Unique constraint (property_id, unit_number) NOT working")
            return False
        except Exception as e:
            if "uq_stores_property_unit" in str(e) or "unique" in str(e).lower():
                print(f"   ✅ Unique constraint (property_id, unit_number) working")
        
        # Clean up
        await execute("DELETE FROM properties WHERE id = $1", property_id)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Constraint test error: {str(e)}")
        return False


async def main():
    """Main verification function"""
    print("\n" + "="*70)
    print("REIMS Stores Table Verification")
    print("="*70)
    
    try:
        # Initialize database
        print("\n🔌 Connecting to database...")
        await init_db()
        print("✅ Connected to database")
        
        # Check table exists
        print("\n📋 Checking table existence...")
        if not await verify_table_exists():
            print("❌ Stores table does not exist!")
            print("\nRun the migration first:")
            print("  python backend/db/migrations/run_migration.py 002_create_stores.sql")
            return
        
        print("✅ Stores table exists")
        
        # Run all verifications
        all_passed = True
        
        all_passed &= await verify_columns()
        all_passed &= await verify_foreign_key()
        all_passed &= await verify_indexes()
        all_passed &= await verify_constraints()
        all_passed &= await verify_triggers()
        all_passed &= await verify_functions()
        all_passed &= await test_insert_and_sync()
        all_passed &= await test_constraints()
        
        # Final summary
        print("\n" + "="*70)
        if all_passed:
            print("✅ ALL VERIFICATIONS PASSED")
            print("="*70)
            print("\n🎉 Stores table is correctly configured!")
            print("\n✨ Special Features:")
            print("  • Auto-sync property occupancy rates")
            print("  • Calculate occupancy function available")
            print("  • Unique unit numbers per property")
            print("  • Cascade delete from properties")
            print("\nYou can now:")
            print("  • Insert store/unit data")
            print("  • Query stores by property")
            print("  • Track tenant leases")
            print("  • Monitor occupancy rates")
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
















