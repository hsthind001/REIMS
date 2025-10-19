#!/usr/bin/env python3
"""
REIMS System Status and Verification
Tests all services and provides comprehensive status report
"""

import requests
import time
import json
from datetime import datetime

def test_service(url, name, timeout=5):
    """Test if a service is responsive"""
    try:
        response = requests.get(url, timeout=timeout)
        return {
            'name': name,
            'status': 'UP' if response.status_code == 200 else f'ERROR {response.status_code}',
            'response_time': response.elapsed.total_seconds(),
            'url': url
        }
    except Exception as e:
        return {
            'name': name,
            'status': 'DOWN',
            'error': str(e),
            'url': url
        }

def test_minio_integration():
    """Test MinIO integration"""
    try:
        from minio import Minio
        client = Minio("localhost:9000", "minioadmin", "minioadmin", secure=False)
        buckets = list(client.list_buckets())
        objects = list(client.list_objects("reims-documents", recursive=True))
        
        return {
            'status': 'UP',
            'buckets': len(buckets),
            'objects': len(objects),
            'bucket_names': [b.name for b in buckets]
        }
    except Exception as e:
        return {
            'status': 'DOWN',
            'error': str(e)
        }

def test_database():
    """Test database connectivity"""
    try:
        import sqlite3
        conn = sqlite3.connect("reims.db")
        cursor = conn.cursor()
        
        # Test documents table
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        
        # Test MinIO integration fields
        cursor.execute("SELECT COUNT(*) FROM documents WHERE storage_type = 'local_and_minio'")
        minio_docs = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'status': 'UP',
            'total_documents': doc_count,
            'minio_documents': minio_docs,
            'database_type': 'SQLite'
        }
    except Exception as e:
        return {
            'status': 'DOWN',
            'error': str(e)
        }

def test_upload_workflow():
    """Test the complete upload workflow"""
    try:
        # Create test file
        test_content = f"Test upload workflow\nTimestamp: {datetime.now().isoformat()}"
        test_filename = "workflow_test.txt"
        
        with open(test_filename, 'w') as f:
            f.write(test_content)
        
        # Upload via API
        with open(test_filename, 'rb') as f:
            files = {'file': (test_filename, f, 'text/plain')}
            data = {'property_id': 'WORKFLOW-TEST'}
            
            response = requests.post(
                'http://localhost:8001/api/documents/upload',
                files=files,
                data=data,
                timeout=10
            )
        
        # Clean up
        import os
        os.unlink(test_filename)
        
        if response.status_code == 200:
            result = response.json()
            return {
                'status': 'SUCCESS',
                'document_id': result.get('document_id'),
                'database_status': result.get('database_status'),
                'minio_location': result.get('minio_location'),
                'workflow_steps': result.get('workflow', {})
            }
        else:
            return {
                'status': 'FAILED',
                'error': f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'error': str(e)
        }

def main():
    """Run comprehensive system verification"""
    print("🔍 REIMS SYSTEM VERIFICATION")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test all services
    services = [
        ("http://localhost:5173", "Frontend UI"),
        ("http://localhost:8001/health", "Backend API"),
        ("http://localhost:9001", "MinIO Console"),
        ("http://localhost:8001/api/documents", "Documents API"),
        ("http://localhost:8001/api/analytics", "Analytics API")
    ]
    
    print("🌐 Service Status:")
    all_services_up = True
    
    for url, name in services:
        result = test_service(url, name)
        status_icon = "✅" if result['status'] == 'UP' else "❌"
        print(f"   {status_icon} {name}: {result['status']}")
        if 'response_time' in result:
            print(f"      Response time: {result['response_time']:.3f}s")
        if 'error' in result:
            print(f"      Error: {result['error']}")
        
        if result['status'] != 'UP':
            all_services_up = False
    
    print()
    
    # Test MinIO integration
    print("🗂️ MinIO Integration:")
    minio_result = test_minio_integration()
    if minio_result['status'] == 'UP':
        print(f"   ✅ MinIO: {minio_result['status']}")
        print(f"      Buckets: {minio_result['buckets']}")
        print(f"      Objects: {minio_result['objects']}")
        print(f"      Bucket names: {', '.join(minio_result['bucket_names'])}")
    else:
        print(f"   ❌ MinIO: {minio_result['status']}")
        print(f"      Error: {minio_result.get('error', 'Unknown error')}")
        all_services_up = False
    
    print()
    
    # Test database
    print("🗄️ Database Integration:")
    db_result = test_database()
    if db_result['status'] == 'UP':
        print(f"   ✅ Database: {db_result['status']} ({db_result['database_type']})")
        print(f"      Total documents: {db_result['total_documents']}")
        print(f"      MinIO-integrated docs: {db_result['minio_documents']}")
    else:
        print(f"   ❌ Database: {db_result['status']}")
        print(f"      Error: {db_result.get('error', 'Unknown error')}")
        all_services_up = False
    
    print()
    
    # Test complete workflow if all services are up
    if all_services_up:
        print("🔄 Testing Complete Workflow:")
        workflow_result = test_upload_workflow()
        
        if workflow_result['status'] == 'SUCCESS':
            print("   ✅ Upload workflow: SUCCESS")
            print(f"      Document ID: {workflow_result['document_id']}")
            print(f"      Database status: {workflow_result['database_status']}")
            print(f"      MinIO location: {workflow_result.get('minio_location', 'None')}")
            
            # Show workflow steps
            if 'workflow_steps' in workflow_result:
                print("      Workflow steps:")
                for step, status in workflow_result['workflow_steps'].items():
                    icon = "✅" if "✅" in status else "❌" if "❌" in status else "🔄"
                    print(f"        {step}: {icon}")
        else:
            print(f"   ❌ Upload workflow: {workflow_result['status']}")
            print(f"      Error: {workflow_result.get('error', 'Unknown error')}")
            all_services_up = False
    else:
        print("🔄 Skipping workflow test - some services are down")
    
    print()
    print("=" * 50)
    
    if all_services_up:
        print("🎉 ✅ ALL SYSTEMS OPERATIONAL!")
        print()
        print("🚀 REIMS is ready for testing:")
        print("   • Frontend:     http://localhost:5173")
        print("   • Backend API:  http://localhost:8001")
        print("   • MinIO Console: http://localhost:9001")
        print()
        print("💡 Test the system:")
        print("   1. Open the frontend in your browser")
        print("   2. Go to Document Management section")
        print("   3. Upload files with Property IDs")
        print("   4. Files will be stored in MinIO and tracked in database")
        print()
        print("📊 Monitoring commands:")
        print("   • python test_data_flow.py - Test complete data flow")
        print("   • python monitor_data_flow.py - Monitor system in real-time")
        print("   • python verify_database.py - Check database contents")
        
    else:
        print("❌ SOME SYSTEMS ARE NOT OPERATIONAL")
        print()
        print("🔧 Troubleshooting:")
        print("   • Ensure all services are started:")
        print("     - MinIO: ./minio.exe server minio-data --console-address :9001")
        print("     - Backend: C:/REIMS/queue_service/venv/Scripts/python.exe simple_backend.py")
        print("     - Frontend: cd frontend && npm run dev")
        print("   • Check for port conflicts")
        print("   • Verify dependencies are installed")

if __name__ == "__main__":
    main()