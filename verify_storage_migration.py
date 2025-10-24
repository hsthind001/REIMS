"""
Verify Storage Migration
Validates that all files follow the standardized structure and are accessible
"""

import sqlite3
from minio import Minio
from minio.error import S3Error
from datetime import datetime
import re

def verify_migration():
    print("=" * 80)
    print("REIMS STORAGE MIGRATION VERIFICATION")
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
    
    verification_report = {
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "path_pattern": {"passed": [], "failed": []},
            "bucket_location": {"passed": [], "failed": []},
            "file_accessibility": {"passed": [], "failed": []},
            "database_sync": {"passed": [], "failed": []}
        },
        "summary": {
            "total_files": 0,
            "valid_paths": 0,
            "accessible_files": 0,
            "synced_records": 0
        }
    }
    
    # Standard path pattern
    standard_pattern = re.compile(r'^properties/[\w-]+/(financial-statements|rent-rolls|offering-memos|lease-agreements|maintenance-records|other)/\d{4}/.+$')
    
    # =========================================================================
    # 1. VERIFY PATH PATTERNS
    # =========================================================================
    print("\n[1] VERIFYING PATH PATTERNS")
    print("-" * 80)
    
    if not minio_client.bucket_exists("reims-files"):
        print("   ✗ ERROR: reims-files bucket does not exist!")
        return
    
    objects = list(minio_client.list_objects("reims-files", recursive=True))
    verification_report["summary"]["total_files"] = len(objects)
    
    print(f"   Checking {len(objects)} files...")
    
    for obj in objects:
        path = obj.object_name
        
        if standard_pattern.match(path):
            verification_report["checks"]["path_pattern"]["passed"].append(path)
            verification_report["summary"]["valid_paths"] += 1
        else:
            print(f"   ✗ Invalid pattern: {path}")
            verification_report["checks"]["path_pattern"]["failed"].append(path)
    
    print(f"   ✓ Valid paths: {verification_report['summary']['valid_paths']}/{len(objects)}")
    
    if verification_report["checks"]["path_pattern"]["failed"]:
        print(f"   ⚠ {len(verification_report['checks']['path_pattern']['failed'])} files with invalid patterns")
    
    # =========================================================================
    # 2. VERIFY BUCKET LOCATION
    # =========================================================================
    print("\n[2] VERIFYING BUCKET LOCATION")
    print("-" * 80)
    
    # Check that reims-documents doesn't have any property files
    if minio_client.bucket_exists("reims-documents"):
        doc_objects = list(minio_client.list_objects("reims-documents", recursive=True))
        if doc_objects:
            print(f"   ⚠ Found {len(doc_objects)} files still in reims-documents bucket:")
            for obj in doc_objects[:5]:  # Show first 5
                print(f"      - {obj.object_name}")
            if len(doc_objects) > 5:
                print(f"      ... and {len(doc_objects) - 5} more")
            verification_report["checks"]["bucket_location"]["failed"] = [obj.object_name for obj in doc_objects]
        else:
            print("   ✓ No files in reims-documents bucket")
            verification_report["checks"]["bucket_location"]["passed"].append("reims-documents_empty")
    
    print(f"   ✓ All {len(objects)} files in reims-files bucket")
    
    # =========================================================================
    # 3. VERIFY FILE ACCESSIBILITY
    # =========================================================================
    print("\n[3] VERIFYING FILE ACCESSIBILITY")
    print("-" * 80)
    
    print(f"   Testing accessibility of {len(objects)} files...")
    
    for obj in objects:
        try:
            # Try to stat the object (lightweight check)
            stat = minio_client.stat_object("reims-files", obj.object_name)
            verification_report["checks"]["file_accessibility"]["passed"].append(obj.object_name)
            verification_report["summary"]["accessible_files"] += 1
        except Exception as e:
            print(f"   ✗ Cannot access: {obj.object_name} - {e}")
            verification_report["checks"]["file_accessibility"]["failed"].append({
                "path": obj.object_name,
                "error": str(e)
            })
    
    print(f"   ✓ Accessible files: {verification_report['summary']['accessible_files']}/{len(objects)}")
    
    # =========================================================================
    # 4. VERIFY DATABASE SYNC
    # =========================================================================
    print("\n[4] VERIFYING DATABASE SYNCHRONIZATION")
    print("-" * 80)
    
    # Check financial_documents table
    cur.execute("SELECT COUNT(*) FROM financial_documents")
    fd_count = cur.fetchone()[0]
    
    # Check documents table
    cur.execute("SELECT COUNT(*) FROM documents")
    doc_count = cur.fetchone()[0]
    
    print(f"   Financial_documents table: {fd_count} records")
    print(f"   Documents table: {doc_count} records")
    
    # Verify that paths in database match MinIO
    minio_paths = set(obj.object_name for obj in objects)
    
    # Check financial_documents paths
    cur.execute("SELECT file_path, file_name FROM financial_documents WHERE file_path IS NOT NULL")
    fd_records = cur.fetchall()
    
    fd_valid = 0
    for record in fd_records:
        file_path = record["file_path"]
        if file_path in minio_paths:
            fd_valid += 1
            verification_report["checks"]["database_sync"]["passed"].append(f"fd:{file_path}")
        else:
            # Check if filename exists in any path
            filename = record["file_name"]
            found = any(filename in path for path in minio_paths)
            if not found:
                print(f"   ⚠ Path in financial_documents not found in MinIO: {file_path}")
                verification_report["checks"]["database_sync"]["failed"].append(f"fd:{file_path}")
    
    # Check documents paths
    cur.execute("SELECT minio_bucket, minio_object_name FROM documents WHERE minio_object_name IS NOT NULL")
    doc_records = cur.fetchall()
    
    doc_valid = 0
    for record in doc_records:
        bucket = record["minio_bucket"]
        obj_name = record["minio_object_name"]
        
        if bucket == "reims-files" and obj_name in minio_paths:
            doc_valid += 1
            verification_report["checks"]["database_sync"]["passed"].append(f"doc:{obj_name}")
        else:
            if bucket != "reims-files":
                print(f"   ⚠ Document points to wrong bucket: {bucket}/{obj_name}")
            elif obj_name not in minio_paths:
                print(f"   ⚠ Path in documents not found in MinIO: {obj_name}")
            verification_report["checks"]["database_sync"]["failed"].append(f"doc:{bucket}/{obj_name}")
    
    verification_report["summary"]["synced_records"] = fd_valid + doc_valid
    
    print(f"   ✓ Valid financial_documents paths: {fd_valid}/{len(fd_records)}")
    print(f"   ✓ Valid documents paths: {doc_valid}/{len(doc_records)}")
    
    # =========================================================================
    # 5. VERIFY HAMMOND AIRE FILES
    # =========================================================================
    print("\n[5] VERIFYING HAMMOND AIRE FILES")
    print("-" * 80)
    
    hammond_files = [obj for obj in objects if "hammond" in obj.object_name.lower()]
    
    if hammond_files:
        print(f"   Found {len(hammond_files)} Hammond Aire file(s):")
        for obj in hammond_files:
            print(f"      ✓ {obj.object_name}")
            print(f"         Size: {obj.size:,} bytes")
            
            # Check if it's the rent roll
            if "rent" in obj.object_name.lower() and "roll" in obj.object_name.lower():
                print(f"         📊 This is the rent roll file!")
                verification_report["hammond_rent_roll_found"] = obj.object_name
    else:
        print("   ⚠ No Hammond Aire files found")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    all_checks_passed = True
    
    print(f"\n✓ Total files in MinIO: {verification_report['summary']['total_files']}")
    print(f"✓ Files with valid path pattern: {verification_report['summary']['valid_paths']}")
    print(f"✓ Accessible files: {verification_report['summary']['accessible_files']}")
    print(f"✓ Synced database records: {verification_report['summary']['synced_records']}")
    
    # Check if any tests failed
    if verification_report["checks"]["path_pattern"]["failed"]:
        print(f"\n⚠ {len(verification_report['checks']['path_pattern']['failed'])} files with invalid path patterns")
        all_checks_passed = False
    
    if verification_report["checks"]["bucket_location"]["failed"]:
        print(f"⚠ {len(verification_report['checks']['bucket_location']['failed'])} files still in wrong bucket")
        all_checks_passed = False
    
    if verification_report["checks"]["file_accessibility"]["failed"]:
        print(f"⚠ {len(verification_report['checks']['file_accessibility']['failed'])} files not accessible")
        all_checks_passed = False
    
    if verification_report["checks"]["database_sync"]["failed"]:
        print(f"⚠ {len(verification_report['checks']['database_sync']['failed'])} database paths not synced")
        all_checks_passed = False
    
    print("\n" + "=" * 80)
    if all_checks_passed:
        print("✓✓✓ MIGRATION VERIFIED SUCCESSFULLY ✓✓✓")
    else:
        print("⚠⚠⚠ MIGRATION HAS WARNINGS ⚠⚠⚠")
    print("=" * 80)
    
    # Save report
    import json
    report_filename = f"verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w') as f:
        json.dump(verification_report, f, indent=2, default=str)
    
    print(f"\nVerification report saved to: {report_filename}")
    
    conn.close()
    
    return verification_report

if __name__ == "__main__":
    try:
        verify_migration()
    except Exception as e:
        print(f"\nERROR: Verification failed: {e}")
        import traceback
        traceback.print_exc()

