import sqlite3

conn = sqlite3.connect('reims.db')
cur = conn.cursor()

# Check stores count
cur.execute('SELECT COUNT(*) FROM stores')
stores_count = cur.fetchone()[0]
print(f'Total stores/units in database: {stores_count}')

if stores_count > 0:
    # Check stores by property
    cur.execute('''
        SELECT property_id, 
               COUNT(*) as total_units,
               SUM(CASE WHEN status="occupied" THEN 1 ELSE 0 END) as occupied_units
        FROM stores 
        GROUP BY property_id
    ''')
    
    print('\nOccupancy data from stores table:')
    for row in cur.fetchall():
        prop_id, total, occupied = row
        occupancy_rate = (occupied / total * 100) if total > 0 else 0
        print(f'  Property ID {prop_id}: {occupied}/{total} occupied ({occupancy_rate:.1f}%)')
    
    # Get property names
    cur.execute('''
        SELECT p.id, p.name, COUNT(s.id) as units, 
               SUM(CASE WHEN s.status="occupied" THEN 1 ELSE 0 END) as occupied
        FROM properties p
        LEFT JOIN stores s ON p.id = s.property_id
        GROUP BY p.id, p.name
        HAVING COUNT(s.id) > 0
    ''')
    
    print('\nProperties with stores:')
    for row in cur.fetchall():
        prop_id, name, total, occupied = row
        occupied = occupied or 0
        occupancy_rate = (occupied / total * 100) if total > 0 else 0
        print(f'  {name}: {occupied}/{total} occupied ({occupancy_rate:.1f}%)')
else:
    print('\nNo stores/units data found in database.')
    print('This explains why occupancy rate is hardcoded.')

conn.close()

