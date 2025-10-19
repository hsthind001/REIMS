#!/usr/bin/env python3
"""Final upload test with correct property ID and content type"""

import sqlite3
import requests
import json

# Get valid property ID
conn = sqlite3.connect('reims.db')
cursor = conn.cursor()
cursor.execute('SELECT id FROM properties LIMIT 1')
property_id = str(cursor.fetchone()[0])
conn.close()

print(f"Using property ID: {property_id}")
print("")

# Test upload
url = "http://localhost:8001/api/documents/upload"

with open('test_upload_financial.csv', 'rb') as f:
    files = {'file': ('test.csv', f, 'text/csv')}
    data = {
        'property_id': property_id,
        'document_type': 'financial_statement'
    }
    
    print(f"Uploading to: {url}")
    response = requests.post(url, files=files, data=data)
    
    print(f"\nStatus: {response.status_code}")
    print(f"\nResponse:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)















