"""
Queue All Documents for Processing
Directly adds documents to Redis queue
"""
import sqlite3
import sys
import os

# Add queue_service to path
sys.path.append(os.path.join(os.path.dirname(__file__), "queue_service"))

from client import QueueClient

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
print(f"{'📋 Queue All Documents for Processing':^80}")
print(f"{'='*80}{RESET}\n")

# Connect to database
print(f"{YELLOW}Step 1: Loading queued documents from database...{RESET}")
conn = sqlite3.connect('reims.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT id, file_name, file_path, document_type
    FROM financial_documents
    WHERE status = 'queued'
    ORDER BY upload_date DESC
""")

documents = cursor.fetchall()
conn.close()

if not documents:
    print(f"{YELLOW}⚠️  No documents in queue!{RESET}\n")
    exit(0)

print(f"{GREEN}✅ Found {len(documents)} documents to process{RESET}\n")

# Show first few
print(f"{CYAN}Documents to process:{RESET}")
for i, (doc_id, file_name, file_path, doc_type) in enumerate(documents[:5], 1):
    print(f"   {i}. {file_name}")
if len(documents) > 5:
    print(f"   ... and {len(documents) - 5} more\n")

# Initialize queue client
print(f"\n{YELLOW}Step 2: Connecting to Redis queue...{RESET}")
try:
    client = QueueClient()
    print(f"{GREEN}✅ Connected to Redis queue{RESET}\n")
except Exception as e:
    print(f"{RED}❌ Failed to connect to Redis: {e}{RESET}")
    print(f"{YELLOW}Make sure Redis is running: docker ps{RESET}\n")
    exit(1)

# Queue each document
print(f"{YELLOW}Step 3: Adding documents to processing queue...{RESET}\n")
queued_jobs = []
failed = []

for doc_id, file_name, file_path, doc_type in documents:
    try:
        # Prepare metadata
        metadata = {
            'file_path': file_path,
            'file_name': file_name,
            'document_type': doc_type,
        }
        
        # Enqueue the document
        job_id = client.enqueue_document(doc_id, metadata)
        queued_jobs.append((doc_id, file_name, job_id))
        print(f"{GREEN}✅ Queued:{RESET} {file_name[:50]}")
        print(f"   Document ID: {doc_id}")
        print(f"   Job ID: {job_id}\n")
        
    except Exception as e:
        failed.append((doc_id, file_name, str(e)))
        print(f"{RED}❌ Failed:{RESET} {file_name}")
        print(f"   Error: {e}\n")

# Summary
print(f"{CYAN}{'='*80}{RESET}")
print(f"\n{BOLD}Summary:{RESET}")
print(f"   {GREEN}✅ Successfully queued: {len(queued_jobs)}{RESET}")
if failed:
    print(f"   {RED}❌ Failed: {len(failed)}{RESET}")

print(f"\n{BOLD}What happens next:{RESET}")
print(f"   1. Worker picks up jobs from Redis queue")
print(f"   2. Each document is processed:")
print(f"      • Load file from path")
print(f"      • Extract text/data")
print(f"      • Parse financial metrics (for PDFs)")
print(f"      • Save to extracted_data table")
print(f"   3. Status updates from 'queued' → 'completed'")

print(f"\n{YELLOW}⏰ Estimated time: {len(queued_jobs) * 30 // 60} - {len(queued_jobs) * 60 // 60} minutes{RESET}")
print(f"   (~30-60 seconds per document)")

print(f"\n{BOLD}Monitor progress:{RESET}")
print(f"   • Check worker terminal for processing logs")
print(f"   • Run: python trace_uploaded_files.py")
print(f"   • Run: python browse_database.py")

print(f"\n{GREEN}{'='*80}")
print(f"{'✅ Documents queued for processing!':^80}")
print(f"{'='*80}{RESET}\n")

if failed:
    print(f"\n{RED}Failed documents:{RESET}")
    for doc_id, file_name, error in failed:
        print(f"   • {file_name}")
        print(f"     Error: {error}\n")

