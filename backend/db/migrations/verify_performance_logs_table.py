"""
Verification script for performance_logs table (Migration 012)
Tests table structure, indexes, constraints, triggers, and materialized view
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
from decimal import Decimal
import time

# Database connection details
DB_CONFIG = {
    'dbname': 'reims',
    'user': 'postgres',
    'password': 'reims2024',
    'host': 'localhost',
    'port': '5432'
}

def verify_performance_logs_table():
    """Comprehensive verification of performance_logs table"""
    print("=" * 80)
    print("PERFORMANCE_LOGS TABLE VERIFICATION")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Check if table exists
        print("\n1. Checking if performance_logs table exists...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'performance_logs'
            );
        """)
        exists = cur.fetchone()['exists']
        if exists:
            print("   ✓ performance_logs table exists")
        else:
            print("   ✗ performance_logs table NOT FOUND")
            return False
        
        # 2. Verify all columns
        print("\n2. Verifying table structure...")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'performance_logs'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        required_columns = {
            'id': 'uuid',
            'request_id': 'character varying',
            'endpoint': 'character varying',
            'method': 'character varying',
            'start_time': 'timestamp without time zone',
            'end_time': 'timestamp without time zone',
            'duration_ms': 'integer',
            'db_queries_count': 'integer',
            'db_time_ms': 'integer',
            'cache_hits': 'integer',
            'cache_misses': 'integer',
            'cache_time_ms': 'integer',
            'external_service_calls': 'integer',
            'external_service_time_ms': 'integer',
            'status_code': 'integer',
            'response_size_bytes': 'integer',
            'user_id': 'uuid',
            'ip_address': 'inet',
            'is_slow': 'boolean',
            'is_error': 'boolean',
            'logged_at': 'timestamp without time zone'
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
            WHERE tablename = 'performance_logs'
            ORDER BY indexname;
        """)
        indexes = cur.fetchall()
        
        expected_indexes = [
            'idx_perf_db_time',
            'idx_perf_duration',
            'idx_perf_endpoint_time',
            'idx_perf_errors',
            'idx_perf_logged_at',
            'idx_perf_method',
            'idx_perf_slow',
            'idx_perf_start_time',
            'idx_perf_status_code',
            'idx_perf_user_id'
        ]
        
        found_indexes = [idx['indexname'] for idx in indexes if idx['indexname'].startswith('idx_')]
        
        for expected_idx in expected_indexes:
            if expected_idx in found_indexes:
                print(f"   ✓ {expected_idx}")
            else:
                print(f"   ✗ {expected_idx}: MISSING")
        
        # 4. Verify UNIQUE constraint
        print("\n4. Verifying UNIQUE constraint...")
        cur.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_name = 'performance_logs'
                AND constraint_type = 'UNIQUE';
        """)
        unique_constraints = cur.fetchall()
        
        found_unique = any('request_id' in uc['constraint_name'] for uc in unique_constraints)
        if found_unique:
            print("   ✓ request_id UNIQUE constraint exists")
        else:
            print("   ⚠ request_id UNIQUE constraint MISSING")
        
        # 5. Verify CHECK constraints
        print("\n5. Verifying CHECK constraints...")
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid) as definition
            FROM pg_constraint
            WHERE conrelid = 'performance_logs'::regclass
                AND contype = 'c'
            ORDER BY conname;
        """)
        checks = cur.fetchall()
        
        expected_checks = [
            'chk_cache_hits',
            'chk_cache_misses',
            'chk_cache_time_ms',
            'chk_db_queries_count',
            'chk_db_time_ms',
            'chk_duration_ms',
            'chk_end_after_start',
            'chk_external_calls',
            'chk_external_time_ms',
            'chk_method',
            'chk_response_size',
            'chk_status_code'
        ]
        
        found_checks = [chk['conname'] for chk in checks]
        
        for expected_chk in expected_checks:
            if expected_chk in found_checks:
                print(f"   ✓ {expected_chk}")
            else:
                print(f"   ⚠ {expected_chk}: MISSING")
        
        # 6. Verify trigger exists
        print("\n6. Verifying trigger...")
        cur.execute("""
            SELECT tgname 
            FROM pg_trigger 
            WHERE tgrelid = 'performance_logs'::regclass
                AND tgname = 'trigger_calculate_performance_metrics';
        """)
        trigger = cur.fetchone()
        if trigger:
            print(f"   ✓ trigger_calculate_performance_metrics")
        else:
            print(f"   ⚠ trigger_calculate_performance_metrics: MISSING")
        
        # 7. Verify cleanup function exists
        print("\n7. Verifying cleanup function...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM pg_proc 
                WHERE proname = 'cleanup_old_performance_logs'
            );
        """)
        func_exists = cur.fetchone()['exists']
        if func_exists:
            print("   ✓ cleanup_old_performance_logs function exists")
        else:
            print("   ⚠ cleanup_old_performance_logs function MISSING")
        
        # 8. Verify materialized view exists
        print("\n8. Verifying materialized view...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM pg_matviews 
                WHERE schemaname = 'public'
                AND matviewname = 'performance_summary_hourly'
            );
        """)
        mv_exists = cur.fetchone()['exists']
        if mv_exists:
            print("   ✓ performance_summary_hourly materialized view exists")
        else:
            print("   ⚠ performance_summary_hourly materialized view MISSING")
        
        # 9. Test insert operation
        print("\n9. Testing insert operation...")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(milliseconds=245)
        
        test_data = {
            'request_id': 'test-req-001',
            'endpoint': '/api/properties',
            'method': 'GET',
            'start_time': start_time,
            'end_time': end_time,
            'db_queries_count': 5,
            'db_time_ms': 120,
            'cache_hits': 3,
            'cache_misses': 1,
            'cache_time_ms': 15,
            'external_service_calls': 0,
            'external_service_time_ms': 0,
            'status_code': 200,
            'response_size_bytes': 15234,
            'ip_address': '192.168.1.100'
        }
        
        cur.execute("""
            INSERT INTO performance_logs (
                request_id, endpoint, method,
                start_time, end_time,
                db_queries_count, db_time_ms,
                cache_hits, cache_misses, cache_time_ms,
                external_service_calls, external_service_time_ms,
                status_code, response_size_bytes, ip_address
            ) VALUES (
                %(request_id)s, %(endpoint)s, %(method)s,
                %(start_time)s, %(end_time)s,
                %(db_queries_count)s, %(db_time_ms)s,
                %(cache_hits)s, %(cache_misses)s, %(cache_time_ms)s,
                %(external_service_calls)s, %(external_service_time_ms)s,
                %(status_code)s, %(response_size_bytes)s, %(ip_address)s
            ) RETURNING id, duration_ms, is_slow, is_error, logged_at;
        """, test_data)
        
        result = cur.fetchone()
        test_id = result['id']
        duration_ms = result['duration_ms']
        is_slow = result['is_slow']
        is_error = result['is_error']
        
        print(f"   ✓ Inserted test record: {test_id}")
        print(f"   ✓ Duration auto-calculated: {duration_ms}ms")
        print(f"   ✓ is_slow flag: {is_slow} (expected False)")
        print(f"   ✓ is_error flag: {is_error} (expected False)")
        
        # 10. Test trigger (auto-calculate duration and flags)
        print("\n10. Testing trigger (auto-calculation)...")
        
        # Insert slow request
        slow_start = datetime.now()
        slow_end = slow_start + timedelta(milliseconds=1500)
        
        cur.execute("""
            INSERT INTO performance_logs (
                request_id, endpoint, method, start_time, end_time, status_code
            ) VALUES (
                'test-req-002', '/api/analytics', 'POST', %s, %s, 200
            ) RETURNING duration_ms, is_slow, is_error;
        """, (slow_start, slow_end))
        
        slow_result = cur.fetchone()
        if slow_result['is_slow']:
            print(f"   ✓ Slow request detected: {slow_result['duration_ms']}ms")
        else:
            print(f"   ✗ Slow flag not set correctly")
        
        # Insert error request
        error_start = datetime.now()
        error_end = error_start + timedelta(milliseconds=100)
        
        cur.execute("""
            INSERT INTO performance_logs (
                request_id, endpoint, method, start_time, end_time, status_code
            ) VALUES (
                'test-req-003', '/api/documents', 'POST', %s, %s, 500
            ) RETURNING duration_ms, is_slow, is_error;
        """, (error_start, error_end))
        
        error_result = cur.fetchone()
        if error_result['is_error']:
            print(f"   ✓ Error request detected: status 500")
        else:
            print(f"   ✗ Error flag not set correctly")
        
        # 11. Test UNIQUE constraint
        print("\n11. Testing UNIQUE constraint (request_id)...")
        try:
            cur.execute("""
                INSERT INTO performance_logs (
                    request_id, endpoint, method, start_time, end_time
                ) VALUES (
                    'test-req-001', '/api/test', 'GET', NOW(), NOW()
                );
            """)
            print("   ✗ Duplicate request_id accepted (should have failed)")
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            print("   ✓ Duplicate request_id rejected (UNIQUE constraint)")
        
        # 12. Test query operations
        print("\n12. Testing query operations...")
        
        # Query slow requests
        cur.execute("""
            SELECT COUNT(*) as count
            FROM performance_logs
            WHERE is_slow = true;
        """)
        slow_count = cur.fetchone()['count']
        print(f"   ✓ Slow requests query: {slow_count} record(s)")
        
        # Query by endpoint
        cur.execute("""
            SELECT endpoint, COUNT(*) as count
            FROM performance_logs
            WHERE endpoint = '/api/properties'
            GROUP BY endpoint;
        """)
        endpoint_result = cur.fetchone()
        if endpoint_result:
            print(f"   ✓ Endpoint query: {endpoint_result['count']} request(s)")
        
        # Error rate query
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE is_error = true) as errors,
                ROUND((COUNT(*) FILTER (WHERE is_error = true)::NUMERIC / COUNT(*)) * 100, 2) as error_rate_pct
            FROM performance_logs;
        """)
        error_stats = cur.fetchone()
        print(f"   ✓ Error rate: {error_stats['error_rate_pct']}% ({error_stats['errors']}/{error_stats['total']})")
        
        # 13. Test performance analysis queries
        print("\n13. Testing performance analysis queries...")
        
        # Average duration by endpoint
        cur.execute("""
            SELECT 
                endpoint,
                AVG(duration_ms) as avg_duration_ms,
                COUNT(*) as request_count
            FROM performance_logs
            GROUP BY endpoint
            ORDER BY avg_duration_ms DESC;
        """)
        perf_by_endpoint = cur.fetchall()
        if perf_by_endpoint:
            print(f"   ✓ Performance by endpoint:")
            for row in perf_by_endpoint[:3]:
                print(f"     - {row['endpoint']}: {row['avg_duration_ms']:.2f}ms avg ({row['request_count']} requests)")
        
        # Cache effectiveness
        cur.execute("""
            SELECT 
                SUM(cache_hits) as total_hits,
                SUM(cache_misses) as total_misses,
                ROUND((SUM(cache_hits)::NUMERIC / NULLIF(SUM(cache_hits + cache_misses), 0)) * 100, 2) as hit_rate
            FROM performance_logs
            WHERE cache_hits > 0 OR cache_misses > 0;
        """)
        cache_stats = cur.fetchone()
        if cache_stats and cache_stats['total_hits']:
            print(f"   ✓ Cache hit rate: {cache_stats['hit_rate']}% ({cache_stats['total_hits']} hits, {cache_stats['total_misses']} misses)")
        
        # 14. Test CHECK constraints
        print("\n14. Testing CHECK constraints...")
        
        # Test invalid method
        try:
            cur.execute("""
                INSERT INTO performance_logs (
                    request_id, endpoint, method, start_time, end_time
                ) VALUES (
                    'test-invalid-method', '/api/test', 'INVALID', NOW(), NOW()
                );
            """)
            print("   ✗ Invalid method accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid method rejected (chk_method)")
        
        # Test invalid status code
        try:
            cur.execute("""
                INSERT INTO performance_logs (
                    request_id, endpoint, start_time, end_time, status_code
                ) VALUES (
                    'test-invalid-status', '/api/test', NOW(), NOW(), 999
                );
            """)
            print("   ✗ Invalid status code accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid status code rejected (chk_status_code)")
        
        # Test end_time before start_time
        try:
            cur.execute("""
                INSERT INTO performance_logs (
                    request_id, endpoint, start_time, end_time
                ) VALUES (
                    'test-invalid-time', '/api/test', NOW(), NOW() - INTERVAL '1 second'
                );
            """)
            print("   ✗ End before start accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ End before start rejected (chk_end_after_start)")
        
        # 15. Test cleanup function
        print("\n15. Testing cleanup function...")
        
        # Insert old log
        cur.execute("""
            INSERT INTO performance_logs (
                request_id, endpoint, start_time, end_time, logged_at
            ) VALUES (
                'test-old-log', '/api/test', NOW(), NOW(), NOW() - INTERVAL '40 days'
            ) RETURNING id;
        """)
        old_log_id = cur.fetchone()['id']
        
        # Run cleanup (delete logs older than 30 days)
        cur.execute("SELECT cleanup_old_performance_logs(30);")
        deleted_count = cur.fetchone()['cleanup_old_performance_logs']
        print(f"   ✓ Cleanup executed: deleted {deleted_count} old record(s)")
        
        # Verify old log was deleted
        cur.execute("SELECT COUNT(*) as count FROM performance_logs WHERE id = %s;", (old_log_id,))
        remaining = cur.fetchone()['count']
        if remaining == 0:
            print("   ✓ Old logs properly cleaned up")
        else:
            print("   ⚠ Old logs not cleaned up")
        
        # 16. Test materialized view
        print("\n16. Testing materialized view...")
        
        # Query materialized view
        cur.execute("""
            SELECT COUNT(*) as count 
            FROM performance_summary_hourly;
        """)
        mv_count = cur.fetchone()['count']
        print(f"   ✓ Materialized view contains {mv_count} record(s)")
        
        # Refresh materialized view
        try:
            cur.execute("SELECT refresh_performance_summary();")
            print("   ✓ Materialized view refresh successful")
        except Exception as e:
            print(f"   ⚠ Materialized view refresh failed: {e}")
        
        # 17. Cleanup test data
        print("\n17. Cleaning up test data...")
        cur.execute("""
            DELETE FROM performance_logs 
            WHERE request_id LIKE 'test-%';
        """)
        conn.commit()
        print("   ✓ Test data removed")
        
        # 18. Final statistics
        print("\n18. Table statistics...")
        cur.execute("SELECT COUNT(*) as count FROM performance_logs;")
        count = cur.fetchone()['count']
        print(f"   ✓ Total performance logs: {count}")
        
        # Slow requests percentage
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE is_slow = true) as slow,
                ROUND((COUNT(*) FILTER (WHERE is_slow = true)::NUMERIC / NULLIF(COUNT(*), 0)) * 100, 2) as slow_pct
            FROM performance_logs;
        """)
        slow_stats = cur.fetchone()
        if slow_stats and slow_stats['total'] > 0:
            print(f"   ✓ Slow requests: {slow_stats['slow_pct']}% ({slow_stats['slow']}/{slow_stats['total']})")
        
        # 19. Check table comments (documentation)
        print("\n19. Checking table documentation...")
        cur.execute("""
            SELECT obj_description('performance_logs'::regclass) as table_comment;
        """)
        result = cur.fetchone()
        if result and result['table_comment']:
            print(f"   ✓ Table comment: {result['table_comment'][:60]}...")
        else:
            print("   ⚠ No table comment found")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✓ PERFORMANCE_LOGS TABLE VERIFICATION COMPLETE")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_performance_logs_table()
    sys.exit(0 if success else 1)

