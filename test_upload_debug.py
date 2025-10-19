#!/usr/bin/env python3
"""
Debug upload test with detailed request/response info
"""
import requests
import json

url = "http://localhost:8001/api/documents/upload"

print("Testing file upload to:", url)
print("")

try:
    with open("test_upload_financial.csv", 'rb') as f:
        files = {'file': ('test.csv', f, 'text/csv')}
        data = {'property_id': '1', 'document_type': 'financial_statement'}
        
        print("Sending request...")
        response = requests.post(url, files=files, data=data, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
        print(f"\nResponse Body:")
        print(response.text)
        
        if response.status_code == 200:
            try:
                print(f"\nParsed JSON:")
                print(json.dumps(response.json(), indent=2))
            except:
                pass
                
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()















