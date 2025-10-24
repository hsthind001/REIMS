import sqlite3

conn = sqlite3.connect("reims.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT id, name, address, city, state, square_footage, 
           purchase_price, current_market_value, monthly_rent, 
           year_built, property_type, status, annual_noi, created_at,
           total_units, occupied_units, occupancy_rate
    FROM properties
""")

row = cursor.fetchone()
print(f"Row data: {row}")
print(f"\nColumn indices:")
print(f"  [0] id: {row[0]}")
print(f"  [15] occupancy_rate (should be): {row[16] if len(row) > 16 else 'NOT FOUND'}")
print(f"  [16] occupancy_rate (actual): {row[16] if len(row) > 16 else 'Column 16 does not exist'}")
print(f"  Row length: {len(row)}")

# Check what column 15 actually contains
if len(row) > 15:
    print(f"\n  Column 15 contains: {row[15]} (should be occupied_units)")
    print(f"  Column 16 contains: {row[16] if len(row) > 16 else 'N/A'} (should be occupancy_rate)")

conn.close()

