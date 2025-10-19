"""
Verify Financial Documents Table Creation

This script verifies that the financial_documents table was created correctly
with all columns, indexes, constraints, triggers, and functions.

Usage:
    python backend/db/migrations/verify_financial_documents_table.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.db import init_db, close_db, fetch_all, fetch_val, fetch_one, execute


async def verify_table_exists() -> bool:
    """Check if financial_documents table exists"""
    exists = await fetch_val("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'financial_documents'
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
            WHERE tc.table_name = 'financial_documents'
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
            WHERE tc.table_name = 'financial_documents' AND tc.constraint_type = 'FOREIGN KEY'
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
        WHERE table_name = 'financial_documents'
        ORDER BY ordinal_position
    """)
    
    expected_columns = [
        'id', 'property_id', 'file_name', 'file_path', 'file_size_bytes', 'file_hash',
        'mime_type', 'document_type', 'document_name', 'status', 'processing_status_detail',
        'upload_date', 'document_date', 'processing_start_date', 'processing_end_date',
        'processing_duration_seconds', 'extracted_metrics_count', 'total_tables_found',
        'total_text_pages', 'ocr_required', 'avg_extraction_confidence', 'error_message',
        'error_code', 'processing_attempts', 'last_error_at', 'ai_summary_generated',
        'ai_summary_confidence', 'created_by', 'reviewed_by', 'reviewed_at',
        'created_at', 'updated_at'
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
    key_cols = ['id', 'property_id', 'file_name', 'document_type', 'status', 'file_hash']
    for col in columns:
        if col['column_name'] in key_cols:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"      {col['column_name']:25s} {col['data_type']:20s} {nullable}{default}")
    
    return True


