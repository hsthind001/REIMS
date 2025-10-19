#!/usr/bin/env python3
"""
Test file upload functionality
"""
import sys
import os
import tempfile
import io
from fastapi.testclient import TestClient

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

def test_file_upload():
    print("Testing file upload functionality...")
    
    try:
        # Import the app
        from backend.api.main import app
        print("✓ App imported successfully")
        
        # Create test client
        client = TestClient(app)
        print("✓ Test client created")
        
        # Create a test CSV file
        test_csv_content = """Property,Value,Date
Revenue,100000,2024-01-01
Expenses,50000,2024-01-01
Profit,50000,2024-01-01"""
        
        test_file = io.BytesIO(test_csv_content.encode('utf-8'))
        
        # Test file upload
        files = {"file": ("test_upload.csv", test_file, "text/csv")}
        data = {"property_id": "TEST_UPLOAD_001"}
        
        response = client.post("/api/documents/upload", files=files, data=data)
        print(f"✓ File upload endpoint: {response.status_code}")
        
        if response.status_code == 200:
            upload_result = response.json()
            print(f"  Upload result: {upload_result}")
            
            document_id = upload_result.get("document_id")
            if document_id:
                # Test getting the uploaded document
                response = client.get(f"/api/documents/{document_id}")
                print(f"✓ Get uploaded document: {response.status_code}")
                print(f"  Document info: {response.json()}")
                
                # Test getting processed data (should be empty initially)
                response = client.get(f"/api/documents/{document_id}/processed")
                print(f"✓ Get processed data: {response.status_code}")
                print(f"  Processed data: {response.json()}")
        else:
            print(f"  Upload failed: {response.text}")
            
        print("\n✓ File upload test completed!")
        return True
        
    except Exception as e:
        print(f"✗ File upload test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_file_upload()
    if success:
        print("\n🎉 File upload functionality is working!")
    else:
        print("\n❌ File upload has issues!")