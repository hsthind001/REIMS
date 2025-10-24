import requests
import json

print("="*80)
print("FINAL QUALITY VERIFICATION - 100% TARGET")
print("="*80)

# Test API
response = requests.get('http://localhost:8001/api/properties')
data = response.json()

print("\n✅ API Status:", response.status_code)
print("✅ Properties Count:", len(data['properties']))

print("\n" + "="*80)
print("PROPERTY DATA VERIFICATION")
print("="*80)

quality_score = 100
issues = []

for prop in data['properties']:
    print(f"\n📊 {prop['name']}")
    print(f"  ID: {prop['id']}")
    
    # Check NOI
    noi = prop.get('noi', 0)
    if noi > 100000:  # Expect NOI > $100k for real properties
        print(f"  ✅ NOI: ${noi:,.2f}")
    else:
        print(f"  ❌ NOI: ${noi:,.2f} (TOO LOW)")
        quality_score -= 20
        issues.append(f"{prop['name']}: NOI too low")
    
    # Check Occupancy
    occ = prop.get('occupancy_rate', 0)
    if 0.5 <= occ <= 1.0:  # Expect 50-100% occupancy
        print(f"  ✅ Occupancy: {occ*100:.1f}%")
    else:
        print(f"  ❌ Occupancy: {occ*100:.4f}% (OUT OF RANGE)")
        quality_score -= 20
        issues.append(f"{prop['name']}: Occupancy out of range")
    
    # Check Status
    status = prop.get('status', 'unknown')
    print(f"  ℹ️  Status: {status}")

print("\n" + "="*80)
print("QUALITY SCORE CALCULATION")
print("="*80)

if issues:
    print("\n❌ ISSUES FOUND:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("\n✅ NO ISSUES FOUND")

print(f"\n{'='*80}")
print(f"FINAL QUALITY SCORE: {quality_score}/100")
if quality_score == 100:
    print("STATUS: ✅ 100% QUALITY ACHIEVED!")
else:
    print(f"STATUS: ❌ QUALITY AT {quality_score}% - NEEDS IMPROVEMENT")
print(f"{'='*80}")

