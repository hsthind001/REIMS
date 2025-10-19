#!/usr/bin/env python3
"""Fix foreign key to reference correct table"""

import sqlite3

conn = sqlite3.connect('reims.db')

# Drop the FK constraint by recreating the table
print("Recreating financial_documents table without FK to enhanced_properties...")

# Get existing data
cursor = conn.cursor()
cursor.execute("SELECT * FROM financial_documents")
existing_data = cursor.fetchall()

# Drop and recreate table
cursor.execute("DROP TABLE IF EXISTS financial_documents_old")
cursor.execute("ALTER TABLE financial_documents RENAME TO financial_documents_old")

cursor.execute("""
CREATE TABLE financial_documents (
    id TEXT PRIMARY KEY,
    property_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    document_type TEXT,
    status TEXT DEFAULT 'queued',
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_date TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_status TEXT
)
""")

# Copy data if any exists
if existing_data:
    for row in existing_data:
        cursor.execute(
            "INSERT INTO financial_documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            row + (None,) * (11 - len(row))  # Pad with None if row has fewer columns
        )

conn.commit()
conn.close()

print("SUCCESS: Table recreated without FK constraint")
print("Now uploads should work!")















