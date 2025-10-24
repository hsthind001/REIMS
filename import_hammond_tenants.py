"""
Import Hammond Aire tenant data from rent roll PDF into stores table
Replace sample data with actual tenant roster
"""

import sqlite3
from minio import Minio
import PyPDF2
import io
import re
import uuid
from datetime import datetime

def download_rent_roll():
    """Download rent roll from MinIO"""
    print("=" * 80)
    print("STEP 1: DOWNLOADING RENT ROLL FROM MINIO")
    print("=" * 80)
    
    minio_client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    
    file_path = "Financial Statements/2025/Rent Rolls/Hammond Rent Roll April 2025.pdf"
    
    response = minio_client.get_object("reims-files", file_path)
    pdf_data = response.read()
    response.close()
    response.release_conn()
    
    print(f"✓ Downloaded: {file_path}")
    print(f"  File size: {len(pdf_data)} bytes")
    
    return pdf_data

def parse_rent_roll(pdf_data):
    """Extract tenant data from rent roll PDF"""
    print("\n" + "=" * 80)
    print("STEP 2: EXTRACTING TENANT DATA FROM PDF")
    print("=" * 80)
    
    pdf_file = io.BytesIO(pdf_data)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    # Extract all text
    full_text = ""
    for page in pdf_reader.pages:
        full_text += page.extract_text() + "\n"
    
    print(f"✓ Extracted {len(full_text)} characters from PDF")
    
    # Replace newlines within entries to make parsing easier
    # The pattern is: Hammond Aire Plaza\n(hmnd)XXX ...
    full_text = re.sub(r'Hammond Aire Plaza\s*\n\s*\(hmnd\)', 'Hammond Aire Plaza (hmnd)', full_text)
    
    # Parse tenant data - look for all occurrences of (hmnd)XXX pattern
    tenants = []
    
    # Find all unit entries
    unit_pattern = r'Hammond Aire Plaza\s+\(hmnd\)(\d+[A-Z-]*)\s+(.+?)(?=Hammond Aire Plaza\s+\(hmnd\)|\Z)'
    matches = re.findall(unit_pattern, full_text, re.DOTALL)
    
    print(f"  Found {len(matches)} unit entries")
    
    for unit_num, content in matches:
        # Clean up content - remove excessive whitespace
        content = ' '.join(content.split())
        
        # Extract tenant name (before tenant ID or "Retail")
        tenant_name = None
        tenant_match = re.search(r'^(.+?)\s+\(t\d{7}\)', content)
        if tenant_match:
            tenant_name = tenant_match.group(1).strip()
        
        # Extract sqft (after NNN or Retail)
        sqft = None
        sqft_match = re.search(r'(?:NNN|Retail)\s+(\d{1,5}(?:,\d{3})?\.?\d{0,2})', content)
        if sqft_match:
            sqft = float(sqft_match.group(1).replace(',', ''))
        
        # Extract dates
        dates = re.findall(r'(\d{2}/\d{2}/\d{4})', content)
        lease_start = dates[0] if len(dates) >= 1 else None
        lease_end = dates[1] if len(dates) >= 2 else None
        
        # Extract monthly rent (complex pattern - look for rent after term years)
        monthly_rent = None
        rent_match = re.search(r'(?:Years|Tenancy)\s*([\d,]+\.\d{2})', content)
        if rent_match:
            monthly_rent = float(rent_match.group(1).replace(',', ''))
        
        # Determine status
        status = 'occupied' if tenant_name else 'vacant'
        
        tenant_data = {
            'unit_number': unit_num,
            'tenant_name': tenant_name,
            'sqft': sqft,
            'lease_start': lease_start,
            'lease_end': lease_end,
            'monthly_rent': monthly_rent,
            'status': status
        }
        
        tenants.append(tenant_data)
    
    print(f"\n✓ Parsed {len(tenants)} tenant records")
    print(f"  Occupied: {sum(1 for t in tenants if t['status'] == 'occupied')}")
    print(f"  Vacant: {sum(1 for t in tenants if t['status'] == 'vacant')}")
    
    # Show sample
    print(f"\n  Sample records:")
    for tenant in tenants[:5]:
        print(f"    Unit {tenant['unit_number']}: {tenant['tenant_name'] or 'VACANT'}")
        if tenant['sqft']:
            print(f"       {tenant['sqft']} sqft")
    
    return tenants

def delete_sample_data():
    """Delete fake sample data from stores table"""
    print("\n" + "=" * 80)
    print("STEP 3: DELETING SAMPLE DATA")
    print("=" * 80)
    
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    # Check current records
    cursor.execute("SELECT COUNT(*) as count FROM stores WHERE property_id = 3")
    before_count = cursor.fetchone()[0]
    print(f"  Current records: {before_count}")
    
    # Delete
    cursor.execute("DELETE FROM stores WHERE property_id = 3")
    deleted = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"✓ Deleted {deleted} sample records")
    
    return deleted

