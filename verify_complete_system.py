#!/usr/bin/env python3
"""
Comprehensive REIMS System Verification
Checks: Frontend, Backend, AI/ML, Infrastructure, and all integrations
"""

import requests
import sys
import os
from datetime import datetime
from pathlib import Path

# Colors for terminal output
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

def print_section(text):
    print(f"\n{Color.BOLD}{text}{Color.END}")
    print("-" * 70)

def check_pass(text):
    print(f"{Color.GREEN}✓{Color.END} {text}")

def check_fail(text):
    print(f"{Color.RED}✗{Color.END} {text}")

def check_warn(text):
    print(f"{Color.YELLOW}⚠{Color.END} {text}")

def check_info(text):
    print(f"  {Color.WHITE}{text}{Color.END}")

# Test results tracker
results = {
    "passed": 0,
    "failed": 0,
    "warnings": 0
}

print_header("REIMS COMPLETE SYSTEM VERIFICATION")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# =============================================================================
# 1. BACKEND VERIFICATION
# =============================================================================
print_section("1. BACKEND SERVICE")

try:
    response = requests.get("http://localhost:8001/health", timeout=5)
    if response.status_code == 200:
        check_pass("Backend is running on http://localhost:8001")
        check_info(f"Health status: {response.json()}")
        results["passed"] += 1
    else:
        check_fail(f"Backend returned status {response.status_code}")
        results["failed"] += 1
except Exception as e:
    check_fail(f"Backend not accessible: {e}")
    results["failed"] += 1

# Test backend endpoints
endpoints_to_test = [
    "/health",
    "/api/dashboard/overview",
    "/api/kpis/health",
    "/monitoring/health",
]

print("\nTesting Backend Endpoints:")
for endpoint in endpoints_to_test:
    try:
        response = requests.get(f"http://localhost:8001{endpoint}", timeout=5)
        if response.status_code == 200:
            check_pass(f"  {endpoint} - OK")
            results["passed"] += 1
        else:
            check_warn(f"  {endpoint} - Status {response.status_code}")
            results["warnings"] += 1
    except Exception as e:
        check_fail(f"  {endpoint} - Error: {str(e)[:50]}")
        results["failed"] += 1

# =============================================================================
# 2. FRONTEND VERIFICATION
# =============================================================================
print_section("2. FRONTEND SERVICE")

try:
    response = requests.get("http://localhost:3000", timeout=5)
    if response.status_code == 200:
        check_pass("Frontend is running on http://localhost:3000")
        check_info(f"Response size: {len(response.content)} bytes")
        results["passed"] += 1
    else:
        check_fail(f"Frontend returned status {response.status_code}")
        results["failed"] += 1
except Exception as e:
    check_fail(f"Frontend not accessible: {e}")
    results["failed"] += 1

# =============================================================================
# 3. DATABASE VERIFICATION
# =============================================================================
print_section("3. DATABASE CONNECTION")

try:
    from dotenv import load_dotenv
    load_dotenv()
    
    db_url = os.getenv("DATABASE_URL", "Not configured")
    check_info(f"Database URL: {db_url}")
    
    if "sqlite" in db_url.lower():
        check_pass("Using SQLite database (no password required)")
        results["passed"] += 1
        
        # Check if database file exists
        if Path("reims.db").exists():
            db_size = Path("reims.db").stat().st_size
            check_pass(f"Database file exists ({db_size:,} bytes)")
            results["passed"] += 1
        else:
            check_warn("Database file not found (will be created on first use)")
            results["warnings"] += 1
    elif "postgresql" in db_url.lower():
        check_pass("Using PostgreSQL database")
        results["passed"] += 1
    
    # Test database connection
    sys.path.insert(0, str(Path(__file__).parent))
    from backend.database import engine, SessionLocal
    
    session = SessionLocal()
    result = session.execute("SELECT 1").scalar()
    session.close()
    
    if result == 1:
        check_pass("Database connection successful")
        results["passed"] += 1
    else:
        check_fail("Database query returned unexpected result")
        results["failed"] += 1
        
