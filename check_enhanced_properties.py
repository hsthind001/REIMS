import sqlite3

conn = sqlite3.connect('backend/reims.db')
cursor = conn.cursor()

# Check enhanced_properties table
cursor.execute("PRAGMA table_info(enhanced_properties)")
columns = cursor.fetchall()
print("Enhanced Properties table columns:")
for col in columns:
    print(f"- {col[1]} ({col[2]})")

print("\n" + "="*50)

# Get data from enhanced_properties
cursor.execute("SELECT * FROM enhanced_properties LIMIT 5")
properties = cursor.fetchall()
print(f"Enhanced Properties table has {len(properties)} records:")
for prop in properties:
    print(f"ID: {prop[0]}, Name: {prop[1]}, Address: {prop[2]}, Acquisition Cost: {prop[4]}, Current Value: {prop[5]}")

conn.close()
