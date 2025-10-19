import sqlite3

conn = sqlite3.connect('reims.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Available tables:")
for table in tables:
    print(f"- {table[0]}")

print("\n" + "="*50)

# Check properties table
cursor.execute("SELECT * FROM properties LIMIT 5")
properties = cursor.fetchall()
print(f"Properties table has {len(properties)} records:")
for prop in properties:
    print(f"ID: {prop[0]}, Property ID: {prop[1]}, Address: {prop[2]}, Type: {prop[3]}, Value: {prop[4]}")

conn.close()
