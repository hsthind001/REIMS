#!/usr/bin/env python3
"""
Organize MinIO buckets by document type as recommended by user
"""

import sqlite3
import json
from minio import Minio
from minio.error import S3Error
import os

# MinIO configuration
MINIO_ENDPOINT = 'localhost:9000'
MINIO_ACCESS_KEY = 'minioadmin'
MINIO_SECRET_KEY = 'minioadmin'
MINIO_SECURE = False

# Bucket organization structure
BUCKET_PATHS = {
    "balance_sheet": "financial-statements/balance-sheets/",
    "income_statement": "financial-statements/income-statements/",
    "cash_flow_statement": "financial-statements/cash-flow-statements/",
    "rent_roll": "financial-statements/rent-rolls/",
    "other": "financial-statements/other/"
}

def get_document_type(filename):
    """Determine document type from filename"""
    filename_lower = filename.lower()
    
    if 'balance sheet' in filename_lower:
        return 'balance_sheet'
    elif 'income statement' in filename_lower:
        return 'income_statement'
    elif 'cash flow' in filename_lower:
        return 'cash_flow_statement'
    elif 'rent roll' in filename_lower:
        return 'rent_roll'
    else:
        return 'other'

def organize_minio_buckets():
    """Organize MinIO files by document type"""
    
    print("=== ORGANIZING MINIO BUCKETS ===")
    
    try:
        # Connect to MinIO
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )
        
        print("✅ Connected to MinIO")
        
        # Connect to database
        conn = sqlite3.connect('reims.db')
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        
        # Get all documents with MinIO paths
        cursor.execute("""
            SELECT document_id, original_filename, minio_object_name, property_id
            FROM documents 
            WHERE minio_object_name IS NOT NULL
        """)
        documents = cursor.fetchall()
        
        print(f"\nFound {len(documents)} documents with MinIO paths")
        
        moved_files = 0
        updated_records = 0
        
        for doc_id, filename, old_path, property_id in documents:
            try:
                print(f"\nProcessing: {filename}")
                
                # Determine new path based on document type
                doc_type = get_document_type(filename)
                new_path = BUCKET_PATHS[doc_type] + filename
                
                print(f"  Document type: {doc_type}")
                print(f"  Old path: {old_path}")
                print(f"  New path: {new_path}")
                
                # Check if file exists in MinIO
                try:
                    stat = client.stat_object('reims-documents', old_path)
                    print(f"  ✅ File exists in MinIO ({stat.size} bytes)")
                    
                    # Copy file to new location
                    from minio.commonconfig import CopySource
                    client.copy_object(
                        'reims-documents',
                        new_path,
                        CopySource('reims-documents', old_path)
                    )
                    print(f"  ✅ Copied to new location")
                    
                    # Remove old file
                    client.remove_object('reims-documents', old_path)
                    print(f"  ✅ Removed old file")
                    
                    # Update database with new path
                    cursor.execute("""
                        UPDATE documents 
                        SET minio_object_name = ? 
                        WHERE document_id = ?
                    """, (new_path, doc_id))
                    
                    moved_files += 1
                    updated_records += 1
                    
                except S3Error as e:
                    if e.code == 'NoSuchKey':
                        print(f"  ⚠️  File not found in MinIO: {old_path}")
                    else:
                        print(f"  ❌ MinIO error: {e}")
                
            except Exception as e:
                print(f"  ❌ Error processing {filename}: {e}")
        
        # Commit database changes
        conn.commit()
        conn.close()
        
        print(f"\n📊 Summary:")
        print(f"  Files moved: {moved_files}")
        print(f"  Database records updated: {updated_records}")
        
        # Show new bucket structure
        print(f"\n📁 New MinIO Structure:")
        for doc_type, path in BUCKET_PATHS.items():
            try:
                objects = list(client.list_objects('reims-documents', prefix=path, recursive=True))
                count = len(objects)
                print(f"  {path}: {count} files")
                if count > 0:
                    for obj in objects[:3]:  # Show first 3 files
                        filename = obj.object_name.split('/')[-1]
                        print(f"    - {filename}")
                    if count > 3:
                        print(f"    ... and {count - 3} more")
            except Exception as e:
                print(f"  {path}: Error listing - {e}")
        
        print("\n✅ MinIO bucket organization completed!")
        
    except Exception as e:
        print(f"❌ Error organizing buckets: {e}")

if __name__ == "__main__":
    organize_minio_buckets()





