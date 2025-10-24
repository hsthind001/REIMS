import sqlite3

conn = sqlite3.connect("reims.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT id, name, total_units, occupied_units, occupancy_rate
    FROM properties
""")

print("Database values:")
print("="*80)
for row in cursor.fetchall():
    prop_id, name, total_units, occupied_units, occ_rate = row
    print(f"\n{prop_id}: {name}")
    print(f"  total_units: {total_units}")
    print(f"  occupied_units: {occupied_units}")
    print(f"  occupancy_rate (DB): {occ_rate}")
    if total_units and occupied_units:
        calculated = occupied_units / total_units
        print(f"  Calculated (occupied/total): {calculated} ({calculated*100:.1f}%)")
    print(f"  API showing: {occ_rate / 100} (DIVIDED BY 100!)")

conn.close()

