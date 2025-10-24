"""
Verify Document-Type-First Structure Implementation
Checks MinIO paths, database records, and file accessibility
"""

import sqlite3
from minio import Minio
from minio.error import S3Error
import json
from datetime import datetime

def verify_structure():
    print("=" * 80)
    print("VERIFICATION: DOCUMENT-TYPE-FIRST STRUCTURE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Connect to database
    conn = sqlite3.connect('reims.db')
    conn.row_factory = sqlite3.Row
    
    # Connect to MinIO
    minio_client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    
    verification_report = {
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "statistics": {
            "total_files": 0,
            "files_in_new_structure": 0,
            "database_synced": 0,
            "files_accessible": 0,
            "issues_found": 0
        }
    }
    
    # =========================================================================
    # CHECK 1: MinIO Structure
    # =========================================================================
    print("\n[1] CHECKING MINIO STRUCTURE")
    print("-" * 80)
    
    new_structure_files = []
    old_structure_files = []
    
    if minio_client.bucket_exists("reims-files"):
        for obj in minio_client.list_objects("reims-files", recursive=True):
            verification_report["statistics"]["total_files"] += 1
            
            if obj.object_name.startswith("Financial Statements/"):
                new_structure_files.append(obj.object_name)
                verification_report["statistics"]["files_in_new_structure"] += 1
            else:
                old_structure_files.append(obj.object_name)
    
    print(f"   Total files in reims-files: {verification_report['statistics']['total_files']}")
    print(f"   Files in new structure: {verification_report['statistics']['files_in_new_structure']}")
    print(f"   Files in old structure: {len(old_structure_files)}")
    
    if old_structure_files:
        print(f"\n   ⚠ WARNING: Found {len(old_structure_files)} files still in old structure:")
        for path in old_structure_files[:10]:
            print(f"      - {path}")
        if len(old_structure_files) > 10:
            print(f"      ... and {len(old_structure_files) - 10} more")
    else:
        print("   ✓ All files follow new structure")
    
    # =========================================================================
    # CHECK 2: Path Pattern Validation
    # =========================================================================
    print("\n[2] VALIDATING PATH PATTERNS")
    print("-" * 80)
    
    expected_patterns = [
        "Financial Statements/2024/Balance Sheets/",
        "Financial Statements/2024/Cash Flow Statements/",
        "Financial Statements/2024/Income Statements/",
        "Financial Statements/2025/Rent Rolls/"
    ]
    
    found_patterns = {}
    for pattern in expected_patterns:
        count = sum(1 for path in new_structure_files if path.startswith(pattern))
        found_patterns[pattern] = count
        status = "✓" if count > 0 else "✗"
        print(f"   {status} {pattern} ({count} files)")
    
    verification_report["checks"]["path_patterns"] = found_patterns
    
    # =========================================================================
    # CHECK 3: Filename Preservation
    # =========================================================================
    print("\n[3] CHECKING FILENAME PRESERVATION")
    print("-" * 80)
    
    files_with_uuid_prefix = []
    files_with_original_names = []
    
    import re
    uuid_pattern = r'^.*[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}_'
    
    for path in new_structure_files:
        filename = path.split('/')[-1]
        if re.match(uuid_pattern, path):
            files_with_uuid_prefix.append(path)
        else:
            files_with_original_names.append(path)
    
    print(f"   Files with original names: {len(files_with_original_names)}")
    print(f"   Files with UUID prefix: {len(files_with_uuid_prefix)}")
    
    if files_with_uuid_prefix:
        print(f"\n   ⚠ WARNING: Found files with UUID prefixes in new structure:")
        for path in files_with_uuid_prefix[:5]:
            print(f"      - {path}")
    else:
        print("   ✓ All files use original filenames")
    
    verification_report["checks"]["filename_preservation"] = {
        "original": len(files_with_original_names),
        "with_uuid": len(files_with_uuid_prefix)
    }
    
    # =========================================================================
    # CHECK 4: Database Synchronization
    # =========================================================================
    print("\n[4] CHECKING DATABASE SYNCHRONIZATION")
    print("-" * 80)
    
    cursor = conn.cursor()
    
    # Check financial_documents
    cursor.execute("""
        SELECT COUNT(*) as count FROM financial_documents
        WHERE file_path LIKE 'Financial Statements/%'
    """)
    fd_new_structure = cursor.fetchone()['count']
    
    # Check documents
    cursor.execute("""
        SELECT COUNT(*) as count FROM documents
        WHERE minio_object_name LIKE 'Financial Statements/%'
    """)
    doc_new_structure = cursor.fetchone()['count']
    
    print(f"   financial_documents with new paths: {fd_new_structure}")
    print(f"   documents with new paths: {doc_new_structure}")
    
    # Check for records pointing to old paths
    cursor.execute("""
        SELECT COUNT(*) as count FROM financial_documents
        WHERE file_path LIKE 'properties/%'
    """)
    fd_old_paths = cursor.fetchone()['count']
    
    cursor.execute("""
        SELECT COUNT(*) as count FROM documents
        WHERE minio_object_name LIKE 'properties/%'
    """)
    doc_old_paths = cursor.fetchone()['count']
    
    print(f"\n   financial_documents with old paths: {fd_old_paths}")
    print(f"   documents with old paths: {doc_old_paths}")
    
    if fd_old_paths > 0 or doc_old_paths > 0:
        print(f"   ⚠ WARNING: Database still contains old path references")
        verification_report["statistics"]["issues_found"] += 1
    else:
        print("   ✓ Database fully synchronized")
    
    verification_report["checks"]["database_sync"] = {
        "financial_documents_new": fd_new_structure,
        "documents_new": doc_new_structure,
        "financial_documents_old": fd_old_paths,
        "documents_old": doc_old_paths
    }
    
    # =========================================================================
    # CHECK 5: File Accessibility
    # =========================================================================
    print("\n[5] CHECKING FILE ACCESSIBILITY")
    print("-" * 80)
    
    accessible_count = 0
    inaccessible_files = []
    
    for path in new_structure_files[:20]:  # Test first 20 files
        try:
            minio_client.stat_object("reims-files", path)
            accessible_count += 1
        except S3Error as e:
            inaccessible_files.append({"path": path, "error": str(e)})
    
    total_tested = min(20, len(new_structure_files))
    print(f"   Tested: {total_tested} files")
    print(f"   Accessible: {accessible_count}")
    print(f"   Inaccessible: {len(inaccessible_files)}")
    
    if inaccessible_files:
        print(f"\n   ✗ WARNING: Some files are not accessible:")
        for item in inaccessible_files[:5]:
            print(f"      - {item['path']}: {item['error']}")
        verification_report["statistics"]["issues_found"] += len(inaccessible_files)
    else:
        print("   ✓ All tested files are accessible")
    
    verification_report["checks"]["accessibility"] = {
        "tested": total_tested,
        "accessible": accessible_count,
        "inaccessible": len(inaccessible_files)
    }
    
    # =========================================================================
    # CHECK 6: Sample Files
    # =========================================================================
    print("\n[6] SAMPLE FILES IN NEW STRUCTURE")
    print("-" * 80)
    
    sample_files = {
        "Balance Sheets": [],
        "Cash Flow Statements": [],
        "Income Statements": [],
        "Rent Rolls": [],
        "Other": []
    }
    
    for path in new_structure_files:
        for category in sample_files.keys():
            if category in path:
                sample_files[category].append(path)
                break
    
    for category, files in sample_files.items():
        print(f"\n   {category} ({len(files)} files):")
        for file in files[:5]:
            filename = file.split('/')[-1]
            print(f"      - {filename}")
        if len(files) > 5:
            print(f"      ... and {len(files) - 5} more")
    
    # =========================================================================
    # SAVE REPORT
    # =========================================================================
    report_filename = f"doctype_structure_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_filename, 'w') as f:
        json.dump(verification_report, f, indent=2, default=str)
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"   Total files: {verification_report['statistics']['total_files']}")
    print(f"   Files in new structure: {verification_report['statistics']['files_in_new_structure']}")
    print(f"   Issues found: {verification_report['statistics']['issues_found']}")
    print(f"\n   Report saved to: {report_filename}")
    
    if verification_report["statistics"]["issues_found"] == 0:
        print("\n   ✅ VERIFICATION PASSED - Structure is correct!")
    else:
        print(f"\n   ⚠ VERIFICATION WARNINGS - {verification_report['statistics']['issues_found']} issues found")
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    
    conn.close()
    
    return verification_report

if __name__ == "__main__":
    try:
        verify_structure()
    except Exception as e:
        print(f"\nERROR: Verification failed: {e}")
        import traceback
        traceback.print_exc()

