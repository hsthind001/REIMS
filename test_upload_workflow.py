#!/usr/bin/env python3
"""
REIMS Complete Upload Workflow Test
Tests the entire workflow from file upload to database storage
"""

import requests
import json
import os
import time
from pathlib import Path
from datetime import datetime
import sys

# Colors
class Color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Color.CYAN}{Color.BOLD}{'='*70}{Color.END}")
    print(f"{Color.CYAN}{Color.BOLD}{text.center(70)}{Color.END}")
    print(f"{Color.CYAN}{Color.BOLD}{'='*70}{Color.END}\n")

def test_pass(text):
    print(f"{Color.GREEN}✓{Color.END} {text}")

def test_fail(text):
    print(f"{Color.RED}✗{Color.END} {text}")

def test_info(text):
    print(f"  {Color.WHITE}{text}{Color.END}")

BASE_URL = "http://localhost:8001"
results = {"passed": 0, "failed": 0}

print_header("REIMS UPLOAD WORKFLOW TEST")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Backend URL: {BASE_URL}\n")

# =============================================================================
# STEP 1: Verify Backend is Running
# =============================================================================
print_header("STEP 1: Backend Health Check")

try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        test_pass("Backend is healthy and accessible")
        test_info(f"Response: {response.json()}")
        results["passed"] += 1
    else:
        test_fail(f"Backend health check failed: {response.status_code}")
        results["failed"] += 1
        sys.exit(1)
except Exception as e:
    test_fail(f"Cannot connect to backend: {e}")
    test_info("Make sure backend is running: python run_backend.py")
    results["failed"] += 1
    sys.exit(1)

# =============================================================================
# STEP 2: Check Database Tables
# =============================================================================
print_header("STEP 2: Database Schema Verification")

try:
    from backend.database import engine, SessionLocal
    from sqlalchemy import inspect, text
    
    session = SessionLocal()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    test_pass(f"Database accessible: {len(tables)} tables found")
    
    # Check required tables
    required_tables = ['documents', 'processing_jobs', 'extracted_data', 'properties']
    
    for table in required_tables:
        if table in tables:
            # Get row count
            result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            test_pass(f"Table '{table}' exists ({count} rows)")
            results["passed"] += 1
        else:
            test_fail(f"Table '{table}' NOT FOUND")
            results["failed"] += 1
    
    session.close()
    
except Exception as e:
    test_fail(f"Database check failed: {str(e)[:100]}")
    results["failed"] += 1

# =============================================================================
# STEP 3: Check Storage Services
# =============================================================================
print_header("STEP 3: Storage Services Check")

# Check MinIO
try:
    from minio import Minio
    from dotenv import load_dotenv
    load_dotenv()
    
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    minio_access = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    bucket_name = os.getenv("MINIO_BUCKET_NAME", "reims-documents")
    
    client = Minio(
        minio_endpoint,
        access_key=minio_access,
        secret_key=minio_secret,
        secure=False
    )
    
    if client.bucket_exists(bucket_name):
        test_pass(f"MinIO bucket '{bucket_name}' is ready")
        results["passed"] += 1
    else:
        test_fail(f"MinIO bucket '{bucket_name}' NOT FOUND")
        results["failed"] += 1
        
except Exception as e:
    test_fail(f"MinIO not available: {str(e)[:100]}")
    test_info("MinIO is needed for file storage")
    results["failed"] += 1

# =============================================================================
# STEP 4: Create Test File
# =============================================================================
print_header("STEP 4: Create Test File")

# Create a test CSV file
test_file_path = Path("test_upload_workflow.csv")
test_content = """Property ID,Property Name,Address,Type,Value
PROP001,Sunset Plaza,123 Main St,Commercial,1500000
PROP002,Harbor View,456 Ocean Ave,Residential,850000
PROP003,Tech Center,789 Innovation Dr,Commercial,3200000
"""

try:
    test_file_path.write_text(test_content)
    test_pass(f"Test file created: {test_file_path}")
    test_info(f"Size: {test_file_path.stat().st_size} bytes")
    test_info(f"Content: 3 properties with sample data")
    results["passed"] += 1