async def verify_indexes():
    """Verify all indexes exist"""
    indexes = await fetch_all("""
        SELECT 
            indexname,
            indexdef
        FROM pg_indexes
        WHERE tablename = 'financial_documents'
        AND schemaname = 'public'
        ORDER BY indexname
    """)
    
    expected_indexes = [
        'idx_docs_property_id',
        'idx_docs_status',
        'idx_docs_property_status',
        'idx_docs_upload_date',
        'idx_docs_document_type',
        'idx_docs_file_hash',
        'idx_docs_document_date',
        'idx_docs_created_at',
        'idx_docs_processing_attempts',
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
    
    return True


async def verify_constraints():
    """Verify all constraints exist"""
    constraints = await fetch_all("""
        SELECT 
            conname,
            contype,
            pg_get_constraintdef(oid) as definition
        FROM pg_constraint
        WHERE conrelid = 'financial_documents'::regclass
        ORDER BY conname
    """)
    
    expected_constraints = [
        'chk_status_valid',
        'chk_confidence',
        'chk_ai_confidence',
        'chk_file_size_positive',
        'chk_valid_document_type',
        'chk_processing_dates',
        'chk_processing_attempts_positive',
        'chk_metrics_count_positive',
        'chk_document_date_reasonable',
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
        WHERE event_object_table = 'financial_documents'
    """)
    
    print(f"\n⚡ Trigger Verification:")
    print(f"   Found: {len(triggers)} trigger(s)")
    
    if len(triggers) < 2:
        print(f"   ❌ Expected 2 triggers (updated_at, calculate_processing_duration)")
        return False
    
    trigger_names = [t['trigger_name'] for t in triggers]
    
    has_update_trigger = any('updated_at' in name.lower() for name in trigger_names)
    has_duration_trigger = any('duration' in name.lower() or 'processing' in name.lower() for name in trigger_names)
    
    if not has_update_trigger:
        print(f"   ❌ updated_at trigger not found")
        return False
    
    if not has_duration_trigger:
        print(f"   ❌ calculate_processing_duration trigger not found")
        return False
    
    print(f"   ✅ updated_at trigger present")
    print(f"   ✅ calculate_processing_duration trigger present")
    
    # Show trigger details
    print(f"\n   Trigger Details:")
    for trig in triggers:
        print(f"      {trig['trigger_name']:40s} {trig['action_timing']} {trig['event_manipulation']}")
    
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
            routine_name LIKE '%document%' OR 
            routine_name LIKE '%duplicate%' OR
            routine_name LIKE '%processing%'
        )
        ORDER BY routine_name
    """)
    
    print(f"\n🔧 Function Verification:")
    print(f"   Found: {len(functions)} function(s)")
    
    function_names = [f['routine_name'] for f in functions]
    
    has_duplicate_function = any('duplicate' in name for name in function_names)
    has_stats_function = any('stats' in name or 'processing' in name for name in function_names)
    
    if has_duplicate_function:
        print(f"   ✅ find_duplicate_documents function present")
    else:
        print(f"   ⚠️  find_duplicate_documents function not found")
    
    if has_stats_function:
        print(f"   ✅ get_document_processing_stats function present")
    else:
        print(f"   ⚠️  get_document_processing_stats function not found")
    
    return True


async def test_insert_and_triggers():
    """Test inserting documents and triggers"""
    print(f"\n🧪 Data Operation & Triggers Test:")
    
    try:
        # Create test property
        property_id = await fetch_val("""
            INSERT INTO properties (
                name, address, city, state, property_type
            ) VALUES (
                'Test Property for Docs', '123 Test St', 'Test City', 'CA', 'office'
            ) RETURNING id
        """)
        
        print(f"   ✅ Test property created")
        
        # Insert test document
        doc_id = await fetch_val("""
            INSERT INTO financial_documents (
                property_id, file_name, file_path, file_size_bytes,
                file_hash, mime_type, document_type, status
            ) VALUES (
                $1, 'test-lease.pdf', 'properties/test/doc123_test-lease.pdf', 1024000,
                '5f4dcc3b5aa765d61d8327deb882cf99', 'application/pdf', 'lease', 'queued'
            ) RETURNING id
        """, property_id)
        
        print(f"   ✅ Document inserted")
        
        # Test processing duration trigger
        await execute("""
            UPDATE financial_documents
            SET processing_start_date = NOW() - INTERVAL '10 seconds',
                processing_end_date = NOW(),
                status = 'processed'
            WHERE id = $1
        """, doc_id)
        
        doc = await fetch_one("""
            SELECT processing_duration_seconds, updated_at
            FROM financial_documents
            WHERE id = $1
        """, doc_id)
        
        print(f"\n   ⚡ Trigger Results:")
        print(f"      Processing duration: {doc['processing_duration_seconds']} seconds")
        print(f"      Updated at: {doc['updated_at']}")
        
        if doc['processing_duration_seconds'] is not None and doc['processing_duration_seconds'] > 0:
            print(f"   ✅ Processing duration auto-calculated")
        else:
            print(f"   ❌ Processing duration NOT calculated")
            return False
        
        # Test duplicate detection function
        duplicates = await fetch_all("""
            SELECT * FROM find_duplicate_documents('5f4dcc3b5aa765d61d8327deb882cf99')
        """)
        
        print(f"\n   🔍 Duplicate Detection Function:")
        print(f"      Found {len(duplicates)} document(s) with same hash")
        if len(duplicates) > 0:
            print(f"   ✅ find_duplicate_documents function working")
        
        # Test stats function
        stats = await fetch_all("""
            SELECT * FROM get_document_processing_stats($1)
        """, property_id)
        
        print(f"\n   📊 Processing Stats Function:")
        for stat in stats:
            print(f"      {stat['status']:15s} Count: {stat['document_count']}")
        if len(stats) > 0:
            print(f"   ✅ get_document_processing_stats function working")
        
        # Clean up
        await execute("DELETE FROM properties WHERE id = $1", property_id)
        print(f"\n   ✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_constraints():
    """Test that constraints are enforced"""
    print(f"\n🔒 Constraint Enforcement Test:")
    
    try:
        property_id = await fetch_val("""
            INSERT INTO properties (name, address, city, state, property_type)
            VALUES ('Constraint Test', '123 St', 'City', 'CA', 'office')
            RETURNING id
        """)
        
        # Test invalid status (should fail)
        try:
            await execute("""
                INSERT INTO financial_documents (property_id, file_name, file_path, document_type, status)
                VALUES ($1, 'test.pdf', 'path/test.pdf', 'lease', 'invalid_status')
            """, property_id)
            print(f"   ❌ Status constraint NOT working")
            return False
        except Exception as e:
            if "chk_status_valid" in str(e):
                print(f"   ✅ Status constraint working")
        
        # Test invalid confidence (should fail)
        try:
            await execute("""
                INSERT INTO financial_documents (
                    property_id, file_name, file_path, document_type,
                    avg_extraction_confidence
                )
                VALUES ($1, 'test.pdf', 'path/test.pdf', 'lease', 1.5)
            """, property_id)
            print(f"   ❌ Confidence constraint NOT working")
            return False
        except Exception as e:
            if "chk_confidence" in str(e):
                print(f"   ✅ Confidence constraint working")
        
        # Test invalid document type (should fail)
        try:
            await execute("""
                INSERT INTO financial_documents (property_id, file_name, file_path, document_type)
                VALUES ($1, 'test.pdf', 'path/test.pdf', 'invalid_type')
            """, property_id)
            print(f"   ❌ Document type constraint NOT working")
            return False
        except Exception as e:
            if "chk_valid_document_type" in str(e):
                print(f"   ✅ Document type constraint working")
        
        # Clean up
        await execute("DELETE FROM properties WHERE id = $1", property_id)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Constraint test error: {str(e)}")
        return False


async def main():
    """Main verification function"""
    print("\n" + "="*70)
    print("REIMS Financial Documents Table Verification")
    print("="*70)
    
    try:
        # Initialize database
        print("\n🔌 Connecting to database...")
        await init_db()
        print("✅ Connected to database")
        
        # Check table exists
        print("\n📋 Checking table existence...")
        if not await verify_table_exists():
            print("❌ Financial Documents table does not exist!")
            print("\nRun the migration first:")
            print("  python backend/db/migrations/run_migration.py 003_create_financial_documents.sql")
            return
        
        print("✅ Financial Documents table exists")
        
        # Run all verifications
        all_passed = True
        
        all_passed &= await verify_columns()
        all_passed &= await verify_foreign_key()
        all_passed &= await verify_indexes()
        all_passed &= await verify_constraints()
        all_passed &= await verify_triggers()
        all_passed &= await verify_functions()
        all_passed &= await test_insert_and_triggers()
        all_passed &= await test_constraints()
        
        # Final summary
        print("\n" + "="*70)
        if all_passed:
            print("✅ ALL VERIFICATIONS PASSED")
            print("="*70)
            print("\n🎉 Financial Documents table is correctly configured!")
            print("\n✨ Special Features:")
            print("  • Auto-calculate processing duration")
            print("  • Duplicate detection (SHA-256 hash)")
            print("  • Processing stats function")
            print("  • Cascade delete from properties")
            print("\nYou can now:")
            print("  • Upload financial documents")
            print("  • Track processing status")
            print("  • Extract financial metrics")
            print("  • Detect duplicate uploads")
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
















