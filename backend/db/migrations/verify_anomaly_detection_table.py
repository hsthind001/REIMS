"""
Verification script for anomaly_detection_results table (Migration 008)
Tests table structure, indexes, constraints, array operations, and queries
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date, timedelta
from decimal import Decimal

# Database connection details
DB_CONFIG = {
    'dbname': 'reims',
    'user': 'postgres',
    'password': 'reims2024',
    'host': 'localhost',
    'port': '5432'
}

def verify_anomaly_detection_table():
    """Comprehensive verification of anomaly_detection_results table"""
    print("=" * 80)
    print("ANOMALY_DETECTION_RESULTS TABLE VERIFICATION")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Check if table exists
        print("\n1. Checking if anomaly_detection_results table exists...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'anomaly_detection_results'
            );
        """)
        exists = cur.fetchone()['exists']
        if exists:
            print("   ✓ anomaly_detection_results table exists")
        else:
            print("   ✗ anomaly_detection_results table NOT FOUND")
            return False
        
        # 2. Verify all columns
        print("\n2. Verifying table structure...")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'anomaly_detection_results'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        required_columns = {
            'id': 'uuid',
            'property_id': 'uuid',
            'metric_name': 'character varying',
            'metric_history_start_date': 'date',
            'metric_history_end_date': 'date',
            'data_points_analyzed': 'integer',
            'zscore_detected': 'boolean',
            'zscore_threshold': 'numeric',
            'zscore_values': 'ARRAY',
            'zscore_anomalies': 'integer',
            'cusum_detected': 'boolean',
            'cusum_threshold': 'numeric',
            'cusum_direction': 'character varying',
            'cusum_anomalies': 'integer',
            'anomalies_found': 'boolean',
            'anomaly_confidence': 'numeric',
            'anomaly_type': 'character varying',
            'anomaly_values': 'ARRAY',
            'anomaly_dates': 'ARRAY',
            'anomaly_descriptions': 'ARRAY',
            'requires_review': 'boolean',
            'requires_alert': 'boolean',
            'lookback_months': 'integer',
            'analysis_method': 'character varying',
            'analysis_date': 'date',
            'analysis_timestamp': 'timestamp without time zone',
            'analysis_duration_seconds': 'numeric'
        }
        
        found_columns = {col['column_name']: col['data_type'] for col in columns}
        
        all_columns_present = True
        for col_name, expected_type in required_columns.items():
            if col_name in found_columns:
                actual_type = found_columns[col_name]
                # Arrays show as 'ARRAY' in data_type
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
            WHERE tablename = 'anomaly_detection_results'
            ORDER BY indexname;
        """)
        indexes = cur.fetchall()
        
        expected_indexes = [
            'idx_anomaly_analysis_date',
            'idx_anomaly_detected',
            'idx_anomaly_metric_name',
            'idx_anomaly_property_id',
            'idx_anomaly_property_metric',
            'idx_anomaly_requires_alert',
            'idx_anomaly_requires_review'
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
                AND tc.table_name = 'anomaly_detection_results';
        """)
        fkeys = cur.fetchall()
        
        expected_fkeys = [
            ('property_id', 'properties')
        ]
        
        for column, ref_table in expected_fkeys:
            found = any(fk['column_name'] == column and fk['foreign_table_name'] == ref_table for fk in fkeys)
            if found:
                print(f"   ✓ {column} → {ref_table}")
            else:
                print(f"   ⚠ {column} → {ref_table}: MISSING (may not exist yet)")
        
        # 5. Verify CHECK constraints
        print("\n5. Verifying CHECK constraints...")
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid) as definition
            FROM pg_constraint
            WHERE conrelid = 'anomaly_detection_results'::regclass
                AND contype = 'c'
            ORDER BY conname;
        """)
        checks = cur.fetchall()
        
        expected_checks = [
            'chk_analysis_date',
            'chk_analysis_duration',
            'chk_analysis_method',
            'chk_anomaly_confidence',
            'chk_anomaly_type',
            'chk_cusum_direction',
            'chk_cusum_threshold',
            'chk_data_points',
            'chk_lookback_months',
            'chk_zscore_threshold'
        ]
        
        found_checks = [chk['conname'] for chk in checks]
        
        for expected_chk in expected_checks:
            if expected_chk in found_checks:
                print(f"   ✓ {expected_chk}")
            else:
                print(f"   ⚠ {expected_chk}: MISSING")
        
        # 6. Test insert operation with arrays
        print("\n6. Testing insert operation with array data...")
        
        # First, get or create a test property
        cur.execute("""
            SELECT id FROM properties LIMIT 1;
        """)
        result = cur.fetchone()
        
        if result:
            test_property_id = result['id']
            print(f"   ✓ Using existing property: {test_property_id}")
        else:
            print("   ⚠ No properties found, creating test property...")
            cur.execute("""
                INSERT INTO properties (
                    name, property_type, status, total_sqft, occupancy_rate
                ) VALUES (
                    'Test Anomaly Property', 'office', 'active', 10000.00, 85.00
                ) RETURNING id;
            """)
            test_property_id = cur.fetchone()['id']
            print(f"   ✓ Created test property: {test_property_id}")
        
        test_data = {
            'property_id': test_property_id,
            'metric_name': 'noi',
            'metric_history_start_date': date.today() - timedelta(days=365),
            'metric_history_end_date': date.today(),
            'data_points_analyzed': 12,
            'zscore_detected': True,
            'zscore_threshold': Decimal('2.5'),
            'zscore_values': [0.5, 1.2, 3.8, 1.1, 0.9, 1.4, 0.7, 1.0, 2.1, 0.8, 1.3, 1.5],
            'zscore_anomalies': 1,
            'anomalies_found': True,
            'anomaly_confidence': Decimal('0.85'),
            'anomaly_type': 'outlier',
            'anomaly_values': [85000.00],
            'anomaly_dates': [date.today() - timedelta(days=90)],
            'anomaly_descriptions': ['NOI dropped 35% below expected value'],
            'requires_review': True,
            'requires_alert': True,
            'lookback_months': 12,
            'analysis_method': 'z_score',
            'analysis_date': date.today(),
            'analysis_duration_seconds': Decimal('2.34')
        }
        
        cur.execute("""
            INSERT INTO anomaly_detection_results (
                property_id, metric_name,
                metric_history_start_date, metric_history_end_date,
                data_points_analyzed,
                zscore_detected, zscore_threshold, zscore_values, zscore_anomalies,
                anomalies_found, anomaly_confidence, anomaly_type,
                anomaly_values, anomaly_dates, anomaly_descriptions,
                requires_review, requires_alert,
                lookback_months, analysis_method, analysis_date, analysis_duration_seconds
            ) VALUES (
                %(property_id)s, %(metric_name)s,
                %(metric_history_start_date)s, %(metric_history_end_date)s,
                %(data_points_analyzed)s,
                %(zscore_detected)s, %(zscore_threshold)s, %(zscore_values)s, %(zscore_anomalies)s,
                %(anomalies_found)s, %(anomaly_confidence)s, %(anomaly_type)s,
                %(anomaly_values)s, %(anomaly_dates)s, %(anomaly_descriptions)s,
                %(requires_review)s, %(requires_alert)s,
                %(lookback_months)s, %(analysis_method)s, %(analysis_date)s, %(analysis_duration_seconds)s
            ) RETURNING id, analysis_timestamp;
        """, test_data)
        
        result = cur.fetchone()
        test_id = result['id']
        test_timestamp = result['analysis_timestamp']
        
        print(f"   ✓ Inserted test record: {test_id}")
        print(f"   ✓ Timestamp auto-generated: {test_timestamp}")
        
        # 7. Test array queries
        print("\n7. Testing array operations...")
        
        # Test reading array data
        cur.execute("""
            SELECT zscore_values, anomaly_dates, anomaly_descriptions
            FROM anomaly_detection_results
            WHERE id = %s;
        """, (test_id,))
        result = cur.fetchone()
        
        if result:
            print(f"   ✓ Z-score values array: {len(result['zscore_values'])} elements")
            print(f"   ✓ Anomaly dates array: {len(result['anomaly_dates'])} elements")
            print(f"   ✓ Descriptions array: {len(result['anomaly_descriptions'])} elements")
        else:
            print("   ✗ Failed to read array data")
        
        # Test UNNEST for expanding arrays
        cur.execute("""
            SELECT 
                UNNEST(anomaly_dates) as anomaly_date,
                UNNEST(anomaly_values) as anomaly_value,
                UNNEST(anomaly_descriptions) as description
            FROM anomaly_detection_results
            WHERE id = %s;
        """, (test_id,))
        unnested = cur.fetchall()
        
        if unnested:
            print(f"   ✓ UNNEST operation successful: {len(unnested)} row(s)")
            for row in unnested:
                print(f"     - {row['anomaly_date']}: ${row['anomaly_value']:,.2f}")
        else:
            print("   ✗ UNNEST operation failed")
        
        # 8. Test query with indexes
        print("\n8. Testing query operations...")
        
        # Query by property
        cur.execute("""
            SELECT id, metric_name, anomalies_found
            FROM anomaly_detection_results
            WHERE property_id = %s;
        """, (test_property_id,))
        results = cur.fetchall()
        print(f"   ✓ Property query returned {len(results)} record(s)")
        
        # Query by metric
        cur.execute("""
            SELECT id, property_id, analysis_date
            FROM anomaly_detection_results
            WHERE metric_name = 'noi';
        """)
        results = cur.fetchall()
        print(f"   ✓ Metric query returned {len(results)} record(s)")
        
        # Query anomalies requiring review
        cur.execute("""
            SELECT id, metric_name, anomaly_confidence
            FROM anomaly_detection_results
            WHERE requires_review = true;
        """)
        results = cur.fetchall()
        print(f"   ✓ Review queue query returned {len(results)} record(s)")
        
        # Query anomalies requiring alerts
        cur.execute("""
            SELECT id, metric_name, anomaly_type
            FROM anomaly_detection_results
            WHERE requires_alert = true;
        """)
        results = cur.fetchall()
        print(f"   ✓ Alert queue query returned {len(results)} record(s)")
        
        # 9. Test CHECK constraints
        print("\n9. Testing CHECK constraints...")
        
        # Test invalid confidence (should fail)
        try:
            cur.execute("""
                INSERT INTO anomaly_detection_results (
                    property_id, metric_name, anomaly_confidence,
                    analysis_method, analysis_date
                ) VALUES (
                    %s, 'test', 1.5, 'z_score', CURRENT_DATE
                );
            """, (test_property_id,))
            print("   ✗ Invalid confidence accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid confidence rejected (chk_anomaly_confidence)")
        
        # Test invalid analysis method (should fail)
        try:
            cur.execute("""
                INSERT INTO anomaly_detection_results (
                    property_id, metric_name, analysis_method, analysis_date
                ) VALUES (
                    %s, 'test', 'invalid_method', CURRENT_DATE
                );
            """, (test_property_id,))
            print("   ✗ Invalid analysis method accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid analysis method rejected (chk_analysis_method)")
        
        # 10. Test CUSUM data
        print("\n10. Testing CUSUM analysis data...")
        cur.execute("""
            INSERT INTO anomaly_detection_results (
                property_id, metric_name,
                cusum_detected, cusum_threshold, cusum_direction, cusum_anomalies,
                anomalies_found, anomaly_confidence, anomaly_type,
                analysis_method, analysis_date
            ) VALUES (
                %s, 'occupancy',
                true, 5.0, 'downward', 1,
                true, 0.92, 'trend_shift',
                'cusum', CURRENT_DATE
            ) RETURNING id;
        """, (test_property_id,))
        cusum_id = cur.fetchone()['id']
        print(f"   ✓ CUSUM analysis record inserted: {cusum_id}")
        
        # 11. Cleanup test data
        print("\n11. Cleaning up test data...")
        cur.execute("DELETE FROM anomaly_detection_results WHERE id IN (%s, %s);", (test_id, cusum_id))
        conn.commit()
        print("   ✓ Test data removed")
        
        # 12. Final statistics
        print("\n12. Table statistics...")
        cur.execute("SELECT COUNT(*) as count FROM anomaly_detection_results;")
        count = cur.fetchone()['count']
        print(f"   ✓ Total anomaly detection records: {count}")
        
        # 13. Check table comments (documentation)
        print("\n13. Checking table documentation...")
        cur.execute("""
            SELECT obj_description('anomaly_detection_results'::regclass) as table_comment;
        """)
        result = cur.fetchone()
        if result and result['table_comment']:
            print(f"   ✓ Table comment: {result['table_comment'][:60]}...")
        else:
            print("   ⚠ No table comment found")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✓ ANOMALY_DETECTION_RESULTS TABLE VERIFICATION COMPLETE")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_anomaly_detection_table()
    sys.exit(0 if success else 1)

