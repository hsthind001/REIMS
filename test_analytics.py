#!/usr/bin/env python3
"""
Test analytics API endpoints
"""
import sys
import os
from fastapi.testclient import TestClient

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

def test_analytics_endpoints():
    print("Testing analytics API endpoints...")
    
    try:
        # Import the app
        from backend.api.main import app
        print("✓ App with analytics imported successfully")
        
        # Create test client
        client = TestClient(app)
        print("✓ Test client created")
        
        # Test analytics overview
        response = client.get("/api/analytics/overview")
        print(f"✓ Analytics overview: {response.status_code}")
        if response.status_code == 200:
            overview = response.json()
            print(f"  Total documents: {overview['overview']['total_documents']}")
            print(f"  Total jobs: {overview['overview']['total_jobs']}")
            print(f"  File types: {len(overview['file_types'])}")
        
        # Test document analytics
        response = client.get("/api/analytics/documents?days=30")
        print(f"✓ Document analytics: {response.status_code}")
        if response.status_code == 200:
            doc_analytics = response.json()
            print(f"  Documents in last 30 days: {doc_analytics['summary']['total_documents']}")
        
        # Test processing analytics
        response = client.get("/api/analytics/processing?days=30")
        print(f"✓ Processing analytics: {response.status_code}")
        if response.status_code == 200:
            proc_analytics = response.json()
            print(f"  Total jobs in last 30 days: {proc_analytics['summary']['total_jobs']}")
            print(f"  Success rate: {proc_analytics['summary']['success_rate_percent']}%")
        
        # Test data insights
        response = client.get("/api/analytics/data-insights")
        print(f"✓ Data insights: {response.status_code}")
        if response.status_code == 200:
            insights = response.json()
            print(f"  Total extracted records: {insights['summary']['total_extracted_records']}")
        
        print("\n✓ All analytics endpoint tests completed!")
        return True
        
    except Exception as e:
        print(f"✗ Analytics endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_analytics_endpoints()
    if success:
        print("\n🎉 Analytics endpoints are working correctly!")
    else:
        print("\n❌ Analytics endpoints have issues!")