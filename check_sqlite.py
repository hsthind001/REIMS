import sqlite3
import os

if os.path.exists('reims.db'):
    print("⚠️  Found SQLite database: reims.db")
    print("   Backend is using SQLite instead of PostgreSQL!\n")
    
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    # Count documents
    cursor.execute('SELECT COUNT(*) FROM documents')
    count = cursor.fetchone()[0]
    print(f"📊 Documents in SQLite: {count}")
    
    # Show recent documents
    cursor.execute('SELECT filename, status, upload_date FROM documents ORDER BY upload_date DESC LIMIT 10')
    rows = cursor.fetchall()
    
    if rows:
        print("\n✅ Recent uploads in SQLite:")
        for row in rows:
            print(f"   • {row[0]} - Status: {row[1]} - Uploaded: {row[2]}")
    
    conn.close()
else:
    print("✅ No SQLite database found")














