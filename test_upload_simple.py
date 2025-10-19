#!/usr/bin/env python3
import requests

url = "http://localhost:8001/api/documents/upload"

with open("test_upload_financial.csv", 'rb') as f:
    response = requests.post(
        url,
        files={'file': ('test.csv', f, 'text/csv')},
        data={'property_id': '1', 'document_type': 'financial_statement'}
    )

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")















