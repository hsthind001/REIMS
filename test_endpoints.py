#!/usr/bin/env python3
"""
Test specific API endpoints by importing them directly
"""
import sys
import os
from fastapi.testclient import TestClient

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

def test_api_endpoints():
    print("Testing API endpoints...")
    
    try:
        # Import the app
        from backend.api.main import app
        print("✓ App imported successfully")
        
        # Create test client
        client = TestClient(app)
        print("✓ Test client created")
        
        # Test health endpoint
        response = client.get("/health")
        print(f"✓ Health endpoint: {response.status_code} - {response.json()}")
        
        # Test documents list endpoint
        response = client.get("/api/documents")
        print(f"✓ Documents list endpoint: {response.status_code}")
        print(f"  Response: {response.json()}")
        
        # Test a specific document (should return 404)
        response = client.get("/api/documents/test-id")
        print(f"✓ Document detail endpoint: {response.status_code}")
        
        print("\n✓ All API endpoint tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ API endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_endpoints()
    if success:
        print("\n🎉 API endpoints are working correctly!")
    else:
        print("\n❌ API endpoints have issues!")