#!/usr/bin/env python3
"""Add missing columns to financial_documents table"""

import sqlite3

conn = sqlite3.connect('reims.db')
cursor = conn.cursor()

# Add missing columns
try:
    cursor.execute("ALTER TABLE financial_documents ADD COLUMN file_name TEXT")
    print("Added file_name column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("file_name column already exists")
    else:
        print(f"Error adding file_name: {e}")

try:
    cursor.execute("ALTER TABLE financial_documents ADD COLUMN status TEXT DEFAULT 'queued'")
    print("Added status column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("status column already exists")
    else:
        print(f"Error adding status: {e}")

try:
    cursor.execute("ALTER TABLE financial_documents ADD COLUMN processing_date TIMESTAMP")
    print("Added processing_date column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("processing_date column already exists")
    else:
        print(f"Error adding processing_date: {e}")

try:
    cursor.execute("ALTER TABLE financial_documents ADD COLUMN error_message TEXT")
    print("Added error_message column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("error_message column already exists")
    else:
        print(f"Error adding error_message: {e}")

try:
    cursor.execute("ALTER TABLE financial_documents ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    print("Added created_at column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("created_at column already exists")
    else:
        print(f"Error adding created_at: {e}")

conn.commit()

# Show current schema
cursor.execute("PRAGMA table_info(financial_documents)")
cols = cursor.fetchall()
print("\nUpdated columns:")
for col in cols:
    print(f"  - {col[1]} ({col[2]})")

conn.close()
print("\nSuccess! Table updated.")















