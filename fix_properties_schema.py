import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('backend/reims.db')
cursor = conn.cursor()

# Step 1: Add missing columns
print("Adding missing columns to properties table...")
columns_to_add = [
    ('name', 'VARCHAR(255)'),
    ('city', 'VARCHAR(100)'),
    ('state', 'VARCHAR(50)'),
    ('zip_code', 'VARCHAR(20)'),
    ('square_footage', 'DECIMAL(10,2)'),
    ('purchase_price', 'DECIMAL(12,2)'),
    ('current_market_value', 'DECIMAL(12,2)'),
    ('monthly_rent', 'DECIMAL(10,2)'),
    ('year_built', 'INTEGER'),
    ('noi', 'DECIMAL(12,2)'),
    ('occupancy_rate', 'DECIMAL(3,2)'),
    ('dscr', 'DECIMAL(5,2)'),
    ('purchase_date', 'DATE')
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f'ALTER TABLE properties ADD COLUMN {col_name} {col_type}')
        print(f'  Added: {col_name}')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print(f'  Exists: {col_name}')
        else:
            print(f'  Error: {col_name} - {e}')

conn.commit()

# Step 2: Migrate data from metadata to columns
print("\nMigrating data from metadata to columns...")
cursor.execute('SELECT id, property_id, address, value, property_metadata FROM properties')
properties = cursor.fetchall()

for prop in properties:
    prop_id, name, address, value, metadata_json = prop
    
    # Parse metadata
    metadata = json.loads(metadata_json) if metadata_json else {}
    
    # Parse address to extract city and state
    address_parts = address.split(',')
    city = address_parts[1].strip() if len(address_parts) > 1 else 'Albany'
    state = address_parts[2].strip().split()[0] if len(address_parts) > 2 else 'NY'
    zip_code = address_parts[2].strip().split()[1] if len(address_parts) > 2 and len(address_parts[2].strip().split()) > 1 else ''
    
    # Update property with all fields
    cursor.execute('''
        UPDATE properties SET
            name = ?,
            city = ?,
            state = ?,
            zip_code = ?,
            square_footage = ?,
            purchase_price = ?,
            current_market_value = ?,
            monthly_rent = ?,
            year_built = ?,
            noi = ?,
            occupancy_rate = ?,
            dscr = ?,
            purchase_date = ?
        WHERE id = ?
    ''', (
        name,
        city,
        state,
        zip_code,
        metadata.get('square_footage', 0),
        metadata.get('purchase_price', value * 0.8),
        value,
        metadata.get('noi', 0) / 12 if metadata.get('noi') else 0,  # Monthly rent from annual NOI
        metadata.get('year_built', 2024),
        metadata.get('noi', value * 0.08),
        metadata.get('occupancy_rate', 0.95),
        1.5,  # Default DSCR
        metadata.get('purchase_date', '2020-01-01'),
        prop_id
    ))
    
    print(f'  Updated: {name}')

conn.commit()

# Step 3: Verify migration
print("\nVerifying migration...")
cursor.execute('SELECT id, name, city, state, current_market_value, noi, occupancy_rate FROM properties')
updated_properties = cursor.fetchall()

for prop in updated_properties:
    print(f'  {prop[1]}: Value=${prop[4]:,.0f}, NOI=${prop[5]:,.0f}, Occupancy={prop[6]:.0%}')

conn.close()
print("\nMigration complete!")
