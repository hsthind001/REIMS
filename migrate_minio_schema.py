#!/usr/bin/env python3
"""
Migrate database to add MinIO integration fields
"""

import sqlite3
from pathlib import Path

def migrate_database():
    print("=== Database Migration: Adding MinIO Fields ===")
    
    db_path = "reims.db"
    if not Path(db_path).exists():
        print(f"❌ Database file {db_path} does not exist")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(documents)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Current columns: {existing_columns}")
        
        # Define new MinIO columns
        minio_columns = [
            "minio_bucket TEXT",
            "minio_object_name TEXT", 
            "minio_url TEXT",
            "storage_type TEXT DEFAULT 'local'",
            "minio_upload_timestamp DATETIME"
        ]
        
        # Add new columns if they don't exist
        added_columns = []
        for column_def in minio_columns:
            column_name = column_def.split()[0]
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE documents ADD COLUMN {column_def}")
                    added_columns.append(column_name)
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    print(f"❌ Failed to add {column_name}: {e}")
        
        if added_columns:
            conn.commit()
            print(f"\n✅ Migration completed! Added {len(added_columns)} columns:")
            for col in added_columns:
                print(f"   - {col}")
        else:
            print("ℹ️ No migration needed - all columns already exist")
        
        # Verify the new schema
        cursor.execute("PRAGMA table_info(documents)")
        new_columns = cursor.fetchall()
        print(f"\n📋 Updated schema ({len(new_columns)} columns):")
        for col in new_columns:
            col_name = col[1]
            col_type = col[2]
            default_val = col[4]
            print(f"   - {col_name} ({col_type})" + (f" DEFAULT {default_val}" if default_val else ""))
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def verify_migration():
    print("\n=== Verifying Migration ===")
    
    try:
        conn = sqlite3.connect("reims.db")
        cursor = conn.cursor()
        
        # Test query with new columns
        cursor.execute("""
            SELECT document_id, original_filename, property_id, storage_type, minio_bucket
            FROM documents 
            LIMIT 3
        """)
        
        results = cursor.fetchall()
        print(f"✅ Migration verified - can query new columns")
        print(f"📄 Sample data ({len(results)} records):")
        
        for row in results:
            print(f"   - {row[1]} (Property: {row[2]}, Storage: {row[3] or 'local'})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    if migrate_database():
        verify_migration()
    else:
        print("Migration failed - cannot proceed with verification")