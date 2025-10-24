"""
Fix ESP Property Name

Updates the ESP property name from "Empire State Plaza" to "Eastern Shore Plaza"
based on audit results showing documents consistently use "Eastern Shore Plaza".
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)

def fix_esp_property_name():
    """Fix ESP property name and aliases"""
    
    try:
        conn = sqlite3.connect('reims.db')
        cursor = conn.cursor()
        
        # Check current property name
        cursor.execute('SELECT id, name FROM properties WHERE id = 1')
        current = cursor.fetchone()
        print(f'Current property 1 name: {current[1]}')
        
        # Update to Eastern Shore Plaza
        cursor.execute('UPDATE properties SET name = ? WHERE id = 1', ('Eastern Shore Plaza',))
        print('✅ Updated property name to "Eastern Shore Plaza"')
        
        # Fix aliases - Eastern Shore Plaza should be primary
        cursor.execute('''
            UPDATE property_name_aliases 
            SET is_primary = 1, alias_type = 'primary' 
            WHERE property_id = 1 AND alias_name = 'Eastern Shore Plaza'
        ''')
        
        # Empire State Plaza should be historical
        cursor.execute('''
            UPDATE property_name_aliases 
            SET is_primary = 0, alias_type = 'historical' 
            WHERE property_id = 1 AND alias_name = 'Empire State Plaza'
        ''')
        
        # Verify the change
        cursor.execute('SELECT id, name FROM properties WHERE id = 1')
        updated = cursor.fetchone()
        print(f'Updated property 1 name: {updated[1]}')
        
        # Check aliases
        cursor.execute('''
            SELECT alias_name, alias_type, is_primary 
            FROM property_name_aliases 
            WHERE property_id = 1 
            ORDER BY is_primary DESC, alias_type
        ''')
        aliases = cursor.fetchall()
        
        print('Final aliases for property 1:')
        for alias in aliases:
            primary_status = "PRIMARY" if alias[2] else "alias"
            print(f'  {alias[0]} ({alias[1]}) - {primary_status}')
        
        conn.commit()
        conn.close()
        
        print('✅ ESP property name and aliases fixed successfully')
        return True
        
    except Exception as e:
        logger.error(f"Error fixing ESP property name: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = fix_esp_property_name()
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Restart the backend to pick up the changes")
        print("2. Check the frontend to verify the name displays correctly")
        print("3. Run validation to ensure all ESP documents now match")
    else:
        print("❌ Failed to fix ESP property name")
