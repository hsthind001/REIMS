import sqlite3
conn = sqlite3.connect('reims.db')
cursor = conn.cursor()

print("Properties table schema:")
cursor.execute("PRAGMA table_info(properties)")
for row in cursor.fetchall():
    print(f"  {row[1]} ({row[2]})")

print("\nExtracted_metrics table schema:")
cursor.execute("PRAGMA table_info(extracted_metrics)")
for row in cursor.fetchall():
    print(f"  {row[1]} ({row[2]})")

conn.close()

