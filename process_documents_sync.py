"""
Synchronous Document Processor for Windows
Processes queued documents directly without Redis worker
"""
import sqlite3
import sys
import os
import time
from datetime import datetime

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), "queue_service"))
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

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

print(f"\n{CYAN}{BOLD}{'='*80}")
print(f"{'🚀 Synchronous Document Processor (Windows-Compatible)':^80}")
print(f"{'='*80}{RESET}\n")

# Load document processor
print(f"{YELLOW}Loading document processor...{RESET}")
try:
    from document_processor import document_processor
    print(f"{GREEN}✅ Document processor loaded{RESET}\n")
except ImportError as e:
    print(f"{RED}❌ Failed to load document processor: {e}{RESET}\n")
    exit(1)

# Connect to database
print(f"{YELLOW}Step 1: Loading queued documents...{RESET}")
conn = sqlite3.connect('reims.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT id, file_name, file_path, document_type, upload_date
    FROM financial_documents
    WHERE status = 'queued'
    ORDER BY upload_date DESC
""")

documents = cursor.fetchall()

if not documents:
    print(f"{YELLOW}⚠️  No documents in queue{RESET}\n")
    conn.close()
    exit(0)

print(f"{GREEN}✅ Found {len(documents)} documents to process{RESET}\n")

# Show what we'll process
print(f"{CYAN}Documents to process:{RESET}")
for i, (doc_id, file_name, file_path, doc_type, upload_date) in enumerate(documents[:10], 1):
    print(f"   {i}. {file_name} (uploaded: {upload_date})")
if len(documents) > 10:
    print(f"   ... and {len(documents) - 10} more")

print(f"\n{YELLOW}⏰ This will take approximately {len(documents) * 30 // 60}-{len(documents) * 60 // 60} minutes{RESET}\n")

input(f"{BOLD}Press Enter to start processing...{RESET}")

# Process each document
print(f"\n{CYAN}{'='*80}{RESET}")
print(f"{BOLD}Starting Processing...{RESET}\n")

completed = []
failed = []
start_time = time.time()

for idx, (doc_id, file_name, file_path, doc_type, upload_date) in enumerate(documents, 1):
    print(f"\n{CYAN}[{idx}/{len(documents)}] Processing: {file_name}{RESET}")
    print(f"   Document ID: {doc_id}")
    print(f"   File Path: {file_path}")
    print(f"   Type: {doc_type}")
    
    doc_start = time.time()
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Prepare metadata
        metadata = {
            'file_path': file_path,
            'file_name': file_name,
            'document_type': doc_type,
            'document_id': doc_id
        }
        
        # Process the document
        print(f"{YELLOW}   Processing...{RESET}")
        result = document_processor.process(file_path, metadata)
        
        # Update database status
        cursor.execute("""
            UPDATE financial_documents
            SET status = 'completed',
                processing_date = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), doc_id))
        conn.commit()
        
        doc_time = time.time() - doc_start
        print(f"{GREEN}   ✅ Completed in {doc_time:.1f}s{RESET}")
        
        # Show extracted data summary
        if 'extracted_data' in result and result['extracted_data']:
            print(f"{CYAN}   📊 Extracted Data:{RESET}")
            for item in result['extracted_data'][:3]:  # Show first 3
                data_type = item.get('type', 'unknown')
                print(f"      • Type: {data_type}")
        
        completed.append((doc_id, file_name))
        
    except FileNotFoundError as e:
        doc_time = time.time() - doc_start
        print(f"{RED}   ❌ File not found: {file_path}{RESET}")
        
        # Update status to error
        cursor.execute("""
            UPDATE financial_documents
            SET status = 'error',
                error_message = ?
            WHERE id = ?
        """, (str(e), doc_id))
        conn.commit()
        
        failed.append((doc_id, file_name, str(e)))
        
    except Exception as e:
        doc_time = time.time() - doc_start
        print(f"{RED}   ❌ Error: {str(e)[:100]}{RESET}")
        
        # Update status to error
        cursor.execute("""
            UPDATE financial_documents
            SET status = 'error',
                error_message = ?
            WHERE id = ?
        """, (str(e), doc_id))
        conn.commit()
        
        failed.append((doc_id, file_name, str(e)))
    
    # Progress update
    elapsed = time.time() - start_time
    avg_time = elapsed / idx
    remaining = (len(documents) - idx) * avg_time
    print(f"{YELLOW}   Progress: {idx}/{len(documents)} | Elapsed: {elapsed:.0f}s | Est. Remaining: {remaining:.0f}s{RESET}")

conn.close()

# Final summary
total_time = time.time() - start_time

print(f"\n{CYAN}{'='*80}{RESET}")
print(f"\n{BOLD}📊 Processing Complete!{RESET}\n")

print(f"{GREEN}✅ Successfully processed: {len(completed)}{RESET}")
if failed:
    print(f"{RED}❌ Failed: {len(failed)}{RESET}")

print(f"\n{CYAN}⏱️  Total Time: {total_time / 60:.1f} minutes ({total_time:.0f} seconds){RESET}")
print(f"{CYAN}⚡ Average: {total_time / len(documents):.1f} seconds per document{RESET}")

if completed:
    print(f"\n{GREEN}Completed files:{RESET}")
    for doc_id, file_name in completed[:5]:
        print(f"   ✅ {file_name}")
    if len(completed) > 5:
        print(f"   ... and {len(completed) - 5} more")

if failed:
    print(f"\n{RED}Failed files:{RESET}")
    for doc_id, file_name, error in failed:
        print(f"   ❌ {file_name}")
        print(f"      Error: {error[:80]}")

print(f"\n{BOLD}Next Steps:{RESET}")
print(f"   1. Check extracted data: {CYAN}python browse_database.py{RESET}")
print(f"   2. Verify processing: {CYAN}python trace_uploaded_files.py{RESET}")
print(f"   3. View your data: {CYAN}python show_my_uploads.py{RESET}")

print(f"\n{GREEN}{'='*80}")
print(f"{'✅ Processing Session Complete!':^80}")
print(f"{'='*80}{RESET}\n")