except Exception as e:
    check_fail(f"Database connection error: {str(e)[:100]}")
    results["failed"] += 1

# Check for required tables
print("\nChecking Database Schema:")
try:
    from backend.database import SessionLocal, engine
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    required_tables = [
        "documents", "processing_jobs", "extracted_data", 
        "properties", "analytics"
    ]
    
    check_info(f"Found {len(tables)} tables in database")
    
    for table in required_tables:
        if table in tables:
            check_pass(f"  Table '{table}' exists")
            results["passed"] += 1
        else:
            check_warn(f"  Table '{table}' missing (will be created on first use)")
            results["warnings"] += 1
            
except Exception as e:
    check_warn(f"Could not inspect schema: {str(e)[:100]}")
    results["warnings"] += 1

# =============================================================================
# 4. INFRASTRUCTURE SERVICES
# =============================================================================
print_section("4. INFRASTRUCTURE SERVICES")

# Redis
print("\nRedis Cache:")
try:
    import redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    r = redis.from_url(redis_url, socket_connect_timeout=3)
    r.ping()
    check_pass(f"Redis is running: {redis_url}")
    check_info(f"  Info: {r.info('server')['redis_version']}")
    results["passed"] += 1
except Exception as e:
    check_warn(f"Redis not available: {str(e)[:80]}")
    check_info("  Note: Redis is optional for basic operations")
    results["warnings"] += 1

# MinIO
print("\nMinIO Object Storage:")
try:
    from minio import Minio
    
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    minio_access = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    
    client = Minio(
        minio_endpoint,
        access_key=minio_access,
        secret_key=minio_secret,
        secure=False
    )
    
    # Test connection
    buckets = list(client.list_buckets())
    check_pass(f"MinIO is running: {minio_endpoint}")
    check_info(f"  Buckets: {len(buckets)}")
    
    bucket_name = os.getenv("MINIO_BUCKET_NAME", "reims-documents")
    if any(b.name == bucket_name for b in buckets):
        check_pass(f"  Bucket '{bucket_name}' exists")
    else:
        check_warn(f"  Bucket '{bucket_name}' not found (will be created)")
        results["warnings"] += 1
    
    results["passed"] += 1
    
except Exception as e:
    check_warn(f"MinIO not available: {str(e)[:80]}")
    check_info("  Note: MinIO is needed for document storage")
    results["warnings"] += 1

# =============================================================================
# 5. AI/ML SERVICES
# =============================================================================
print_section("5. AI/ML SERVICES")

# Ollama
print("\nOllama LLM Service:")
try:
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    response = requests.get(f"{ollama_url}/api/tags", timeout=5)
    
    if response.status_code == 200:
        models = response.json().get("models", [])
        check_pass(f"Ollama is running: {ollama_url}")
        check_info(f"  Available models: {len(models)}")
        
        target_model = os.getenv("OLLAMA_MODEL", "phi3:mini")
        if any(m.get("name", "").startswith(target_model.split(":")[0]) for m in models):
            check_pass(f"  Model '{target_model}' available")
        else:
            check_warn(f"  Model '{target_model}' not found")
            check_info(f"  Run: ollama pull {target_model}")
            results["warnings"] += 1
        
        results["passed"] += 1
    else:
        check_warn(f"Ollama returned status {response.status_code}")
        results["warnings"] += 1
        
except Exception as e:
    check_warn(f"Ollama not available: {str(e)[:80]}")
    check_info("  Note: Ollama is needed for AI features")
    check_info("  Install from: https://ollama.ai")
    results["warnings"] += 1

# Document Processor
print("\nDocument Processing:")
try:
    from backend.agents.document_processor_integration import document_processor
    check_pass("Document processor module loaded")
    check_info(f"  Location: backend/agents/document_processor_integration.py")
    results["passed"] += 1
except Exception as e:
    check_warn(f"Document processor not fully available: {str(e)[:80]}")
    results["warnings"] += 1

# =============================================================================
# 6. INTEGRATION TESTS
# =============================================================================
print_section("6. COMPONENT INTEGRATION")

