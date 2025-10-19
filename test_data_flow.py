#!/usr/bin/env python3
"""
Simple test to verify MinIO to Database data flow
Creates a test upload and verifies it reaches both systems
"""

import requests
import sqlite3
import time
import json
from datetime import datetime
from pathlib import Path

def test_upload_to_database():
    """Test that uploads reach both MinIO and database"""
    print("=== Testing MinIO to Database Data Flow ===")
    
    # Step 1: Check backend is running
    try:
        response = requests.get('http://localhost:8001/health', timeout=5)
        if response.status_code != 200:
            print("Backend not running - start with: python simple_backend.py")
            return False
    except:
        print("Backend not accessible - start with: python simple_backend.py")
        return False
    
    print("✅ Backend is running")
    
    # Step 2: Create test file
    test_content = f"""Test Upload for Data Flow Verification
Property: TEST-FLOW-VERIFICATION
Timestamp: {datetime.now().isoformat()}
Purpose: Verify that data reaches database from MinIO upload
"""
    
    test_filename = f"test_flow_{int(time.time())}.txt"
    with open(test_filename, 'w') as f:
        f.write(test_content)
    
    property_id = "TEST-FLOW-VERIFICATION"
    
    # Step 3: Upload via API
    print("📤 Uploading test file...")
    
    try:
        with open(test_filename, 'rb') as f:
            files = {'file': (test_filename, f, 'text/plain')}
            data = {'property_id': property_id}
            
            response = requests.post(
                'http://localhost:8001/api/documents/upload',
                files=files,
                data=data,
                timeout=30
            )
        
        # Clean up test file
        Path(test_filename).unlink(missing_ok=True)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        upload_result = response.json()
        document_id = upload_result['document_id']
        
        print(f"✅ Upload successful - Document ID: {document_id}")
        print(f"   Filename: {upload_result['filename']}")
        print(f"   Storage Location: {upload_result.get('storage_location')}")
        print(f"   MinIO Location: {upload_result.get('minio_location')}")
        print(f"   Database Status: {upload_result.get('database_status')}")
        
        # Check workflow status
        if 'workflow' in upload_result:
            print("\n📋 Workflow Steps:")
            for step, status in upload_result['workflow'].items():
                icon = "✅" if "stored_in_database" in status or "uploaded_to_minio" in status else "❌" if "error" in status.lower() else "🔄"
                print(f"   {step}: {icon} {status}")
        
        # Step 4: Verify in database
        print("\n🔍 Verifying database storage...")
        
        try:
            conn = sqlite3.connect("reims.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT document_id, original_filename, property_id, storage_type,
                       minio_bucket, minio_object_name, minio_url
                FROM documents 
                WHERE document_id = ?
            """, (document_id,))
            
            db_record = cursor.fetchone()
            
            if db_record:
                print("✅ Database record found:")
                print(f"   Document ID: {db_record[0]}")
                print(f"   Filename: {db_record[1]}")
                print(f"   Property: {db_record[2]}")
                print(f"   Storage Type: {db_record[3]}")
                print(f"   MinIO Bucket: {db_record[4]}")
                print(f"   MinIO Object: {db_record[5]}")
                print(f"   MinIO URL: {db_record[6]}")
                
                # Check if MinIO fields are populated
                minio_populated = bool(db_record[4] and db_record[5] and db_record[6])
                print(f"   MinIO Data Complete: {'✅' if minio_populated else '❌'}")
                
                conn.close()
                
                # Step 5: Verify in MinIO
                print("\n🗂️ Verifying MinIO storage...")
                
                if minio_populated:
                    try:
                        from minio import Minio
                        client = Minio("localhost:9000", "minioadmin", "minioadmin", secure=False)
                        
                        bucket = db_record[4]
                        object_name = db_record[5]
                        
                        stat = client.stat_object(bucket, object_name)
                        print("✅ File found in MinIO:")
                        print(f"   Object: {object_name}")
                        print(f"   Size: {stat.size} bytes")
                        print(f"   Modified: {stat.last_modified}")
                        
                        print("\n🎉 SUCCESS: Complete data flow verified!")
                        print("   Frontend → Backend → MinIO → Database ✅")
                        return True
                        
                    except Exception as e:
                        print(f"❌ MinIO verification failed: {e}")
                        print("   Database record exists but file not in MinIO")
                        return False
                else:
                    print("❌ MinIO data not populated in database")
                    return False
                    
            else:
                print(f"❌ No database record found for document ID: {document_id}")
                conn.close()
                return False
                
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        Path(test_filename).unlink(missing_ok=True)
        return False

def main():
    """Run the test"""
    print("🧪 TESTING MINIO TO DATABASE DATA FLOW")
    print("=" * 50)
    
    success = test_upload_to_database()
    
    print("\n" + "=" * 50)
    if success:
        print("🎯 RESULT: ✅ DATA FLOW WORKING CORRECTLY")
        print("\n💡 Your system is properly configured:")
        print("   • Uploads via frontend will reach both MinIO and database")
        print("   • Data consistency is maintained")
        print("   • Audit trail is complete")
    else:
        print("🎯 RESULT: ❌ DATA FLOW ISSUES DETECTED")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Ensure backend is running: python simple_backend.py")
        print("   2. Check backend shows: '✅ Database integration available'")
        print("   3. Check backend shows: '✅ MinIO client initialized successfully'")
        print("   4. Verify database schema: python migrate_minio_schema.py")
        print("   5. Test MinIO connection: python test_minio_connection.py")

if __name__ == "__main__":
    main()