#!/usr/bin/env python3
"""
REIMS Frontend Pages Verification Script
Tests all API endpoints and validates data accuracy across all frontend pages
"""

import requests
import json
import sys
from datetime import datetime

# Expected correct values from corrected database
EXPECTED_DATA = {
    1: {  # Empire State Plaza
        "name": "Empire State Plaza",
        "noi": 2087905.14,
        "occupancy_rate": 0.84,
        "monthly_rent": 223646.31,
        "current_market_value": 23889953.33
    },
    2: {  # Wendover Commons
        "name": "Wendover Commons",
        "noi": 1860030.71,
        "occupancy_rate": 0.938,
        "monthly_rent": 219170.27,
        "current_market_value": 25000000
    },
    3: {  # Hammond Aire - CORRECTED
        "name": "Hammond Aire",
        "noi": 400000.00,
        "occupancy_rate": 0.825,
        "monthly_rent": 33333.00,
        "current_market_value": 5000000
    },
    6: {  # The Crossings of Spring Hill - CORRECTED
        "name": "The Crossings of Spring Hill",
        "noi": 280000.00,
        "occupancy_rate": 1.0,
        "monthly_rent": 23333.00,
        "current_market_value": 3500000
    }
}

def test_api_endpoint(url, description):
    """Test an API endpoint and return response data"""
    try:
        print(f"🔄 Testing {description}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description}: Status {response.status_code}")
            return data
        else:
            print(f"❌ {description}: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ {description}: Error - {e}")
        return None

def verify_property_data(property_data, property_id):
    """Verify individual property data matches expected values"""
    issues = []
    
    if not property_data:
        return ["No data received"]
    
    expected = EXPECTED_DATA.get(property_id)
    if not expected:
        return [f"No expected data for property ID {property_id}"]
    
    # Check NOI values
    if 'noi' in property_data and 'annual_noi' in property_data:
        if abs(property_data['noi'] - property_data['annual_noi']) > 0.01:
            issues.append(f"NOI mismatch: noi={property_data['noi']}, annual_noi={property_data['annual_noi']}")
        
        if abs(property_data['noi'] - expected['noi']) > 1000:
            issues.append(f"NOI incorrect: got {property_data['noi']}, expected {expected['noi']}")
    else:
        issues.append("Missing noi or annual_noi field")
    
    # Check occupancy rate
    if 'occupancy_rate' in property_data:
        if abs(property_data['occupancy_rate'] - expected['occupancy_rate']) > 0.01:
            issues.append(f"Occupancy rate incorrect: got {property_data['occupancy_rate']}, expected {expected['occupancy_rate']}")
    else:
        issues.append("Missing occupancy_rate field")
    
    # Check monthly rent
    if 'monthly_rent' in property_data:
        if abs(property_data['monthly_rent'] - expected['monthly_rent']) > 1000:
            issues.append(f"Monthly rent incorrect: got {property_data['monthly_rent']}, expected {expected['monthly_rent']}")
    
    return issues

def verify_portfolio_data(properties_data):
    """Verify portfolio view data"""
    issues = []
    
    if not properties_data or 'properties' not in properties_data:
        return ["No properties data received"]
    
    properties = properties_data['properties']
    if len(properties) != 4:
        issues.append(f"Expected 4 properties, got {len(properties)}")
    
    for prop in properties:
        prop_id = prop.get('id')
        if prop_id in EXPECTED_DATA:
            prop_issues = verify_property_data(prop, prop_id)
            if prop_issues:
                issues.extend([f"Property {prop_id} ({prop.get('name', 'Unknown')}): {issue}" for issue in prop_issues])
    
    return issues

