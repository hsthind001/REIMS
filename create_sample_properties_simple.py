import sqlite3
from datetime import datetime
import json

# Connect to database
conn = sqlite3.connect('backend/reims.db')
cursor = conn.cursor()

# Clear existing data
cursor.execute("DELETE FROM properties")

# Create sample properties with the current schema
sample_properties = [
    {
        'id': 1,
        'property_id': 'Empire State Plaza',
        'address': '1 Empire State Plaza, Albany, NY 12242',
        'property_type': 'office',
        'value': 125000000,  # $125M
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        'property_metadata': json.dumps({
            'purchase_price': 100000000,
            'purchase_date': '2018-03-15',
            'noi': 10000000,
            'occupancy_rate': 0.92,
            'square_footage': 2500000,
            'year_built': 1973
        })
    },
    {
        'id': 2,
        'property_id': 'Wendover Commons',
        'address': '123 Wendover Drive, Albany, NY 12205',
        'property_type': 'retail',
        'value': 12000000,  # $12M
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        'property_metadata': json.dumps({
            'purchase_price': 8500000,
            'purchase_date': '2020-06-01',
            'noi': 960000,
            'occupancy_rate': 0.88,
            'square_footage': 45000,
            'year_built': 1995
        })
    }
]

# Insert sample properties
for prop in sample_properties:
    cursor.execute("""
        INSERT INTO properties (
            id, property_id, address, property_type, value, 
            created_at, updated_at, property_metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        prop['id'], prop['property_id'], prop['address'], prop['property_type'],
        prop['value'], prop['created_at'], prop['updated_at'], prop['property_metadata']
    ))

# Commit changes
conn.commit()

# Verify insertion
cursor.execute("SELECT COUNT(*) FROM properties")
count = cursor.fetchone()[0]
print(f"Inserted {count} properties")

cursor.execute("SELECT id, property_id, value FROM properties")
properties = cursor.fetchall()
print("Properties in database:")
for prop in properties:
    print(f"  ID: {prop[0]}, Name: {prop[1]}, Value: ${prop[2]:,}")

conn.close()
print("Sample properties created successfully!")
