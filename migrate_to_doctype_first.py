"""
Migrate MinIO Storage to Document-Type-First Structure
Reorganizes files to: Financial Statements/{year}/{subtype}/{original_filename}
"""

import sqlite3
from minio import Minio
from minio.error import S3Error
from minio.commonconfig import CopySource
from datetime import datetime
import json
import re

def get_document_subtype(filename):
    """Analyze filename to determine document subtype"""
    filename_lower = filename.lower()
    
    if 'balance' in filename_lower and 'sheet' in filename_lower:
        return 'Balance Sheets'
    elif 'cash' in filename_lower and 'flow' in filename_lower:
        return 'Cash Flow Statements'
    elif 'income' in filename_lower and 'statement' in filename_lower:
        return 'Income Statements'
    elif 'rent' in filename_lower and 'roll' in filename_lower:
        return 'Rent Rolls'
    else:
        return 'Other Financial Documents'

def extract_original_filename(path):
    """Extract original filename from path, removing any UUID prefixes"""
    filename = path.split('/')[-1]
    
    # Remove UUID prefix if present (format: uuid_filename)
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}_'
    filename = re.sub(uuid_pattern, '', filename, flags=re.IGNORECASE)
    
    return filename

def extract_year_from_filename(filename):
    """Extract year from filename"""
    # Look for 4-digit year (2020-2029)
    match = re.search(r'20(2[0-9])', filename)
    if match:
        return int(match.group(0))
    return datetime.now().year

def migrate_to_doctype_first():
    print("=" * 80)
    print("MIGRATION TO DOCUMENT-TYPE-FIRST STRUCTURE")
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
    
    # Ensure target bucket exists
    if not minio_client.bucket_exists("reims-files"):
        minio_client.make_bucket("reims-files")
        print("✓ Created reims-files bucket")
    
    migration_log = {
        "timestamp": datetime.now().isoformat(),
        "migrations": [],
        "errors": [],
        "statistics": {
            "files_migrated": 0,
            "files_skipped": 0,
            "files_failed": 0
        }
    }
    
    # =========================================================================
    # MIGRATE ALL FILES TO NEW STRUCTURE
    # =========================================================================
    print("\n[1] MIGRATING FILES TO DOCUMENT-TYPE-FIRST STRUCTURE")
    print("-" * 80)
    
    # Get all files from both buckets
    all_files = []
    
    for bucket_name in ["reims-files", "reims-documents"]:
        if minio_client.bucket_exists(bucket_name):
            objects = list(minio_client.list_objects(bucket_name, recursive=True))
            for obj in objects:
                all_files.append((bucket_name, obj))
    
    print(f"   Found {len(all_files)} total files to process")
    
    for bucket_name, obj in all_files:
        try:
            old_path = obj.object_name
            print(f"\n   Processing: {bucket_name}/{old_path}")
            
            # Extract original filename
            original_filename = extract_original_filename(old_path)
            
            # Determine document subtype
            doc_subtype = get_document_subtype(original_filename)
            
            # Extract year
            year = extract_year_from_filename(original_filename)
            
            # Build new path
            new_path = f"Financial Statements/{year}/{doc_subtype}/{original_filename}"
            
            print(f"      Original filename: {original_filename}")
            print(f"      Document type: {doc_subtype}")
            print(f"      Year: {year}")
            print(f"      New path: {new_path}")
            
            # Check if already in correct location
            if bucket_name == "reims-files" and old_path == new_path:
                print(f"      ✓ Already in correct location")
                migration_log["statistics"]["files_skipped"] += 1
                continue
            
            # Check if target already exists
            try:
                minio_client.stat_object("reims-files", new_path)
                print(f"      ⚠ File already exists at new location, skipping")
                migration_log["statistics"]["files_skipped"] += 1
                continue
            except:
                pass  # File doesn't exist, proceed
            
            # Copy to new location
            result = minio_client.copy_object(
                bucket_name="reims-files",
                object_name=new_path,
                source=CopySource(bucket_name, old_path)
            )
            
            print(f"      ✓ Copied to: reims-files/{new_path}")
            
            # Update database records
            cur = conn.cursor()
            
            # Update financial_documents
            cur.execute("""
                UPDATE financial_documents
                SET file_path = ?, file_name = ?
                WHERE file_name = ? OR file_path LIKE ?
            """, (new_path, original_filename, original_filename, f"%{original_filename}%"))
            
            rows_updated_fd = cur.rowcount
            
            # Update documents
            cur.execute("""
                UPDATE documents
                SET minio_bucket = 'reims-files',
                    minio_object_name = ?,
                    minio_url = ?,
                    file_path = ?,
                    original_filename = ?,
                    stored_filename = ?
                WHERE original_filename = ? OR minio_object_name LIKE ?
            """, (
                new_path,
                f"http://localhost:9000/reims-files/{new_path}",
                new_path,
                original_filename,
                original_filename,
                original_filename,
                f"%{original_filename}%"
            ))
            
            rows_updated_doc = cur.rowcount
            
            conn.commit()
            print(f"      ✓ Updated database ({rows_updated_fd} financial_documents, {rows_updated_doc} documents)")
            
            migration_log["migrations"].append({
                "old_path": f"{bucket_name}/{old_path}",
                "new_path": f"reims-files/{new_path}",
                "original_filename": original_filename,
                "year": year,
                "subtype": doc_subtype,
                "status": "success"
            })
            
            migration_log["statistics"]["files_migrated"] += 1
            
        except Exception as e:
            print(f"      ✗ Error: {e}")
            migration_log["errors"].append({
                "file": f"{bucket_name}/{old_path}",
                "error": str(e)
            })
            migration_log["statistics"]["files_failed"] += 1
    
    # =========================================================================
    # SAVE MIGRATION LOG
    # =========================================================================
    log_filename = f"doctype_first_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(log_filename, 'w') as f:
        json.dump(migration_log, f, indent=2, default=str)
    
    print("\n" + "=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)
    print(f"   Files migrated: {migration_log['statistics']['files_migrated']}")
    print(f"   Files skipped: {migration_log['statistics']['files_skipped']}")
    print(f"   Files failed: {migration_log['statistics']['files_failed']}")
    print(f"\n   Migration log saved to: {log_filename}")
    
    if migration_log["errors"]:
        print(f"\n   ⚠ {len(migration_log['errors'])} errors occurred:")
        for error in migration_log["errors"][:10]:  # Show first 10
            print(f"      {error['file']}: {error['error']}")
    
    print("\n   ⚠ NOTE: Old files have NOT been deleted for safety.")
    print("   After verifying migration, you can manually delete old files.")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("MIGRATION COMPLETE")
    print("=" * 80)
    
    return migration_log

if __name__ == "__main__":
    try:
        migrate_to_doctype_first()
    except Exception as e:
        print(f"\nERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()

