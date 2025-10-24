#!/usr/bin/env python3
"""
Create year-based financial schema for REIMS
"""

import sqlite3
import json
from datetime import datetime

def create_year_schema():
    """Create the property_financials_history table and add year columns to documents"""
    
    conn = sqlite3.connect("reims.db")
    cursor = conn.cursor()
    
    try:
        # 1. Create property_financials_history table
        print("Creating property_financials_history table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS property_financials_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                fiscal_year INTEGER NOT NULL,
                is_partial_year BOOLEAN DEFAULT FALSE,
                data_through_date DATE,
                
                -- Financial Metrics
                current_market_value DECIMAL(15, 2),
                monthly_rent DECIMAL(10, 2),
                annual_noi DECIMAL(12, 2),
                occupancy_rate DECIMAL(5, 4),
                total_units INTEGER,
                occupied_units INTEGER,
                
                -- Data Source & Metadata
                data_source VARCHAR(100),
                document_ids TEXT,
                confidence_score DECIMAL(3, 2),
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Constraints
                UNIQUE(property_id, fiscal_year),
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        """)
        
        # 2. Create indexes
        print("Creating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_financials_property_year 
            ON property_financials_history(property_id, fiscal_year)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_financials_year 
            ON property_financials_history(fiscal_year)
        """)
        
        # 3. Add year columns to documents table
        print("Adding year columns to documents table...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(documents)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'fiscal_year' not in columns:
            cursor.execute("ALTER TABLE documents ADD COLUMN fiscal_year INTEGER")
            print("Added fiscal_year column")
        else:
            print("fiscal_year column already exists")
            
        if 'is_partial_year' not in columns:
            cursor.execute("ALTER TABLE documents ADD COLUMN is_partial_year BOOLEAN DEFAULT FALSE")
            print("Added is_partial_year column")
        else:
            print("is_partial_year column already exists")
            
        if 'document_period' not in columns:
            cursor.execute("ALTER TABLE documents ADD COLUMN document_period VARCHAR(50)")
            print("Added document_period column")
        else:
            print("document_period column already exists")
        
        # 4. Create documents year index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_documents_year 
            ON documents(property_id, fiscal_year)
        """)
        
        conn.commit()
        print("✅ Database schema updated successfully!")
        
        # 5. Show current tables
        print("\nCurrent tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
            
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_year_schema()
