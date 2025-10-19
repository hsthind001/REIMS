#!/usr/bin/env python3
"""
Clear Sample Data from REIMS Database
Removes all sample/test data while preserving table structures
"""

import sqlite3
from datetime import datetime

def clear_sample_data(db_path='reims.db'):
    """Delete all sample data from database tables"""
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║          🗑️  CLEARING SAMPLE DATA FROM REIMS DATABASE 🗑️            ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    # Tables to clear (order matters due to foreign keys)
    tables_to_clear = [
        # Delete child records first (foreign key constraints)
        'rent_payments',
        'maintenance_requests',
        'property_documents',
        'financial_transactions',
        'leases',
        'tenants',
        'processing_jobs',
        'extracted_data',
        'processed_data',
        'financial_documents',
        'documents',
        'properties',
        'enhanced_properties',
        'users',
        'stores',
        'property_costs',
        'committee_alerts',
        'audit_log',
        'anomalies',
        'market_analysis',
        'exit_strategy_analysis',
        'extracted_metrics',
        'workflow_locks'
    ]
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Disable foreign key constraints temporarily
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        print(f"📊 Database: {db_path}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        deleted_summary = []
        total_deleted = 0
        
        print("🗑️  Deleting data from tables:\n")
        
        for table in tables_to_clear:
            try:
                # Get count before deletion
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count_before = cursor.fetchone()[0]
                
                if count_before > 0:
                    # Delete all records
                    cursor.execute(f"DELETE FROM {table}")
                    deleted_summary.append(f"  ✅ {table}: {count_before} records deleted")
                    total_deleted += count_before
                else:
                    deleted_summary.append(f"  ⏭️  {table}: already empty")
                    
            except sqlite3.OperationalError as e:
                # Table might not exist
                deleted_summary.append(f"  ⚠️  {table}: {str(e)}")
        
        # Reset auto-increment sequences
        print("\n🔄 Resetting auto-increment sequences...\n")
        cursor.execute("DELETE FROM sqlite_sequence")
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Commit all changes
        conn.commit()
        
        # Print summary
        print("\n" + "="*70)
        print("📋 DELETION SUMMARY")
        print("="*70 + "\n")
        
        for line in deleted_summary:
            print(line)
        
        print("\n" + "="*70)
        print(f"✅ Total records deleted: {total_deleted}")
        print("="*70 + "\n")
        
        # Verify all tables are empty
        print("🔍 Verification - Checking table counts:\n")
        
        for table in tables_to_clear:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                status = "✅" if count == 0 else "❌"
                print(f"  {status} {table}: {count} records")
            except:
                pass
        
        print("\n╔══════════════════════════════════════════════════════════════════════╗")
        print("║          ✅ DATABASE CLEANUP COMPLETE! ✅                            ║")
        print("╚══════════════════════════════════════════════════════════════════════╝\n")
        
        print("🎯 Database is now ready for fresh test uploads!\n")
        print("📝 Next steps:")
        print("  1. Upload test files through the frontend or API")
        print("  2. Verify end-to-end functionality")
        print("  3. Check data in database and MinIO\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error clearing database: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    clear_sample_data()

