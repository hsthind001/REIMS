#!/usr/bin/env python3
"""
Create the required tables for file upload functionality
"""

import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('reims.db')
cursor = conn.cursor()

# Create financial_documents table
print("Creating financial_documents table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS financial_documents (
    id TEXT PRIMARY KEY,
    property_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    document_type TEXT,
    status TEXT DEFAULT 'queued',
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_date TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Create extracted_metrics table
print("Creating extracted_metrics table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS extracted_metrics (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    property_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL,
    confidence_score REAL,
    extraction_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES financial_documents(id),
    FOREIGN KEY (property_id) REFERENCES properties(id)
)
""")

# Create committee_alerts table (if it doesn't exist)
print("Creating committee_alerts table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS committee_alerts (
    id TEXT PRIMARY KEY,
    property_id TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    value REAL,
    threshold REAL,
    level TEXT,
    committee TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    approved_by TEXT,
    notes TEXT,
    FOREIGN KEY (property_id) REFERENCES properties(id)
)
""")

# Create audit_log table (if it doesn't exist)
print("Creating audit_log table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    user_id TEXT,
    document_id TEXT,
    property_id TEXT,
    alert_id TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Commit changes
conn.commit()

# Verify tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("\n✅ Database tables created successfully!")
print("\nExisting tables:")
for table in tables:
    print(f"  • {table[0]}")

# Check if we need to add test property
cursor.execute("SELECT COUNT(*) FROM properties WHERE id = 'test-property-001'")
if cursor.fetchone()[0] == 0:
    print("\n📝 Adding test property...")
    cursor.execute("""
        INSERT INTO properties (
            id, property_code, name, address, city, state, 
            status, current_market_value, monthly_rent
        ) VALUES (
            'test-property-001',
            'TEST-001',
            'Test Property for Upload',
            '123 Test St',
            'Test City',
            'TS',
            'active',
            1000000,
            5000
        )
    """)
    conn.commit()
    print("✅ Test property added")

conn.close()

print("\n✅ Setup complete! Ready for file uploads.")















