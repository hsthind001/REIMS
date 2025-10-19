#!/usr/bin/env python3
"""
Reorganize MinIO files into Property/Year/DocumentType structure
"""
from minio import Minio
import sqlite3
from datetime import datetime

def reorganize_minio_files():
    """
    Reorganize MinIO files from:
      properties/1/uuid_ESP 2024 Income Statement.pdf
    
    To:
      ESP/2024/Income_Statement/uuid_ESP_2024_Income_Statement.pdf
    """
    
    print("\n" + "="*80)
    print("REORGANIZE MINIO FILES - Property/Year/DocumentType Structure")
    print("="*80 + "\n")
    
    # Connect to MinIO
    client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    
    # Connect to database to get file metadata
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    # Get all files from financial_documents with metadata
    cursor.execute("""
        SELECT id, file_name, file_path, property_name, document_year, document_type
        FROM financial_documents
        WHERE property_name IS NOT NULL 
          AND document_year IS NOT NULL
        ORDER BY upload_date DESC
    """)
    
    files = cursor.fetchall()
    
    if not files:
        print("⚠️ No files with metadata found to reorganize")
        conn.close()
        return
    
    print(f"Found {len(files)} files to reorganize\n")
    
    bucket_name = "reims-files"
    
    for doc_id, filename, old_path, prop_name, year, doc_type in files:
        # Create new path: PropertyName/Year/DocumentType/filename
        # Clean up document type for folder name
        folder_type = doc_type.replace(" ", "_") if doc_type else "Other"
        
        new_path = f"{prop_name}/{year}/{folder_type}/{filename}"
        
        print(f"📄 {filename}")
        print(f"   Old: {old_path}")
        print(f"   New: {new_path}")
        
        try:
            # Check if file exists at old path
            try:
                stat = client.stat_object(bucket_name, old_path)
                file_exists = True
            except:
                file_exists = False
                print(f"   ⚠️ File not found at old path (skipping)")
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
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    conn.commit()
    conn.close()
    
    print("="*80)
    print("✅ Reorganization complete!")
    print("="*80 + "\n")

def show_new_structure():
    """Show the new MinIO structure"""
    print("\n" + "="*80)
    print("NEW MINIO STRUCTURE")
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
    for prop in sorted(structure.keys()):
        print(f"📁 {prop}/")
        for year in sorted(structure[prop].keys()):
            print(f"  📁 {year}/")
            for doc_type in sorted(structure[prop][year].keys()):
                files = structure[prop][year][doc_type]
                print(f"    📁 {doc_type}/ ({len(files)} files)")
                for file in files:
                    print(f"      📄 {file}")
        print()
    
    print("="*80 + "\n")

if __name__ == "__main__":
    print("\n🔄 This script will reorganize MinIO files into:")
    print("   PropertyName/Year/DocumentType/filename.pdf\n")
    
    response = input("Do you want to proceed? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        reorganize_minio_files()
        show_new_structure()
    else:
        print("\n❌ Cancelled\n")



