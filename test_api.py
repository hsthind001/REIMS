#!/usr/bin/env python3
"""
Simple test to verify the API endpoints work
"""
import requests
import json
import time
from pathlib import Path

def test_api():
    base_url = "http://localhost:8001"
    
    # Test health endpoint
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health endpoint working")
            print(f"Response: {response.json()}")
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health endpoint error: {e}")
        return False
    
    # Test documents list endpoint
    print("\nTesting documents list endpoint...")
    try:
        response = requests.get(f"{base_url}/api/documents", timeout=5)
        if response.status_code == 200:
            print("✓ Documents list endpoint working")
            data = response.json()
            print(f"Response: {data}")
        else:
            print(f"✗ Documents list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Documents list error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting API test...\n")
    if test_api():
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")