#!/usr/bin/env python3
"""
Database migration to add created_at column to processing_jobs table
"""
import sys
import os
import sqlite3
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

def migrate_database():
    print("Migrating database...")
    
    # Connect to SQLite database
    db_path = "reims.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check if created_at column exists
            cursor.execute("PRAGMA table_info(processing_jobs)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'created_at' not in columns:
                print("Adding created_at column to processing_jobs table...")
                
                # Add the column without default value first
                cursor.execute("""
                    ALTER TABLE processing_jobs 
                    ADD COLUMN created_at DATETIME
                """)
                
                # Update existing records with current timestamp
                current_time = datetime.now().isoformat()
                cursor.execute("""
                    UPDATE processing_jobs 
                    SET created_at = ? 
                    WHERE created_at IS NULL
                """, (current_time,))
                
                conn.commit()
                print("✓ Successfully added created_at column")
            else:
                print("✓ created_at column already exists")
                
            # Verify the column exists
            cursor.execute("PRAGMA table_info(processing_jobs)")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"  Processing jobs columns: {columns}")
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
            
        return True
    else:
        print("Database file doesn't exist yet - will be created with correct schema")
        return True

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\n🎉 Database migration completed!")
    else:
        print("\n❌ Database migration failed!")