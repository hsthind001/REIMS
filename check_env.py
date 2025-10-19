#!/usr/bin/env python3
"""Check environment variables and database connection"""

import os
from dotenv import load_dotenv

print("\n" + "="*70)
print("🔍 ENVIRONMENT VARIABLE DIAGNOSTIC")
print("="*70)

# Check environment BEFORE load_dotenv
print("\n1️⃣  BEFORE load_dotenv():")
print(f"   DATABASE_URL from os.environ: {os.environ.get('DATABASE_URL', 'NOT SET')}")

# Load .env file
print("\n2️⃣  Loading .env file...")
load_dotenv()

# Check environment AFTER load_dotenv
print("\n3️⃣  AFTER load_dotenv():")
print(f"   DATABASE_URL from os.getenv(): {os.getenv('DATABASE_URL', 'NOT SET')}")

# Determine which database
db_url = os.getenv('DATABASE_URL', 'NOT SET')
if 'postgresql' in db_url:
    print("\n✅ CONFIGURED TO USE: PostgreSQL")
    print(f"   Connection string: {db_url}")
elif 'sqlite' in db_url:
    print("\n⚠️  CONFIGURED TO USE: SQLite")
    print(f"   Database file: {db_url}")
else:
    print("\n❌ DATABASE NOT CONFIGURED")

print("\n" + "="*70)

# Test actual connection
print("\n4️⃣  Testing database connection...")
try:
    from backend.database import engine, DATABASE_URL
    print(f"   backend.database.DATABASE_URL: {DATABASE_URL}")
    
    with engine.connect() as conn:
        # Check if it's PostgreSQL or SQLite
        try:
            result = conn.execute("SELECT version();")
            version = result.fetchone()[0]
            print(f"\n✅ CONNECTED TO: PostgreSQL")
            print(f"   Version: {version[:50]}...")
        except:
            print(f"\n⚠️  CONNECTED TO: SQLite")
            import sqlite3
            conn_sqlite = sqlite3.connect('reims.db')
            cursor = conn_sqlite.cursor()
            cursor.execute('SELECT COUNT(*) FROM documents')
            count = cursor.fetchone()[0]
            print(f"   Documents in SQLite: {count}")
            conn_sqlite.close()
            
except Exception as e:
    print(f"\n❌ CONNECTION FAILED: {e}")

print("\n" + "="*70 + "\n")














