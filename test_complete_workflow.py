#!/usr/bin/env python3
"""
Test the complete workflow: Frontend → MinIO → Database
"""

import requests
import json
from pathlib import Path

def test_upload_workflow():
    print("=== Testing Complete Upload Workflow ===")
    
    # Test file
    test_file = "test_database_integration.txt"
    property_id = "TEST-DB-WORKFLOW-001"
    
    try:
        # 1. Test upload endpoint
        print("\n1. Testing file upload...")
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'text/plain')}
            data = {'property_id': property_id}
            
            response = requests.post(
                'http://localhost:8001/api/documents/upload',
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            upload_result = response.json()
            print("✅ Upload successful!")
            print(f"   Document ID: {upload_result['document_id']}")
            print(f"   Storage: {upload_result.get('storage_location')}")
            print(f"   MinIO: {upload_result.get('minio_location')}")
            print(f"   Database: {upload_result.get('database_status')}")
            
            # Show workflow steps
            if 'workflow' in upload_result:
                print("\n   Workflow Steps:")
                for step, status in upload_result['workflow'].items():
                    print(f"     {step}: {status}")
            
            document_id = upload_result['document_id']
            
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # 2. Test document retrieval
        print("\n2. Testing document retrieval...")
        
        response = requests.get('http://localhost:8001/api/documents')
        if response.status_code == 200:
            docs_result = response.json()
            print(f"✅ Retrieved {docs_result['total']} documents from {docs_result.get('source', 'unknown')}")
            
            # Find our uploaded document
            our_doc = None
            for doc in docs_result['documents']:
                if doc.get('document_id') == document_id:
                    our_doc = doc
                    break
            
            if our_doc:
                print(f"✅ Found our document: {our_doc['original_filename']}")
                print(f"   Property ID: {our_doc['property_id']}")
                print(f"   Storage Type: {our_doc.get('storage_type', 'unknown')}")
                print(f"   MinIO URL: {our_doc.get('minio_url', 'none')}")
            else:
                print("❌ Could not find our uploaded document in the list")
        else:
            print(f"❌ Document retrieval failed: {response.status_code}")
            return False
            
        # 3. Test property-specific retrieval
        print(f"\n3. Testing property-specific retrieval for {property_id}...")
        
        response = requests.get(f'http://localhost:8001/api/documents/property/{property_id}')
        if response.status_code == 200:
            property_docs = response.json()
            print(f"✅ Retrieved {property_docs['total']} documents for property {property_id}")
            print(f"   Source: {property_docs.get('source', 'unknown')}")
        else:
            print(f"❌ Property document retrieval failed: {response.status_code}")
            
        # 4. Test analytics
        print("\n4. Testing analytics...")
        
        response = requests.get('http://localhost:8001/api/analytics')
        if response.status_code == 200:
            analytics = response.json()
            print(f"✅ Analytics retrieved:")
            print(f"   Total documents: {analytics.get('total_documents', 0)}")
            print(f"   MinIO stored: {analytics.get('minio_stored_documents', 0)}")
            print(f"   Source: {analytics.get('source', 'unknown')}")
        else:
            print(f"❌ Analytics failed: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_backend_health():
    print("=== Testing Backend Health ===")
    
    try:
        response = requests.get('http://localhost:8001/health')
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

if __name__ == "__main__":
    if test_backend_health():
        test_upload_workflow()
    else:
        print("Cannot proceed - backend is not responding")