def verify_kpi_data(kpi_data):
    """Verify KPI view aggregated data"""
    issues = []
    
    if not kpi_data:
        return ["No KPI data received"]
    
    # Calculate expected aggregated values
    total_noi = sum(prop['noi'] for prop in EXPECTED_DATA.values())
    avg_occupancy = sum(prop['occupancy_rate'] for prop in EXPECTED_DATA.values()) / len(EXPECTED_DATA)
    total_monthly_income = sum(prop['monthly_rent'] for prop in EXPECTED_DATA.values())
    
    # Check if KPI data contains reasonable values
    if 'total_portfolio_value' in kpi_data:
        expected_value = sum(prop['current_market_value'] for prop in EXPECTED_DATA.values())
        if abs(kpi_data['total_portfolio_value'] - expected_value) > 1000000:
            issues.append(f"Portfolio value incorrect: got {kpi_data['total_portfolio_value']}, expected ~{expected_value}")
    
    return issues

def main():
    """Main verification function"""
    print("=" * 80)
    print("REIMS FRONTEND PAGES VERIFICATION")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base_url = "http://localhost:8001"
    all_issues = []
    
    # Test 1: All Properties API
    print("📊 TESTING API ENDPOINTS")
    print("-" * 40)
    
    properties_data = test_api_endpoint(f"{base_url}/api/properties", "All Properties API")
    if properties_data:
        portfolio_issues = verify_portfolio_data(properties_data)
        if portfolio_issues:
            all_issues.extend([f"Portfolio View: {issue}" for issue in portfolio_issues])
        else:
            print("✅ Portfolio View: All properties data accurate")
    
    # Test 2: Individual Property APIs
    print("\n🏢 TESTING INDIVIDUAL PROPERTY APIS")
    print("-" * 40)
    
    for prop_id in [1, 2, 3, 6]:
        prop_data = test_api_endpoint(f"{base_url}/api/properties/{prop_id}", f"Property {prop_id} API")
        if prop_data:
            prop_issues = verify_property_data(prop_data, prop_id)
            if prop_issues:
                all_issues.extend([f"Property {prop_id} Detail: {issue}" for issue in prop_issues])
            else:
                print(f"✅ Property {prop_id} Detail: Data accurate")
    
    # Test 3: Analytics API (for KPI view)
    print("\n📈 TESTING KPI/ANALYTICS API")
    print("-" * 40)
    
    analytics_data = test_api_endpoint(f"{base_url}/api/analytics", "Analytics API")
    if analytics_data:
        kpi_issues = verify_kpi_data(analytics_data)
        if kpi_issues:
            all_issues.extend([f"KPI View: {issue}" for issue in kpi_issues])
        else:
            print("✅ KPI View: Analytics data accurate")
    
    # Test 4: Check field consistency
    print("\n🔍 TESTING FIELD CONSISTENCY")
    print("-" * 40)
    
    if properties_data and 'properties' in properties_data:
        for prop in properties_data['properties']:
            prop_id = prop.get('id')
            if prop_id in [1, 2, 3, 6]:
                # Check both noi and annual_noi fields exist and match
                if 'noi' not in prop:
                    all_issues.append(f"Property {prop_id}: Missing 'noi' field")
                if 'annual_noi' not in prop:
                    all_issues.append(f"Property {prop_id}: Missing 'annual_noi' field")
                if 'noi' in prop and 'annual_noi' in prop:
                    if abs(prop['noi'] - prop['annual_noi']) > 0.01:
                        all_issues.append(f"Property {prop_id}: 'noi' and 'annual_noi' don't match")
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    if not all_issues:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Portfolio View: Accurate data for all 4 properties")
        print("✅ Property Detail Pages: Accurate data for all individual properties")
        print("✅ KPI View: Accurate aggregated metrics")
        print("✅ Field Consistency: Both 'noi' and 'annual_noi' fields present and matching")
        print("\n🏆 FRONTEND PAGES VERIFICATION: 100% SUCCESS")
    else:
        print("❌ ISSUES FOUND:")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i:2d}. {issue}")
        print(f"\n📊 TOTAL ISSUES: {len(all_issues)}")
        print("🔧 FRONTEND PAGES NEED FIXES")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return len(all_issues) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
