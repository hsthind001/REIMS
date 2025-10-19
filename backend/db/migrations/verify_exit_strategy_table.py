"""
Verification script for exit_strategy_analysis table (Migration 009)
Tests table structure, indexes, constraints, triggers, and array operations
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

def verify_exit_strategy_table():
    """Comprehensive verification of exit_strategy_analysis table"""
    print("=" * 80)
    print("EXIT_STRATEGY_ANALYSIS TABLE VERIFICATION")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Check if table exists
        print("\n1. Checking if exit_strategy_analysis table exists...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'exit_strategy_analysis'
            );
        """)
        exists = cur.fetchone()['exists']
        if exists:
            print("   ✓ exit_strategy_analysis table exists")
        else:
            print("   ✗ exit_strategy_analysis table NOT FOUND")
            return False
        
        # 2. Verify all columns
        print("\n2. Verifying table structure...")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'exit_strategy_analysis'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        required_columns = {
            'id': 'uuid',
            'property_id': 'uuid',
            'analysis_date': 'date',
            'analysis_timestamp': 'timestamp without time zone',
            'market_cap_rate': 'numeric',
            'market_mortgage_rate': 'numeric',
            'property_condition_adjustment': 'numeric',
            'location_premium': 'numeric',
            'hold_projected_noi_5yr': 'ARRAY',
            'hold_irr': 'numeric',
            'hold_total_return': 'numeric',
            'hold_terminal_value': 'numeric',
            'hold_pros': 'ARRAY',
            'hold_cons': 'ARRAY',
            'refinance_new_loan_amount': 'numeric',
            'refinance_new_rate': 'numeric',
            'refinance_cash_out': 'numeric',
            'refinance_monthly_savings': 'numeric',
            'refinance_new_dscr': 'numeric',
            'refinance_feasible': 'boolean',
            'refinance_pros': 'ARRAY',
            'refinance_cons': 'ARRAY',
            'sale_estimated_price': 'numeric',
            'sale_transaction_costs': 'numeric',
            'sale_loan_payoff': 'numeric',
            'sale_net_proceeds': 'numeric',
            'sale_total_return_pct': 'numeric',
            'sale_annualized_return': 'numeric',
            'sale_pros': 'ARRAY',
            'sale_cons': 'ARRAY',
            'recommended_strategy': 'character varying',
            'recommendation_confidence': 'numeric',
            'recommendation_rationale': 'text',
            'analyst_id': 'uuid',
            'analysis_complete': 'boolean',
            'updated_at': 'timestamp without time zone'
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
            WHERE tablename = 'exit_strategy_analysis'
            ORDER BY indexname;
        """)
        indexes = cur.fetchall()
        
        expected_indexes = [
            'idx_exit_analysis_date',
            'idx_exit_confidence',
            'idx_exit_property_date',
            'idx_exit_property_id',
            'idx_exit_recommendation'
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
                AND tc.table_name = 'exit_strategy_analysis';
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
            WHERE conrelid = 'exit_strategy_analysis'::regclass
                AND contype = 'c'
            ORDER BY conname;
        """)
        checks = cur.fetchall()
        
        expected_checks = [
            'chk_analysis_date',
            'chk_hold_irr',
            'chk_location_premium',
            'chk_market_cap_rate',
            'chk_market_mortgage_rate',
            'chk_property_condition',
            'chk_recommendation_confidence',
            'chk_recommended_strategy',
            'chk_refinance_dscr',
            'chk_refinance_rate',
            'chk_sale_annualized_return',
            'chk_sale_return_pct'
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
            WHERE tgrelid = 'exit_strategy_analysis'::regclass
                AND tgname = 'trigger_update_exit_strategy_timestamp';
        """)
        trigger = cur.fetchone()
        if trigger:
            print(f"   ✓ trigger_update_exit_strategy_timestamp")
        else:
            print(f"   ⚠ trigger_update_exit_strategy_timestamp: MISSING")
        
        # 7. Get or create test property
        print("\n7. Setting up test data...")
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
                    'Test Exit Strategy Property', 'office', 'active', 50000.00, 92.00
                ) RETURNING id;
            """)
            test_property_id = cur.fetchone()['id']
            print(f"   ✓ Created test property: {test_property_id}")
        
        # 8. Test insert with complete exit strategy analysis
        print("\n8. Testing insert operation with all scenarios...")
        
        test_data = {
            'property_id': test_property_id,
            'analysis_date': date.today(),
            'market_cap_rate': Decimal('0.065'),
            'market_mortgage_rate': Decimal('0.055'),
            'property_condition_adjustment': Decimal('0.95'),
            'location_premium': Decimal('1.05'),
            # HOLD scenario
            'hold_projected_noi_5yr': [850000, 875000, 900000, 925000, 950000],
            'hold_irr': Decimal('0.082'),
            'hold_total_return': Decimal('2500000'),
            'hold_terminal_value': Decimal('15000000'),
            'hold_pros': ['Strong market fundamentals', 'Consistent cash flow', 'Long-term appreciation'],
            'hold_cons': ['Capital tied up', 'Property management burden'],
            # REFINANCE scenario
            'refinance_new_loan_amount': Decimal('10000000'),
            'refinance_new_rate': Decimal('0.050'),
            'refinance_cash_out': Decimal('1500000'),
            'refinance_monthly_savings': Decimal('5000'),
            'refinance_new_dscr': Decimal('1.45'),
            'refinance_feasible': True,
            'refinance_pros': ['Unlock equity', 'Lower monthly payments'],
            'refinance_cons': ['Closing costs', 'Extended loan term'],
            # SALE scenario
            'sale_estimated_price': Decimal('14500000'),
            'sale_transaction_costs': Decimal('725000'),
            'sale_loan_payoff': Decimal('9000000'),
            'sale_net_proceeds': Decimal('4775000'),
            'sale_total_return_pct': Decimal('38.20'),
            'sale_annualized_return': Decimal('0.078'),
            'sale_pros': ['Immediate liquidity', 'Strong market conditions'],
            'sale_cons': ['Capital gains tax', 'Loss of future appreciation'],
            # Recommendation
            'recommended_strategy': 'hold',
            'recommendation_confidence': Decimal('0.85'),
            'recommendation_rationale': 'Strong fundamentals with consistent NOI growth',
            'analysis_complete': True
        }
        
        cur.execute("""
            INSERT INTO exit_strategy_analysis (
                property_id, analysis_date,
                market_cap_rate, market_mortgage_rate, property_condition_adjustment, location_premium,
                hold_projected_noi_5yr, hold_irr, hold_total_return, hold_terminal_value,
                hold_pros, hold_cons,
                refinance_new_loan_amount, refinance_new_rate, refinance_cash_out,
                refinance_monthly_savings, refinance_new_dscr, refinance_feasible,
                refinance_pros, refinance_cons,
                sale_estimated_price, sale_transaction_costs, sale_loan_payoff,
                sale_net_proceeds, sale_total_return_pct, sale_annualized_return,
                sale_pros, sale_cons,
                recommended_strategy, recommendation_confidence, recommendation_rationale,
                analysis_complete
            ) VALUES (
                %(property_id)s, %(analysis_date)s,
                %(market_cap_rate)s, %(market_mortgage_rate)s, %(property_condition_adjustment)s, %(location_premium)s,
                %(hold_projected_noi_5yr)s, %(hold_irr)s, %(hold_total_return)s, %(hold_terminal_value)s,
                %(hold_pros)s, %(hold_cons)s,
                %(refinance_new_loan_amount)s, %(refinance_new_rate)s, %(refinance_cash_out)s,
                %(refinance_monthly_savings)s, %(refinance_new_dscr)s, %(refinance_feasible)s,
                %(refinance_pros)s, %(refinance_cons)s,
                %(sale_estimated_price)s, %(sale_transaction_costs)s, %(sale_loan_payoff)s,
                %(sale_net_proceeds)s, %(sale_total_return_pct)s, %(sale_annualized_return)s,
                %(sale_pros)s, %(sale_cons)s,
                %(recommended_strategy)s, %(recommendation_confidence)s, %(recommendation_rationale)s,
                %(analysis_complete)s
            ) RETURNING id, analysis_timestamp, updated_at;
        """, test_data)
        
        result = cur.fetchone()
        test_id = result['id']
        test_timestamp = result['analysis_timestamp']
        original_updated_at = result['updated_at']
        
        print(f"   ✓ Inserted test record: {test_id}")
        print(f"   ✓ Analysis timestamp: {test_timestamp}")
        print(f"   ✓ Updated_at timestamp: {original_updated_at}")
        
        # 9. Test array operations
        print("\n9. Testing array operations...")
        
        # Read array data
        cur.execute("""
            SELECT 
                hold_projected_noi_5yr,
                hold_pros,
                refinance_pros,
                sale_pros
            FROM exit_strategy_analysis
            WHERE id = %s;
        """, (test_id,))
        result = cur.fetchone()
        
        if result:
            print(f"   ✓ NOI projections: {len(result['hold_projected_noi_5yr'])} years")
            print(f"   ✓ Hold pros: {len(result['hold_pros'])} items")
            print(f"   ✓ Refinance pros: {len(result['refinance_pros'])} items")
            print(f"   ✓ Sale pros: {len(result['sale_pros'])} items")
        
        # Test UNNEST for NOI projections
        cur.execute("""
            SELECT 
                UNNEST(hold_projected_noi_5yr) as projected_noi,
                generate_series(1, ARRAY_LENGTH(hold_projected_noi_5yr, 1)) as year
            FROM exit_strategy_analysis
            WHERE id = %s;
        """, (test_id,))
        noi_projections = cur.fetchall()
        
        if noi_projections:
            print(f"   ✓ UNNEST NOI projections: {len(noi_projections)} years")
            for row in noi_projections[:3]:  # Show first 3
                print(f"     - Year {row['year']}: ${row['projected_noi']:,.2f}")
        
        # 10. Test query operations
        print("\n10. Testing query operations...")
        
        # Query by property
        cur.execute("""
            SELECT id, analysis_date, recommended_strategy
            FROM exit_strategy_analysis
            WHERE property_id = %s;
        """, (test_property_id,))
        results = cur.fetchall()
        print(f"   ✓ Property query returned {len(results)} record(s)")
        
        # Query by recommendation
        cur.execute("""
            SELECT id, recommended_strategy, recommendation_confidence
            FROM exit_strategy_analysis
            WHERE recommended_strategy = 'hold';
        """)
        results = cur.fetchall()
        print(f"   ✓ Recommendation query returned {len(results)} record(s)")
        
        # Query high-confidence recommendations
        cur.execute("""
            SELECT id, recommended_strategy, recommendation_confidence
            FROM exit_strategy_analysis
            WHERE recommendation_confidence >= 0.70;
        """)
        results = cur.fetchall()
        print(f"   ✓ High-confidence query returned {len(results)} record(s)")
        
        # Query refinancing opportunities
        cur.execute("""
            SELECT id, refinance_new_dscr, refinance_feasible
            FROM exit_strategy_analysis
            WHERE refinance_feasible = true
                AND refinance_new_dscr >= 1.25;
        """)
        results = cur.fetchall()
        print(f"   ✓ Refinancing query returned {len(results)} record(s)")
        
        # 11. Test trigger (updated_at auto-update)
        print("\n11. Testing trigger (updated_at auto-update)...")
        time.sleep(1)  # Ensure timestamp difference
        
        cur.execute("""
            UPDATE exit_strategy_analysis
            SET recommendation_confidence = 0.90
            WHERE id = %s
            RETURNING updated_at;
        """, (test_id,))
        new_updated_at = cur.fetchone()['updated_at']
        
        if new_updated_at > original_updated_at:
            print(f"   ✓ Trigger working: updated_at changed")
            print(f"     Original: {original_updated_at}")
            print(f"     Updated:  {new_updated_at}")
        else:
            print(f"   ✗ Trigger not working: updated_at unchanged")
        
        # 12. Test CHECK constraints
        print("\n12. Testing CHECK constraints...")
        
        # Test invalid confidence (> 1.00)
        try:
            cur.execute("""
                INSERT INTO exit_strategy_analysis (
                    property_id, analysis_date, recommended_strategy,
                    recommendation_confidence
                ) VALUES (
                    %s, CURRENT_DATE, 'hold', 1.5
                );
            """, (test_property_id,))
            print("   ✗ Invalid confidence accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid confidence rejected (chk_recommendation_confidence)")
        
        # Test invalid property condition adjustment
        try:
            cur.execute("""
                INSERT INTO exit_strategy_analysis (
                    property_id, analysis_date, recommended_strategy,
                    property_condition_adjustment
                ) VALUES (
                    %s, CURRENT_DATE, 'hold', 1.50
                );
            """, (test_property_id,))
            print("   ✗ Invalid condition adjustment accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid condition adjustment rejected (chk_property_condition)")
        
        # Test invalid recommended strategy
        try:
            cur.execute("""
                INSERT INTO exit_strategy_analysis (
                    property_id, analysis_date, recommended_strategy
                ) VALUES (
                    %s, CURRENT_DATE, 'invalid_strategy'
                );
            """, (test_property_id,))
            print("   ✗ Invalid strategy accepted (should have failed)")
        except psycopg2.errors.CheckViolation:
            conn.rollback()
            print("   ✓ Invalid strategy rejected (chk_recommended_strategy)")
        
        # 13. Test scenario comparison query
        print("\n13. Testing scenario comparison...")
        cur.execute("""
            SELECT 
                'Hold' as scenario,
                hold_irr as return_rate,
                ARRAY_LENGTH(hold_pros, 1) as num_pros,
                ARRAY_LENGTH(hold_cons, 1) as num_cons
            FROM exit_strategy_analysis
            WHERE id = %s
            UNION ALL
            SELECT 
                'Sale' as scenario,
                sale_annualized_return as return_rate,
                ARRAY_LENGTH(sale_pros, 1) as num_pros,
                ARRAY_LENGTH(sale_cons, 1) as num_cons
            FROM exit_strategy_analysis
            WHERE id = %s;
        """, (test_id, test_id))
        comparison = cur.fetchall()
        
        print(f"   ✓ Scenario comparison query returned {len(comparison)} scenarios")
        for row in comparison:
            print(f"     - {row['scenario']}: IRR={row['return_rate']}, Pros={row['num_pros']}, Cons={row['num_cons']}")
        
        # 14. Cleanup test data
        print("\n14. Cleaning up test data...")
        cur.execute("DELETE FROM exit_strategy_analysis WHERE id = %s;", (test_id,))
        conn.commit()
        print("   ✓ Test data removed")
        
        # 15. Final statistics
        print("\n15. Table statistics...")
        cur.execute("SELECT COUNT(*) as count FROM exit_strategy_analysis;")
        count = cur.fetchone()['count']
        print(f"   ✓ Total exit strategy analyses: {count}")
        
        # 16. Check table comments (documentation)
        print("\n16. Checking table documentation...")
        cur.execute("""
            SELECT obj_description('exit_strategy_analysis'::regclass) as table_comment;
        """)
        result = cur.fetchone()
        if result and result['table_comment']:
            print(f"   ✓ Table comment: {result['table_comment'][:60]}...")
        else:
            print("   ⚠ No table comment found")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✓ EXIT_STRATEGY_ANALYSIS TABLE VERIFICATION COMPLETE")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_exit_strategy_table()
    sys.exit(0 if success else 1)

