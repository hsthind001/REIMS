"""
Create Property Name Validation Database Schema

Creates the necessary database tables for property name validation system:
- property_name_validations: Stores validation results
- property_name_aliases: Stores property name aliases and abbreviations
"""

import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def create_validation_tables(db_path: str = "reims.db"):
    """Create validation system database tables"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create property_name_validations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS property_name_validations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                property_id INTEGER NOT NULL,
                
                -- Extracted Information
                extracted_name VARCHAR(255),
                database_name VARCHAR(255),
                extraction_method VARCHAR(50), -- 'pdf_header', 'filename', 'manual'
                
                -- Validation Results
                match_score DECIMAL(3, 2), -- 0.00-1.00
                validation_status VARCHAR(20), -- 'exact', 'fuzzy', 'mismatch', 'pending'
                
                -- Resolution
                resolution_action VARCHAR(50), -- 'approved', 'corrected', 'manual_review'
                corrected_name VARCHAR(255),
                reviewed_by VARCHAR(100),
                reviewed_at TIMESTAMP,
                
                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        """)
        
        # Create property_name_aliases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS property_name_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                alias_name VARCHAR(255) NOT NULL UNIQUE,
                alias_type VARCHAR(50), -- 'abbreviation', 'common_name', 'historical', 'legal'
                is_primary BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_validations_property_id 
            ON property_name_validations(property_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_validations_status 
            ON property_name_validations(validation_status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_validations_created_at 
            ON property_name_validations(created_at)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_aliases_property_id 
            ON property_name_aliases(property_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_aliases_alias_name 
            ON property_name_aliases(alias_name)
        """)
        
        # Commit changes
        conn.commit()
        
        logger.info("✅ Validation tables created successfully")
        
        # Populate with known aliases
        populate_known_aliases(cursor)
        
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating validation tables: {e}")
        return False

def populate_known_aliases(cursor):
    """Populate aliases table with known property aliases"""
    
    # Get current properties
    cursor.execute("SELECT id, name FROM properties")
    properties = cursor.fetchall()
    
    # Known aliases mapping
    known_aliases = {
        'Empire State Plaza': [
            ('ESP', 'abbreviation'),
            ('Eastern Shore Plaza', 'historical'),
            ('Eastern Shore', 'common_name'),
        ],
        'The Crossings of Spring Hill': [
            ('TCSH', 'abbreviation'),
            ('The Crossings', 'common_name'),
            ('Crossings of Spring Hill', 'common_name'),
            ('Spring Hill Crossings', 'common_name'),
        ],
        'Hammond Aire': [
            ('HA', 'abbreviation'),
            ('Hammond', 'common_name'),
        ],
        'Wendover Commons': [
            ('WC', 'abbreviation'),
            ('Wendover', 'common_name'),
        ],
    }
    
    try:
        for property_id, property_name in properties:
            # Insert primary name as alias
            cursor.execute("""
                INSERT OR IGNORE INTO property_name_aliases 
                (property_id, alias_name, alias_type, is_primary)
                VALUES (?, ?, 'primary', TRUE)
            """, (property_id, property_name))
            
            # Insert known aliases
            if property_name in known_aliases:
                for alias_name, alias_type in known_aliases[property_name]:
                    cursor.execute("""
                        INSERT OR IGNORE INTO property_name_aliases 
                        (property_id, alias_name, alias_type, is_primary)
                        VALUES (?, ?, ?, FALSE)
                    """, (property_id, alias_name, alias_type))
        
        logger.info("✅ Known aliases populated successfully")
        
    except Exception as e:
        logger.error(f"❌ Error populating aliases: {e}")

def verify_validation_tables(db_path: str = "reims.db"):
    """Verify that validation tables were created correctly"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('property_name_validations', 'property_name_aliases')
        """)
        
        tables = cursor.fetchall()
        
        if len(tables) != 2:
            logger.error(f"❌ Expected 2 tables, found {len(tables)}")
            return False
        
        # Check table structures
        cursor.execute("PRAGMA table_info(property_name_validations)")
        validations_columns = cursor.fetchall()
        
        cursor.execute("PRAGMA table_info(property_name_aliases)")
        aliases_columns = cursor.fetchall()
        
        logger.info(f"✅ property_name_validations: {len(validations_columns)} columns")
        logger.info(f"✅ property_name_aliases: {len(aliases_columns)} columns")
        
        # Check alias data
        cursor.execute("SELECT COUNT(*) FROM property_name_aliases")
        alias_count = cursor.fetchone()[0]
        logger.info(f"✅ {alias_count} aliases loaded")
        
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verifying tables: {e}")
        return False

def get_validation_summary(db_path: str = "reims.db"):
    """Get summary of validation system status"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if validation tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='property_name_validations'
        """)
        
        if not cursor.fetchone():
            return {
                'validation_tables': False,
                'aliases_count': 0,
                'validations_count': 0
            }
        
        # Get validation counts
        cursor.execute("SELECT COUNT(*) FROM property_name_validations")
        validations_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM property_name_aliases")
        aliases_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'validation_tables': True,
            'aliases_count': aliases_count,
            'validations_count': validations_count
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting validation summary: {e}")
        return {
            'validation_tables': False,
            'aliases_count': 0,
            'validations_count': 0
        }

if __name__ == "__main__":
    import sys
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else "reims.db"
    
    print(f"🔧 Creating validation schema for database: {db_path}")
    
    # Create tables
    success = create_validation_tables(db_path)
    
    if success:
        print("✅ Validation schema created successfully")
        
        # Verify tables
        if verify_validation_tables(db_path):
            print("✅ Validation tables verified")
        else:
            print("❌ Validation table verification failed")
        
        # Show summary
        summary = get_validation_summary(db_path)
        print(f"📊 Validation Summary:")
        print(f"   Tables created: {summary['validation_tables']}")
        print(f"   Aliases loaded: {summary['aliases_count']}")
        print(f"   Validations: {summary['validations_count']}")
        
    else:
        print("❌ Failed to create validation schema")
        sys.exit(1)
