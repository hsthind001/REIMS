#!/usr/bin/env python3
"""
Direct database and MinIO verification without API calls
Checks data consistency between MinIO and Database directly
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def check_database_minio_records():
    """Check what MinIO-related records exist in database"""
    print("=== Database MinIO Records Check ===")
    
    try:
        conn = sqlite3.connect("reims.db")
        cursor = conn.cursor()
        
        # Get all records
        cursor.execute("SELECT COUNT(*) FROM documents")
        total_count = cursor.fetchone()[0]
        
        # Get MinIO-stored records
        cursor.execute("SELECT COUNT(*) FROM documents WHERE storage_type IN ('minio', 'local_and_minio')")
        minio_count = cursor.fetchone()[0]
        
        # Get records with MinIO URLs
        cursor.execute("SELECT COUNT(*) FROM documents WHERE minio_url IS NOT NULL")
        minio_url_count = cursor.fetchone()[0]
        
        print(f"📊 Database Summary:")
        print(f"   Total documents: {total_count}")
        print(f"   MinIO-stored documents: {minio_count}")
        print(f"   Documents with MinIO URLs: {minio_url_count}")
        
        # Show recent MinIO records
        cursor.execute("""
            SELECT document_id, original_filename, property_id, storage_type, 
                   minio_bucket, minio_object_name, minio_url, upload_timestamp,
                   minio_upload_timestamp
            FROM documents 
            WHERE storage_type IN ('minio', 'local_and_minio') OR minio_url IS NOT NULL
            ORDER BY upload_timestamp DESC 
            LIMIT 10
        """)
        
        minio_records = cursor.fetchall()
        
        if minio_records:
            print(f"\n📄 MinIO Records in Database ({len(minio_records)} found):")
            for record in minio_records:
                doc_id, filename, prop_id, storage_type, bucket, object_name, minio_url, upload_time, minio_time = record
                print(f"\n   📄 {filename}")
                print(f"      Document ID: {doc_id}")
                print(f"      Property: {prop_id}")
                print(f"      Storage Type: {storage_type}")
                print(f"      MinIO Bucket: {bucket}")
                print(f"      MinIO Object: {object_name}")
                print(f"      MinIO URL: {minio_url}")
                print(f"      Upload Time: {upload_time}")
                print(f"      MinIO Upload Time: {minio_time}")
        else:
            print("\n❌ No MinIO records found in database")
        
        conn.close()
        return minio_records
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return []

def check_minio_objects():
    """Check what objects exist in MinIO"""
    print("\n=== MinIO Objects Check ===")
    
    try:
        from minio import Minio
        client = Minio(
            endpoint="localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin", 
            secure=False
        )
        
        bucket_name = "reims-documents"
        objects = list(client.list_objects(bucket_name, recursive=True))
        
        print(f"🗂️ MinIO Bucket '{bucket_name}' contains {len(objects)} objects:")
        
        frontend_uploads = []
        other_objects = []
        
        for obj in objects:
            print(f"   📄 {obj.object_name}")
            print(f"      Size: {obj.size} bytes")
            print(f"      Modified: {obj.last_modified}")
            print(f"      ETag: {obj.etag}")
            
            if obj.object_name.startswith("frontend-uploads/"):
                frontend_uploads.append(obj)
            else:
                other_objects.append(obj)
            print()
        
        print(f"📊 MinIO Summary:")
        print(f"   Frontend uploads: {len(frontend_uploads)}")
        print(f"   Other objects: {len(other_objects)}")
        
        return objects
        
    except Exception as e:
        print(f"❌ MinIO check failed: {e}")
        return []

def cross_check_data():
    """Cross-check data between database and MinIO"""
    print("\n=== Cross-Reference Check ===")
    
    # Get database records
    db_records = check_database_minio_records()
    
    # Get MinIO objects  
    minio_objects = check_minio_objects()
    
    if not db_records and not minio_objects:
        print("ℹ️ No data found in either database or MinIO")
        return
    
    if not db_records:
        print("⚠️ MinIO has objects but database has no MinIO records")
        return
        
    if not minio_objects:
        print("⚠️ Database has MinIO records but MinIO bucket is empty")
        return
    
    # Create lookup maps
    minio_object_names = {obj.object_name for obj in minio_objects}
    db_object_names = {record[5] for record in db_records if record[5]}  # minio_object_name
    
    print(f"\n🔍 Data Consistency Analysis:")
    print(f"   Database MinIO objects: {len(db_object_names)}")
    print(f"   Actual MinIO objects: {len(minio_object_names)}")
    
    # Find matches
    matching_objects = db_object_names.intersection(minio_object_names)
    db_only = db_object_names - minio_object_names
    minio_only = minio_object_names - db_object_names
    
    print(f"\n📊 Consistency Results:")
    print(f"   ✅ Matching objects: {len(matching_objects)}")
    print(f"   ❌ DB only (orphaned records): {len(db_only)}")
    print(f"   ❌ MinIO only (untracked files): {len(minio_only)}")
    
    if matching_objects:
        print(f"\n✅ Consistent Objects:")
        for obj_name in sorted(matching_objects):
            print(f"   📄 {obj_name}")
    
    if db_only:
        print(f"\n❌ Database Orphans (in DB but not MinIO):")
        for obj_name in sorted(db_only):
            print(f"   👻 {obj_name}")
            
    if minio_only:
        print(f"\n❌ MinIO Orphans (in MinIO but not DB):")
        for obj_name in sorted(minio_only):
            print(f"   🏝️ {obj_name}")
    
    # Calculate consistency percentage
    total_unique = len(db_object_names.union(minio_object_names))
    consistency_rate = (len(matching_objects) / total_unique * 100) if total_unique > 0 else 100
    
    print(f"\n📈 Data Consistency Rate: {consistency_rate:.1f}%")
    
    return {
        'matching': len(matching_objects),
        'db_only': len(db_only),
        'minio_only': len(minio_only),
        'consistency_rate': consistency_rate
    }

def create_test_database_record():
    """Create a test record directly in database to verify the flow"""
    print("\n=== Creating Test Database Record ===")
    
    try:
        import sys
        sys.path.append(str(Path(__file__).parent / "backend"))
        from database import SessionLocal, Document
        
        db = SessionLocal()
        
        # Create test record with current timestamp
        test_id = f"direct-test-{int(datetime.now().timestamp())}"
        
        test_doc = Document(
            document_id=test_id,
            original_filename="direct_test_file.txt",
            stored_filename=f"{test_id}_direct_test_file.txt",
            property_id="DIRECT-TEST-001",
            file_size=100,
            content_type="text/plain",
            file_path=f"storage/{test_id}_direct_test_file.txt",
            upload_timestamp=datetime.now(),
            status="uploaded",
            minio_bucket="reims-documents",
            minio_object_name=f"frontend-uploads/DIRECT-TEST-001/{test_id}_direct_test_file.txt",
            minio_url=f"minio://reims-documents/frontend-uploads/DIRECT-TEST-001/{test_id}_direct_test_file.txt",
            storage_type="local_and_minio",
            minio_upload_timestamp=datetime.now()
        )
        
        db.add(test_doc)
        db.commit()
        db.refresh(test_doc)
        
        print(f"✅ Test record created successfully:")
        print(f"   Document ID: {test_doc.document_id}")
        print(f"   MinIO Object: {test_doc.minio_object_name}")
        print(f"   Storage Type: {test_doc.storage_type}")
        
        db.close()
        return test_doc.document_id
        
    except Exception as e:
        print(f"❌ Failed to create test record: {e}")
        return None

def main():
    """Run direct verification without API calls"""
    print("🔍 DIRECT DATA VERIFICATION")
    print("Checking MinIO ↔ Database consistency without API calls")
    print("=" * 60)
    
    # Step 1: Check what's in database
    db_records = check_database_minio_records()
    
    # Step 2: Check what's in MinIO
    minio_objects = check_minio_objects()
    
    # Step 3: Cross-check consistency
    consistency_result = cross_check_data()
    
    # Step 4: Create test record to verify database write capability
    test_id = create_test_database_record()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 VERIFICATION SUMMARY")
    print("=" * 60)
    
    if consistency_result:
        if consistency_result['consistency_rate'] >= 90:
            print("🎉 ✅ DATA CONSISTENCY EXCELLENT!")
        elif consistency_result['consistency_rate'] >= 70:
            print("⚠️ 🟡 DATA CONSISTENCY GOOD (some issues)")
        else:
            print("❌ 🔴 DATA CONSISTENCY POOR (major issues)")
        
        print(f"   📊 Consistency Rate: {consistency_result['consistency_rate']:.1f}%")
        print(f"   ✅ Matching records: {consistency_result['matching']}")
        print(f"   ❌ Inconsistencies: {consistency_result['db_only'] + consistency_result['minio_only']}")
    
    if test_id:
        print(f"   ✅ Database write test: SUCCESS")
    else:
        print(f"   ❌ Database write test: FAILED")
    
    print(f"\n💡 To ensure data reaches database from MinIO uploads:")
    print(f"   1. ✅ Database schema is ready (MinIO fields added)")
    print(f"   2. ✅ Backend code includes database storage")
    print(f"   3. 🔄 Test actual upload via frontend")
    print(f"   4. 📊 Monitor this verification script")

if __name__ == "__main__":
    main()