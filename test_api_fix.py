import requests
import json

response = requests.get('http://localhost:8001/api/properties')
data = response.json()

print("=" * 80)
print("API RESPONSE TEST")
print("=" * 80)

for prop in data['properties']:
    print(f"\nProperty: {prop['name']}")
    print(f"  NOI: ${prop['noi']:,.2f}")
    print(f"  Occupancy Rate: {prop['occupancy_rate']} ({prop['occupancy_rate']*100:.1f}%)")
    print(f"  Status: {prop['status']}")

