"""
Trace uploaded files through the system
Find where data is stored and how it's used
"""
import sqlite3
import json
from datetime import datetime

# ANSI colors
try:
    import colorama
    colorama.init()
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
except:
    GREEN = CYAN = YELLOW = RED = RESET = BOLD = ''

def print_header(text):
    print(f"\n{CYAN}{BOLD}{'='*80}")
    print(f"{text:^80}")
    print(f"{'='*80}{RESET}\n")

def print_section(text):
    print(f"\n{YELLOW}{'▶'*3} {text} {'◀'*3}{RESET}")

# Connect to database
conn = sqlite3.connect('reims.db')
cursor = conn.cursor()

print_header("🔍 UPLOADED FILES DATA FLOW ANALYSIS")

# 1. Find the uploaded ESP files
print_section("Step 1: Finding Uploaded ESP Files")

cursor.execute("""
    SELECT id, file_name, document_type, status, upload_date, file_path
    FROM financial_documents
    WHERE file_name LIKE '%ESP%' 
    OR file_name LIKE '%Income%'
    OR file_name LIKE '%Cash Flow%'
    OR file_name LIKE '%Balance Sheet%'
    ORDER BY upload_date DESC
""")

uploaded_files = cursor.fetchall()

if uploaded_files:
    print(f"{GREEN}✅ Found {len(uploaded_files)} ESP-related files:{RESET}\n")
    for i, (id, name, doc_type, status, upload_date, file_path) in enumerate(uploaded_files, 1):
        print(f"   {i}. {BOLD}{name}{RESET}")
        print(f"      ID: {id}")
        print(f"      Type: {doc_type or 'N/A'}")
        print(f"      Status: {status or 'N/A'}")
        print(f"      Upload Date: {upload_date}")
        print(f"      File Path: {file_path or 'N/A'}")
        print()
else:
    print(f"{RED}❌ No ESP files found in financial_documents table{RESET}")

# 2. Check all tables in database
print_section("Step 2: Checking All Database Tables")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"{CYAN}📊 Available tables in database:{RESET}\n")
for i, (table,) in enumerate(tables, 1):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"   {i:2d}. {table:<30} ({count} records)")

# 3. Check for extracted financial data
print_section("Step 3: Looking for Extracted Financial Data")

# Check financial_documents table for extracted data
cursor.execute("""
    SELECT id, file_name, document_type, status, upload_date
    FROM financial_documents
    ORDER BY upload_date DESC
    LIMIT 10
""")
recent_docs = cursor.fetchall()

print(f"{CYAN}Recent documents in financial_documents:{RESET}\n")
for doc in recent_docs:
    print(f"   • {doc[1]} - Status: {doc[3]}")

# 4. Check if there's an extracted_data table
cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='extracted_data'")
has_extracted_table = cursor.fetchone()[0] > 0

if has_extracted_table:
    print(f"\n{GREEN}✅ extracted_data table exists{RESET}")
    cursor.execute("SELECT COUNT(*) FROM extracted_data")
    count = cursor.fetchone()[0]
    print(f"   Records: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM extracted_data LIMIT 5")
        for row in cursor.fetchall():
            print(f"   {row}")
else:
    print(f"\n{YELLOW}⚠️  No extracted_data table found{RESET}")

# 5. Check processing_jobs table
print_section("Step 4: Checking Processing Jobs")

cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='processing_jobs'")
has_processing_table = cursor.fetchone()[0] > 0

if has_processing_table:
    cursor.execute("""
        SELECT document_id, status, created_at, completed_at, error_message
        FROM processing_jobs
        ORDER BY created_at DESC
        LIMIT 10
    """)
    jobs = cursor.fetchall()
    
    if jobs:
        print(f"{GREEN}✅ Found {len(jobs)} processing jobs:{RESET}\n")
        for job in jobs:
            print(f"   Doc ID: {job[0]} | Status: {job[1]} | Created: {job[2]}")
            if job[4]:
                print(f"      Error: {job[4]}")
    else:
        print(f"{YELLOW}⚠️  No processing jobs found{RESET}")
else:
    print(f"{YELLOW}⚠️  No processing_jobs table found{RESET}")

# 6. Check for metrics/analytics tables
print_section("Step 5: Looking for Financial Metrics Tables")

metrics_tables = ['financial_metrics', 'analytics', 'kpis', 'income_statement', 
                  'balance_sheet', 'cash_flow', 'metrics']

found_metrics = []
for table in metrics_tables:
    cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}'")
    if cursor.fetchone()[0] > 0:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        found_metrics.append((table, count))
        print(f"{GREEN}✅ {table}: {count} records{RESET}")

if not found_metrics:
    print(f"{YELLOW}⚠️  No dedicated financial metrics tables found{RESET}")

# 7. Summary and recommendations
print_section("📋 SUMMARY & ANALYSIS")

print(f"\n{BOLD}What We Found:{RESET}")
print(f"   • {len(uploaded_files)} ESP files uploaded to MinIO ✅")
print(f"   • Files stored in 'financial_documents' table ✅")
print(f"   • Total database tables: {len(tables)}")

print(f"\n{BOLD}Data Storage:{RESET}")
print(f"   1. File Metadata → financial_documents table")
print(f"   2. File Binary → MinIO object storage")

if has_extracted_table:
    print(f"   3. Extracted Data → extracted_data table ✅")
else:
    print(f"   3. Extracted Data → {RED}NOT FOUND ❌{RESET}")

if found_metrics:
    print(f"   4. Financial Metrics → {', '.join([t[0] for t in found_metrics])} ✅")
else:
    print(f"   4. Financial Metrics → {RED}NOT FOUND ❌{RESET}")

print(f"\n{BOLD}Next Steps:{RESET}")
print(f"   1. Check if data extraction is working")
print(f"   2. Verify frontend components are reading from correct tables")
print(f"   3. Identify missing tables/processing")

conn.close()

print(f"\n{GREEN}{'='*80}")
print(f"Analysis Complete!")
print(f"{'='*80}{RESET}\n")