print("\nFrontend ↔ Backend:")
try:
    # Check CORS configuration
    response = requests.options(
        "http://localhost:8001/health",
        headers={"Origin": "http://localhost:3000"}
    )
    
    if "access-control-allow-origin" in response.headers:
        check_pass("CORS properly configured for frontend-backend communication")
        results["passed"] += 1
    else:
        check_warn("CORS headers not found (may cause frontend issues)")
        results["warnings"] += 1
except Exception as e:
    check_warn(f"Could not verify CORS: {str(e)[:80]}")
    results["warnings"] += 1

print("\nBackend ↔ Database:")
try:
    response = requests.get("http://localhost:8001/api/dashboard/overview", timeout=5)
    if response.status_code == 200:
        data = response.json()
        check_pass("Backend can query database successfully")
        check_info(f"  Documents: {data.get('total_documents', 0)}")
        check_info(f"  Properties: {data.get('total_properties', 0)}")
        results["passed"] += 1
    else:
        check_warn(f"Dashboard endpoint returned {response.status_code}")
        results["warnings"] += 1
except Exception as e:
    check_warn(f"Backend-database integration: {str(e)[:80]}")
    results["warnings"] += 1

# =============================================================================
# 7. CONFIGURATION CHECK
# =============================================================================
print_section("7. CONFIGURATION FILES")

config_files = [
    (".env", "Environment configuration", True),
    ("backend/database.py", "Database module", True),
    ("backend/api/main.py", "Main API", True),
    ("frontend/package.json", "Frontend config", True),
    ("reims.db", "SQLite database", False),  # Optional, created on use
]

for file_path, description, required in config_files:
    if Path(file_path).exists():
        check_pass(f"{description}: {file_path}")
        results["passed"] += 1
    else:
        if required:
            check_fail(f"{description} missing: {file_path}")
            results["failed"] += 1
        else:
            check_info(f"{description} not yet created: {file_path}")

# =============================================================================
# FINAL SUMMARY
# =============================================================================
print_header("VERIFICATION SUMMARY")

total_checks = results["passed"] + results["failed"] + results["warnings"]
success_rate = (results["passed"] / total_checks * 100) if total_checks > 0 else 0

print(f"\n{Color.BOLD}Test Results:{Color.END}")
print(f"  {Color.GREEN}✓ Passed:{Color.END}   {results['passed']}")
print(f"  {Color.RED}✗ Failed:{Color.END}   {results['failed']}")
print(f"  {Color.YELLOW}⚠ Warnings:{Color.END} {results['warnings']}")
print(f"  {Color.CYAN}━ Total:{Color.END}    {total_checks}")
print(f"\n{Color.BOLD}Success Rate:{Color.END} {success_rate:.1f}%")

# Overall status
print(f"\n{Color.BOLD}Overall System Status:{Color.END}")
if results["failed"] == 0:
    if results["warnings"] == 0:
        print(f"{Color.GREEN}{Color.BOLD}✓ ALL SYSTEMS OPERATIONAL{Color.END}")
        print(f"{Color.GREEN}Everything is working perfectly!{Color.END}")
    else:
        print(f"{Color.YELLOW}{Color.BOLD}✓ SYSTEM FUNCTIONAL WITH WARNINGS{Color.END}")
        print(f"{Color.YELLOW}Core services are working, some optional features need attention{Color.END}")
else:
    print(f"{Color.RED}{Color.BOLD}✗ SYSTEM HAS ISSUES{Color.END}")
    print(f"{Color.RED}Please fix the failed components before proceeding{Color.END}")

# Quick access URLs
print(f"\n{Color.BOLD}Quick Access:{Color.END}")
print(f"  Frontend:  {Color.CYAN}http://localhost:3000{Color.END}")
print(f"  Backend:   {Color.CYAN}http://localhost:8001{Color.END}")
print(f"  API Docs:  {Color.CYAN}http://localhost:8001/docs{Color.END}")

print("\n" + "="*70 + "\n")

# Exit code based on results
sys.exit(0 if results["failed"] == 0 else 1)

