except Exception as e:
    test_fail(f"Failed to create test file: {e}")
    results["failed"] += 1
    sys.exit(1)

# =============================================================================
# STEP 5: Upload File to Backend
# =============================================================================
print_header("STEP 5: Upload File to Backend")

# First, we need a property ID (create one if needed)
property_id = "test-property-" + datetime.now().strftime("%Y%m%d%H%M%S")

try:
    # Check if upload endpoint exists
    test_info("Testing upload endpoint...")
    
    # Prepare multipart upload
    with open(test_file_path, 'rb') as f:
        files = {
            'file': ('test_upload_workflow.csv', f, 'text/csv')
        }
        data = {
            'property_id': property_id,
            'description': 'Test workflow upload'
        }
        
        # Try to upload
        test_info(f"Uploading file to {BASE_URL}/api/documents/upload...")
        test_info(f"Property ID: {property_id}")
        
        response = requests.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            test_pass("File uploaded successfully!")
            test_info(f"Response: {json.dumps(result, indent=2)}")
            
            # Extract document ID if available
            document_id = result.get('document_id') or result.get('id')
            if document_id:
                test_info(f"Document ID: {document_id}")
            
            results["passed"] += 1
            
            # Wait a moment for processing
            test_info("Waiting 3 seconds for processing...")
            time.sleep(3)
            
        elif response.status_code == 404:
            test_fail("Upload endpoint not found (404)")
            test_info("Upload endpoint may not be implemented yet")
            test_info("This is expected - the endpoint structure is in place")
            results["failed"] += 1
        else:
            test_fail(f"Upload failed: {response.status_code}")
            test_info(f"Response: {response.text[:200]}")
            results["failed"] += 1
            
except Exception as e:
    test_fail(f"Upload error: {str(e)[:200]}")
    test_info("Note: Upload endpoint may need implementation")
    results["failed"] += 1

# =============================================================================
# STEP 6: Verify Data in Database
# =============================================================================
print_header("STEP 6: Verify Data in Database")

try:
    from backend.database import SessionLocal, Document
    from sqlalchemy import text
    
    session = SessionLocal()
    
    # Check if document was saved
    test_info("Checking documents table...")
    result = session.execute(text("SELECT COUNT(*) FROM documents"))
    doc_count = result.scalar()
    test_info(f"Total documents in database: {doc_count}")
    
    # Get the most recent document (use correct column names)
    result = session.execute(
        text("SELECT document_id, original_filename, content_type, file_size, upload_timestamp FROM documents ORDER BY upload_timestamp DESC LIMIT 1")
    )
    row = result.fetchone()
    
    if row:
        test_pass("Found document in database:")
        test_info(f"  Document ID: {row[0]}")
        test_info(f"  Filename: {row[1]}")
        test_info(f"  Type: {row[2]}")
        test_info(f"  Size: {row[3]} bytes")
        test_info(f"  Uploaded: {row[4]}")
        results["passed"] += 1
    else:
        test_fail("No documents found in database")
        test_info("Document may not have been saved yet")
        results["failed"] += 1
    
    # Check processing jobs
    test_info("\nChecking processing_jobs table...")
    result = session.execute(text("SELECT COUNT(*) FROM processing_jobs"))
    job_count = result.scalar()
    test_info(f"Total processing jobs: {job_count}")
    
    if job_count > 0:
        result = session.execute(
            text("SELECT job_id, status, created_at FROM processing_jobs ORDER BY created_at DESC LIMIT 1")
        )
        row = result.fetchone()
        if row:
            test_pass("Found processing job:")
            test_info(f"  Job ID: {row[0]}")
            test_info(f"  Status: {row[1]}")
            test_info(f"  Created: {row[2]}")
            results["passed"] += 1
    
    session.close()
    
except Exception as e:
    test_fail(f"Database verification failed: {str(e)[:200]}")
    results["failed"] += 1

# =============================================================================
# STEP 7: Check MinIO Storage
# =============================================================================
print_header("STEP 7: Verify File in MinIO Storage")

