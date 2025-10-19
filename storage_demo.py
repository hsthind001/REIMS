#!/usr/bin/env python3
"""
REIMS Storage Service Demo
Demonstrates storage integration without database dependencies
"""

import requests
import json
from datetime import datetime
import os
import tempfile


def test_storage_service():
    """Test the storage service endpoints"""
    base_url = "http://localhost:8002"
    
    print("🧪 REIMS Storage Service Demo")
    print("=" * 50)
    
    # Test health check
    try:
        print("\n1. Testing Health Check...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Storage service is healthy")
            health_data = response.json()
            print(f"   MinIO Status: {health_data.get('minio_status', 'Unknown')}")
            print(f"   Service: {health_data.get('service', 'Unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test statistics
    try:
        print("\n2. Testing Storage Statistics...")
        response = requests.get(f"{base_url}/statistics")
        if response.status_code == 200:
            print("✅ Statistics retrieved successfully")
            stats = response.json()
            print(f"   Service Status: {stats.get('service_status', 'Unknown')}")
            if 'data' in stats:
                data = stats['data']
                print(f"   Total Storage: {data.get('total_storage_used', 0)} bytes")
                if 'primary_bucket' in data:
                    bucket = data['primary_bucket']
                    print(f"   Objects: {bucket.get('object_count', 0)}")
        else:
            print(f"❌ Statistics failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Statistics error: {e}")
    
    # Test file upload (create a temporary test file)
    try:
        print("\n3. Testing File Upload...")
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(f"REIMS Storage Test File\nCreated: {datetime.now()}\n")
            tmp_file.write("This is a test file for the REIMS storage service.\n")
            tmp_file_path = tmp_file.name
        
        # Upload the file
        with open(tmp_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'metadata': json.dumps({
                    'description': 'Test file upload',
                    'type': 'demo',
                    'created_by': 'storage_demo'
                })
            }
            response = requests.post(f"{base_url}/upload", files=files, data=data)
        
        if response.status_code == 200:
            print("✅ File uploaded successfully")
            upload_result = response.json()
            print(f"   Document ID: {upload_result.get('document_id', 'Unknown')}")
            print(f"   File Size: {upload_result.get('file_size', 0)} bytes")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
    
    # Test documents list
    try:
        print("\n4. Testing Documents List...")
        response = requests.get(f"{base_url}/documents")
        if response.status_code == 200:
            print("✅ Documents retrieved successfully")
            docs = response.json()
            print(f"   Total documents: {len(docs)}")
            for doc in docs[:3]:  # Show first 3
                print(f"   - {doc.get('filename', 'Unknown')} ({doc.get('size', 0)} bytes)")
        else:
            print(f"❌ Documents list failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Documents error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Demo completed!")
    print("\n📊 Storage Analytics Integration:")
    print("- Frontend dashboard shows storage statistics")
    print("- Real-time storage usage monitoring")
    print("- MinIO integration with versioning")
    print("- Backup and archival capabilities")


if __name__ == "__main__":
    test_storage_service()