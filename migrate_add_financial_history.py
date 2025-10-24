#!/usr/bin/env python3
"""
Database Migration: Add property_financials_history table
Creates table to track year-over-year financial data for properties
"""

import sqlite3
import os
from datetime import datetime

def create_financial_history_table():
    """Create the property_financials_history table"""
    
    # Connect to database
    db_path = 'reims.db'
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create the property_financials_history table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS property_financials_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER,  -- NULL for annual data
            current_market_value DECIMAL(15, 2),
            monthly_rent DECIMAL(10, 2),
            annual_noi DECIMAL(12, 2),
            occupancy_rate DECIMAL(5, 4),
            total_units INTEGER,
            occupied_units INTEGER,
            data_source TEXT,  -- 'balance_sheet', 'income_statement', 'rent_roll'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (property_id) REFERENCES properties(id),
            UNIQUE(property_id, year, month)
        );
        """
        
        cursor.execute(create_table_sql)
        print("✅ Created property_financials_history table")
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_property_financials_history_property_year 
            ON property_financials_history(property_id, year);
        """)
        print("✅ Created index on property_id and year")
        
        conn.commit()
        print("✅ Database migration completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def verify_table_creation():
    """Verify the table was created correctly"""
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='property_financials_history';
        """)
        result = cursor.fetchone()
        
        if result:
            print("✅ Table 'property_financials_history' exists")
            
            # Get table schema
            cursor.execute("PRAGMA table_info(property_financials_history);")
            columns = cursor.fetchall()
            print(f"📊 Table has {len(columns)} columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            return True
        else:
            print("❌ Table 'property_financials_history' not found")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying table: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 80)
    print("DATABASE MIGRATION: Add Financial History Table")
    print("=" * 80)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create the table
    success = create_financial_history_table()
    
    if success:
        # Verify the table was created
        verify_table_creation()
        print("\n🎯 NEXT STEPS:")
        print("1. Run populate_financial_history.py to populate with existing data")
        print("2. Update backend API to use the new table")
        print("3. Add year-based endpoints to simple_backend.py")
    else:
        print("\n❌ Migration failed. Check the error messages above.")
    
    print(f"🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
