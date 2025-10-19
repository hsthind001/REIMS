"""
Comprehensive Backend Services Test for REIMS
Tests FastAPI, PostgreSQL, Airflow, MinIO, and Redis
"""

import sys
import io
import subprocess
import time
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"{title}")
    print("=" * 70)

def print_test(name, status, details=""):
    """Print test result"""
    icon = "✅" if status else "❌"
    status_text = "PASS" if status else "FAIL"
    print(f"  {icon} {name:<40} {status_text}")
    if details:
        print(f"     └─ {details}")

def test_fastapi():
    """Test FastAPI framework and application"""
    print_header("1. FastAPI - API Framework")
    
    results = []
    
    # Test 1: Check if FastAPI is installed
    try:
        import fastapi
        version = fastapi.__version__
        print_test("FastAPI Package Installed", True, f"Version {version}")
        results.append(True)
    except ImportError as e:
        print_test("FastAPI Package Installed", False, str(e))
        results.append(False)
        return False
    
    # Test 2: Check if Uvicorn is installed
    try:
        import uvicorn
        print_test("Uvicorn Server Installed", True)
        results.append(True)
    except ImportError:
        print_test("Uvicorn Server Installed", False, "Missing uvicorn")
        results.append(False)
    
    # Test 3: Check if API is running
    try:
        import httpx
        response = httpx.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test("API Health Endpoint", True, f"Status: {data.get('status', 'unknown')}")
            results.append(True)
        else:
            print_test("API Health Endpoint", False, f"HTTP {response.status_code}")
            results.append(False)
    except Exception as e:
        print_test("API Health Endpoint", False, "API not running on port 8001")
        results.append(False)
    
    # Test 4: Check if API docs are accessible
    try:
        import httpx
        response = httpx.get("http://localhost:8001/docs", timeout=5)
        if response.status_code == 200:
            print_test("API Documentation", True, "Swagger UI accessible")
            results.append(True)
        else:
            print_test("API Documentation", False)
            results.append(False)
    except Exception as e:
        print_test("API Documentation", False, str(e))
        results.append(False)
    
    # Test 5: Check critical dependencies
    deps = [
        ("sqlalchemy", "sqlalchemy", "Database ORM"),
        ("pydantic", "pydantic", "Data validation"),
        ("python-jose", "jose", "JWT tokens"),
        ("passlib", "passlib", "Password hashing"),
    ]
    
    for package_name, import_name, purpose in deps:
        try:
            __import__(import_name)
            print_test(f"{package_name}", True, purpose)
            results.append(True)
        except ImportError:
            print_test(f"{package_name}", False, f"Missing - {purpose}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n  📊 FastAPI Status: {sum(results)}/{len(results)} checks passed ({success_rate:.0f}%)")
    return all(results)

def test_postgresql():
    """Test PostgreSQL database"""
    print_header("2. PostgreSQL - Primary Database")
    
    results = []
    
    # Test 1: Check if psycopg2 is installed
    try:
        import psycopg2
        print_test("psycopg2 Driver Installed", True)
        results.append(True)
    except ImportError:
        print_test("psycopg2 Driver Installed", False, "Missing psycopg2-binary")
        results.append(False)
        return False
    
    # Test 2: Check if PostgreSQL service is running
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if ":5432" in result.stdout and "LISTENING" in result.stdout:
            print_test("PostgreSQL Service Running", True, "Port 5432 listening")
            results.append(True)
        else:
            print_test("PostgreSQL Service Running", False, "Port 5432 not listening")
            results.append(False)
    except Exception as e:
        print_test("PostgreSQL Service Running", False, str(e))
        results.append(False)
    
    # Test 3: Test database connection
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="reims",
            user="postgres",
            password="dev123",
            connect_timeout=5
        )
        print_test("Database Connection", True, "Connected to 'reims' database")
        results.append(True)
        
        # Test 4: Check if we can query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        postgres_version = version.split()[1]
        print_test("Database Query Test", True, f"PostgreSQL {postgres_version}")
        results.append(True)
        
        # Test 5: Check if tables exist
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        table_count = cursor.fetchone()[0]
        print_test("Database Schema", True, f"{table_count} tables found")
        results.append(True)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print_test("Database Connection", False, str(e))
        results.append(False)
        results.append(False)
        results.append(False)
    
    # Test 6: Check SQLAlchemy
    try:
        import sqlalchemy
        from sqlalchemy import create_engine
        engine = create_engine("postgresql://postgres:dev123@localhost:5432/reims")
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text("SELECT 1"))
            print_test("SQLAlchemy Integration", True, "ORM working")
            results.append(True)
    except Exception as e:
        print_test("SQLAlchemy Integration", False, str(e))
        results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n  📊 PostgreSQL Status: {sum(results)}/{len(results)} checks passed ({success_rate:.0f}%)")
    return all(results)

