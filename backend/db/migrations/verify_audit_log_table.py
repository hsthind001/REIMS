"""
Verification script for audit_log table (Migration 007)
Tests table structure, indexes, constraints, and basic operations
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# Database connection details
DB_CONFIG = {
    'dbname': 'reims',
    'user': 'postgres',
    'password': 'reims2024',
    'host': 'localhost',
    'port': '5432'
}

def verify_audit_log_table():
    """Comprehensive verification of audit_log table"""
    print("=" * 80)
    print("AUDIT_LOG TABLE VERIFICATION")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Check if table exists
        print("\n1. Checking if audit_log table exists...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'audit_log'
            );
        """)
        exists = cur.fetchone()['exists']
        if exists:
            print("   ✓ audit_log table exists")
        else:
            print("   ✗ audit_log table NOT FOUND")
            return False
        
        # 2. Verify all columns
        print("\n2. Verifying table structure...")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'audit_log'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        required_columns = {
            'id': 'uuid',
            'action': 'character varying',
            'action_category': 'character varying',
            'br_id': 'character varying',
            'br_description': 'character varying',
            'property_id': 'uuid',
            'document_id': 'uuid',
            'alert_id': 'uuid',
            'user_id': 'uuid',
            'user_email': 'character varying',
            'user_role': 'character varying',
            'ip_address': 'inet',
            'user_agent': 'text',
            'old_values': 'jsonb',
            'new_values': 'jsonb',
            'details': 'jsonb',
            'success': 'boolean',
            'error_message': 'text',
            'session_id': 'character varying',
            'request_id': 'character varying',
            'timestamp': 'timestamp without time zone'
        }
        
        found_columns = {col['column_name']: col['data_type'] for col in columns}
        
        all_columns_present = True
        for col_name, expected_type in required_columns.items():
            if col_name in found_columns:
                actual_type = found_columns[col_name]
                if actual_type == expected_type:
                    print(f"   ✓ {col_name}: {actual_type}")
                else:
                    print(f"   ⚠ {col_name}: expected {expected_type}, got {actual_type}")
            else:
                print(f"   ✗ {col_name}: MISSING")
                all_columns_present = False
        
        if not all_columns_present:
            return False
        
        # 3. Verify indexes
        print("\n3. Verifying indexes...")
        cur.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'audit_log'
            ORDER BY indexname;
        """)
        indexes = cur.fetchall()
        
        expected_indexes = [
            'idx_audit_action',
            'idx_audit_br_id',
            'idx_audit_document_id',
            'idx_audit_property_id',
            'idx_audit_property_timestamp',
            'idx_audit_timestamp',
            'idx_audit_user_id',
            'idx_audit_user_timestamp'
        ]
        
        found_indexes = [idx['indexname'] for idx in indexes if idx['indexname'].startswith('idx_')]
        
        for expected_idx in expected_indexes:
            if expected_idx in found_indexes:
                print(f"   ✓ {expected_idx}")
            else:
                print(f"   ✗ {expected_idx}: MISSING")
        
        # 4. Verify foreign key constraints
        print("\n4. Verifying foreign key constraints...")
        cur.execute("""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name = 'audit_log';
        """)
        fkeys = cur.fetchall()
        
        expected_fkeys = [
            ('property_id', 'properties'),
            ('document_id', 'financial_documents'),
            ('alert_id', 'committee_alerts')
        ]
        
        for column, ref_table in expected_fkeys:
            found = any(fk['column_name'] == column and fk['foreign_table_name'] == ref_table for fk in fkeys)
            if found:
                print(f"   ✓ {column} → {ref_table}")
            else:
                print(f"   ⚠ {column} → {ref_table}: MISSING (may not exist yet)")
        
        # 5. Test insert operation
        print("\n5. Testing insert operation...")
        test_data = {
            'action': 'TEST_ACTION',
            'action_category': 'test',
            'br_id': 'BR-TEST',
            'br_description': 'Test audit log entry',
            'user_email': 'test@reims.com',
            'user_role': 'analyst',
            'new_values': json.dumps({'test': 'data'}),
            'details': json.dumps({'test_mode': True}),
            'success': True,
            'session_id': 'test-session-123',
            'request_id': 'test-request-456'
        }
        
        cur.execute("""
            INSERT INTO audit_log (
                action, action_category, br_id, br_description,
                user_email, user_role, new_values, details,
                success, session_id, request_id
            ) VALUES (
                %(action)s, %(action_category)s, %(br_id)s, %(br_description)s,
                %(user_email)s, %(user_role)s, %(new_values)s::jsonb, %(details)s::jsonb,
                %(success)s, %(session_id)s, %(request_id)s
            ) RETURNING id, timestamp;
        """, test_data)
        
        result = cur.fetchone()
        test_id = result['id']
        test_timestamp = result['timestamp']
        
        print(f"   ✓ Inserted test record: {test_id}")
        print(f"   ✓ Timestamp auto-generated: {test_timestamp}")
        
        # 6. Test query with indexes
        print("\n6. Testing query operations...")
        
        # Query by timestamp
        cur.execute("""
            SELECT id, action, user_email
            FROM audit_log
            WHERE timestamp >= NOW() - INTERVAL '1 hour'
            ORDER BY timestamp DESC
            LIMIT 5;
        """)
        results = cur.fetchall()
        print(f"   ✓ Timestamp query returned {len(results)} record(s)")
        
        # Query by action
        cur.execute("""
            SELECT id, action, timestamp
            FROM audit_log
            WHERE action = 'TEST_ACTION';
        """)
        results = cur.fetchall()
        print(f"   ✓ Action query returned {len(results)} record(s)")
        
        # Query by br_id
        cur.execute("""
            SELECT id, br_id, br_description
            FROM audit_log
            WHERE br_id = 'BR-TEST';
        """)
        results = cur.fetchall()
        print(f"   ✓ BR_ID query returned {len(results)} record(s)")
        
        # 7. Test JSONB queries
        print("\n7. Testing JSONB operations...")
        cur.execute("""
            SELECT id, new_values->>'test' as test_value
            FROM audit_log
            WHERE id = %s;
        """, (test_id,))
        result = cur.fetchone()
        if result and result['test_value'] == 'data':
            print(f"   ✓ JSONB query successful: {result['test_value']}")
        else:
            print(f"   ✗ JSONB query failed")
        
        # 8. Cleanup test data
        print("\n8. Cleaning up test data...")
        cur.execute("DELETE FROM audit_log WHERE id = %s;", (test_id,))
        conn.commit()
        print("   ✓ Test data removed")
        
        # 9. Final statistics
        print("\n9. Table statistics...")
        cur.execute("SELECT COUNT(*) as count FROM audit_log;")
        count = cur.fetchone()['count']
        print(f"   ✓ Total audit records: {count}")
        
        # 10. Check table comments (documentation)
        print("\n10. Checking table documentation...")
        cur.execute("""
            SELECT obj_description('audit_log'::regclass) as table_comment;
        """)
        result = cur.fetchone()
        if result and result['table_comment']:
            print(f"   ✓ Table comment: {result['table_comment'][:60]}...")
        else:
            print("   ⚠ No table comment found")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✓ AUDIT_LOG TABLE VERIFICATION COMPLETE")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_audit_log_table()
    sys.exit(0 if success else 1)

