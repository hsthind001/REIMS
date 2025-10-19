#!/usr/bin/env python3
"""
Check uploaded files in MinIO and Database
"""
import sqlite3
from minio import Minio
from datetime import datetime

def check_database():
    """Check all database tables for uploaded files"""
    print("\n" + "="*80)
    print("DATABASE CHECK - All Tables with Uploads")
    print("="*80 + "\n")
    
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    # Check documents table
    print("📊 1. DOCUMENTS TABLE")
    print("-" * 80)
    cursor.execute("""
        SELECT document_id, original_filename, property_id, property_name, 
               document_year, document_type, document_period, status,
               minio_bucket, minio_object_name, upload_timestamp
        FROM documents 
        ORDER BY upload_timestamp DESC 
        LIMIT 10
    """)
    
    documents = cursor.fetchall()
    if documents:
        print(f"Found {len(documents)} recent documents:\n")
        for i, doc in enumerate(documents, 1):
            doc_id, filename, prop_id, prop_name, year, dtype, period, status, bucket, obj_name, timestamp = doc
            print(f"{i}. {filename}")
            print(f"   Document ID: {doc_id[:8]}...")
            print(f"   Property ID: {prop_id}")
            print(f"   Property Name: {prop_name or '❌ NULL'}")
            print(f"   Year: {year or '❌ NULL'}")
            print(f"   Type: {dtype or '❌ NULL'}")
            print(f"   Period: {period}")
            print(f"   Status: {status}")
            print(f"   MinIO Bucket: {bucket or 'Not in MinIO'}")
            print(f"   MinIO Object: {obj_name or 'N/A'}")
            print(f"   Uploaded: {timestamp}")
            print()
    else:
        print("  ⚠ No documents found\n")
    
    # Check financial_documents table
    print("📊 2. FINANCIAL_DOCUMENTS TABLE")
    print("-" * 80)
    cursor.execute("""
        SELECT id, file_name, property_id, document_type, 
               upload_date, file_path, property_name, document_year, document_period
        FROM financial_documents 
        ORDER BY upload_date DESC 
        LIMIT 10
    """)
    
    fin_docs = cursor.fetchall()
    if fin_docs:
        print(f"Found {len(fin_docs)} recent financial documents:\n")
        for i, doc in enumerate(fin_docs, 1):
            file_id, filename, prop_id, dtype, upload_date, file_path, prop_name, year, period = doc
            print(f"{i}. {filename}")
            print(f"   ID: {file_id}")
            print(f"   Property ID: {prop_id}")
            print(f"   Property Name: {prop_name or '❌ NULL'}")
            print(f"   Year: {year or '❌ NULL'}")
            print(f"   Type: {dtype}")
            print(f"   Period: {period}")
            print(f"   File Path: {file_path}")
            print(f"   Uploaded: {upload_date}")
            print()
    else:
        print("  ⚠ No financial documents found\n")
    
    # Summary
    cursor.execute("SELECT COUNT(*) FROM documents")
    doc_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM financial_documents")
    fin_doc_count = cursor.fetchone()[0]
    
    print("=" * 80)
    print("DATABASE SUMMARY")
    print("=" * 80)
    print(f"Total Documents: {doc_count}")
    print(f"Total Financial Documents: {fin_doc_count}")
    print(f"Total Files: {doc_count + fin_doc_count}")
    print()
    
    conn.close()
    return doc_count, fin_doc_count

def check_minio():
    """Check MinIO buckets for uploaded files"""
    print("\n" + "="*80)
    print("MINIO CHECK - All Buckets")
    print("="*80 + "\n")
    
    try:
        client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        
        buckets = list(client.list_buckets())
        print(f"Found {len(buckets)} buckets:\n")
        
        total_objects = 0
        bucket_details = []
        
        for bucket in buckets:
            bucket_name = bucket.name
            objects = list(client.list_objects(bucket_name, recursive=True))
            total_objects += len(objects)
            bucket_details.append((bucket_name, objects))
            
            if len(objects) > 0:
                print(f"📦 {bucket_name} ({len(objects)} files)")
                for obj in objects[:5]:  # Show first 5
                    size_kb = obj.size / 1024
                    print(f"   - {obj.object_name} ({size_kb:.2f} KB)")
                if len(objects) > 5:
                    print(f"   ... and {len(objects) - 5} more files")
                print()
            else:
                print(f"📦 {bucket_name} (empty)")
        
        print("=" * 80)
        print("MINIO SUMMARY")
        print("=" * 80)
        print(f"Total Buckets: {len(buckets)}")
        print(f"Total Files: {total_objects}")
        print()
        
        return total_objects, bucket_details
        
    except Exception as e:
        print(f"❌ Error connecting to MinIO: {e}")
        return 0, []

def cross_reference():
    """Cross-reference database entries with MinIO files"""
    print("\n" + "="*80)
    print("CROSS-REFERENCE CHECK")
    print("="*80 + "\n")
    
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    # Get documents with MinIO references
    cursor.execute("""
        SELECT original_filename, minio_bucket, minio_object_name 
        FROM documents 
        WHERE minio_bucket IS NOT NULL
    """)
    
    db_files = cursor.fetchall()
    
    if not db_files:
        print("⚠ No files in database have MinIO references")
        conn.close()
        return
    
    print(f"Found {len(db_files)} files with MinIO references in database\n")
    
    try:
        client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        
        verified = 0
        missing = 0
        
        for filename, bucket, obj_name in db_files:
            try:
                stat = client.stat_object(bucket, obj_name)
                print(f"✅ {filename}")
                print(f"   → {bucket}/{obj_name}")
                verified += 1
            except Exception:
                print(f"❌ {filename}")
                print(f"   → {bucket}/{obj_name} (NOT FOUND IN MINIO)")
                missing += 1
        
        print("\n" + "=" * 80)
        print(f"✅ Verified: {verified}")
        print(f"❌ Missing: {missing}")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"❌ Error checking MinIO: {e}")
    
    conn.close()

def main():
    print("\n" + "="*80)
    print("UPLOADED FILES VERIFICATION")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Check database
    doc_count, fin_count = check_database()
    
    # Check MinIO
    minio_count, bucket_details = check_minio()
    
    # Cross-reference
    cross_reference()
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"Database (documents table): {doc_count} files")
    print(f"Database (financial_documents table): {fin_count} files")
    print(f"MinIO (all buckets): {minio_count} files")
    print()
    
    if doc_count > 0 or fin_count > 0:
        print("✅ Files found in database!")
        print("\n📌 PRIMARY TABLE: 'documents' table is the main storage")
        print("   - Contains: document_id, original_filename, property_id")
        print("   - NEW: property_name, document_year, document_type, document_period")
        print("   - MinIO: minio_bucket, minio_object_name")
    else:
        print("⚠ No files found in database")
    
    if minio_count > 0:
        print("\n✅ Files found in MinIO!")
    else:
        print("\n⚠ No files found in MinIO")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