def import_tenant_data(tenants):
    """Import tenant data into stores table"""
    print("\n" + "=" * 80)
    print("STEP 4: IMPORTING TENANT DATA")
    print("=" * 80)
    
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    inserted = 0
    
    for tenant in tenants:
        tenant_id = str(uuid.uuid4())
        
        # Convert date format from MM/DD/YYYY to YYYY-MM-DD
        lease_start = None
        lease_end = None
        
        if tenant['lease_start']:
            try:
                parts = tenant['lease_start'].split('/')
                lease_start = f"{parts[2]}-{parts[0]}-{parts[1]}"
            except:
                pass
        
        if tenant['lease_end']:
            try:
                parts = tenant['lease_end'].split('/')
                lease_end = f"{parts[2]}-{parts[0]}-{parts[1]}"
            except:
                pass
        
        # Set default values for missing data
        sqft = tenant['sqft'] if tenant['sqft'] else 1000.0  # Default sqft
        monthly_rent = tenant['monthly_rent'] if tenant['monthly_rent'] else 0.0
        
        cursor.execute("""
            INSERT INTO stores (
                id, property_id, unit_number, sqft, status,
                tenant_name, lease_start, lease_end, monthly_rent,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            tenant_id,
            3,  # Hammond Aire property_id
            tenant['unit_number'],
            sqft,
            tenant['status'],
            tenant['tenant_name'],
            lease_start,
            lease_end,
            monthly_rent
        ))
        
        inserted += 1
    
    conn.commit()
    conn.close()
    
    print(f"✓ Inserted {inserted} tenant records")
    
    return inserted

def verify_import():
    """Verify the imported data"""
    print("\n" + "=" * 80)
    print("STEP 5: VERIFYING IMPORT")
    print("=" * 80)
    
    conn = sqlite3.connect('reims.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Total count
    cursor.execute("SELECT COUNT(*) as count FROM stores WHERE property_id = 3")
    total = cursor.fetchone()['count']
    
    # Occupied count
    cursor.execute("SELECT COUNT(*) as count FROM stores WHERE property_id = 3 AND status = 'occupied'")
    occupied = cursor.fetchone()['count']
    
    # Vacant count
    cursor.execute("SELECT COUNT(*) as count FROM stores WHERE property_id = 3 AND status = 'vacant'")
    vacant = cursor.fetchone()['count']
    
    print(f"\nDatabase verification:")
    print(f"  Total records: {total}")
    print(f"  Occupied: {occupied}")
    print(f"  Vacant: {vacant}")
    
    # Show sample records
    cursor.execute("""
        SELECT unit_number, tenant_name, sqft, monthly_rent, lease_start, lease_end, status
        FROM stores 
        WHERE property_id = 3 
        ORDER BY unit_number
        LIMIT 10
    """)
    
    samples = cursor.fetchall()
    
    print(f"\n  Sample imported records:")
    for sample in samples:
        status_icon = "✓" if sample['status'] == 'occupied' else "○"
        tenant = sample['tenant_name'] or 'VACANT'
        print(f"    {status_icon} Unit {sample['unit_number']}: {tenant}")
        if sample['sqft']:
            print(f"       {sample['sqft']} sqft, ${sample['monthly_rent']}/mo" if sample['monthly_rent'] else f"       {sample['sqft']} sqft")
    
    conn.close()
    
    return total, occupied, vacant

def main():
    print("=" * 80)
    print("IMPORT HAMMOND AIRE TENANT DATA")
    print("=" * 80)
    
    # Step 1: Download rent roll
    pdf_data = download_rent_roll()
    
    # Step 2: Parse tenant data
    tenants = parse_rent_roll(pdf_data)
    
    # Step 3: Delete sample data
    deleted = delete_sample_data()
    
    # Step 4: Import tenant data
    inserted = import_tenant_data(tenants)
    
    # Step 5: Verify import
    total, occupied, vacant = verify_import()
    
    # Summary
    print("\n" + "=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    
    print(f"\n✓ Import completed successfully")
    print(f"  Deleted {deleted} sample records")
    print(f"  Imported {inserted} tenant records from rent roll")
    print(f"  Final count: {total} total ({occupied} occupied, {vacant} vacant)")
    
    if total == 39 and occupied == 33 and vacant == 6:
        print(f"\n✅ VERIFICATION PASSED")
        print(f"   Database now contains actual tenant roster from rent roll!")
    else:
        print(f"\n⚠️ VERIFICATION WARNING")
        print(f"   Expected: 39 total (33 occupied, 6 vacant)")
        print(f"   Got: {total} total ({occupied} occupied, {vacant} vacant)")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

