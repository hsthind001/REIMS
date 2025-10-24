"""
Test Validation Endpoints

Tests the property name validation API endpoints.
"""

import requests
import json

def test_validation_endpoints():
    """Test all validation endpoints"""
    
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Property Name Validation Endpoints...")
    
    # Test validation statistics
    print("\n📊 Testing validation statistics endpoint:")
    try:
        response = requests.get(f"{base_url}/api/validation/statistics")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Success: {data['success']}")
            print(f"  📈 Statistics: {data['statistics']}")
        else:
            print(f"  ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    
    # Test validation queue
    print("\n📋 Testing validation queue endpoint:")
    try:
        response = requests.get(f"{base_url}/api/validation/queue")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Success: {data['success']}")
            print(f"  📝 Queue count: {data['count']}")
        else:
            print(f"  ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    
    # Test property aliases
    print("\n🏷️ Testing property aliases endpoint:")
    try:
        response = requests.get(f"{base_url}/api/validation/aliases/1")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Success: {data['success']}")
            print(f"  🏢 Property ID: {data['property_id']}")
            print(f"  📝 Aliases count: {data['count']}")
            print("  📋 Aliases:")
            for alias in data['aliases']:
                primary_status = "PRIMARY" if alias['is_primary'] else "alias"
                print(f"    - {alias['alias_name']} ({alias['alias_type']}) - {primary_status}")
        else:
            print(f"  ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    
    print("\n✅ Validation endpoints test completed")

if __name__ == "__main__":
    test_validation_endpoints()
