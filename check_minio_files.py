"""
Check which files are in MinIO
"""
from minio import Minio
from minio.error import S3Error

def check_minio_files():
    """Check files in MinIO buckets"""
    
    print("\n" + "="*60)
    print("CHECKING MINIO FILES")
    print("="*60 + "\n")
    
    try:
        # Connect to MinIO
        client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        
        # List all buckets
        buckets = client.list_buckets()
        
        print(f"Found {len(buckets)} buckets\n")
        
        # Check each bucket for objects
        for bucket in buckets:
            print(f"\nBucket: {bucket.name}")
            print("-" * 60)
            
            try:
                objects = list(client.list_objects(bucket.name, recursive=True))
                
                if objects:
                    print(f"  Files: {len(objects)}")
                    for obj in objects[:10]:  # Show first 10
                        print(f"    - {obj.object_name} ({obj.size} bytes)")
                    if len(objects) > 10:
                        print(f"    ... and {len(objects) - 10} more files")
                else:
                    print(f"  (empty)")
                    
            except S3Error as e:
                print(f"  Error listing objects: {e}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_minio_files()



