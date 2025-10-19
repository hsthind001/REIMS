#!/usr/bin/env python3
"""
Complete verification of MinIO to Database data flow
Tests the entire pipeline and ensures data consistency
"""

import requests
import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime

def check_backend_status():
    """Check if backend is running and responsive"""
    print("=== Backend Status Check ===")
    try:
        response = requests.get('http://localhost:8001/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not responding: {e}")
        return False

def verify_minio_connection():
    """Test MinIO connection through backend"""
    print("\n=== MinIO Connection Verification ===")
    try:
        # Check if MinIO is working by checking the test file we uploaded earlier
        from minio import Minio
        client = Minio(
            endpoint="localhost:9000",
            access_key="minioadmin", 
            secret_key="minioadmin",
            secure=False
        )
        
        # List objects in the bucket
        bucket_name = "reims-documents"
        objects = list(client.list_objects(bucket_name, recursive=True))
        print(f"✅ MinIO connected - Found {len(objects)} objects in bucket '{bucket_name}'")
        
        for obj in objects[:3]:  # Show first 3 objects
            print(f"   📄 {obj.object_name} ({obj.size} bytes)")
        
        return True, len(objects)
    except Exception as e:
        print(f"❌ MinIO connection failed: {e}")
        return False, 0

def test_upload_with_tracking(test_name="verification"):
    """Upload a test file and track it through the entire pipeline"""
    print(f"\n=== Testing Upload Pipeline ({test_name}) ===")
    
    # Create test file
    test_content = f"""Test File for Data Flow Verification
Test Name: {test_name}
Timestamp: {datetime.now().isoformat()}
Purpose: Verify MinIO → Database data flow
Property: TEST-FLOW-{test_name.upper()}
"""
    
    test_filename = f"test_flow_{test_name}_{int(time.time())}.txt"
    test_filepath = Path(test_filename)
    
    with open(test_filepath, 'w') as f:
        f.write(test_content)
    
    property_id = f"TEST-FLOW-{test_name.upper()}"
    
    try:
        # Step 1: Upload via API
        print("1. Uploading file via API...")
        with open(test_filepath, 'rb') as f:
            files = {'file': (test_filename, f, 'text/plain')}
            data = {'property_id': property_id}
            
            response = requests.post(
                'http://localhost:8001/api/documents/upload',
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        upload_result = response.json()
        document_id = upload_result['document_id']
        print(f"✅ Upload successful - Document ID: {document_id}")
        
        # Show workflow status
        if 'workflow' in upload_result:
            print("   Workflow Steps:")
            for step, status in upload_result['workflow'].items():
                icon = "✅" if "✅" in status else "❌" if "❌" in status else "🔄"
                print(f"     {step}: {icon} {status}")
        
        # Step 2: Wait a moment for processing
        print("2. Waiting for processing...")
        time.sleep(2)
        
        # Step 3: Verify in MinIO
        print("3. Verifying in MinIO...")
        minio_verified = False
        if 'minio_location' in upload_result and upload_result['minio_location']:
            try:
                from minio import Minio
                client = Minio("localhost:9000", "minioadmin", "minioadmin", secure=False)
                
                # Extract object name from minio URL
                minio_url = upload_result['minio_location']
                object_name = minio_url.split('/')[-1]  # Get last part after /
                # Actually, let's construct the expected path
                expected_object = f"frontend-uploads/{property_id}/{document_id}_{test_filename}"
                
                try:
                    stat = client.stat_object("reims-documents", expected_object)
                    print(f"✅ File found in MinIO: {expected_object}")
                    print(f"   Size: {stat.size} bytes")
                    print(f"   Modified: {stat.last_modified}")
                    minio_verified = True
                except Exception as e:
                    print(f"❌ File not found in MinIO at expected path: {expected_object}")
                    print(f"   Error: {e}")
                    
                    # Try to find it by listing all objects
                    objects = client.list_objects("reims-documents", recursive=True)
                    for obj in objects:
                        if document_id in obj.object_name:
                            print(f"✅ Found file at alternate path: {obj.object_name}")
                            minio_verified = True
                            break
                
            except Exception as e:
                print(f"❌ MinIO verification failed: {e}")
        else:
            print("❌ No MinIO location in upload response")
        
        # Step 4: Verify in Database
        print("4. Verifying in Database...")
        db_verified = False
        try:
            conn = sqlite3.connect("reims.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT document_id, original_filename, property_id, storage_type, 
                       minio_bucket, minio_object_name, minio_url, upload_timestamp
                FROM documents 
                WHERE document_id = ?
            """, (document_id,))
            
            db_record = cursor.fetchone()
            if db_record:
                print(f"✅ Database record found:")
                print(f"   Document ID: {db_record[0]}")
                print(f"   Filename: {db_record[1]}")
                print(f"   Property: {db_record[2]}")
                print(f"   Storage Type: {db_record[3]}")
                print(f"   MinIO Bucket: {db_record[4]}")
                print(f"   MinIO Object: {db_record[5]}")
                print(f"   MinIO URL: {db_record[6]}")
                print(f"   Upload Time: {db_record[7]}")
                db_verified = True
            else:
                print(f"❌ Database record not found for document ID: {document_id}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
        
        # Step 5: Summary
        print("5. Verification Summary:")
        print(f"   ✅ API Upload: Success")
        print(f"   {'✅' if minio_verified else '❌'} MinIO Storage: {'Success' if minio_verified else 'Failed'}")
        print(f"   {'✅' if db_verified else '❌'} Database Record: {'Success' if db_verified else 'Failed'}")
        
        success = minio_verified and db_verified
        print(f"\n{'✅ COMPLETE SUCCESS' if success else '❌ PARTIAL FAILURE'}: Data flow verification {('PASSED' if success else 'FAILED')}")
        
        # Cleanup
        test_filepath.unlink(missing_ok=True)
        
        return {
            'document_id': document_id,
            'minio_verified': minio_verified,
            'db_verified': db_verified,
            'success': success
        }
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        test_filepath.unlink(missing_ok=True)
        return None

def check_data_consistency():
    """Check for any inconsistencies between MinIO and Database"""
    print("\n=== Data Consistency Check ===")
    
    try:
        # Get all database records with MinIO data
        conn = sqlite3.connect("reims.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT document_id, original_filename, property_id, minio_bucket, 
                   minio_object_name, storage_type
            FROM documents 
            WHERE storage_type IN ('minio', 'local_and_minio')
            ORDER BY upload_timestamp DESC
        """)
        
        db_records = cursor.fetchall()
        print(f"📊 Found {len(db_records)} records marked as MinIO-stored in database")
        
        if len(db_records) == 0:
            print("ℹ️ No MinIO records found in database")
            return True
        
        # Check each record in MinIO
        from minio import Minio
        client = Minio("localhost:9000", "minioadmin", "minioadmin", secure=False)
        
        consistent_count = 0
        inconsistent_count = 0
        
        for record in db_records:
            doc_id, filename, prop_id, bucket, object_name, storage_type = record
            
            try:
                if bucket and object_name:
                    stat = client.stat_object(bucket, object_name)
                    consistent_count += 1
                    print(f"✅ {filename} (Property: {prop_id}) - Consistent")
                else:
                    inconsistent_count += 1
                    print(f"❌ {filename} (Property: {prop_id}) - Missing MinIO info in DB")
                    
            except Exception as e:
                inconsistent_count += 1
                print(f"❌ {filename} (Property: {prop_id}) - Not found in MinIO: {e}")
        
        conn.close()
        
        print(f"\n📊 Consistency Results:")
        print(f"   ✅ Consistent records: {consistent_count}")
        print(f"   ❌ Inconsistent records: {inconsistent_count}")
        print(f"   📈 Consistency rate: {(consistent_count / len(db_records) * 100):.1f}%")
        
        return inconsistent_count == 0
        
    except Exception as e:
        print(f"❌ Consistency check failed: {e}")
        return False

def main():
    """Run complete verification suite"""
    print("🔍 COMPLETE DATA FLOW VERIFICATION")
    print("=" * 50)
    
    # Step 1: Check prerequisites
    if not check_backend_status():
        print("\n❌ Cannot proceed - Backend not running")
        print("💡 Start backend with: python simple_backend.py")
        return
    
    minio_ok, object_count = verify_minio_connection()
    if not minio_ok:
        print("\n❌ Cannot proceed - MinIO not accessible")
        return
    
    # Step 2: Test new upload
    test_result = test_upload_with_tracking("consistency")
    
    # Step 3: Check overall consistency
    consistency_ok = check_data_consistency()
    
    # Final summary
    print("\n" + "=" * 50)
    print("🎯 FINAL VERIFICATION RESULTS")
    print("=" * 50)
    
    if test_result and test_result['success'] and consistency_ok:
        print("🎉 ✅ ALL SYSTEMS WORKING PERFECTLY!")
        print("   • Frontend uploads working")
        print("   • MinIO storage working") 
        print("   • Database integration working")
        print("   • Data consistency maintained")
    else:
        print("⚠️ ❌ ISSUES DETECTED:")
        if not test_result or not test_result['success']:
            print("   • New upload pipeline has issues")
        if not consistency_ok:
            print("   • Data consistency problems found")
        
        print("\n💡 Troubleshooting suggestions:")
        print("   1. Restart backend: python simple_backend.py")
        print("   2. Check MinIO is running: http://localhost:9001")
        print("   3. Verify database schema: python verify_database.py")

if __name__ == "__main__":
    main()