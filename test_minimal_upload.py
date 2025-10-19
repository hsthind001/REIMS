#!/usr/bin/env python3
"""
Minimal upload test with detailed error output
"""
import sys
import traceback

try:
    import requests
    print("✅ requests module imported")
    
    # Test health endpoint first
    health_url = "http://localhost:8001/health"
    print(f"\n📡 Testing health endpoint: {health_url}")
    health_response = requests.get(health_url, timeout=5)
    print(f"   Status: {health_response.status_code}")
    print(f"   Response: {health_response.text}")
    
    # Test upload
    upload_url = "http://localhost:8001/api/documents/upload"
    print(f"\n📤 Testing upload endpoint: {upload_url}")
    
    with open("test_upload_financial.csv", 'rb') as f:
        files = {'file': ('test.csv', f, 'text/csv')}
        data = {
            'property_id': '1',
            'document_type': 'financial_statement'
        }
        
        print(f"   Sending file: test_upload_financial.csv")
        print(f"   Property ID: 1")
        
        response = requests.post(
            upload_url,
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"\n📊 Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Body: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS!")
            print(response.json())
        else:
            print(f"\n❌ FAILED: {response.status_code}")
            print(f"   Error: {response.text}")
            
except FileNotFoundError as e:
    print(f"❌ File not found: {e}")
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection error: {e}")
    print(f"   Is the backend running on http://localhost:8001?")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print(f"\nFull traceback:")
    traceback.print_exc()















