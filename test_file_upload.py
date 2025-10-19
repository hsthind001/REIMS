#!/usr/bin/env python3
"""
Test file upload functionality end-to-end
"""

import requests
import json
import time

# Test configuration
BACKEND_URL = "http://localhost:8001"
TEST_FILE = "test_upload_financial.csv"
PROPERTY_ID = "1"

print("🧪 TESTING FILE UPLOAD FUNCTIONALITY\n")
print("━" * 60)

# Step 1: Upload file
print("\n📤 Step 1: Uploading file...")
print(f"   File: {TEST_FILE}")
print(f"   Property ID: {PROPERTY_ID}")

try:
    with open(TEST_FILE, 'rb') as f:
        files = {'file': (TEST_FILE, f, 'text/csv')}
        data = {
            'property_id': PROPERTY_ID,
            'document_type': 'financial_statement'
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/documents/upload",
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            upload_result = response.json()
            print(f"   ✅ Success!")
            print(f"   Document ID: {upload_result['data']['document_id']}")
            print(f"   Status: {upload_result['data']['status']}")
            
            document_id = upload_result['data']['document_id']
            
            # Step 2: Check document status
            print(f"\n📊 Step 2: Checking document status...")
            time.sleep(1)
            
            status_response = requests.get(
                f"{BACKEND_URL}/api/documents/{document_id}/status",
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                print(f"   ✅ Status retrieved!")
                print(f"   Document Status: {status_result['data']['status']}")
                print(f"   File Name: {status_result['data']['file_name']}")
                
                # Step 3: Check if in database
                print(f"\n💾 Step 3: Verifying database record...")
                import sqlite3
                conn = sqlite3.connect('reims.db')
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, file_name, status FROM financial_documents WHERE id = ?",
                    (document_id,)
                )
                row = cursor.fetchone()
                if row:
                    print(f"   ✅ Record found in database!")
                    print(f"   ID: {row[0]}")
                    print(f"   File: {row[1]}")
                    print(f"   Status: {row[2]}")
                else:
                    print(f"   ❌ Record not found in database")
                conn.close()
                
                print("\n" + "━" * 60)
                print("✅ FILE UPLOAD TEST COMPLETED SUCCESSFULLY!")
                print("━" * 60)
                
            else:
                print(f"   ❌ Failed to get status: {status_response.status_code}")
                print(f"   Error: {status_response.text}")
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
except FileNotFoundError:
    print(f"   ❌ Error: File '{TEST_FILE}' not found")
except requests.exceptions.ConnectionError:
    print(f"   ❌ Error: Could not connect to backend at {BACKEND_URL}")
    print(f"   Make sure backend is running: python run_backend.py")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()















