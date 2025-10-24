"""
Extract and Validate Hammond Aire Rent Roll Occupancy Data
Downloads the rent roll PDF from MinIO and extracts occupancy information
"""

from minio import Minio
from minio.error import S3Error
import sqlite3
import os
from pathlib import Path

def extract_rent_roll():
    print("=" * 80)
    print("HAMMOND AIRE RENT ROLL EXTRACTION")
    print("=" * 80)
    
    # Connect to MinIO
    minio_client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    
    # Connect to database
    conn = sqlite3.connect('reims.db')
    cur = conn.cursor()
    
    # Find the Hammond rent roll file
    print("\n[1] LOCATING HAMMOND RENT ROLL")
    print("-" * 80)
    
    # Search for rent roll files
    objects = list(minio_client.list_objects("reims-files", prefix="properties/", recursive=True))
    
    rent_roll_files = [
        obj for obj in objects
        if "hammond" in obj.object_name.lower() and "rent" in obj.object_name.lower() and "roll" in obj.object_name.lower()
    ]
    
    if not rent_roll_files:
        print("   ✗ No Hammond rent roll file found in MinIO")
        return
    
    # Use the first (or latest) rent roll file
    rent_roll = rent_roll_files[0]
    print(f"   ✓ Found: {rent_roll.object_name}")
    print(f"   Size: {rent_roll.size:,} bytes")
    print(f"   Modified: {rent_roll.last_modified}")
    
    # =========================================================================
    # 2. DOWNLOAD FILE
    # =========================================================================
    print("\n[2] DOWNLOADING FILE")
    print("-" * 80)
    
    # Create temp directory
    temp_dir = Path("temp_rentroll")
    temp_dir.mkdir(exist_ok=True)
    
    local_file = temp_dir / rent_roll.object_name.split('/')[-1]
    
    try:
        minio_client.fget_object("reims-files", rent_roll.object_name, str(local_file))
        print(f"   ✓ Downloaded to: {local_file}")
        print(f"   File size: {local_file.stat().st_size:,} bytes")
    except Exception as e:
        print(f"   ✗ Error downloading: {e}")
        return
    
    # =========================================================================
    # 3. EXTRACT DATA FROM PDF
    # =========================================================================
    print("\n[3] EXTRACTING DATA FROM PDF")
    print("-" * 80)
    
    try:
        import PyPDF2
        
        with open(local_file, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            print(f"   PDF has {len(pdf.pages)} page(s)")
            
            # Extract text from all pages
            full_text = ""
            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                text = page.extract_text()
                full_text += text + "\n"
            
            print(f"   Extracted {len(full_text)} characters")
            
            # Look for occupancy information
            print("\n   Searching for occupancy data...")
            
            occupied_count = 0
            vacant_count = 0
            units = []
            
            lines = full_text.split('\n')
            for i, line in enumerate(lines):
                line_lower = line.lower()
                
                # Look for unit/suite information
                if ('unit' in line_lower or 'suite' in line_lower) and any(char.isdigit() for char in line):
                    # Try to determine if occupied or vacant
                    context = ' '.join(lines[max(0, i-2):min(len(lines), i+3)]).lower()
                    
                    is_occupied = 'occupied' in context or 'tenant' in context
                    is_vacant = 'vacant' in context or 'available' in context
                    
                    if is_occupied:
                        occupied_count += 1
                        units.append({"unit": line.strip(), "status": "occupied"})
                    elif is_vacant:
                        vacant_count += 1
                        units.append({"unit": line.strip(), "status": "vacant"})
            
            # If we didn't find specific unit info, look for summary
            if occupied_count == 0 and vacant_count == 0:
                print("   Looking for summary information...")
                for line in lines:
                    line_lower = line.lower()
                    if 'total' in line_lower and 'unit' in line_lower:
                        print(f"      Found summary: {line}")
                    if 'occupied' in line_lower:
                        print(f"      Found occupancy: {line}")
                    if 'vacant' in line_lower:
                        print(f"      Found vacancy: {line}")
            
            print("\n   " + "=" * 76)
            print("   EXTRACTED OCCUPANCY DATA")
            print("   " + "=" * 76)
            
            if units:
                print(f"   Total Units Found: {len(units)}")
                print(f"   Occupied: {occupied_count}")
                print(f"   Vacant: {vacant_count}")
                print(f"   Occupancy Rate: {(occupied_count / len(units) * 100):.1f}%")
            else:
                print("   ⚠ Could not extract detailed unit information from PDF")
                print("   This PDF may require manual review or specialized parsing")
            
            # Show first 2000 characters for manual review
            print("\n   " + "=" * 76)
            print("   PDF CONTENT PREVIEW (First 2000 chars):")
            print("   " + "=" * 76)
            print(full_text[:2000])
            
    except ImportError:
        print("   ⚠ PyPDF2 not installed. Install with: pip install PyPDF2")
        print("   Manual review of PDF required")
    except Exception as e:
        print(f"   ✗ Error extracting PDF: {e}")
    
    # =========================================================================
    # 4. COMPARE WITH DATABASE
    # =========================================================================
    print("\n\n[4] COMPARING WITH DATABASE")
    print("-" * 80)
    
    # Get occupancy from stores table
    cur.execute("""
        SELECT 
            COUNT(*) as total_units,
            SUM(CASE WHEN status = 'occupied' THEN 1 ELSE 0 END) as occupied_units,
            SUM(CASE WHEN status = 'vacant' THEN 1 ELSE 0 END) as vacant_units
        FROM stores 
        WHERE property_id = ?
    """, ("3",))  # Hammond Aire is property ID 3
    
    db_occupancy = cur.fetchone()
    
    if db_occupancy and db_occupancy[0] > 0:
        db_total, db_occupied, db_vacant = db_occupancy
        db_rate = (db_occupied / db_total * 100) if db_total > 0 else 0
        
        print("   DATABASE (Hammond Aire - Property ID 3):")
        print(f"      Total Units: {db_total}")
        print(f"      Occupied: {db_occupied}")
        print(f"      Vacant: {db_vacant}")
        print(f"      Occupancy Rate: {db_rate:.1f}%")
        
        print("\n   COMPARISON:")
        if units and len(units) == db_total:
            print("      ✓ Unit count matches!")
            if occupied_count == db_occupied:
                print("      ✓ Occupied count matches!")
            else:
                print(f"      ⚠ Occupied count differs (PDF: {occupied_count}, DB: {db_occupied})")
        elif units:
            print(f"      ⚠ Unit count differs (PDF: {len(units)}, DB: {db_total})")
        else:
            print("      ⚠ Could not extract detailed data from PDF for comparison")
    else:
        print("   ⚠ No occupancy data in database for Hammond Aire")
    
    # Show all Hammond Aire units from database
    print("\n   DETAILED DATABASE RECORDS:")
    cur.execute("""
        SELECT unit_number, status, tenant_name, monthly_rent, sqft
        FROM stores 
        WHERE property_id = ?
        ORDER BY unit_number
    """, ("3",))
    
    db_units = cur.fetchall()
    
    if db_units:
        for unit in db_units:
            unit_num, status, tenant, rent, sqft = unit
            status_icon = "🟢" if status == "occupied" else "🔴"
            print(f"\n      {status_icon} {unit_num} - {status.upper()}")
            if sqft:
                print(f"         Size: {sqft:,} sq ft")
            if status == "occupied" and tenant:
                print(f"         Tenant: {tenant}")
                if rent:
                    print(f"         Rent: ${rent:,.2f}/month")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"\n   Downloaded file location: {local_file}")
    print("   You can manually review the PDF for detailed information")
    print("=" * 80)

if __name__ == "__main__":
    try:
        extract_rent_roll()
    except Exception as e:
        print(f"\nERROR: Extraction failed: {e}")
        import traceback
        traceback.print_exc()

