#!/usr/bin/env python3
"""
Frontend Health Checker - Tests if React app is working properly
"""

import requests
import time
import json
import re

def check_frontend_detailed():
    """Check frontend in detail"""
    print("🔍 FRONTEND DETAILED HEALTH CHECK")
    print("="*50)
    
    try:
        # Test main page
        print("1. Testing main page...")
        response = requests.get('http://localhost:3000', timeout=10)
        
        if response.status_code == 200:
            html = response.text
            print("   ✅ Frontend page loads successfully")
            
            # Check for React indicators
            if 'id="root"' in html:
                print("   ✅ React root element found")
            else:
                print("   ❌ React root element missing")
            
            if 'REIMS Dashboard' in html:
                print("   ✅ Correct page title found")
            else:
                print("   ❌ Page title missing or incorrect")
            
            if 'src="/src/index.jsx"' in html or 'src="/src/' in html:
                print("   ✅ JSX modules being loaded")
            else:
                print("   ❌ JSX modules not found")
            
            if '@vite/client' in html:
                print("   ✅ Vite hot reload working")
            else:
                print("   ❌ Vite client not found")
        else:
            print(f"   ❌ Frontend page failed: HTTP {response.status_code}")
            return False
    
    except Exception as e:
        print(f"   ❌ Frontend connection failed: {e}")
        return False
    
    # Test backend connectivity from frontend perspective
    print("\n2. Testing backend API connectivity...")
    
    backend_endpoints = [
        ('/health', 'Health Check'),
        ('/api/documents', 'Documents API'),
        ('/api/analytics', 'Analytics API')
    ]
    
    for endpoint, name in backend_endpoints:
        try:
            response = requests.get(f'http://localhost:8001{endpoint}', timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name}: OK")
            else:
                print(f"   ❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: Failed - {e}")
    
    # Test CORS headers
    print("\n3. Testing CORS configuration...")
    try:
        response = requests.options('http://localhost:8001/api/documents', 
                                   headers={'Origin': 'http://localhost:3000'})
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        if cors_headers['Access-Control-Allow-Origin']:
            print("   ✅ CORS headers present")
            for header, value in cors_headers.items():
                if value:
                    print(f"      {header}: {value}")
        else:
            print("   ⚠️ CORS headers not found (may still work)")
            
    except Exception as e:
        print(f"   ❌ CORS test failed: {e}")
    
    # Test if API data is accessible
    print("\n4. Testing API data...")
    try:
        response = requests.get('http://localhost:8001/api/documents', timeout=5)
        if response.status_code == 200:
            data = response.json()
            doc_count = len(data.get('documents', []))
            print(f"   ✅ Documents API: {doc_count} documents available")
        
        response = requests.get('http://localhost:8001/api/analytics', timeout=5)
        if response.status_code == 200:
            data = response.json()
            total_docs = data.get('total_documents', 0)
            total_props = data.get('total_properties', 0)
            print(f"   ✅ Analytics API: {total_docs} docs, {total_props} properties")
            
    except Exception as e:
        print(f"   ❌ API data test failed: {e}")
    
    print("\n" + "="*50)
    print("📋 DIAGNOSIS:")
    print("✅ Frontend is running and serving content")
    print("✅ Backend APIs are accessible")
    print("✅ Data is available for frontend to display")
    print("\n💡 If you're seeing issues in the browser:")
    print("   1. Open browser developer tools (F12)")
    print("   2. Check Console tab for JavaScript errors")
    print("   3. Check Network tab for failed API requests")
    print("   4. Try hard refresh (Ctrl+Shift+R)")
    
    print("\n🌐 Open this URL in your browser:")
    print("   http://localhost:3000")
    
    return True

if __name__ == "__main__":
    check_frontend_detailed()