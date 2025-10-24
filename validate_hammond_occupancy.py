"""
Validate Hammond Aire occupancy data from database against rent roll PDF in MinIO
"""

import sqlite3
from minio import Minio
import PyPDF2
import io
import re

def download_rent_roll():
    """Download Hammond Aire rent roll from MinIO"""
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
    
    try:
        response = minio_client.get_object("reims-files", file_path)
        pdf_data = response.read()
        response.close()
        response.release_conn()
        
        print(f"✓ Downloaded: {file_path}")
        print(f"  File size: {len(pdf_data)} bytes")
        
        return pdf_data
    except Exception as e:
        print(f"✗ Error downloading file: {e}")
        return None

def extract_tenant_data(pdf_data):
    """Extract tenant information from rent roll PDF"""
    print("\n" + "=" * 80)
    print("STEP 2: EXTRACTING TENANT DATA FROM PDF")
    print("=" * 80)
    
    if not pdf_data:
        print("✗ No PDF data to parse")
        return None
    
    try:
        pdf_file = io.BytesIO(pdf_data)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        print(f"✓ PDF loaded: {len(pdf_reader.pages)} pages")
        
        # Extract all text
        full_text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            full_text += text + "\n"
            print(f"  Page {page_num + 1}: {len(text)} characters")
        
        print(f"\n✓ Total text extracted: {len(full_text)} characters")
        
        # Parse tenant data - this rent roll has format:
        # Property Unit(s) Tenant_Name/Company (ID) Retail...
        tenants = []
        vacant_units = []
        
        lines = full_text.split('\n')
        
        # Look for "Hammond Aire Plaza" followed by unit number and tenant info
        property_pattern = re.compile(r'Hammond Aire Plaza\s+\(hmnd\)(\d+[A-Z-]*)\s+(.+?)\s+\(t\d+\)', re.IGNORECASE)
        vacant_pattern = re.compile(r'vacant|available|unleased', re.IGNORECASE)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for property + unit + tenant pattern
            match = property_pattern.search(line)
            if match:
                unit_num = match.group(1)
                tenant_name = match.group(2).strip()
                
                # Check if vacant
                if vacant_pattern.search(tenant_name) or not tenant_name:
                    vacant_units.append(f"Unit {unit_num}")
                else:
                    tenants.append({
                        'unit': f"Unit {unit_num}",
                        'tenant': tenant_name,
                        'occupied': True
                    })
        
        # If we didn't find any with the specific pattern, try a simpler approach
        if not tenants and not vacant_units:
            # Look for lines starting with unit numbers
            for line in lines:
                if line.startswith(('001 ', '002', '003', '004', '005', '006', '007', '008', '009')):
                    # Extract tenant info
                    parts = line.split()
                    if len(parts) > 1:
                        unit_num = parts[0]
                        # Tenant name usually follows unit number
                        tenant_info = ' '.join(parts[1:]).split('Retail')[0].split('NNN')[0].strip()
                        if tenant_info and not vacant_pattern.search(tenant_info):
                            tenants.append({
                                'unit': f"Unit {unit_num}",
                                'tenant': tenant_info,
                                'occupied': True
                            })
        
        print(f"\n✓ Parsed tenant data:")
        print(f"  Occupied units found: {len(tenants)}")
        print(f"  Vacant units found: {len(vacant_units)}")
        
        if tenants:
            print(f"\n  Occupied units:")
            for t in tenants:
                print(f"    - {t['unit']}: {t['tenant']}")
        
        if vacant_units:
            print(f"\n  Vacant units:")
            for v in vacant_units:
                print(f"    - {v}")
        
        # Also save full text for manual review
        print(f"\n  Full extracted text (first 2000 chars):")
        print("-" * 80)
        print(full_text[:2000])
        print("-" * 80)
        
        return {
            'tenants': tenants,
            'vacant_units': vacant_units,
            'total_occupied': len(tenants),
            'total_vacant': len(vacant_units),
            'total_units': len(tenants) + len(vacant_units),
            'full_text': full_text
        }
        
    except Exception as e:
        print(f"✗ Error parsing PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_database_data():
    """Get occupancy data from database"""
    print("\n" + "=" * 80)
    print("STEP 3: GETTING DATABASE DATA")
    print("=" * 80)
    
    conn = sqlite3.connect('reims.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get property data
    cursor.execute("""
        SELECT id, name, total_units, occupied_units, occupancy_rate
        FROM properties
        WHERE id = 3
    """)
    
    property_data = cursor.fetchone()
    
    if property_data:
        print(f"✓ Database data for Hammond Aire:")
        print(f"  Total units: {property_data['total_units']}")
        print(f"  Occupied units: {property_data['occupied_units']}")
        print(f"  Vacant units: {property_data['total_units'] - property_data['occupied_units']}")
        print(f"  Occupancy rate: {property_data['occupancy_rate']}%")
    
    # Check stores table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stores'")
    if cursor.fetchone():
        cursor.execute("SELECT * FROM stores WHERE property_id = 3")
        stores = cursor.fetchall()
        print(f"\n✓ Stores table has {len(stores)} records for property 3")
    
    conn.close()
    
    return {
        'total_units': property_data['total_units'],
        'occupied_units': property_data['occupied_units'],
        'occupancy_rate': property_data['occupancy_rate']
    } if property_data else None

def compare_and_report(db_data, pdf_data):
    """Compare database with PDF data and generate report"""
    print("\n" + "=" * 80)
    print("STEP 4: VALIDATION REPORT")
    print("=" * 80)
    
    if not db_data or not pdf_data:
        print("✗ Cannot compare - missing data")
        return
    
    print("\nCOMPARISON:")
    print("-" * 80)
    
    print(f"\n{'Metric':<20} {'Database':<15} {'PDF':<15} {'Match':<10}")
    print("-" * 80)
    
    db_total = db_data['total_units']
    pdf_total = pdf_data['total_units']
    total_match = "✓" if db_total == pdf_total else "✗"
    print(f"{'Total Units':<20} {db_total:<15} {pdf_total:<15} {total_match:<10}")
    
    db_occupied = db_data['occupied_units']
    pdf_occupied = pdf_data['total_occupied']
    occupied_match = "✓" if db_occupied == pdf_occupied else "✗"
    print(f"{'Occupied Units':<20} {db_occupied:<15} {pdf_occupied:<15} {occupied_match:<10}")
    
    db_vacant = db_total - db_occupied
    pdf_vacant = pdf_data['total_vacant']
    vacant_match = "✓" if db_vacant == pdf_vacant else "✗"
    print(f"{'Vacant Units':<20} {db_vacant:<15} {pdf_vacant:<15} {vacant_match:<10}")
    
    db_rate = db_data['occupancy_rate']
    pdf_rate = (pdf_occupied / pdf_total * 100) if pdf_total > 0 else 0
    rate_match = "✓" if abs(db_rate - pdf_rate) < 1 else "✗"
    print(f"{'Occupancy Rate':<20} {db_rate:.1f}%{' ':<10} {pdf_rate:.1f}%{' ':<10} {rate_match:<10}")
    
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    
    all_match = (total_match == "✓" and occupied_match == "✓" and 
                 vacant_match == "✓" and rate_match == "✓")
    
    if all_match:
        print("\n✅ VALIDATION PASSED")
        print("   Database occupancy data matches the rent roll PDF!")
    else:
        print("\n⚠️ VALIDATION MISMATCH DETECTED")
        print("\n   Discrepancies found:")
        
        if total_match == "✗":
            print(f"   - Total units: Database shows {db_total}, PDF shows {pdf_total}")
        if occupied_match == "✗":
            print(f"   - Occupied units: Database shows {db_occupied}, PDF shows {pdf_occupied}")
        if vacant_match == "✗":
            print(f"   - Vacant units: Database shows {db_vacant}, PDF shows {pdf_vacant}")
        if rate_match == "✗":
            print(f"   - Occupancy rate: Database shows {db_rate:.1f}%, PDF shows {pdf_rate:.1f}%")
        
        print("\n   RECOMMENDATION:")
        if pdf_total == 0:
            print("   - PDF data extraction may have failed")
            print("   - Manual review of rent roll PDF required")
            print("   - Database data appears to be manually entered sample data")
        else:
            print("   - Update database with actual tenant data from rent roll")
            print(f"   - Set total_units = {pdf_total}")
            print(f"   - Set occupied_units = {pdf_occupied}")
            print(f"   - Set occupancy_rate = {pdf_rate:.1f}")

def main():
    print("=" * 80)
    print("HAMMOND AIRE OCCUPANCY VALIDATION")
    print("=" * 80)
    
    # Step 1: Download rent roll
    pdf_data = download_rent_roll()
    
    # Step 2: Extract tenant data
    pdf_tenant_data = extract_tenant_data(pdf_data)
    
    # Step 3: Get database data
    db_data = get_database_data()
    
    # Step 4: Compare and report
    compare_and_report(db_data, pdf_tenant_data)
    
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