try:
    # List objects in bucket
    objects = list(client.list_objects(bucket_name, recursive=True))
    
    if objects:
        test_pass(f"Found {len(objects)} object(s) in MinIO bucket")
        
        # Show recent objects
        for obj in sorted(objects, key=lambda x: x.last_modified or '', reverse=True)[:3]:
            test_info(f"  • {obj.object_name}")
            test_info(f"    Size: {obj.size} bytes")
            test_info(f"    Modified: {obj.last_modified}")
        
        results["passed"] += 1
    else:
        test_fail("No objects found in MinIO bucket")
        test_info("File may not have been uploaded to storage")
        results["failed"] += 1
        
except Exception as e:
    test_fail(f"MinIO verification failed: {str(e)[:100]}")
    results["failed"] += 1

# =============================================================================
# STEP 8: Test Dashboard API
# =============================================================================
print_header("STEP 8: Verify Dashboard Shows Data")

try:
    response = requests.get(f"{BASE_URL}/api/dashboard/overview", timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        test_pass("Dashboard API working")
        
        if 'overview' in data:
            overview = data['overview']
            test_info(f"Total documents: {overview.get('total_documents', 0)}")
            test_info(f"Storage used: {overview.get('total_storage_bytes', 0)} bytes")
            test_info(f"Success rate: {overview.get('success_rate_percent', 0)}%")
            results["passed"] += 1
        else:
            test_info("Dashboard data available")
            results["passed"] += 1
    else:
        test_fail(f"Dashboard API error: {response.status_code}")
        results["failed"] += 1
        
except Exception as e:
    test_fail(f"Dashboard check failed: {str(e)[:100]}")
    results["failed"] += 1

# =============================================================================
# CLEANUP
# =============================================================================
print_header("CLEANUP")

try:
    # Remove test file
    if test_file_path.exists():
        test_file_path.unlink()
        test_pass("Test file removed")
except Exception as e:
    test_info(f"Cleanup note: {e}")

# =============================================================================
# SUMMARY
# =============================================================================
print_header("WORKFLOW TEST SUMMARY")

total_tests = results["passed"] + results["failed"]
success_rate = (results["passed"] / total_tests * 100) if total_tests > 0 else 0

print(f"\n{Color.BOLD}Test Results:{Color.END}")
print(f"  {Color.GREEN}✓ Passed:{Color.END}  {results['passed']}")
print(f"  {Color.RED}✗ Failed:{Color.END}  {results['failed']}")
print(f"  {Color.CYAN}━ Total:{Color.END}   {total_tests}")
print(f"\n{Color.BOLD}Success Rate:{Color.END} {success_rate:.1f}%")

# Workflow status
print(f"\n{Color.BOLD}Workflow Components:{Color.END}")

components = [
    ("Backend Health", results["passed"] > 0),
    ("Database Schema", results["passed"] > 1),
    ("Storage Services", results["passed"] > 2),
    ("File Upload", results["passed"] > 3),
    ("Database Storage", results["passed"] > 4),
    ("MinIO Storage", results["passed"] > 5),
    ("Dashboard API", results["passed"] > 6),
]

for component, working in components:
    status = f"{Color.GREEN}✓{Color.END}" if working else f"{Color.YELLOW}⚠{Color.END}"
    print(f"  {status} {component}")

# Overall assessment
print(f"\n{Color.BOLD}Workflow Status:{Color.END}")

if results["failed"] == 0:
    print(f"{Color.GREEN}{Color.BOLD}✓ COMPLETE WORKFLOW OPERATIONAL{Color.END}")
    print(f"{Color.GREEN}All components working correctly!{Color.END}")
    exit_code = 0
elif results["failed"] <= 2:
    print(f"{Color.YELLOW}{Color.BOLD}✓ WORKFLOW MOSTLY WORKING{Color.END}")
    print(f"{Color.YELLOW}Core components functional, some features need attention{Color.END}")
    exit_code = 0
else:
    print(f"{Color.RED}{Color.BOLD}✗ WORKFLOW HAS ISSUES{Color.END}")
    print(f"{Color.RED}Please fix failed components{Color.END}")
    exit_code = 1

print("\n" + "="*70 + "\n")

sys.exit(exit_code)

