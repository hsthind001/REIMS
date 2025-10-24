"""
Audit Current MinIO Storage Structure and Database Records
Generates a report of all files and their storage patterns
"""

import sqlite3
from minio import Minio
from minio.error import S3Error
from datetime import datetime
import json

def audit_storage():
    print("=" * 80)
    print("REIMS STORAGE STRUCTURE AUDIT")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Connect to database
    conn = sqlite3.connect('reims.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Connect to MinIO
    minio_client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "minio_files": {},
        "database_records": {
            "financial_documents": [],
            "documents": []
        },
        "inconsistencies": [],
        "statistics": {}
    }
    
    # =========================================================================
    # 1. AUDIT MINIO BUCKETS
    # =========================================================================
    print("\n[1] SCANNING MINIO BUCKETS")
    print("-" * 80)
    
    buckets_to_check = ["reims-files", "reims-documents"]
    
    for bucket_name in buckets_to_check:
        try:
            if not minio_client.bucket_exists(bucket_name):
                print(f"   Bucket '{bucket_name}': Does not exist")
                report["minio_files"][bucket_name] = {"exists": False, "files": []}
                continue
            
            print(f"   Bucket '{bucket_name}': Scanning...")
            report["minio_files"][bucket_name] = {"exists": True, "files": []}
            
            objects = minio_client.list_objects(bucket_name, recursive=True)
            file_count = 0
            
            for obj in objects:
                file_count += 1
                file_info = {
                    "path": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified.isoformat(),
                    "etag": obj.etag
                }
                report["minio_files"][bucket_name]["files"].append(file_info)
                
                # Parse path to identify property
                parts = obj.object_name.split('/')
                property_indicator = "unknown"
                if len(parts) > 1:
                    property_indicator = parts[0] if parts[0] != "frontend-uploads" else parts[1]
                
                print(f"      {obj.object_name}")
                print(f"         Size: {obj.size:,} bytes | Modified: {obj.last_modified}")
            
            print(f"   Total files: {file_count}")
            report["minio_files"][bucket_name]["count"] = file_count
            
        except S3Error as e:
            print(f"   Error scanning bucket '{bucket_name}': {e}")
            report["minio_files"][bucket_name] = {"exists": False, "error": str(e)}
    
    # =========================================================================
    # 2. AUDIT FINANCIAL_DOCUMENTS TABLE
    # =========================================================================
    print("\n[2] SCANNING FINANCIAL_DOCUMENTS TABLE")
    print("-" * 80)
    
    cur.execute("""
        SELECT id, property_id, file_path, file_name, document_type, 
               property_name, document_year, document_period, upload_date
        FROM financial_documents
        ORDER BY upload_date DESC
    """)
    
    fd_records = cur.fetchall()
    print(f"   Total records: {len(fd_records)}")
    
    for record in fd_records:
        rec_dict = dict(record)
        report["database_records"]["financial_documents"].append(rec_dict)
        
        print(f"\n   Document ID: {rec_dict['id']}")
        print(f"      Property: {rec_dict['property_name']} (ID: {rec_dict['property_id']})")
        print(f"      File: {rec_dict['file_name']}")
        print(f"      Path: {rec_dict['file_path']}")
        print(f"      Type: {rec_dict['document_type']} | Year: {rec_dict['document_year']}")
    
    # =========================================================================
    # 3. AUDIT DOCUMENTS TABLE
    # =========================================================================
    print("\n[3] SCANNING DOCUMENTS TABLE")
    print("-" * 80)
    
    cur.execute("""
        SELECT id, document_id, original_filename, property_id, 
               minio_bucket, minio_object_name, minio_url, storage_type,
               property_name, document_year, upload_timestamp
        FROM documents
        ORDER BY upload_timestamp DESC
    """)
    
    doc_records = cur.fetchall()
    print(f"   Total records: {len(doc_records)}")
    
    for record in doc_records:
        rec_dict = dict(record)
        report["database_records"]["documents"].append(rec_dict)
        
        print(f"\n   Document ID: {rec_dict['document_id']}")
        print(f"      Property: {rec_dict['property_name']} (ID: {rec_dict['property_id']})")
        print(f"      File: {rec_dict['original_filename']}")
        print(f"      MinIO: {rec_dict['minio_bucket']}/{rec_dict['minio_object_name']}")
        print(f"      Storage: {rec_dict['storage_type']}")
    
    # =========================================================================
    # 4. IDENTIFY INCONSISTENCIES
    # =========================================================================
    print("\n[4] ANALYZING INCONSISTENCIES")
    print("-" * 80)
    
    # Check for files in MinIO without database records
    minio_paths = set()
    for bucket_name, bucket_data in report["minio_files"].items():
        if bucket_data.get("exists"):
            for file_info in bucket_data.get("files", []):
                minio_paths.add(f"{bucket_name}/{file_info['path']}")
    
    # Check for database records without MinIO files
    db_paths = set()
    
    # From financial_documents
    for rec in report["database_records"]["financial_documents"]:
        if rec["file_path"]:
            # Assume reims-files if no bucket specified
            db_paths.add(f"reims-files/{rec['file_path']}")
    
    # From documents
    for rec in report["database_records"]["documents"]:
        if rec["minio_bucket"] and rec["minio_object_name"]:
            db_paths.add(f"{rec['minio_bucket']}/{rec['minio_object_name']}")
    
    # Files in MinIO but not in DB
    orphaned_files = minio_paths - db_paths
    if orphaned_files:
        print(f"\n   WARNING: {len(orphaned_files)} files in MinIO without database records:")
        for path in sorted(orphaned_files):
            print(f"      {path}")
            report["inconsistencies"].append({
                "type": "orphaned_file",
                "path": path,
                "description": "File in MinIO without database record"
            })
    
    # DB records without MinIO files
    missing_files = db_paths - minio_paths
    if missing_files:
        print(f"\n   WARNING: {len(missing_files)} database records without MinIO files:")
        for path in sorted(missing_files):
            print(f"      {path}")
            report["inconsistencies"].append({
                "type": "missing_file",
                "path": path,
                "description": "Database record without MinIO file"
            })
    
    # Check for path pattern violations
    print("\n   Checking path patterns...")
    
    standard_pattern = "properties/{property_id}/{doc_type}/{year}/"
    non_standard = []
    
    for bucket_name, bucket_data in report["minio_files"].items():
        if bucket_data.get("exists"):
            for file_info in bucket_data.get("files", []):
                path = file_info["path"]
                # Check if it matches standard pattern
                if not path.startswith("properties/"):
                    non_standard.append(f"{bucket_name}/{path}")
                elif bucket_name != "reims-files":
                    non_standard.append(f"{bucket_name}/{path}")
    
    if non_standard:
        print(f"\n   WARNING: {len(non_standard)} files not following standard pattern:")
        for path in sorted(non_standard):
            print(f"      {path}")
            report["inconsistencies"].append({
                "type": "non_standard_path",
                "path": path,
                "description": "Path does not follow standard pattern"
            })
    
    # =========================================================================
    # 5. GENERATE STATISTICS
    # =========================================================================
    print("\n[5] STATISTICS")
    print("-" * 80)
    
    stats = {
        "total_minio_files": sum(
            bucket.get("count", 0) 
            for bucket in report["minio_files"].values() 
            if isinstance(bucket, dict)
        ),
        "total_financial_documents_records": len(report["database_records"]["financial_documents"]),
        "total_documents_records": len(report["database_records"]["documents"]),
        "inconsistencies_count": len(report["inconsistencies"]),
        "files_by_bucket": {
            bucket: data.get("count", 0)
            for bucket, data in report["minio_files"].items()
            if isinstance(data, dict) and data.get("exists")
        }
    }
    
    report["statistics"] = stats
    
    print(f"   Total files in MinIO: {stats['total_minio_files']}")
    print(f"   Files by bucket:")
    for bucket, count in stats["files_by_bucket"].items():
        print(f"      {bucket}: {count}")
    print(f"   Financial_documents table: {stats['total_financial_documents_records']} records")
    print(f"   Documents table: {stats['total_documents_records']} records")
    print(f"   Inconsistencies found: {stats['inconsistencies_count']}")
    
    # =========================================================================
    # 6. SAVE REPORT
    # =========================================================================
    report_filename = f"storage_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n[6] REPORT SAVED")
    print("-" * 80)
    print(f"   Report saved to: {report_filename}")
    
    # =========================================================================
    # 7. MIGRATION RECOMMENDATIONS
    # =========================================================================
    print("\n[7] MIGRATION RECOMMENDATIONS")
    print("-" * 80)
    
    if stats["inconsistencies_count"] > 0:
        print(f"   ACTION REQUIRED: {stats['inconsistencies_count']} issues need to be resolved")
        print("   Recommended steps:")
        print("   1. Run migration script to reorganize files")
        print("   2. Update database records with new paths")
        print("   3. Verify all files are accessible")
    else:
        print("   No inconsistencies found. Storage structure is clean.")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    
    return report

if __name__ == "__main__":
    try:
        audit_storage()
    except Exception as e:
        print(f"\nERROR: Audit failed: {e}")
        import traceback
        traceback.print_exc()

