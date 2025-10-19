#!/usr/bin/env python3
"""
Complete Migration: Parse filenames, update database, reorganize MinIO
Creates structure: PropertyName/Year/DocumentType/filename.pdf
"""
from minio import Minio
import sqlite3
import sys
import os

# Add path for filename parser
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
from backend.utils.filename_parser import parse_filename

def migrate_metadata():
    """Step 1: Parse filenames and update database with metadata"""
    print("\n" + "="*80)
    print("STEP 1: EXTRACT METADATA FROM FILENAMES")
    print("="*80 + "\n")
    
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    # Get files with NULL metadata
    cursor.execute("""
        SELECT id, file_name
        FROM financial_documents
        WHERE property_name IS NULL OR document_year IS NULL
    """)
    
    files = cursor.fetchall()
    
    if not files:
        print("✅ All files already have metadata!\n")
        conn.close()
        return 0
    
    print(f"Found {len(files)} files without metadata\n")
    
    updated = 0
    for doc_id, filename in files:
        parsed = parse_filename(filename)
        
        prop_name = parsed.get('property_name')
        doc_year = parsed.get('document_year')
        doc_type = parsed.get('document_type')
        doc_period = parsed.get('document_period', 'Annual')
        
        if prop_name or doc_year or doc_type:
            print(f"📄 {filename}")
            print(f"   → Property: {prop_name}, Year: {doc_year}, Type: {doc_type}")
            
            cursor.execute("""
                UPDATE financial_documents
                SET property_name = ?,
                    document_year = ?,
                    document_type = ?,
                    document_period = ?
                WHERE id = ?
            """, (prop_name, doc_year, doc_type, doc_period, doc_id))
            
            updated += 1
        else:
            print(f"⚠️ {filename} - Could not extract metadata")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Updated {updated} files with metadata\n")
    return updated

def reorganize_minio():
    """Step 2: Reorganize MinIO files into Property/Year/DocumentType structure"""
    print("\n" + "="*80)
    print("STEP 2: REORGANIZE MINIO FILES")
    print("="*80 + "\n")
    
    # Connect to MinIO
    client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    
    # Connect to database
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    # Get files with metadata
    cursor.execute("""
        SELECT id, file_name, file_path, property_name, document_year, document_type
        FROM financial_documents
        WHERE property_name IS NOT NULL 
          AND document_year IS NOT NULL
        ORDER BY upload_date DESC
    """)
    
    files = cursor.fetchall()
    
    if not files:
        print("⚠️ No files with metadata found to reorganize\n")
        conn.close()
        return 0
    
    print(f"Found {len(files)} files to reorganize\n")
    
    bucket_name = "reims-files"
    reorganized = 0
    
    for doc_id, filename, old_path, prop_name, year, doc_type in files:
        # Create new path: PropertyName/Year/DocumentType/filename
        # Clean up document type for folder name (replace spaces with underscores)
        folder_type = doc_type.replace(" ", "_") if doc_type else "Other"
        
        new_path = f"{prop_name}/{year}/{folder_type}/{filename}"
        
        # Skip if already in new format
        if old_path == new_path:
            print(f"✓ {filename} - Already organized")
            continue
        
        print(f"📄 {filename}")
        print(f"   From: {old_path}")
        print(f"   To:   {new_path}")
        
        try:
            # Check if file exists at old path
            try:
                stat = client.stat_object(bucket_name, old_path)
            except:
                print(f"   ⚠️ File not found in MinIO (skipping)")
                print()
                continue
            
            # Copy to new location
            client.copy_object(
                bucket_name,
                new_path,
                f"{bucket_name}/{old_path}"
            )
            print(f"   ✅ Copied to new location")
            
            # Update database with new path
            cursor.execute("""
                UPDATE financial_documents
                SET file_path = ?
                WHERE id = ?
            """, (new_path, doc_id))
            print(f"   ✅ Updated database")
            
            # Delete old file
            client.remove_object(bucket_name, old_path)
            print(f"   ✅ Removed old file")
            
            reorganized += 1
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    conn.commit()
    conn.close()
    
    print(f"✅ Reorganized {reorganized} files\n")
    return reorganized

def show_final_structure():
    """Step 3: Display the final MinIO structure"""
    print("\n" + "="*80)
    print("STEP 3: FINAL MINIO STRUCTURE")
    print("="*80 + "\n")
    
    client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    
    bucket_name = "reims-files"
    objects = list(client.list_objects(bucket_name, recursive=True))
    
    # Organize by property/year
    structure = {}
    for obj in objects:
        parts = obj.object_name.split('/')
        if len(parts) >= 3:
            prop = parts[0]
            year = parts[1]
            doc_type = parts[2]
            
            if prop not in structure:
                structure[prop] = {}
            if year not in structure[prop]:
                structure[prop][year] = {}
            if doc_type not in structure[prop][year]:
                structure[prop][year][doc_type] = []
            
            structure[prop][year][doc_type].append(parts[-1])
    
    # Print structure
    print(f"📦 Bucket: {bucket_name}\n")
    for prop in sorted(structure.keys()):
        print(f"📁 {prop}/")
        for year in sorted(structure[prop].keys()):
            print(f"  📁 {year}/")
            for doc_type in sorted(structure[prop][year].keys()):
                files = structure[prop][year][doc_type]
                print(f"    📁 {doc_type}/ ({len(files)} files)")
                for file in files[:3]:  # Show first 3 files
                    print(f"      📄 {file}")
                if len(files) > 3:
                    print(f"      ... and {len(files) - 3} more")
            print()
    
    print("="*80 + "\n")

def main():
    print("\n" + "="*80)
    print("COMPLETE MINIO MIGRATION")
    print("Reorganize files into: PropertyName/Year/DocumentType/")
    print("="*80)
    
    print("\nThis will:")
    print("  1. Parse filenames to extract metadata (property, year, type)")
    print("  2. Update database with extracted metadata")
    print("  3. Reorganize MinIO files into new structure")
    print("  4. Update database file paths")
    print("  5. Delete old files from MinIO")
    
    response = input("\nDo you want to proceed? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("\n❌ Cancelled\n")
        return
    
    # Execute migration
    updated = migrate_metadata()
    reorganized = reorganize_minio()
    show_final_structure()
    
    # Summary
    print("="*80)
    print("✅ MIGRATION COMPLETE!")
    print("="*80)
    print(f"  • Metadata extracted: {updated} files")
    print(f"  • Files reorganized: {reorganized} files")
    print("\nNew structure:")
    print("  reims-files/ESP/2024/Income_Statement/ESP 2024 Income Statement.pdf")
    print("  reims-files/ESP/2024/Cash_Flow_Statement/ESP 2024 Cash Flow Statement.pdf")
    print("  reims-files/ESP/2024/Balance_Sheet/ESP 2024 Balance Sheet.pdf")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()



