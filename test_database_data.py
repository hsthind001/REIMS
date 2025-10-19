#!/usr/bin/env python3
"""
Test and Verify Uploaded Data in REIMS Database
Shows all data from the uploaded files across all relevant tables
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "reims.db"

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_table_data(cursor, table_name, description):
    """Print all data from a table"""
    print_header(f"📋 {table_name.upper()} - {description}")
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Get all data
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    print(f"\n📊 Total Records: {len(rows)}\n")
    
    if not rows:
        print("  (No records found)\n")
        return
    
    for i, row in enumerate(rows, 1):
        print(f"─── Record {i} ───")
        for col, val in zip(columns, row):
            if val is not None:
                # Format JSON fields nicely
                if col in ['extracted_content', 'processing_result'] and val:
                    try:
                        val_obj = json.loads(val)
                        print(f"  {col}:")
                        print(f"    {json.dumps(val_obj, indent=4)[:200]}...")
                    except:
                        print(f"  {col}: {str(val)[:100]}...")
                else:
                    print(f"  {col}: {val}")
        print()

def show_summary(cursor):
    """Show summary statistics"""
    print_header("📊 DATABASE SUMMARY")
    
    tables_to_check = [
        ('documents', 'Uploaded file metadata'),
        ('extracted_data', 'Extracted PDF/Excel content'),
        ('processing_jobs', 'Processing status'),
        ('properties', 'Property information'),
        ('financial_documents', 'Financial statements'),
        ('financial_transactions', 'Transaction records'),
        ('tenants', 'Tenant records'),
        ('leases', 'Lease agreements')
    ]
    
    print()
    for table, description in tables_to_check:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            status = "✅" if count > 0 else "⏹️ "
            print(f"  {status} {table:25} {count:5} records - {description}")
        except sqlite3.OperationalError:
            print(f"  ⚠️  {table:25}       - Table not found")
    print()

def test_uploaded_data():
    """Main function to test all uploaded data"""
    print("\n╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║          🔍 TESTING UPLOADED DATA IN REIMS DATABASE 🔍                    ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Summary
    show_summary(cursor)
    
    # Detailed data from each table with uploaded data
    print_header("📄 DETAILED DATA FROM UPLOADED FILES")
    
    # 1. DOCUMENTS TABLE - File metadata
    print_table_data(cursor, 'documents', 'File Metadata & Storage Info')
    
    # 2. EXTRACTED_DATA TABLE - Extracted content
    print_table_data(cursor, 'extracted_data', 'Extracted Text & Metrics')
    
    # 3. PROCESSING_JOBS TABLE - Processing status
    print_table_data(cursor, 'processing_jobs', 'Job Processing Status')
    
    # Show quick queries
    print_header("🔎 QUICK QUERY EXAMPLES")
    
    print("\n1️⃣  Get all document filenames:")
    cursor.execute("SELECT original_filename, file_size, status FROM documents")
    for row in cursor.fetchall():
        print(f"  • {row[0]} ({row[1]} bytes) - Status: {row[2]}")
    
    print("\n2️⃣  Get extraction metrics:")
    cursor.execute("""
        SELECT d.original_filename, e.data_type, e.page_count, e.word_count
        FROM documents d
        JOIN extracted_data e ON d.document_id = e.document_id
    """)
    for row in cursor.fetchall():
        print(f"  • {row[0]}")
        print(f"    Type: {row[1]}, Pages: {row[2]}, Words: {row[3]}")
    
    print("\n3️⃣  Get processing job statuses:")
    cursor.execute("""
        SELECT d.original_filename, j.status, j.created_at, j.completed_at
        FROM documents d
        JOIN processing_jobs j ON d.document_id = j.document_id
    """)
    for row in cursor.fetchall():
        print(f"  • {row[0]}: {row[1]}")
        print(f"    Created: {row[2]}, Completed: {row[3]}")
    
    print("\n4️⃣  Get extracted text preview:")
    cursor.execute("""
        SELECT d.original_filename, e.extracted_content
        FROM documents d
        JOIN extracted_data e ON d.document_id = e.document_id
        LIMIT 1
    """)
    row = cursor.fetchone()
    if row:
        print(f"  • File: {row[0]}")
        try:
            content = json.loads(row[1])
            text_preview = content.get('text_preview', content.get('full_text', ''))[:300]
            print(f"  • Text Preview:\n{text_preview}...")
        except:
            print(f"  • Content: {str(row[1])[:300]}...")
    
    print("\n" + "="*80)
    print("✅ DATA VERIFICATION COMPLETE")
    print("="*80)
    print(f"\n💡 Tip: You can also use 'VIEW_DATABASE.bat' to browse the database visually\n")
    
    conn.close()

if __name__ == "__main__":
    test_uploaded_data()

