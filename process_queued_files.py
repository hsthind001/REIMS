"""
Process All Queued ESP Financial Files
Quick script to trigger processing of uploaded files
"""
import requests
import sqlite3
import time
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

print(f"\n{CYAN}{BOLD}{'='*80}")
print(f"{'🚀 Process Queued Financial Documents':^80}")
print(f"{'='*80}{RESET}\n")

# Check backend is running
print(f"{YELLOW}Step 1: Checking backend status...{RESET}")
try:
    response = requests.get('http://localhost:8001/health', timeout=5)
    if response.status_code == 200:
        print(f"{GREEN}✅ Backend is running{RESET}\n")
    else:
        print(f"{RED}❌ Backend returned status {response.status_code}{RESET}")
        print(f"{YELLOW}Please start the backend first: python run_backend.py{RESET}\n")
        exit(1)
except requests.exceptions.ConnectionError:
    print(f"{RED}❌ Cannot connect to backend on port 8001{RESET}")
    print(f"{YELLOW}Please start the backend first: python run_backend.py{RESET}\n")
    exit(1)

# Get count of queued documents
print(f"{YELLOW}Step 2: Checking queued documents...{RESET}")
try:
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM financial_documents 
        WHERE status='queued'
    """)
    queued_count = cursor.fetchone()[0]
    
    if queued_count == 0:
        print(f"{YELLOW}⚠️  No documents in queue{RESET}")
        print(f"{CYAN}All documents may have already been processed!{RESET}\n")
        
        # Show completed count
        cursor.execute("SELECT COUNT(*) FROM financial_documents WHERE status='completed'")
        completed_count = cursor.fetchone()[0]
        print(f"{GREEN}✅ {completed_count} documents already processed{RESET}\n")
        conn.close()
        exit(0)
    
    print(f"{GREEN}✅ Found {queued_count} documents in queue{RESET}")
    
    # Show sample files
    cursor.execute("""
        SELECT file_name, upload_date 
        FROM financial_documents 
        WHERE status='queued' 
        ORDER BY upload_date DESC 
        LIMIT 5
    """)
    sample_files = cursor.fetchall()
    
    print(f"\n{CYAN}Sample queued files:{RESET}")
    for i, (name, upload_date) in enumerate(sample_files, 1):
        print(f"   {i}. {name} (uploaded: {upload_date})")
    
    if queued_count > 5:
        print(f"   ... and {queued_count - 5} more")
    
    conn.close()
    
except Exception as e:
    print(f"{RED}❌ Error checking database: {e}{RESET}\n")
    exit(1)

# Trigger processing
print(f"\n{YELLOW}Step 3: Triggering batch processing...{RESET}")

try:
    # Check if worker is needed
    print(f"{CYAN}   Note: Background worker must be running!{RESET}")
    print(f"{CYAN}   If not running: ./start_worker.ps1{RESET}\n")
    
    time.sleep(2)  # Give user time to read
    
    # Make API call to trigger processing
    response = requests.post(
        'http://localhost:8001/api/ai-processing/process-all',
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"{GREEN}✅ Processing started!{RESET}\n")
        print(f"{BOLD}Results:{RESET}")
        print(f"   Status: {result.get('status')}")
        print(f"   Documents queued: {result.get('documents_queued', 0)}")
        print(f"   Message: {result.get('message')}")
        
        print(f"\n{CYAN}{'─'*80}{RESET}")
        print(f"{BOLD}What's happening now:{RESET}")
        print(f"   1. Background worker is picking up jobs from queue")
        print(f"   2. Each document is being processed:")
        print(f"      • Load PDF from MinIO")
        print(f"      • Extract text using AI")
        print(f"      • Parse financial metrics")
        print(f"      • Save to extracted_data table")
        print(f"   3. Status will change from 'queued' → 'completed'")
        
        print(f"\n{YELLOW}⏰ Processing time: ~30-60 seconds per document{RESET}")
        print(f"{YELLOW}📊 Total estimated time: {queued_count * 45 // 60} - {queued_count * 60 // 60} minutes{RESET}")
        
        print(f"\n{CYAN}{'─'*80}{RESET}")
        print(f"{BOLD}Monitor progress:{RESET}")
        print(f"   • Watch worker terminal for logs")
        print(f"   • Run: python trace_uploaded_files.py")
        print(f"   • Run: python browse_database.py")
        
        print(f"\n{GREEN}{'='*80}")
        print(f"{'✅ Processing Started Successfully!':^80}")
        print(f"{'='*80}{RESET}\n")
        
    else:
        print(f"{RED}❌ Failed to start processing{RESET}")
        print(f"   Status code: {response.status_code}")
        print(f"   Response: {response.text}")
        
except requests.exceptions.Timeout:
    print(f"{RED}❌ Request timed out{RESET}")
    print(f"{YELLOW}Backend might be processing - check worker logs{RESET}\n")
    
except Exception as e:
    print(f"{RED}❌ Error triggering processing: {e}{RESET}\n")
    exit(1)

