#!/usr/bin/env python3
"""
Database Migration: Add Property Name and Year Columns
Adds metadata columns for property name, document year, type, and period
"""
import sqlite3
import sys
from datetime import datetime

def migrate_database():
    """Add new columns to documents and financial_documents tables"""
    
    print("\n" + "="*70)
    print("DATABASE MIGRATION: Adding Property & Year Columns")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Connect to database
        conn = sqlite3.connect('reims.db')
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(documents)")
        existing_columns = {col[1] for col in cursor.fetchall()}
        print(f"✓ Connected to database")
        print(f"  Existing columns in 'documents': {len(existing_columns)}\n")
        
        # Add columns to documents table
        columns_to_add = {
            'property_name': 'VARCHAR(255)',
            'document_year': 'INTEGER',
            'document_type': 'VARCHAR(100)',
            'document_period': "VARCHAR(50) DEFAULT 'Annual'"
        }
        
        added_count = 0
        skipped_count = 0
        
        print("Migrating 'documents' table:")
        print("-" * 70)
        
        for column_name, column_type in columns_to_add.items():
            if column_name in existing_columns:
                print(f"  ⊘ Skipped '{column_name}' (already exists)")
                skipped_count += 1
            else:
                try:
                    cursor.execute(f"ALTER TABLE documents ADD COLUMN {column_name} {column_type}")
                    print(f"  ✓ Added '{column_name}' ({column_type})")
                    added_count += 1
                except sqlite3.OperationalError as e:
                    print(f"  ⚠ Warning for '{column_name}': {e}")
        
        # Check financial_documents table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='financial_documents'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(financial_documents)")
            fin_doc_columns = {col[1] for col in cursor.fetchall()}
            
            print("\nMigrating 'financial_documents' table:")
            print("-" * 70)
            
            for column_name, column_type in columns_to_add.items():
                if column_name in fin_doc_columns:
                    print(f"  ⊘ Skipped '{column_name}' (already exists)")
                    skipped_count += 1
                else:
                    try:
                        cursor.execute(f"ALTER TABLE financial_documents ADD COLUMN {column_name} {column_type}")
                        print(f"  ✓ Added '{column_name}' ({column_type})")
                        added_count += 1
                    except sqlite3.OperationalError as e:
                        print(f"  ⚠ Warning for '{column_name}': {e}")
        
        # Create indexes for better query performance
        print("\nCreating indexes:")
        print("-" * 70)
        
        indexes = [
            ("idx_documents_property_name", "documents", "property_name"),
            ("idx_documents_year", "documents", "document_year"),
            ("idx_documents_type", "documents", "document_type"),
            ("idx_documents_prop_year", "documents", "property_name, document_year"),
        ]
        
        for index_name, table_name, columns in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({columns})")
                print(f"  ✓ Created index '{index_name}' on {table_name}({columns})")
            except sqlite3.OperationalError as e:
                print(f"  ⊘ Index '{index_name}' already exists or error: {e}")
        
        # Commit changes
        conn.commit()
        
        # Verify changes
        print("\nVerifying migration:")
        print("-" * 70)
        cursor.execute("PRAGMA table_info(documents)")
        final_columns = cursor.fetchall()
        
        print(f"  ✓ Total columns in 'documents': {len(final_columns)}")
        
        # Show new columns
        new_cols = [col for col in final_columns if col[1] in columns_to_add.keys()]
        if new_cols:
            print(f"  ✓ New metadata columns:")
            for col in new_cols:
                print(f"     - {col[1]:<20} {col[2]}")
        
        conn.close()
        
        # Summary
        print("\n" + "="*70)
        print("MIGRATION SUMMARY")
        print("="*70)
        print(f"  ✓ Columns added: {added_count}")
        print(f"  ⊘ Columns skipped (already exist): {skipped_count}")
        print(f"  ✓ Indexes created: {len(indexes)}")
        print("="*70)
        print("\n✅ Migration completed successfully!\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🔄 Starting database migration...")
    success = migrate_database()
    sys.exit(0 if success else 1)



