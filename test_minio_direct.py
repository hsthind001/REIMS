#!/usr/bin/env python3
"""Test MinIO connection directly"""

try:
    from minio import Minio
    from io import BytesIO
    
    print("🔌 Testing MinIO connection...")
    
    client = Minio(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    
    print("✅ MinIO client created")
    
    # Test bucket list
    buckets = list(client.list_buckets())
    print(f"✅ Buckets: {[b.name for b in buckets]}")
    
    # Check if reims-files bucket exists
    exists = client.bucket_exists("reims-files")
    print(f"✅ Bucket 'reims-files' exists: {exists}")
    
    if not exists:
        print("📦 Creating bucket 'reims-files'...")
        client.make_bucket("reims-files")
        print("✅ Bucket created")
    
    # Test upload
    print("\n📤 Testing file upload to MinIO...")
    test_data = b"Test file content for MinIO"
    client.put_object(
        bucket_name="reims-files",
        object_name="test/test_file.txt",
        data=BytesIO(test_data),
        length=len(test_data)
    )
    print("✅ File uploaded successfully!")
    
    # Test read
    print("📥 Testing file download from MinIO...")
    response = client.get_object("reims-files", "test/test_file.txt")
    data = response.read()
    print(f"✅ File downloaded: {len(data)} bytes")
    
    print("\n✅ MinIO is working correctly!")
    
except Exception as e:
    print(f"❌ MinIO error: {e}")
    import traceback
    traceback.print_exc()















