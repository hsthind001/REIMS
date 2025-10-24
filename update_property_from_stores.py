"""
Update property occupancy to match actual stores table data
"""

import sqlite3

conn = sqlite3.connect('reims.db')
cursor = conn.cursor()

print("=" * 80)
print("SYNCING PROPERTY OCCUPANCY WITH STORES TABLE")
print("=" * 80)

# Count from stores table
cursor.execute("SELECT COUNT(*) as total FROM stores WHERE property_id = 3")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) as occupied FROM stores WHERE property_id = 3 AND status = 'occupied'")
occupied = cursor.fetchone()[0]

occupancy_rate = (occupied / total * 100) if total > 0 else 0

print(f"\nStores table data:")
print(f"  Total units: {total}")
print(f"  Occupied: {occupied}")
print(f"  Vacant: {total - occupied}")
print(f"  Occupancy rate: {occupancy_rate:.1f}%")

# Update properties table
cursor.execute("""
    UPDATE properties
    SET total_units = ?,
        occupied_units = ?,
        occupancy_rate = ?,
        updated_at = datetime('now')
    WHERE id = 3
""", (total, occupied, occupancy_rate))

conn.commit()

print(f"\n✓ Updated properties table to match stores data")

# Verify
cursor.execute("SELECT total_units, occupied_units, occupancy_rate FROM properties WHERE id = 3")
prop = cursor.fetchone()

print(f"\nProperties table now shows:")
print(f"  Total units: {prop[0]}")
print(f"  Occupied: {prop[1]}")
print(f"  Occupancy rate: {prop[2]}%")

conn.close()

print("\n" + "=" * 80)
print("SYNC COMPLETE")
print("=" * 80)

