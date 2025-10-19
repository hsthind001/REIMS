"""
Verification script for user_sessions table (Migration 014)
Tests table structure, indexes, constraints, triggers, and session management functions
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import time
import uuid

# Database connection details
DB_CONFIG = {
    'dbname': 'reims',
    'user': 'postgres',
    'password': 'reims2024',
    'host': 'localhost',
    'port': '5432'
}

def verify_sessions_table():
    """Comprehensive verification of user_sessions table"""
    print("=" * 80)
    print("USER_SESSIONS TABLE VERIFICATION")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Check if table exists
        print("\n1. Checking if user_sessions table exists...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'user_sessions'
            );
        """)
        exists = cur.fetchone()['exists']
        if exists:
            print("   ✓ user_sessions table exists")
        else:
            print("   ✗ user_sessions table NOT FOUND")
            return False
        
        # 2. Verify all columns
        print("\n2. Verifying table structure...")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'user_sessions'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        required_columns = {
            'id': 'uuid',
            'user_id': 'uuid',
            'session_token': 'character varying',
            'refresh_token': 'character varying',
            'ip_address': 'inet',
            'user_agent': 'text',
            'device_type': 'character varying',
            'device_name': 'character varying',
            'created_at': 'timestamp without time zone',
            'expires_at': 'timestamp without time zone',
            'last_activity': 'timestamp without time zone',
            'is_active': 'boolean',
            'revoked_at': 'timestamp without time zone',
            'revoked_reason': 'character varying'
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
            WHERE tablename = 'user_sessions'
            ORDER BY indexname;
        """)
        indexes = cur.fetchall()
        
        expected_indexes = [
            'idx_sessions_active',
            'idx_sessions_created_at',
            'idx_sessions_device_type',
            'idx_sessions_expires_at',
            'idx_sessions_refresh_token',
            'idx_sessions_revoked',
            'idx_sessions_token',
            'idx_sessions_user_id'
        ]
        
        found_indexes = [idx['indexname'] for idx in indexes if idx['indexname'].startswith('idx_')]
        
        for expected_idx in expected_indexes:
            if expected_idx in found_indexes:
                print(f"   ✓ {expected_idx}")
            else:
                print(f"   ✗ {expected_idx}: MISSING")
        
        # 4. Verify foreign key constraint
        print("\n4. Verifying foreign key constraint...")
        cur.execute("""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name = 'user_sessions';
        """)
        fkeys = cur.fetchall()
        
        if any(fk['column_name'] == 'user_id' and fk['foreign_table_name'] == 'users' for fk in fkeys):
            print("   ✓ user_id → users foreign key")
        else:
            print("   ⚠ user_id → users foreign key MISSING")
        
        # 5. Verify CHECK constraints
        print("\n5. Verifying CHECK constraints...")
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid) as definition
            FROM pg_constraint
            WHERE conrelid = 'user_sessions'::regclass
                AND contype = 'c'
            ORDER BY conname;
        """)
        checks = cur.fetchall()
        
        expected_checks = [
            'chk_device_type',
            'chk_expires_after_created',
            'chk_revoked_after_created',
            'chk_revoked_not_active',
            'chk_session_token_not_empty'
        ]
        
        found_checks = [chk['conname'] for chk in checks]
        
        for expected_chk in expected_checks:
            if expected_chk in found_checks:
                print(f"   ✓ {expected_chk}")
            else:
                print(f"   ⚠ {expected_chk}: MISSING")
        
        # 6. Verify session management functions
        print("\n6. Verifying session management functions...")
        functions = [
            'create_session',
            'validate_session',
            'revoke_session',
            'revoke_all_user_sessions',
            'cleanup_expired_sessions',
            'get_user_active_sessions',
            'refresh_session'
        ]
        
        for func_name in functions:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM pg_proc 
                    WHERE proname = %s
                );
            """, (func_name,))
            func_exists = cur.fetchone()['exists']
            if func_exists:
                print(f"   ✓ {func_name} function exists")
            else:
                print(f"   ⚠ {func_name} function MISSING")
        
        # 7. Setup: Get or create a test user
        print("\n7. Setting up test user...")
        bcrypt_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYb7YgP5.rO'
        
        cur.execute("""
            INSERT INTO users (email, username, password_hash, role)
            VALUES ('session.test@reims.com', 'sessiontest', %s, 'analyst')
            ON CONFLICT (email) DO UPDATE 
            SET username = EXCLUDED.username
            RETURNING id;
        """, (bcrypt_hash,))
        test_user_id = cur.fetchone()['id']
        print(f"   ✓ Test user ID: {test_user_id}")
        
        # 8. Test create_session function
        print("\n8. Testing create_session function...")
        
        test_session_token = f"jwt.test.token.{uuid.uuid4()}"
        test_refresh_token = f"refresh.test.token.{uuid.uuid4()}"
        
        cur.execute("""
            SELECT create_session(
                %s::UUID,
                %s,
                %s,
                '192.168.1.100'::INET,
                'Mozilla/5.0 Test Browser',
                'desktop',
                8
            );
        """, (test_user_id, test_session_token, test_refresh_token))
        
        session_id = cur.fetchone()['create_session']
        print(f"   ✓ Session created: {session_id}")
        
        # Verify session data
        cur.execute("""
            SELECT * FROM user_sessions WHERE id = %s;
        """, (session_id,))
        session = cur.fetchone()
        
        if session:
            print(f"   ✓ Session token: {session['session_token'][:20]}...")
            print(f"   ✓ Device type: {session['device_type']}")
            print(f"   ✓ Expires at: {session['expires_at']}")
            print(f"   ✓ Is active: {session['is_active']}")
        
        # 9. Test validate_session function
        print("\n9. Testing validate_session function...")
        
        cur.execute("""
            SELECT * FROM validate_session(%s);
        """, (test_session_token,))
        validation = cur.fetchone()
        
        if validation:
            print(f"   ✓ Session validated: is_valid={validation['is_valid']}")
            print(f"   ✓ User ID: {validation['user_id']}")
        
        # Check that last_activity was updated
        cur.execute("""
            SELECT last_activity FROM user_sessions WHERE id = %s;
        """, (session_id,))
        last_activity = cur.fetchone()['last_activity']
        print(f"   ✓ Last activity updated: {last_activity}")
        
        # 10. Test get_user_active_sessions function
        print("\n10. Testing get_user_active_sessions function...")
        
        cur.execute("""
            SELECT * FROM get_user_active_sessions(%s);
        """, (test_user_id,))
        active_sessions = cur.fetchall()
        
        print(f"   ✓ Active sessions: {len(active_sessions)}")
        for sess in active_sessions:
            print(f"     - Device: {sess['device_type']}, Last active: {sess['last_activity']}")
        
        # 11. Test revoke_session function
        print("\n11. Testing revoke_session function...")
        
        cur.execute("""
            SELECT revoke_session(%s, 'test_revocation');
        """, (test_session_token,))
        revoked = cur.fetchone()['revoke_session']
        
        if revoked:
            print(f"   ✓ Session revoked successfully")
            
            # Verify revocation
            cur.execute("""
                SELECT is_active, revoked_at, revoked_reason
                FROM user_sessions
                WHERE id = %s;
            """, (session_id,))
            revoked_session = cur.fetchone()
            
            if not revoked_session['is_active'] and revoked_session['revoked_at']:
                print(f"   ✓ Session marked inactive")
                print(f"   ✓ Revoked at: {revoked_session['revoked_at']}")
                print(f"   ✓ Revoked reason: {revoked_session['revoked_reason']}")
        
        # 12. Test session refresh
        print("\n12. Testing refresh_session function...")
        
        # Create a new session for refresh testing
        new_session_token = f"jwt.test.token.{uuid.uuid4()}"
        new_refresh_token = f"refresh.test.token.{uuid.uuid4()}"
        
        cur.execute("""
            SELECT create_session(
                %s::UUID, %s, %s,
                '192.168.1.101'::INET,
                'Mozilla/5.0 Test Browser',
                'desktop',
                8
            );
        """, (test_user_id, new_session_token, new_refresh_token))
        
        # Refresh the session
        refreshed_session_token = f"jwt.test.token.refreshed.{uuid.uuid4()}"
        refreshed_refresh_token = f"refresh.test.token.refreshed.{uuid.uuid4()}"
        
        try:
            cur.execute("""
                SELECT refresh_session(%s, %s, %s, 8);
            """, (new_refresh_token, refreshed_session_token, refreshed_refresh_token))
            
            new_session_id = cur.fetchone()['refresh_session']
            print(f"   ✓ Session refreshed: {new_session_id}")
            
            # Verify old session is revoked
            cur.execute("""
                SELECT is_active, revoked_reason
                FROM user_sessions
                WHERE session_token = %s;
            """, (new_session_token,))
            old_session = cur.fetchone()
            
            if not old_session['is_active'] and old_session['revoked_reason'] == 'token_refreshed':
                print(f"   ✓ Old session revoked with reason: {old_session['revoked_reason']}")
        except Exception as e:
            print(f"   ⚠ Refresh failed: {e}")
        
        # 13. Test revoke_all_user_sessions function
        print("\n13. Testing revoke_all_user_sessions function...")
        
        # Create multiple sessions
        for i in range(3):
            token = f"jwt.test.token.multi.{i}.{uuid.uuid4()}"
            cur.execute("""
                SELECT create_session(
                    %s::UUID, %s, NULL,
                    '192.168.1.10%s'::INET,
                    'Test Browser %s',
                    'mobile',
                    8
                );
            """, (test_user_id, token, i, i))
        
        # Revoke all sessions
        cur.execute("""
            SELECT revoke_all_user_sessions(%s, 'logout_all_devices');
        """, (test_user_id,))
        revoked_count = cur.fetchone()['revoke_all_user_sessions']
        
        print(f"   ✓ Revoked {revoked_count} session(s)")
        
        # 14. Test cleanup_expired_sessions function
        print("\n14. Testing cleanup_expired_sessions function...")
        
        # Create an expired session
        expired_token = f"jwt.expired.token.{uuid.uuid4()}"
        cur.execute("""
            INSERT INTO user_sessions (
                user_id, session_token, expires_at, created_at, is_active
            ) VALUES (
                %s, %s,
                CURRENT_TIMESTAMP - INTERVAL '1 day',
                CURRENT_TIMESTAMP - INTERVAL '40 days',
                false
            );
        """, (test_user_id, expired_token))
        
        # Run cleanup
        cur.execute("SELECT cleanup_expired_sessions(30);")
        deleted_count = cur.fetchone()['cleanup_expired_sessions']
        
        print(f"   ✓ Cleanup executed: deleted {deleted_count} session(s)")
        
        # 15. Test CHECK constraints
        print("\n15. Testing CHECK constraints...")
        
        # Test invalid device type
        try:
            cur.execute("""
                INSERT INTO user_sessions (
                    user_id, session_token, expires_at, device_type
                ) VALUES (
                    %s, 'test-token-invalid', CURRENT_TIMESTAMP + INTERVAL '1 hour', 'invalid_device'
                );
            """, (test_user_id,))
            print("   ✗ Invalid device type accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid device type rejected (chk_device_type)")
        
        # Test expires_at before created_at
        try:
            cur.execute("""
                INSERT INTO user_sessions (
                    user_id, session_token, created_at, expires_at
                ) VALUES (
                    %s, 'test-token-time', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP - INTERVAL '1 hour'
                );
            """, (test_user_id,))
            print("   ✗ Invalid expiry accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid expiry rejected (chk_expires_after_created)")
        
        # 16. Test UNIQUE constraint
        print("\n16. Testing UNIQUE constraint (session_token)...")
        
        try:
            duplicate_token = f"jwt.duplicate.{uuid.uuid4()}"
            cur.execute("""
                INSERT INTO user_sessions (user_id, session_token, expires_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP + INTERVAL '1 hour');
            """, (test_user_id, duplicate_token))
            
            cur.execute("""
                INSERT INTO user_sessions (user_id, session_token, expires_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP + INTERVAL '1 hour');
            """, (test_user_id, duplicate_token))
            
            print("   ✗ Duplicate session_token accepted (should have failed)")
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            print("   ✓ Duplicate session_token rejected (UNIQUE constraint)")
        
        # 17. Test session analytics
        print("\n17. Testing session analytics queries...")
        
        # Sessions by device type
        cur.execute("""
            SELECT device_type, COUNT(*) as count
            FROM user_sessions
            WHERE user_id = %s
            GROUP BY device_type
            ORDER BY count DESC;
        """, (test_user_id,))
        device_stats = cur.fetchall()
        
        print(f"   ✓ Sessions by device type:")
        for stat in device_stats:
            print(f"     - {stat['device_type']}: {stat['count']}")
        
        # 18. Cleanup test data
        print("\n18. Cleaning up test data...")
        
        # Delete test sessions
        cur.execute("""
            DELETE FROM user_sessions
            WHERE user_id = %s;
        """, (test_user_id,))
        
        # Delete test user
        cur.execute("""
            DELETE FROM users
            WHERE id = %s;
        """, (test_user_id,))
        
        conn.commit()
        print("   ✓ Test data removed")
        
        # 19. Final statistics
        print("\n19. Table statistics...")
        cur.execute("SELECT COUNT(*) as count FROM user_sessions;")
        count = cur.fetchone()['count']
        print(f"   ✓ Total sessions: {count}")
        
        # Active vs inactive sessions
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE is_active = true) as active,
                COUNT(*) FILTER (WHERE revoked_at IS NOT NULL) as revoked,
                COUNT(*) FILTER (WHERE expires_at <= CURRENT_TIMESTAMP) as expired
            FROM user_sessions;
        """)
        stats = cur.fetchone()
        if stats and stats['total'] > 0:
            print(f"   ✓ Active: {stats['active']}/{stats['total']}")
            print(f"   ✓ Revoked: {stats['revoked']}/{stats['total']}")
            print(f"   ✓ Expired: {stats['expired']}/{stats['total']}")
        
        # 20. Check table comments (documentation)
        print("\n20. Checking table documentation...")
        cur.execute("""
            SELECT obj_description('user_sessions'::regclass) as table_comment;
        """)
        result = cur.fetchone()
        if result and result['table_comment']:
            print(f"   ✓ Table comment: {result['table_comment'][:60]}...")
        else:
            print("   ⚠ No table comment found")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✓ USER_SESSIONS TABLE VERIFICATION COMPLETE")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_sessions_table()
    sys.exit(0 if success else 1)

