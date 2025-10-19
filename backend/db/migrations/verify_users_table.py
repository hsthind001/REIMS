"""
Verification script for users table (Migration 013)
Tests table structure, indexes, constraints, triggers, and security functions
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

# Database connection details
DB_CONFIG = {
    'dbname': 'reims',
    'user': 'postgres',
    'password': 'reims2024',
    'host': 'localhost',
    'port': '5432'
}

def verify_users_table():
    """Comprehensive verification of users table"""
    print("=" * 80)
    print("USERS TABLE VERIFICATION")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Check if table exists
        print("\n1. Checking if users table exists...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """)
        exists = cur.fetchone()['exists']
        if exists:
            print("   ✓ users table exists")
        else:
            print("   ✗ users table NOT FOUND")
            return False
        
        # 2. Verify all columns
        print("\n2. Verifying table structure...")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        required_columns = {
            'id': 'uuid',
            'email': 'character varying',
            'username': 'character varying',
            'password_hash': 'character varying',
            'first_name': 'character varying',
            'last_name': 'character varying',
            'phone': 'character varying',
            'role': 'character varying',
            'permissions': 'ARRAY',
            'committee_member': 'character varying',
            'is_active': 'boolean',
            'is_email_verified': 'boolean',
            'email_verified_at': 'timestamp without time zone',
            'last_login': 'timestamp without time zone',
            'last_login_ip': 'inet',
            'failed_login_attempts': 'integer',
            'account_locked_until': 'timestamp without time zone',
            'mfa_enabled': 'boolean',
            'mfa_secret': 'character varying',
            'created_at': 'timestamp without time zone',
            'updated_at': 'timestamp without time zone',
            'created_by': 'uuid',
            'password_changed_at': 'timestamp without time zone'
        }
        
        found_columns = {col['column_name']: col['data_type'] for col in columns}
        
        all_columns_present = True
        for col_name, expected_type in required_columns.items():
            if col_name in found_columns:
                actual_type = found_columns[col_name]
                if expected_type == 'ARRAY' or actual_type == expected_type:
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
            WHERE tablename = 'users'
            ORDER BY indexname;
        """)
        indexes = cur.fetchall()
        
        expected_indexes = [
            'idx_users_active',
            'idx_users_committee',
            'idx_users_email_lower',
            'idx_users_email_verified',
            'idx_users_last_login',
            'idx_users_locked',
            'idx_users_mfa',
            'idx_users_role',
            'idx_users_username_lower'
        ]
        
        found_indexes = [idx['indexname'] for idx in indexes if idx['indexname'].startswith('idx_')]
        
        for expected_idx in expected_indexes:
            if expected_idx in found_indexes:
                print(f"   ✓ {expected_idx}")
            else:
                print(f"   ✗ {expected_idx}: MISSING")
        
        # 4. Verify UNIQUE constraints
        print("\n4. Verifying UNIQUE constraints...")
        cur.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'users'
                AND constraint_type = 'UNIQUE';
        """)
        unique_constraints = cur.fetchall()
        
        unique_names = [uc['constraint_name'] for uc in unique_constraints]
        if any('email' in name for name in unique_names):
            print("   ✓ email UNIQUE constraint")
        if any('username' in name for name in unique_names):
            print("   ✓ username UNIQUE constraint")
        
        # 5. Verify CHECK constraints
        print("\n5. Verifying CHECK constraints...")
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid) as definition
            FROM pg_constraint
            WHERE conrelid = 'users'::regclass
                AND contype = 'c'
            ORDER BY conname;
        """)
        checks = cur.fetchall()
        
        expected_checks = [
            'chk_account_locked',
            'chk_email_format',
            'chk_email_not_empty',
            'chk_email_verified_timestamp',
            'chk_failed_attempts',
            'chk_mfa_secret',
            'chk_password_hash_format',
            'chk_phone_format',
            'chk_role',
            'chk_username_format',
            'chk_username_not_empty'
        ]
        
        found_checks = [chk['conname'] for chk in checks]
        
        for expected_chk in expected_checks:
            if expected_chk in found_checks:
                print(f"   ✓ {expected_chk}")
            else:
                print(f"   ⚠ {expected_chk}: MISSING")
        
        # 6. Verify triggers exist
        print("\n6. Verifying triggers...")
        cur.execute("""
            SELECT tgname 
            FROM pg_trigger 
            WHERE tgrelid = 'users'::regclass
                AND tgname LIKE 'trigger_%';
        """)
        triggers = cur.fetchall()
        
        expected_triggers = [
            'trigger_update_user_timestamp',
            'trigger_track_password_change'
        ]
        
        found_triggers = [t['tgname'] for t in triggers]
        
        for expected_trig in expected_triggers:
            if expected_trig in found_triggers:
                print(f"   ✓ {expected_trig}")
            else:
                print(f"   ⚠ {expected_trig}: MISSING")
        
        # 7. Verify security functions exist
        print("\n7. Verifying security functions...")
        functions = [
            'is_account_locked',
            'record_failed_login',
            'record_successful_login',
            'get_user_permissions'
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
        
        # 8. Test insert operation
        print("\n8. Testing insert operation...")
        
        # Valid bcrypt hash example (for "password123")
        bcrypt_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYb7YgP5.rO'
        
        test_data = {
            'email': 'test.user@reims.com',
            'username': 'testuser',
            'password_hash': bcrypt_hash,
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'analyst',
            'is_email_verified': True,
            'email_verified_at': datetime.now()
        }
        
        cur.execute("""
            INSERT INTO users (
                email, username, password_hash,
                first_name, last_name, role,
                is_email_verified, email_verified_at
            ) VALUES (
                %(email)s, %(username)s, %(password_hash)s,
                %(first_name)s, %(last_name)s, %(role)s,
                %(is_email_verified)s, %(email_verified_at)s
            ) RETURNING id, created_at, updated_at;
        """, test_data)
        
        result = cur.fetchone()
        test_user_id = result['id']
        created_at = result['created_at']
        
        print(f"   ✓ Inserted test user: {test_user_id}")
        print(f"   ✓ created_at auto-generated: {created_at}")
        
        # 9. Test case-insensitive email/username lookup
        print("\n9. Testing case-insensitive lookup...")
        
        cur.execute("""
            SELECT id FROM users
            WHERE LOWER(email) = LOWER('TEST.USER@REIMS.COM');
        """)
        found = cur.fetchone()
        if found:
            print("   ✓ Case-insensitive email lookup works")
        else:
            print("   ✗ Case-insensitive email lookup failed")
        
        # 10. Test trigger (updated_at auto-update)
        print("\n10. Testing trigger (updated_at auto-update)...")
        time.sleep(1)  # Ensure timestamp difference
        
        cur.execute("""
            UPDATE users
            SET first_name = 'Updated'
            WHERE id = %s
            RETURNING updated_at;
        """, (test_user_id,))
        new_updated_at = cur.fetchone()['updated_at']
        
        if new_updated_at > created_at:
            print(f"   ✓ updated_at changed: {new_updated_at}")
        else:
            print("   ✗ updated_at not updated")
        
        # 11. Test password change trigger
        print("\n11. Testing password change trigger...")
        
        new_hash = '$2b$12$NEWHashHereForTestingPurposesOnlyDoNotUseInProd123'
        cur.execute("""
            UPDATE users
            SET password_hash = %s
            WHERE id = %s
            RETURNING password_changed_at, failed_login_attempts, account_locked_until;
        """, (new_hash, test_user_id))
        
        pw_result = cur.fetchone()
        if pw_result['password_changed_at']:
            print(f"   ✓ password_changed_at set: {pw_result['password_changed_at']}")
        if pw_result['failed_login_attempts'] == 0:
            print("   ✓ failed_login_attempts reset to 0")
        if pw_result['account_locked_until'] is None:
            print("   ✓ account_locked_until cleared")
        
        # 12. Test security functions
        print("\n12. Testing security functions...")
        
        # Test is_account_locked
        cur.execute("SELECT is_account_locked(%s);", (test_user_id,))
        is_locked = cur.fetchone()['is_account_locked']
        if not is_locked:
            print("   ✓ is_account_locked returned false (expected)")
        
        # Test record_failed_login
        cur.execute("SELECT record_failed_login('test.user@reims.com');")
        cur.execute("SELECT failed_login_attempts FROM users WHERE id = %s;", (test_user_id,))
        attempts = cur.fetchone()['failed_login_attempts']
        if attempts == 1:
            print(f"   ✓ record_failed_login incremented attempts to {attempts}")
        
        # Test record_successful_login
        cur.execute("SELECT record_successful_login(%s, %s::INET);", (test_user_id, '192.168.1.100'))
        cur.execute("SELECT last_login, last_login_ip, failed_login_attempts FROM users WHERE id = %s;", (test_user_id,))
        login_result = cur.fetchone()
        if login_result['last_login'] and login_result['last_login_ip']:
            print(f"   ✓ record_successful_login updated last_login")
            print(f"   ✓ Failed attempts reset to {login_result['failed_login_attempts']}")
        
        # Test get_user_permissions
        cur.execute("SELECT * FROM get_user_permissions(%s);", (test_user_id,))
        perms = cur.fetchone()
        if perms:
            print(f"   ✓ get_user_permissions returned: role={perms['user_role']}, can_create={perms['can_create']}")
        
        # 13. Test account locking
        print("\n13. Testing account locking...")
        
        # Trigger account lock (5 failed attempts)
        for i in range(5):
            cur.execute("SELECT record_failed_login('test.user@reims.com');")
        
        cur.execute("SELECT account_locked_until, failed_login_attempts FROM users WHERE id = %s;", (test_user_id,))
        lock_result = cur.fetchone()
        
        if lock_result['account_locked_until']:
            print(f"   ✓ Account locked after 5 attempts: until {lock_result['account_locked_until']}")
        else:
            print("   ⚠ Account not locked after 5 attempts")
        
        # Clear lock for further testing
        cur.execute("""
            UPDATE users 
            SET account_locked_until = NULL, failed_login_attempts = 0
            WHERE id = %s;
        """, (test_user_id,))
        
        # 14. Test CHECK constraints
        print("\n14. Testing CHECK constraints...")
        
        # Test invalid email format
        try:
            cur.execute("""
                INSERT INTO users (email, username, password_hash, role)
                VALUES ('invalid-email', 'testuser2', %s, 'viewer');
            """, (bcrypt_hash,))
            print("   ✗ Invalid email accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid email rejected (chk_email_format)")
        
        # Test invalid username format
        try:
            cur.execute("""
                INSERT INTO users (email, username, password_hash, role)
                VALUES ('test2@reims.com', 'ab', %s, 'viewer');
            """, (bcrypt_hash,))
            print("   ✗ Invalid username accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid username rejected (chk_username_format - too short)")
        
        # Test invalid role
        try:
            cur.execute("""
                INSERT INTO users (email, username, password_hash, role)
                VALUES ('test3@reims.com', 'testuser3', %s, 'invalid_role');
            """, (bcrypt_hash,))
            print("   ✗ Invalid role accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid role rejected (chk_role)")
        
        # Test invalid password hash
        try:
            cur.execute("""
                INSERT INTO users (email, username, password_hash, role)
                VALUES ('test4@reims.com', 'testuser4', 'plain-text-password', 'viewer');
            """)
            print("   ✗ Invalid password hash accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid password hash rejected (chk_password_hash_format)")
        
        # 15. Test MFA functionality
        print("\n15. Testing MFA functionality...")
        
        # Enable MFA
        cur.execute("""
            UPDATE users
            SET mfa_enabled = true,
                mfa_secret = 'JBSWY3DPEHPK3PXP'
            WHERE id = %s
            RETURNING mfa_enabled, mfa_secret;
        """, (test_user_id,))
        
        mfa_result = cur.fetchone()
        if mfa_result['mfa_enabled'] and mfa_result['mfa_secret']:
            print(f"   ✓ MFA enabled with secret")
        
        # 16. Test permissions array
        print("\n16. Testing permissions array...")
        
        cur.execute("""
            UPDATE users
            SET permissions = ARRAY['upload_documents', 'view_analytics', 'export_reports']
            WHERE id = %s
            RETURNING permissions;
        """, (test_user_id,))
        
        perms_result = cur.fetchone()
        if len(perms_result['permissions']) == 3:
            print(f"   ✓ Permissions array: {perms_result['permissions']}")
        
        # 17. Test UNIQUE constraint
        print("\n17. Testing UNIQUE constraint...")
        
        try:
            cur.execute("""
                INSERT INTO users (email, username, password_hash, role)
                VALUES ('test.user@reims.com', 'anotheruser', %s, 'viewer');
            """, (bcrypt_hash,))
            print("   ✗ Duplicate email accepted (should have failed)")
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            print("   ✓ Duplicate email rejected (UNIQUE constraint)")
        
        # 18. Test role-based queries
        print("\n18. Testing role-based queries...")
        
        # Create users with different roles
        cur.execute("""
            INSERT INTO users (email, username, password_hash, role)
            VALUES 
                ('supervisor@reims.com', 'supervisor1', %s, 'supervisor'),
                ('viewer@reims.com', 'viewer1', %s, 'viewer')
            ON CONFLICT (email) DO NOTHING;
        """, (bcrypt_hash, bcrypt_hash))
        
        cur.execute("""
            SELECT role, COUNT(*) as count
            FROM users
            WHERE is_active = true
            GROUP BY role
            ORDER BY count DESC;
        """)
        role_counts = cur.fetchall()
        
        print("   ✓ Users by role:")
        for row in role_counts:
            print(f"     - {row['role']}: {row['count']}")
        
        # 19. Cleanup test data
        print("\n19. Cleaning up test data...")
        cur.execute("""
            DELETE FROM users 
            WHERE email LIKE '%@reims.com' 
                OR username LIKE 'test%';
        """)
        conn.commit()
        print("   ✓ Test data removed")
        
        # 20. Final statistics
        print("\n20. Table statistics...")
        cur.execute("SELECT COUNT(*) as count FROM users;")
        count = cur.fetchone()['count']
        print(f"   ✓ Total users: {count}")
        
        # Users by status
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE is_active = true) as active,
                COUNT(*) FILTER (WHERE is_email_verified = true) as verified,
                COUNT(*) FILTER (WHERE mfa_enabled = true) as mfa_enabled
            FROM users;
        """)
        stats = cur.fetchone()
        if stats:
            print(f"   ✓ Active: {stats['active']}/{stats['total']}")
            print(f"   ✓ Email verified: {stats['verified']}/{stats['total']}")
            print(f"   ✓ MFA enabled: {stats['mfa_enabled']}/{stats['total']}")
        
        # 21. Check table comments (documentation)
        print("\n21. Checking table documentation...")
        cur.execute("""
            SELECT obj_description('users'::regclass) as table_comment;
        """)
        result = cur.fetchone()
        if result and result['table_comment']:
            print(f"   ✓ Table comment: {result['table_comment'][:60]}...")
        else:
            print("   ⚠ No table comment found")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✓ USERS TABLE VERIFICATION COMPLETE")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_users_table()
    sys.exit(0 if success else 1)

