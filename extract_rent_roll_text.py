"""
Extract and analyze Hammond Aire rent roll text
"""

from minio import Minio
import PyPDF2
import io
import re

# Download PDF
minio_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

response = minio_client.get_object("reims-files", "Financial Statements/2025/Rent Rolls/Hammond Rent Roll April 2025.pdf")
pdf_data = response.read()
response.close()
response.release_conn()

# Extract text
pdf_file = io.BytesIO(pdf_data)
pdf_reader = PyPDF2.PdfReader(pdf_file)

full_text = ""
for page in pdf_reader.pages:
    full_text += page.extract_text() + "\n"

# Save to file for analysis
with open("hammond_rent_roll_text.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print("=" * 80)
print("HAMMOND AIRE RENT ROLL ANALYSIS")
print("=" * 80)

# Count occurrences of "Hammond Aire Plaza (hmnd)" which indicates a unit
unit_pattern = re.compile(r'Hammond Aire Plaza\s+\(hmnd\)(\d+[A-Z-]*)', re.IGNORECASE)
units = unit_pattern.findall(full_text)

print(f"\nTotal units found: {len(units)}")
print(f"\nUnit numbers:")
for unit in units:
    print(f"  - Unit {unit}")

# Look for tenant IDs (t0000xxx) which indicate occupied units
tenant_pattern = re.compile(r'\(t\d{7}\)')
tenants = tenant_pattern.findall(full_text)

print(f"\nTenant IDs found: {len(tenants)}")

# Count "vacant" or similar keywords
vacant_pattern = re.compile(r'vacant|available|unleased', re.IGNORECASE)
vacant_mentions = len(vacant_pattern.findall(full_text))

print(f"Vacant mentions: {vacant_mentions}")

# Extract unit details more carefully
print("\n" + "=" * 80)
print("DETAILED UNIT ANALYSIS")
print("=" * 80)

lines = full_text.split('\n')
for i, line in enumerate(lines):
    if 'Hammond Aire Plaza' in line and '(hmnd)' in line:
        # This line contains unit info
        unit_match = re.search(r'\(hmnd\)(\d+[A-Z-]*)', line)
        if unit_match:
            unit_num = unit_match.group(1)
            # Get the next few lines for tenant info
            next_lines = lines[i:min(i+5, len(lines))]
            combined = ' '.join(next_lines)
            
            # Check for tenant ID
            tenant_id_match = re.search(r'\(t(\d{7})\)', combined)
            if tenant_id_match:
                # Extract tenant name (text between unit number and tenant ID)
                tenant_text = re.search(r'\(hmnd\)' + unit_num + r'\s+(.+?)\s+\(t\d{7}\)', combined, re.DOTALL)
                tenant_name = tenant_text.group(1).strip() if tenant_text else "Unknown"
                tenant_name = ' '.join(tenant_name.split())  # Clean up whitespace
                
                print(f"\nUnit {unit_num}: OCCUPIED")
                print(f"  Tenant: {tenant_name[:100]}")  # First 100 chars
            else:
                print(f"\nUnit {unit_num}: Status unclear")

print(f"\n✓ Full text saved to hammond_rent_roll_text.txt")
print("\n" + "=" * 80)

