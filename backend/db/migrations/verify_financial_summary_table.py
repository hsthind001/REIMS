"""
Verification script for property_financial_summary table (Migration 010)
Tests table structure, indexes, constraints, triggers, and unique constraints
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
import time

# Database connection details
DB_CONFIG = {
    'dbname': 'reims',
    'user': 'postgres',
    'password': 'reims2024',
    'host': 'localhost',
    'port': '5432'
}

def verify_financial_summary_table():
    """Comprehensive verification of property_financial_summary table"""
    print("=" * 80)
    print("PROPERTY_FINANCIAL_SUMMARY TABLE VERIFICATION")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Check if table exists
        print("\n1. Checking if property_financial_summary table exists...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'property_financial_summary'
            );
        """)
        exists = cur.fetchone()['exists']
        if exists:
            print("   ✓ property_financial_summary table exists")
        else:
            print("   ✗ property_financial_summary table NOT FOUND")
            return False
        
        # 2. Verify all columns
        print("\n2. Verifying table structure...")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'property_financial_summary'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        required_columns = {
            'id': 'uuid',
            'property_id': 'uuid',
            'summary_date': 'date',
            'summary_month': 'character varying',
            'gross_revenue': 'numeric',
            'total_expenses': 'numeric',
            'noi': 'numeric',
            'noi_margin': 'numeric',
            'annual_debt_service': 'numeric',
            'dscr': 'numeric',
            'ltv': 'numeric',
            'total_units': 'integer',
            'occupied_units': 'integer',
            'occupancy_rate': 'numeric',
            'leased_not_occupied': 'integer',
            'vacant_units': 'integer',
            'tenant_count': 'integer',
            'average_lease_term_months': 'numeric',
            'expiring_leases_12mo': 'integer',
            'cap_rate': 'numeric',
            'roi_pct': 'numeric',
            'days_on_market': 'integer',
            'expense_per_sqft': 'numeric',
            'revenue_per_sqft': 'numeric',
            'rent_per_occupied_sqft': 'numeric',
            'avg_rent_per_unit': 'numeric',
            'rent_growth_pct_yoy': 'numeric',
            'expense_ratio': 'numeric',
            'below_market_rent': 'boolean',
            'above_average_expense': 'boolean',
            'lease_expiration_risk': 'boolean',
            'calculated_at': 'timestamp without time zone',
            'data_complete': 'boolean'
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
            WHERE tablename = 'property_financial_summary'
            ORDER BY indexname;
        """)
        indexes = cur.fetchall()
        
        expected_indexes = [
            'idx_summary_below_market',
            'idx_summary_date',
            'idx_summary_dscr',
            'idx_summary_high_expense',
            'idx_summary_lease_risk',
            'idx_summary_month',
            'idx_summary_noi',
            'idx_summary_occupancy',
            'idx_summary_property_id'
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
                AND tc.table_name = 'property_financial_summary';
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
        
        # 5. Verify UNIQUE constraint
        print("\n5. Verifying UNIQUE constraint...")
        cur.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_name = 'property_financial_summary'
                AND constraint_type = 'UNIQUE';
        """)
        unique_constraints = cur.fetchall()
        
        found_unique = any('unique_property_month' in uc['constraint_name'] for uc in unique_constraints)
        if found_unique:
            print("   ✓ unique_property_month constraint exists")
        else:
            print("   ⚠ unique_property_month constraint MISSING")
        
        # 6. Verify CHECK constraints
        print("\n6. Verifying CHECK constraints...")
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid) as definition
            FROM pg_constraint
            WHERE conrelid = 'property_financial_summary'::regclass
                AND contype = 'c'
            ORDER BY conname;
        """)
        checks = cur.fetchall()
        
        expected_checks = [
            'chk_avg_lease_term',
            'chk_cap_rate',
            'chk_days_on_market',
            'chk_dscr',
            'chk_expense_per_sqft',
            'chk_expense_ratio',
            'chk_expiring_leases',
            'chk_ltv',
            'chk_noi_margin',
            'chk_occupied_units',
            'chk_occupancy_rate',
            'chk_rent_per_sqft',
            'chk_revenue_per_sqft',
            'chk_roi_pct',
            'chk_summary_date',
            'chk_summary_month_format',
            'chk_tenant_count',
            'chk_vacant_units'
        ]
        
        found_checks = [chk['conname'] for chk in checks]
        
        for expected_chk in expected_checks:
            if expected_chk in found_checks:
                print(f"   ✓ {expected_chk}")
            else:
                print(f"   ⚠ {expected_chk}: MISSING")
        
        # 7. Verify trigger exists
        print("\n7. Verifying trigger...")
        cur.execute("""
            SELECT tgname 
            FROM pg_trigger 
            WHERE tgrelid = 'property_financial_summary'::regclass
                AND tgname = 'trigger_set_summary_month';
        """)
        trigger = cur.fetchone()
        if trigger:
            print(f"   ✓ trigger_set_summary_month")
        else:
            print(f"   ⚠ trigger_set_summary_month: MISSING")
        
        # 8. Get or create test property
        print("\n8. Setting up test data...")
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
                    'Test Financial Summary Property', 'retail', 'active', 75000.00, 88.00
                ) RETURNING id;
            """)
            test_property_id = cur.fetchone()['id']
            print(f"   ✓ Created test property: {test_property_id}")
        
        # 9. Test insert with complete financial summary
        print("\n9. Testing insert operation...")
        
        test_data = {
            'property_id': test_property_id,
            'summary_date': date.today(),
            'gross_revenue': Decimal('1200000.00'),
            'total_expenses': Decimal('350000.00'),
            'noi': Decimal('850000.00'),
            'noi_margin': Decimal('0.708'),
            'annual_debt_service': Decimal('600000.00'),
            'dscr': Decimal('1.42'),
            'ltv': Decimal('0.65'),
            'total_units': 50,
            'occupied_units': 46,
            'occupancy_rate': Decimal('0.92'),
            'leased_not_occupied': 2,
            'vacant_units': 4,
            'tenant_count': 46,
            'average_lease_term_months': Decimal('24.5'),
            'expiring_leases_12mo': 12,
            'cap_rate': Decimal('0.057'),
            'roi_pct': Decimal('12.50'),
            'days_on_market': 0,
            'expense_per_sqft': Decimal('7.00'),
            'revenue_per_sqft': Decimal('24.00'),
            'rent_per_occupied_sqft': Decimal('26.09'),
            'avg_rent_per_unit': Decimal('2500.00'),
            'rent_growth_pct_yoy': Decimal('3.50'),
            'expense_ratio': Decimal('0.292'),
            'below_market_rent': False,
            'above_average_expense': False,
            'lease_expiration_risk': True,
            'data_complete': True
        }
        
        cur.execute("""
            INSERT INTO property_financial_summary (
                property_id, summary_date,
                gross_revenue, total_expenses, noi, noi_margin,
                annual_debt_service, dscr, ltv,
                total_units, occupied_units, occupancy_rate, leased_not_occupied, vacant_units,
                tenant_count, average_lease_term_months, expiring_leases_12mo,
                cap_rate, roi_pct, days_on_market,
                expense_per_sqft, revenue_per_sqft, rent_per_occupied_sqft,
                avg_rent_per_unit, rent_growth_pct_yoy, expense_ratio,
                below_market_rent, above_average_expense, lease_expiration_risk,
                data_complete
            ) VALUES (
                %(property_id)s, %(summary_date)s,
                %(gross_revenue)s, %(total_expenses)s, %(noi)s, %(noi_margin)s,
                %(annual_debt_service)s, %(dscr)s, %(ltv)s,
                %(total_units)s, %(occupied_units)s, %(occupancy_rate)s, %(leased_not_occupied)s, %(vacant_units)s,
                %(tenant_count)s, %(average_lease_term_months)s, %(expiring_leases_12mo)s,
                %(cap_rate)s, %(roi_pct)s, %(days_on_market)s,
                %(expense_per_sqft)s, %(revenue_per_sqft)s, %(rent_per_occupied_sqft)s,
                %(avg_rent_per_unit)s, %(rent_growth_pct_yoy)s, %(expense_ratio)s,
                %(below_market_rent)s, %(above_average_expense)s, %(lease_expiration_risk)s,
                %(data_complete)s
            ) RETURNING id, summary_month, calculated_at;
        """, test_data)
        
        result = cur.fetchone()
        test_id = result['id']
        test_month = result['summary_month']
        test_calculated_at = result['calculated_at']
        
        print(f"   ✓ Inserted test record: {test_id}")
        print(f"   ✓ Summary month auto-generated: {test_month}")
        print(f"   ✓ Calculated_at timestamp: {test_calculated_at}")
        
        # 10. Test trigger (summary_month auto-generation)
        print("\n10. Testing trigger (summary_month auto-generation)...")
        
        # Verify the summary_month matches expected format
        expected_month = date.today().strftime('%Y-%m')
        if test_month == expected_month:
            print(f"   ✓ Trigger working: summary_month = {test_month}")
        else:
            print(f"   ✗ Trigger not working: expected {expected_month}, got {test_month}")
        
        # 11. Test UNIQUE constraint
        print("\n11. Testing UNIQUE constraint (property_id + summary_month)...")
        try:
            cur.execute("""
                INSERT INTO property_financial_summary (
                    property_id, summary_date, noi
                ) VALUES (
                    %s, %s, 100000.00
                );
            """, (test_property_id, date.today()))
            print("   ✗ Duplicate record accepted (should have failed)")
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            print("   ✓ Duplicate rejected (unique_property_month constraint)")
        
        # 12. Test query operations
        print("\n12. Testing query operations...")
        
        # Query by property
        cur.execute("""
            SELECT id, summary_month, noi, occupancy_rate
            FROM property_financial_summary
            WHERE property_id = %s;
        """, (test_property_id,))
        results = cur.fetchall()
        print(f"   ✓ Property query returned {len(results)} record(s)")
        
        # Query by month
        cur.execute("""
            SELECT id, property_id, noi
            FROM property_financial_summary
            WHERE summary_month = %s;
        """, (test_month,))
        results = cur.fetchall()
        print(f"   ✓ Month query returned {len(results)} record(s)")
        
        # Query with risk flags
        cur.execute("""
            SELECT id, property_id
            FROM property_financial_summary
            WHERE lease_expiration_risk = true;
        """)
        results = cur.fetchall()
        print(f"   ✓ Risk flag query returned {len(results)} record(s)")
        
        # Dashboard query (no joins needed)
        cur.execute("""
            SELECT 
                summary_month, noi, occupancy_rate, dscr, cap_rate,
                below_market_rent, above_average_expense, lease_expiration_risk
            FROM property_financial_summary
            WHERE property_id = %s
            ORDER BY summary_date DESC
            LIMIT 1;
        """, (test_property_id,))
        dashboard_data = cur.fetchone()
        if dashboard_data:
            print(f"   ✓ Dashboard query successful (denormalized, no joins)")
            print(f"     - NOI: ${dashboard_data['noi']:,.2f}")
            print(f"     - Occupancy: {dashboard_data['occupancy_rate'] * 100:.1f}%")
            print(f"     - DSCR: {dashboard_data['dscr']}")
        
        # 13. Test CHECK constraints
        print("\n13. Testing CHECK constraints...")
        
        # Test invalid occupancy rate (> 1.00)
        try:
            cur.execute("""
                INSERT INTO property_financial_summary (
                    property_id, summary_date, occupancy_rate
                ) VALUES (
                    %s, CURRENT_DATE - INTERVAL '1 day', 1.50
                );
            """, (test_property_id,))
            print("   ✗ Invalid occupancy rate accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid occupancy rate rejected (chk_occupancy_rate)")
        
        # Test invalid summary_month format
        try:
            cur.execute("""
                INSERT INTO property_financial_summary (
                    property_id, summary_date
                ) VALUES (
                    %s, CURRENT_DATE - INTERVAL '1 day'
                ) RETURNING id;
            """, (test_property_id,))
            
            result = cur.fetchone()
            temp_id = result['id']
            
            # Try to manually set invalid format
            cur.execute("""
                UPDATE property_financial_summary
                SET summary_month = 'invalid-format'
                WHERE id = %s;
            """, (temp_id,))
            print("   ✗ Invalid month format accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid month format rejected (chk_summary_month_format)")
        
        # Test occupied units > total units
        try:
            cur.execute("""
                INSERT INTO property_financial_summary (
                    property_id, summary_date, total_units, occupied_units
                ) VALUES (
                    %s, CURRENT_DATE - INTERVAL '2 days', 50, 60
                );
            """, (test_property_id,))
            print("   ✗ Invalid unit count accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid unit count rejected (chk_occupied_units)")
        
        # 14. Test UPSERT (ON CONFLICT)
        print("\n14. Testing UPSERT operation...")
        
        cur.execute("""
            INSERT INTO property_financial_summary (
                property_id, summary_date, noi, occupancy_rate
            ) VALUES (
                %s, %s, 900000.00, 0.95
            )
            ON CONFLICT (property_id, summary_month)
            DO UPDATE SET
                noi = EXCLUDED.noi,
                occupancy_rate = EXCLUDED.occupancy_rate,
                calculated_at = CURRENT_TIMESTAMP
            RETURNING id, noi, occupancy_rate;
        """, (test_property_id, date.today()))
        
        updated = cur.fetchone()
        if updated and updated['noi'] == Decimal('900000.00'):
            print(f"   ✓ UPSERT successful: NOI updated to ${updated['noi']:,.2f}")
        else:
            print("   ✗ UPSERT failed")
        
        # 15. Test portfolio aggregation
        print("\n15. Testing portfolio aggregation query...")
        cur.execute("""
            SELECT 
                COUNT(*) as property_count,
                SUM(noi) as total_noi,
                AVG(occupancy_rate) as avg_occupancy,
                AVG(dscr) as avg_dscr,
                SUM(CASE WHEN lease_expiration_risk THEN 1 ELSE 0 END) as risk_count
            FROM property_financial_summary
            WHERE summary_month = %s
                AND data_complete = true;
        """, (test_month,))
        
        portfolio = cur.fetchone()
        if portfolio:
            print(f"   ✓ Portfolio aggregation successful")
            print(f"     - Properties: {portfolio['property_count']}")
            print(f"     - Total NOI: ${portfolio['total_noi']:,.2f}")
            if portfolio['avg_occupancy']:
                print(f"     - Avg Occupancy: {portfolio['avg_occupancy'] * 100:.1f}%")
        
        # 16. Cleanup test data
        print("\n16. Cleaning up test data...")
        cur.execute("DELETE FROM property_financial_summary WHERE property_id = %s;", (test_property_id,))
        conn.commit()
        print("   ✓ Test data removed")
        
        # 17. Final statistics
        print("\n17. Table statistics...")
        cur.execute("SELECT COUNT(*) as count FROM property_financial_summary;")
        count = cur.fetchone()['count']
        print(f"   ✓ Total financial summaries: {count}")
        
        # 18. Check table comments (documentation)
        print("\n18. Checking table documentation...")
        cur.execute("""
            SELECT obj_description('property_financial_summary'::regclass) as table_comment;
        """)
        result = cur.fetchone()
        if result and result['table_comment']:
            print(f"   ✓ Table comment: {result['table_comment'][:60]}...")
        else:
            print("   ⚠ No table comment found")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✓ PROPERTY_FINANCIAL_SUMMARY TABLE VERIFICATION COMPLETE")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_financial_summary_table()
    sys.exit(0 if success else 1)

