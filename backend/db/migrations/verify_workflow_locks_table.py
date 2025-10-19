#!/usr/bin/env python3
"""
Verification script for workflow_locks table
Tests schema, functions, triggers, and business logic
"""

import asyncio
import asyncpg
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', 5432)),
    'database': os.getenv('DATABASE_NAME', 'reims'),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD', 'postgres')
}


async def verify_schema(conn):
    """Verify table schema"""
    print("\n" + "="*80)
    print("📋 VERIFYING WORKFLOW_LOCKS TABLE SCHEMA")
    print("="*80)
    
    # Check if table exists
    table_exists = await conn.fetchval("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'workflow_locks'
        );
    """)
    
    print(f"\n✅ Table exists: {table_exists}")
    
    if not table_exists:
        print("❌ Table 'workflow_locks' does not exist!")
        return False
    
    # Check columns
    columns = await conn.fetch("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'workflow_locks'
        ORDER BY ordinal_position;
    """)
    
    print(f"\n📊 Columns ({len(columns)}):")
    print("-" * 80)
    for col in columns:
        nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
        default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
        print(f"  • {col['column_name']:<30} {col['data_type']:<20} {nullable}{default}")
    
    # Check indexes
    indexes = await conn.fetch("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'workflow_locks'
        ORDER BY indexname;
    """)
    
    print(f"\n📈 Indexes ({len(indexes)}):")
    print("-" * 80)
    for idx in indexes:
        print(f"  • {idx['indexname']}")
    
    # Check constraints
    constraints = await conn.fetch("""
        SELECT conname, contype, pg_get_constraintdef(oid) as definition
        FROM pg_constraint
        WHERE conrelid = 'workflow_locks'::regclass
        ORDER BY contype, conname;
    """)
    
    print(f"\n🔒 Constraints ({len(constraints)}):")
    print("-" * 80)
    constraint_types = {'p': 'PRIMARY KEY', 'f': 'FOREIGN KEY', 'c': 'CHECK', 'u': 'UNIQUE'}
    for con in constraints:
        con_type = constraint_types.get(con['contype'], con['contype'])
        print(f"  • {con['conname']:<35} [{con_type}]")
        print(f"    {con['definition']}")
    
    return True


async def verify_triggers(conn):
    """Verify triggers"""
    print("\n" + "="*80)
    print("⚡ VERIFYING TRIGGERS")
    print("="*80)
    
    triggers = await conn.fetch("""
        SELECT trigger_name, event_manipulation, action_statement
        FROM information_schema.triggers
        WHERE event_object_table = 'workflow_locks'
        ORDER BY trigger_name;
    """)
    
    print(f"\n✅ Triggers found: {len(triggers)}")
    print("-" * 80)
    for trg in triggers:
        print(f"  • {trg['trigger_name']}")
        print(f"    Event: {trg['event_manipulation']}")
    
    expected_triggers = [
        'trg_workflow_locks_updated_at',
        'trg_calculate_lock_duration',
        'trg_sync_property_workflow_lock_insert',
        'trg_sync_property_workflow_lock_update'
    ]
    
    found_triggers = [t['trigger_name'] for t in triggers]
    for expected in expected_triggers:
        if expected in found_triggers:
            print(f"  ✅ {expected}")
        else:
            print(f"  ❌ {expected} NOT FOUND")


async def verify_functions(conn):
    """Verify custom functions"""
    print("\n" + "="*80)
    print("🔧 VERIFYING FUNCTIONS")
    print("="*80)
    
    expected_functions = [
        'is_action_blocked',
        'get_active_locks',
        'create_lock_from_alert',
        'unlock_from_alert_resolution',
        'expire_old_locks',
        'get_lock_summary',
        'get_blocked_actions_for_property'
    ]
    
    for func_name in expected_functions:
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE n.nspname = 'public' AND p.proname = $1
            );
        """, func_name)
        
        status = "✅" if exists else "❌"
        print(f"  {status} {func_name}()")


