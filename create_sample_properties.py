import sqlite3
from datetime import datetime, date

# Connect to database
conn = sqlite3.connect('backend/reims.db')
cursor = conn.cursor()

# Create sample properties with the expected schema
sample_properties = [
    {
        'id': 1,
        'name': 'Empire State Plaza',
        'address': '1 Empire State Plaza, Albany, NY 12242',
        'city': 'Albany',
        'state': 'NY',
        'zip_code': '12242',
        'property_type': 'office',
        'property_class': 'A',
        'total_sqft': 2500000,
        'year_built': 1973,
        'acquisition_cost': 85000000,
        'acquisition_date': '2018-03-15',
        'current_value': 125000000,
        'monthly_rent': 850000,
        'noi': 10200000,  # Annual NOI
        'dscr': 1.45,
        'occupancy_rate': 0.92,
        'status': 'active',
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    },
    {
        'id': 2,
        'name': 'Wendover Commons',
        'address': '123 Wendover Drive, Albany, NY 12205',
        'city': 'Albany',
        'state': 'NY',
        'zip_code': '12205',
        'property_type': 'retail',
        'property_class': 'B',
        'total_sqft': 45000,
        'year_built': 1995,
        'acquisition_cost': 8500000,
        'acquisition_date': '2020-06-01',
        'current_value': 12000000,
        'monthly_rent': 45000,
        'noi': 540000,  # Annual NOI
        'dscr': 1.35,
        'occupancy_rate': 0.88,
        'status': 'active',
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
]

# Clear existing data
cursor.execute("DELETE FROM properties")

# Insert sample properties
for prop in sample_properties:
    cursor.execute("""
        INSERT INTO properties (
            id, name, address, city, state, zip_code, property_type, property_class,
            total_sqft, year_built, acquisition_cost, acquisition_date, current_value,
            monthly_rent, noi, dscr, occupancy_rate, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        prop['id'], prop['name'], prop['address'], prop['city'], prop['state'],
        prop['zip_code'], prop['property_type'], prop['property_class'],
        prop['total_sqft'], prop['year_built'], prop['acquisition_cost'],
        prop['acquisition_date'], prop['current_value'], prop['monthly_rent'],
        prop['noi'], prop['dscr'], prop['occupancy_rate'], prop['status'],
        prop['created_at'], prop['updated_at']
    ))

# Commit changes
conn.commit()

# Verify insertion
cursor.execute("SELECT COUNT(*) FROM properties")
count = cursor.fetchone()[0]
print(f"Inserted {count} properties")

cursor.execute("SELECT id, name, current_value, noi FROM properties")
properties = cursor.fetchall()
print("Properties in database:")
for prop in properties:
    print(f"  ID: {prop[0]}, Name: {prop[1]}, Value: ${prop[2]:,}, NOI: ${prop[3]:,}")

conn.close()
print("Sample properties created successfully!")
