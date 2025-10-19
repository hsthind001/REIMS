#!/usr/bin/env python3
"""
Test MinIO connection and list bucket contents
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "storage_service"))

from minio import Minio
from minio.error import S3Error
import os
from datetime import datetime

def test_minio_connection():
    print("=== MinIO Connection Test ===")
    
    try:
        # Connect to MinIO
        client = Minio(
            endpoint="localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        
        print("✅ MinIO client created successfully")
        
        # List all buckets
        buckets = client.list_buckets()
        print(f"\n📦 Found {len(buckets)} buckets:")
        for bucket in buckets:
            print(f"  - {bucket.name} (created: {bucket.creation_date})")
        
        # Check specific bucket contents
        bucket_name = "reims-documents"
        if client.bucket_exists(bucket_name):
            print(f"\n📁 Contents of '{bucket_name}' bucket:")
            objects = client.list_objects(bucket_name, recursive=True)
            object_count = 0
            for obj in objects:
                object_count += 1
                print(f"  {object_count}. {obj.object_name} ({obj.size} bytes, modified: {obj.last_modified})")
            
            if object_count == 0:
                print("  (bucket is empty)")
                
        else:
            print(f"❌ Bucket '{bucket_name}' does not exist")
            
    except Exception as e:
        print(f"❌ MinIO connection failed: {e}")
        return False
    
    return True

def test_upload():
    print("\n=== Testing File Upload ===")
    
    try:
        client = Minio(
            endpoint="localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        
        bucket_name = "reims-documents"
        
        # Ensure bucket exists
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"✅ Created bucket '{bucket_name}'")
        
        # Upload test file
        test_content = f"Test upload at {datetime.now().isoformat()}"
        test_filename = "test_upload_verification.txt"
        
        # Create temporary file
        with open(test_filename, "w") as f:
            f.write(test_content)
        
        # Upload to MinIO
        object_name = f"test-uploads/{test_filename}"
        client.fput_object(bucket_name, object_name, test_filename)
        print(f"✅ Successfully uploaded '{test_filename}' as '{object_name}'")
        
        # Verify upload
        stat = client.stat_object(bucket_name, object_name)
        print(f"✅ File verified: {stat.size} bytes, uploaded at {stat.last_modified}")
        
        # Clean up local file
        os.unlink(test_filename)
        
        return True
        
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False

if __name__ == "__main__":
    if test_minio_connection():
        test_upload()
    else:
        print("Cannot proceed with upload test due to connection issues")