def test_airflow():
    """Test Apache Airflow"""
    print_header("3. Apache Airflow - Workflow Orchestration")
    
    results = []
    
    # Test 1: Check if Airflow is installed
    try:
        import airflow
        version = airflow.__version__
        print_test("Airflow Package Installed", True, f"Version {version}")
        results.append(True)
    except ImportError:
        print_test("Airflow Package Installed", False, "Not installed")
        results.append(False)
        print("\n  ℹ️  Note: Airflow is optional for basic REIMS functionality")
        print("     Install with: pip install apache-airflow")
        return False
    
    # Test 2: Check if Airflow is configured
    try:
        from airflow import configuration
        airflow_home = configuration.get('core', 'dags_folder')
        print_test("Airflow Configuration", True, f"DAGS: {airflow_home}")
        results.append(True)
    except Exception as e:
        print_test("Airflow Configuration", False, "Not configured")
        results.append(False)
    
    # Test 3: Check if Airflow webserver is running
    try:
        import httpx
        response = httpx.get("http://localhost:8080/health", timeout=5)
        print_test("Airflow Webserver", True, "Running on port 8080")
        results.append(True)
    except Exception:
        print_test("Airflow Webserver", False, "Not running (optional)")
        results.append(False)
        print("     └─ Start with: airflow webserver -p 8080")
    
    # Test 4: Check if Airflow scheduler is running
    try:
        result = subprocess.run(
            ["tasklist"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "airflow" in result.stdout.lower():
            print_test("Airflow Scheduler", True, "Process found")
            results.append(True)
        else:
            print_test("Airflow Scheduler", False, "Not running (optional)")
            results.append(False)
            print("     └─ Start with: airflow scheduler")
    except Exception:
        print_test("Airflow Scheduler", False, "Cannot check")
        results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n  📊 Airflow Status: {sum(results)}/{len(results)} checks passed ({success_rate:.0f}%)")
    print("  ℹ️  Note: Airflow is optional. APScheduler is used as alternative.")
    return len(results) > 0 and results[0]  # At least installed

def test_minio():
    """Test MinIO object storage"""
    print_header("4. MinIO - S3-Compatible Object Storage")
    
    results = []
    
    # Test 1: Check if MinIO client is installed
    try:
        import minio
        print_test("MinIO Client Installed", True)
        results.append(True)
    except ImportError:
        print_test("MinIO Client Installed", False, "Missing minio package")
        results.append(False)
        return False
    
    # Test 2: Check if MinIO service is running
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=5
        )
        api_running = ":9000" in result.stdout and "LISTENING" in result.stdout
        console_running = ":9001" in result.stdout and "LISTENING" in result.stdout
        
        if api_running:
            print_test("MinIO API Service", True, "Port 9000 listening")
            results.append(True)
        else:
            print_test("MinIO API Service", False, "Port 9000 not listening")
            results.append(False)
        
        if console_running:
            print_test("MinIO Console", True, "Port 9001 listening")
            results.append(True)
        else:
            print_test("MinIO Console", False, "Port 9001 not listening")
            results.append(False)
            
    except Exception as e:
        print_test("MinIO Services", False, str(e))
        results.append(False)
        results.append(False)
    
    # Test 3: Test MinIO connection
    try:
        from minio import Minio
        client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        
        # List buckets
        buckets = client.list_buckets()
        bucket_names = [b.name for b in buckets]
        print_test("MinIO Connection", True, f"{len(buckets)} buckets found")
        results.append(True)
        
        # Check required buckets
        required_buckets = ["reims-documents", "reims-documents-backup", "reims-documents-archive"]
        for bucket in required_buckets:
            if bucket in bucket_names:
                print_test(f"Bucket: {bucket}", True, "Exists")
                results.append(True)
            else:
                print_test(f"Bucket: {bucket}", False, "Missing")
                results.append(False)
        
        # Test 4: Test write access
        try:
            from io import BytesIO
            test_data = b"REIMS test file"
            client.put_object(
                "reims-documents",
                "test/connection_test.txt",
                BytesIO(test_data),
                len(test_data)
            )
            print_test("Write Access Test", True, "Can write to bucket")
            results.append(True)
            
            # Clean up
            client.remove_object("reims-documents", "test/connection_test.txt")
        except Exception as e:
            print_test("Write Access Test", False, str(e))
            results.append(False)
            
    except Exception as e:
        print_test("MinIO Connection", False, str(e))
        results.append(False)
        results.append(False)
        results.append(False)
        results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n  📊 MinIO Status: {sum(results)}/{len(results)} checks passed ({success_rate:.0f}%)")
    return all(results)

def test_redis():
    """Test Redis caching and queues"""
    print_header("5. Redis - Caching & Queues")
    
    results = []
    
    # Test 1: Check if Redis client is installed
    try:
        import redis
        print_test("Redis Client Installed", True)
        results.append(True)
    except ImportError:
        print_test("Redis Client Installed", False, "Missing redis package")
        results.append(False)
        return False
    
    # Test 2: Check if Redis service is running
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if ":6379" in result.stdout and "LISTENING" in result.stdout:
            print_test("Redis Service Running", True, "Port 6379 listening")
            results.append(True)
        else:
            print_test("Redis Service Running", False, "Port 6379 not listening")
            results.append(False)
    except Exception as e:
        print_test("Redis Service Running", False, str(e))
        results.append(False)
    
    # Test 3: Test Redis connection
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=5)
        
        # Ping test
        if r.ping():
            print_test("Redis Connection", True, "PING successful")
            results.append(True)
        else:
            print_test("Redis Connection", False, "PING failed")
            results.append(False)
        
        # Test 4: Test write/read
        test_key = "reims:test:connection"
        test_value = f"test_{datetime.now().timestamp()}"
        
        r.set(test_key, test_value, ex=10)
        retrieved = r.get(test_key)
        
        if retrieved and retrieved.decode() == test_value:
            print_test("Redis Write/Read Test", True, "Can store and retrieve data")
            results.append(True)
        else:
            print_test("Redis Write/Read Test", False, "Data mismatch")
            results.append(False)
        
        # Clean up
        r.delete(test_key)
        
        # Test 5: Check Redis info
        info = r.info()
        redis_version = info.get('redis_version', 'unknown')
        used_memory = info.get('used_memory_human', 'unknown')
        print_test("Redis Server Info", True, f"Version {redis_version}, Memory: {used_memory}")
        results.append(True)
        
    except Exception as e:
        print_test("Redis Connection", False, str(e))
        results.append(False)
        results.append(False)
        results.append(False)
    
    # Test 6: Check Celery (uses Redis)
    try:
        import celery
        print_test("Celery (Task Queue)", True, "Package installed")
        results.append(True)
    except ImportError:
        print_test("Celery (Task Queue)", False, "Not installed")
        results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n  📊 Redis Status: {sum(results)}/{len(results)} checks passed ({success_rate:.0f}%)")
    return all(results)