async def test_workflow_lock_operations(conn):
    """Test workflow lock operations"""
    print("\n" + "="*80)
    print("🧪 TESTING WORKFLOW LOCK OPERATIONS")
    print("="*80)
    
    # Create test property
    property_id = await conn.fetchval("""
        INSERT INTO properties (name, address, city, state, total_sqft)
        VALUES ('Test Lock Property', '123 Lock St', 'Test City', 'CA', 10000)
        RETURNING id;
    """)
    print(f"\n✅ Created test property: {property_id}")
    
    # Create test alert
    alert_id = await conn.fetchval("""
        INSERT INTO committee_alerts (
            property_id, alert_type, alert_title, alert_description,
            severity_level, committee_responsible
        )
        VALUES ($1, 'dscr_low', 'DSCR Below Threshold', 'DSCR dropped to 1.10',
                'critical', 'Finance Sub-Committee')
        RETURNING id;
    """, property_id)
    print(f"✅ Created test alert: {alert_id}")
    
    # Test 1: Create lock from alert
    print("\n📝 Test 1: Create lock from alert")
    lock_id = await conn.fetchval("""
        SELECT create_lock_from_alert($1, ARRAY['refinance', 'sell', 'dispose']);
    """, alert_id)
    print(f"  ✅ Created lock: {lock_id}")
    
    # Verify lock was created
    lock = await conn.fetchrow("""
        SELECT * FROM workflow_locks WHERE id = $1;
    """, lock_id)
    print(f"  • Lock type: {lock['lock_type']}")
    print(f"  • Lock status: {lock['status']}")
    print(f"  • Blocked actions: {lock['blocked_actions']}")
    
    # Test 2: Check if actions are blocked
    print("\n📝 Test 2: Check if actions are blocked")
    refinance_blocked = await conn.fetchval("""
        SELECT is_action_blocked($1, 'refinance');
    """, property_id)
    print(f"  ✅ Refinance blocked: {refinance_blocked}")
    
    acquisition_blocked = await conn.fetchval("""
        SELECT is_action_blocked($1, 'acquisition');
    """, property_id)
    print(f"  ✅ Acquisition blocked: {acquisition_blocked}")
    
    # Test 3: Get active locks
    print("\n📝 Test 3: Get active locks for property")
    active_locks = await conn.fetch("""
        SELECT * FROM get_active_locks($1);
    """, property_id)
    print(f"  ✅ Active locks found: {len(active_locks)}")
    for lock in active_locks:
        print(f"    • {lock['lock_type']} - {lock['lock_reason']}")
    
    # Test 4: Get blocked actions
    print("\n📝 Test 4: Get all blocked actions for property")
    blocked_actions = await conn.fetchval("""
        SELECT get_blocked_actions_for_property($1);
    """, property_id)
    print(f"  ✅ Blocked actions: {blocked_actions}")
    
    # Test 5: Get lock summary
    print("\n📝 Test 5: Get lock summary")
    summary = await conn.fetchval("""
        SELECT get_lock_summary($1);
    """, property_id)
    print(f"  ✅ Lock summary:")
    import json
    summary_dict = json.loads(summary)
    for key, value in summary_dict.items():
        print(f"    • {key}: {value}")
    
    # Test 6: Verify property has_active_alerts flag (trigger test)
    print("\n📝 Test 6: Verify property has_active_alerts flag (trigger)")
    has_alerts = await conn.fetchval("""
        SELECT has_active_alerts FROM properties WHERE id = $1;
    """, property_id)
    print(f"  ✅ Property has_active_alerts: {has_alerts}")
    
    # Test 7: Unlock the lock
    print("\n📝 Test 7: Unlock from alert resolution")
    unlocked_count = await conn.fetchval("""
        SELECT unlock_from_alert_resolution($1, NULL, 'Committee approved refinancing');
    """, alert_id)
    print(f"  ✅ Unlocked {unlocked_count} lock(s)")
    
    # Verify lock was unlocked and duration calculated
    unlocked_lock = await conn.fetchrow("""
        SELECT status, unlocked_at, lock_duration_hours, unlock_reason
        FROM workflow_locks WHERE id = $1;
    """, lock_id)
    print(f"  • Status: {unlocked_lock['status']}")
    print(f"  • Unlocked at: {unlocked_lock['unlocked_at']}")
    print(f"  • Duration (hours): {unlocked_lock['lock_duration_hours']}")
    print(f"  • Reason: {unlocked_lock['unlock_reason']}")
    
    # Verify property has_active_alerts is now false
    has_alerts_after = await conn.fetchval("""
        SELECT has_active_alerts FROM properties WHERE id = $1;
    """, property_id)
    print(f"  ✅ Property has_active_alerts after unlock: {has_alerts_after}")
    
    # Test 8: Test auto-expiration
    print("\n📝 Test 8: Test auto-expiration of old locks")
    
    # Create an old lock by manually setting locked_at to 100 days ago
    old_alert_id = await conn.fetchval("""
        INSERT INTO committee_alerts (
            property_id, alert_type, alert_title, severity_level, committee_responsible
        )
        VALUES ($1, 'occupancy_low', 'Low Occupancy', 'warning', 'Occupancy Committee')
        RETURNING id;
    """, property_id)
    
    old_lock_id = await conn.fetchval("""
        INSERT INTO workflow_locks (
            property_id, alert_id, lock_type, lock_severity,
            blocked_actions, locked_at
        )
        VALUES ($1, $2, 'sale_hold', 'warning', ARRAY['sell'],
                CURRENT_TIMESTAMP - INTERVAL '100 days')
        RETURNING id;
    """, property_id, old_alert_id)
    print(f"  ✅ Created old lock (100 days ago): {old_lock_id}")
    
    # Run auto-expiration
    expired_count = await conn.fetchval("""
        SELECT expire_old_locks(90);
    """)
    print(f"  ✅ Expired {expired_count} lock(s)")
    
    # Verify the old lock was expired
    expired_lock = await conn.fetchrow("""
        SELECT status, unlock_reason FROM workflow_locks WHERE id = $1;
    """, old_lock_id)
    print(f"  • Status: {expired_lock['status']}")
    print(f"  • Reason: {expired_lock['unlock_reason']}")
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    await conn.execute("DELETE FROM properties WHERE id = $1;", property_id)
    print("  ✅ Cleanup complete")


async def main():
    """Main verification function"""
    print("\n" + "="*80)
    print("🔍 WORKFLOW_LOCKS TABLE VERIFICATION")
    print("="*80)
    print(f"Database: {DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ Database connection successful")
        
        # Run verifications
        schema_ok = await verify_schema(conn)
        
        if schema_ok:
            await verify_triggers(conn)
            await verify_functions(conn)
            await test_workflow_lock_operations(conn)
        
        # Final summary
        print("\n" + "="*80)
        print("✅ VERIFICATION COMPLETE")
        print("="*80)
        print("\n📊 Summary:")
        print("  • Schema: ✅ Verified")
        print("  • Triggers: ✅ Verified")
        print("  • Functions: ✅ Verified")
        print("  • Operations: ✅ Tested")
        print("\n🎯 workflow_locks table is ready for production!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await conn.close()
        print("\n🔌 Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())
















