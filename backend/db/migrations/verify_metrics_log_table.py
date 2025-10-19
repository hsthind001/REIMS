"""
Verification script for metrics_log table (Migration 011)
Tests table structure, indexes, constraints, JSONB operations, and time-series queries
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
import json

# Database connection details
DB_CONFIG = {
    'dbname': 'reims',
    'user': 'postgres',
    'password': 'reims2024',
    'host': 'localhost',
    'port': '5432'
}

def verify_metrics_log_table():
    """Comprehensive verification of metrics_log table"""
    print("=" * 80)
    print("METRICS_LOG TABLE VERIFICATION")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Check if table exists
        print("\n1. Checking if metrics_log table exists...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'metrics_log'
            );
        """)
        exists = cur.fetchone()['exists']
        if exists:
            print("   ✓ metrics_log table exists")
        else:
            print("   ✗ metrics_log table NOT FOUND")
            return False
        
        # 2. Verify all columns
        print("\n2. Verifying table structure...")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'metrics_log'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        required_columns = {
            'id': 'uuid',
            'metric_name': 'character varying',
            'metric_type': 'character varying',
            'labels': 'jsonb',
            'metric_value': 'numeric',
            'recorded_at': 'timestamp without time zone',
            'application': 'character varying',
            'environment': 'character varying'
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
            WHERE tablename = 'metrics_log'
            ORDER BY indexname;
        """)
        indexes = cur.fetchall()
        
        expected_indexes = [
            'idx_metrics_application',
            'idx_metrics_environment',
            'idx_metrics_labels_gin',
            'idx_metrics_name_labels',
            'idx_metrics_name_time',
            'idx_metrics_recorded_at',
            'idx_metrics_type'
        ]
        
        found_indexes = [idx['indexname'] for idx in indexes if idx['indexname'].startswith('idx_')]
        
        for expected_idx in expected_indexes:
            if expected_idx in found_indexes:
                print(f"   ✓ {expected_idx}")
            else:
                print(f"   ✗ {expected_idx}: MISSING")
        
        # 4. Verify CHECK constraints
        print("\n4. Verifying CHECK constraints...")
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid) as definition
            FROM pg_constraint
            WHERE conrelid = 'metrics_log'::regclass
                AND contype = 'c'
            ORDER BY conname;
        """)
        checks = cur.fetchall()
        
        expected_checks = [
            'chk_application',
            'chk_environment',
            'chk_metric_type',
            'chk_recorded_at'
        ]
        
        found_checks = [chk['conname'] for chk in checks]
        
        for expected_chk in expected_checks:
            if expected_chk in found_checks:
                print(f"   ✓ {expected_chk}")
            else:
                print(f"   ⚠ {expected_chk}: MISSING")
        
        # 5. Verify cleanup function exists
        print("\n5. Verifying cleanup function...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM pg_proc 
                WHERE proname = 'cleanup_old_metrics'
            );
        """)
        func_exists = cur.fetchone()['exists']
        if func_exists:
            print("   ✓ cleanup_old_metrics function exists")
        else:
            print("   ⚠ cleanup_old_metrics function MISSING")
        
        # 6. Test insert operations
        print("\n6. Testing insert operations...")
        
        # Insert API request counter
        cur.execute("""
            INSERT INTO metrics_log (
                metric_name, metric_type, labels, metric_value,
                application, environment
            ) VALUES (
                'api_requests_total', 'counter',
                '{"method": "GET", "endpoint": "/api/properties", "status": "200"}'::jsonb,
                12543,
                'backend', 'production'
            ) RETURNING id, recorded_at;
        """)
        result1 = cur.fetchone()
        test_id1 = result1['id']
        print(f"   ✓ Inserted counter metric: {test_id1}")
        
        # Insert API latency gauge
        cur.execute("""
            INSERT INTO metrics_log (
                metric_name, metric_type, labels, metric_value,
                application, environment
            ) VALUES (
                'api_latency_seconds', 'gauge',
                '{"method": "POST", "endpoint": "/api/documents/upload"}'::jsonb,
                0.245,
                'backend', 'production'
            ) RETURNING id;
        """)
        test_id2 = cur.fetchone()['id']
        print(f"   ✓ Inserted gauge metric: {test_id2}")
        
        # Insert database connections metric
        cur.execute("""
            INSERT INTO metrics_log (
                metric_name, metric_type, labels, metric_value,
                application, environment
            ) VALUES (
                'db_connections_active', 'gauge',
                '{"pool": "main", "database": "reims"}'::jsonb,
                8,
                'backend', 'production'
            ) RETURNING id;
        """)
        test_id3 = cur.fetchone()['id']
        print(f"   ✓ Inserted db connections metric: {test_id3}")
        
        # 7. Test JSONB queries
        print("\n7. Testing JSONB label queries...")
        
        # Query by label value
        cur.execute("""
            SELECT id, metric_name, labels->>'endpoint' as endpoint, metric_value
            FROM metrics_log
            WHERE labels->>'endpoint' = '/api/properties'
                AND id = %s;
        """, (test_id1,))
        result = cur.fetchone()
        if result and result['endpoint'] == '/api/properties':
            print(f"   ✓ JSONB arrow operator query: {result['endpoint']}")
        
        # Query using containment operator
        cur.execute("""
            SELECT id, metric_name, labels
            FROM metrics_log
            WHERE labels @> '{"status": "200"}'::jsonb;
        """)
        results = cur.fetchall()
        print(f"   ✓ JSONB containment query returned {len(results)} record(s)")
        
        # Query multiple label conditions
        cur.execute("""
            SELECT id, metric_name, labels->>'method' as method
            FROM metrics_log
            WHERE labels->>'method' = 'POST'
                AND labels->>'endpoint' = '/api/documents/upload';
        """)
        result = cur.fetchone()
        if result:
            print(f"   ✓ Multiple label query: method={result['method']}")
        
        # 8. Test time-series queries
        print("\n8. Testing time-series queries...")
        
        # Query by metric name and time
        cur.execute("""
            SELECT metric_name, COUNT(*) as count
            FROM metrics_log
            WHERE metric_name = 'api_requests_total'
                AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
            GROUP BY metric_name;
        """)
        result = cur.fetchone()
        if result:
            print(f"   ✓ Time-range query: {result['count']} record(s)")
        
        # Query all metrics in last hour
        cur.execute("""
            SELECT COUNT(*) as count
            FROM metrics_log
            WHERE recorded_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour';
        """)
        count = cur.fetchone()['count']
        print(f"   ✓ All metrics (last hour): {count} record(s)")
        
        # 9. Test aggregation queries
        print("\n9. Testing aggregation queries...")
        
        # Batch insert for aggregation testing
        cur.execute("""
            INSERT INTO metrics_log (metric_name, metric_type, labels, metric_value, application, environment)
            VALUES 
                ('api_latency_seconds', 'gauge', '{"endpoint": "/api/test"}'::jsonb, 0.100, 'backend', 'production'),
                ('api_latency_seconds', 'gauge', '{"endpoint": "/api/test"}'::jsonb, 0.150, 'backend', 'production'),
                ('api_latency_seconds', 'gauge', '{"endpoint": "/api/test"}'::jsonb, 0.200, 'backend', 'production');
        """)
        
        # Calculate average
        cur.execute("""
            SELECT 
                AVG(metric_value) as avg_latency,
                MIN(metric_value) as min_latency,
                MAX(metric_value) as max_latency,
                COUNT(*) as sample_count
            FROM metrics_log
            WHERE metric_name = 'api_latency_seconds'
                AND labels->>'endpoint' = '/api/test';
        """)
        agg = cur.fetchone()
        if agg:
            print(f"   ✓ Aggregation query successful")
            print(f"     - Avg: {agg['avg_latency']:.3f}s")
            print(f"     - Min: {agg['min_latency']:.3f}s")
            print(f"     - Max: {agg['max_latency']:.3f}s")
            print(f"     - Samples: {agg['sample_count']}")
        
        # 10. Test query by application
        print("\n10. Testing application-specific queries...")
        cur.execute("""
            SELECT application, COUNT(*) as count
            FROM metrics_log
            WHERE application = 'backend'
            GROUP BY application;
        """)
        result = cur.fetchone()
        if result:
            print(f"   ✓ Application query: {result['application']} has {result['count']} metrics")
        
        # 11. Test query by environment
        print("\n11. Testing environment-specific queries...")
        cur.execute("""
            SELECT environment, COUNT(*) as count
            FROM metrics_log
            WHERE environment = 'production'
            GROUP BY environment;
        """)
        result = cur.fetchone()
        if result:
            print(f"   ✓ Environment query: {result['environment']} has {result['count']} metrics")
        
        # 12. Test query by metric type
        print("\n12. Testing metric type queries...")
        cur.execute("""
            SELECT metric_type, COUNT(*) as count
            FROM metrics_log
            GROUP BY metric_type
            ORDER BY count DESC;
        """)
        results = cur.fetchall()
        print(f"   ✓ Metric type summary:")
        for row in results:
            print(f"     - {row['metric_type']}: {row['count']} metrics")
        
        # 13. Test CHECK constraints
        print("\n13. Testing CHECK constraints...")
        
        # Test invalid metric type
        try:
            cur.execute("""
                INSERT INTO metrics_log (
                    metric_name, metric_type, metric_value
                ) VALUES (
                    'test_metric', 'invalid_type', 100
                );
            """)
            print("   ✗ Invalid metric type accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid metric type rejected (chk_metric_type)")
        
        # Test invalid application
        try:
            cur.execute("""
                INSERT INTO metrics_log (
                    metric_name, application, metric_value
                ) VALUES (
                    'test_metric', 'invalid_app', 100
                );
            """)
            print("   ✗ Invalid application accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid application rejected (chk_application)")
        
        # Test invalid environment
        try:
            cur.execute("""
                INSERT INTO metrics_log (
                    metric_name, environment, metric_value
                ) VALUES (
                    'test_metric', 'invalid_env', 100
                );
            """)
            print("   ✗ Invalid environment accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid environment rejected (chk_environment)")
        
        # 14. Test cleanup function
        print("\n14. Testing cleanup function...")
        
        # Insert old metric (simulate)
        cur.execute("""
            INSERT INTO metrics_log (
                metric_name, metric_value, recorded_at
            ) VALUES (
                'old_metric', 100, CURRENT_TIMESTAMP - INTERVAL '100 days'
            ) RETURNING id;
        """)
        old_metric_id = cur.fetchone()['id']
        
        # Run cleanup (delete metrics older than 90 days)
        cur.execute("SELECT cleanup_old_metrics(90);")
        deleted_count = cur.fetchone()['cleanup_old_metrics']
        print(f"   ✓ Cleanup function executed: deleted {deleted_count} old record(s)")
        
        # Verify old metric was deleted
        cur.execute("SELECT COUNT(*) as count FROM metrics_log WHERE id = %s;", (old_metric_id,))
        remaining = cur.fetchone()['count']
        if remaining == 0:
            print("   ✓ Old metrics properly cleaned up")
        else:
            print("   ⚠ Old metrics not cleaned up")
        
        # 15. Test GIN index (JSONB)
        print("\n15. Testing GIN index performance...")
        cur.execute("""
            EXPLAIN (ANALYZE OFF, COSTS OFF) 
            SELECT * FROM metrics_log 
            WHERE labels @> '{"status": "200"}'::jsonb;
        """)
        plan = cur.fetchall()
        uses_gin = any('Bitmap Index Scan' in str(row) or 'Index Scan' in str(row) for row in plan)
        if uses_gin:
            print("   ✓ GIN index being used for JSONB queries")
        else:
            print("   ⚠ GIN index may not be used (table might be too small)")
        
        # 16. Cleanup test data
        print("\n16. Cleaning up test data...")
        cur.execute("""
            DELETE FROM metrics_log 
            WHERE id IN (%s, %s, %s)
                OR labels->>'endpoint' = '/api/test';
        """, (test_id1, test_id2, test_id3))
        conn.commit()
        print("   ✓ Test data removed")
        
        # 17. Final statistics
        print("\n17. Table statistics...")
        cur.execute("SELECT COUNT(*) as count FROM metrics_log;")
        count = cur.fetchone()['count']
        print(f"   ✓ Total metrics logged: {count}")
        
        # Metrics by type
        cur.execute("""
            SELECT metric_type, COUNT(*) as count 
            FROM metrics_log 
            GROUP BY metric_type 
            ORDER BY count DESC;
        """)
        by_type = cur.fetchall()
        if by_type:
            print(f"   ✓ Breakdown by type:")
            for row in by_type:
                print(f"     - {row['metric_type']}: {row['count']}")
        
        # 18. Check table comments (documentation)
        print("\n18. Checking table documentation...")
        cur.execute("""
            SELECT obj_description('metrics_log'::regclass) as table_comment;
        """)
        result = cur.fetchone()
        if result and result['table_comment']:
            print(f"   ✓ Table comment: {result['table_comment'][:60]}...")
        else:
            print("   ⚠ No table comment found")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✓ METRICS_LOG TABLE VERIFICATION COMPLETE")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_metrics_log_table()
    sys.exit(0 if success else 1)