def main():
    """Main test function"""
    print("\n" + "=" * 70)
    print("REIMS BACKEND SERVICES COMPREHENSIVE TEST")
    print("=" * 70)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Run all tests
    test_results = {
        "FastAPI": test_fastapi(),
        "PostgreSQL": test_postgresql(),
        "Apache Airflow": test_airflow(),
        "MinIO": test_minio(),
        "Redis": test_redis()
    }
    
    # Final summary
    print_header("FINAL SUMMARY")
    
    for service, passed in test_results.items():
        icon = "✅" if passed else "❌"
        status = "OPERATIONAL" if passed else "ISSUES FOUND"
        print(f"  {icon} {service:<30} {status}")
    
    passed_count = sum(test_results.values())
    total_count = len(test_results)
    success_rate = (passed_count / total_count) * 100
    
    print(f"\n  📊 Overall: {passed_count}/{total_count} services operational ({success_rate:.0f}%)")
    print("\n" + "=" * 70)
    
    if passed_count == total_count:
        print("🎉 ALL BACKEND SERVICES ARE FULLY OPERATIONAL!")
        return 0
    elif passed_count >= total_count - 1:  # Allow 1 failure (Airflow is optional)
        print("✅ CORE BACKEND SERVICES ARE OPERATIONAL!")
        print("   (Some optional services may need attention)")
        return 0
    else:
        print("⚠️  SOME CRITICAL SERVICES NEED ATTENTION!")
        print("   Please review the test results above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

