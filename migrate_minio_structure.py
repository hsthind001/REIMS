"""
Migrate MinIO Storage to Standardized Structure
Reorganizes files from old patterns to: properties/{property_id}/{doc_type}/{year}/{filename}
"""

import sqlite3
from minio import Minio
from minio.error import S3Error
from datetime import datetime
import json
from io import BytesIO

def get_property_info(conn, property_id):
    """Get property name from properties table"""
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM properties WHERE id = ?", (property_id,))
    result = cur.fetchone()
    return result if result else (property_id, "Unknown")

def parse_document_metadata(conn, filename):
    """Extract metadata from database for a file"""
    cur = conn.cursor()
    
    # Try financial_documents first
    cur.execute("""
        SELECT property_id, property_name, document_year, document_type, document_period
        FROM financial_documents
        WHERE file_name = ? OR file_path LIKE ?
        ORDER BY upload_date DESC
        LIMIT 1
    """, (filename, f"%{filename}%"))
    
    result = cur.fetchone()
    if result:
        return {
            "property_id": result[0],
            "property_name": result[1],
            "year": result[2] or 2024,
            "doc_type": result[3] or "other",
            "period": result[4] or "Annual"
        }
    
    # Try documents table
    cur.execute("""
        SELECT property_id, property_name, document_year, document_type
        FROM documents
        WHERE original_filename = ? OR minio_object_name LIKE ?
        ORDER BY upload_timestamp DESC
        LIMIT 1
    """, (filename, f"%{filename}%"))
    
    result = cur.fetchone()
    if result:
        return {
            "property_id": result[0],
            "property_name": result[1],
            "year": result[2] or 2024,
            "doc_type": result[3] or "other",
            "period": "Annual"
        }
    
    # Fallback: parse from filename
    year = 2024
    if "2025" in filename:
        year = 2025
    elif "2024" in filename:
        year = 2024
    elif "2023" in filename:
        year = 2023
    
    # Determine document type
    doc_type = "other"
    filename_lower = filename.lower()
    if "rent" in filename_lower and "roll" in filename_lower:
        doc_type = "rent_roll"
    elif "balance" in filename_lower and "sheet" in filename_lower:
        doc_type = "financial_statement"
    elif "income" in filename_lower and "statement" in filename_lower:
        doc_type = "financial_statement"
    elif "cash" in filename_lower and "flow" in filename_lower:
        doc_type = "financial_statement"
    
    return {
        "property_id": "1",  # Default
        "property_name": "Unknown",
        "year": year,
        "doc_type": doc_type,
        "period": "Annual"
    }

def map_doc_type_to_folder(doc_type):
    """Map document type to standardized folder name"""
    mapping = {
        'financial_statement': 'financial-statements',
        'rent_roll': 'rent-rolls',
        'offering_memo': 'offering-memos',
        'lease_agreement': 'lease-agreements',
        'maintenance_record': 'maintenance-records',
        'other': 'other'
    }
    return mapping.get(doc_type, 'other')

def migrate_storage():
    print("=" * 80)
    print("REIMS STORAGE MIGRATION")
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
    # MIGRATE FILES FROM REIMS-DOCUMENTS BUCKET
    # =========================================================================
    print("\n[1] MIGRATING FILES FROM REIMS-DOCUMENTS BUCKET")
    print("-" * 80)
    
    if minio_client.bucket_exists("reims-documents"):
        objects = list(minio_client.list_objects("reims-documents", recursive=True))
        print(f"   Found {len(objects)} files in reims-documents bucket")
        
        for obj in objects:
            try:
                old_path = obj.object_name
                filename = old_path.split('/')[-1]
                
                print(f"\n   Processing: {old_path}")
                
                # Get metadata
                metadata = parse_document_metadata(conn, filename)
                property_id = metadata["property_id"]
                year = metadata["year"]
                doc_type = metadata["doc_type"]
                
                # Map document type
                doc_type_folder = map_doc_type_to_folder(doc_type)
                
                # Build new path
                new_path = f"properties/{property_id}/{doc_type_folder}/{year}/{filename}"
                
                print(f"      Property ID: {property_id} ({metadata.get('property_name', 'Unknown')})")
                print(f"      Type: {doc_type} -> {doc_type_folder}")
                print(f"      Year: {year}")
                print(f"      New path: {new_path}")
                
                # Check if already exists in new location
                try:
                    minio_client.stat_object("reims-files", new_path)
                    print(f"      ⚠ File already exists at new location, skipping")
                    migration_log["statistics"]["files_skipped"] += 1
                    continue
                except:
                    pass  # File doesn't exist, proceed with migration
                
                # Copy file to new location
                from minio.commonconfig import CopySource
                result = minio_client.copy_object(
                    bucket_name="reims-files",
                    object_name=new_path,
                    source=CopySource("reims-documents", old_path)
                )
                
                print(f"      ✓ Copied to: reims-files/{new_path}")
                
                # Update database records
                cur = conn.cursor()
                
                # Update financial_documents
                cur.execute("""
                    UPDATE financial_documents
                    SET file_path = ?
                    WHERE file_name = ? OR file_path LIKE ?
                """, (new_path, filename, f"%{filename}%"))
                
                # Update documents
                cur.execute("""
                    UPDATE documents
                    SET minio_bucket = 'reims-files',
                        minio_object_name = ?,
                        minio_url = ?,
                        file_path = ?
                    WHERE original_filename = ? OR minio_object_name LIKE ?
                """, (
                    new_path,
                    f"http://localhost:9000/reims-files/{new_path}",
                    new_path,
                    filename,
                    f"%{filename}%"
                ))
                
                conn.commit()
                print(f"      ✓ Updated database records")
                
                # Delete old file (commented out for safety - uncomment after verification)
                # minio_client.remove_object("reims-documents", old_path)
                # print(f"      ✓ Deleted old file")
                
                migration_log["migrations"].append({
                    "old_path": f"reims-documents/{old_path}",
                    "new_path": f"reims-files/{new_path}",
                    "property_id": property_id,
                    "year": year,
                    "status": "success"
                })
                
                migration_log["statistics"]["files_migrated"] += 1
                
            except Exception as e:
                print(f"      ✗ Error: {e}")
                migration_log["errors"].append({
                    "file": old_path,
                    "error": str(e)
                })
                migration_log["statistics"]["files_failed"] += 1
    else:
        print("   No reims-documents bucket found")
    
    # =========================================================================
    # UPDATE FILES IN REIMS-FILES BUCKET (Add year folder)
    # =========================================================================
    print("\n\n[2] UPDATING FILES IN REIMS-FILES BUCKET")
    print("-" * 80)
    
    objects = list(minio_client.list_objects("reims-files", recursive=True))
    print(f"   Found {len(objects)} files in reims-files bucket")
    
    for obj in objects:
        try:
            old_path = obj.object_name
            filename = old_path.split('/')[-1]
            
            # Check if already in correct format
            parts = old_path.split('/')
            if len(parts) >= 4 and parts[0] == "properties":
                # Already has year folder
                print(f"   ✓ Already standardized: {old_path}")
                migration_log["statistics"]["files_skipped"] += 1
                continue
            
            print(f"\n   Processing: {old_path}")
            
            # Get metadata
            metadata = parse_document_metadata(conn, filename)
            property_id = metadata["property_id"]
            year = metadata["year"]
            doc_type = metadata["doc_type"]
            
            # Map document type
            doc_type_folder = map_doc_type_to_folder(doc_type)
            
            # Build new path
            new_path = f"properties/{property_id}/{doc_type_folder}/{year}/{filename}"
            
            print(f"      Property ID: {property_id}")
            print(f"      Type: {doc_type} -> {doc_type_folder}")
            print(f"      Year: {year}")
            print(f"      New path: {new_path}")
            
            if old_path == new_path:
                print(f"      ✓ Path is already correct")
                migration_log["statistics"]["files_skipped"] += 1
                continue
            
            # Check if target already exists
            try:
                minio_client.stat_object("reims-files", new_path)
                print(f"      ⚠ File already exists at new location, skipping")
                migration_log["statistics"]["files_skipped"] += 1
                continue
            except:
                pass
            
            # Copy to new location
            from minio.commonconfig import CopySource
            result = minio_client.copy_object(
                bucket_name="reims-files",
                object_name=new_path,
                source=CopySource("reims-files", old_path)
            )
            
            print(f"      ✓ Copied to: {new_path}")
            
            # Update database records
            cur = conn.cursor()
            
            # Update financial_documents
            cur.execute("""
                UPDATE financial_documents
                SET file_path = ?
                WHERE file_path = ? OR file_name = ?
            """, (new_path, old_path, filename))
            
            # Update documents
            cur.execute("""
                UPDATE documents
                SET minio_object_name = ?,
                    minio_url = ?,
                    file_path = ?
                WHERE minio_object_name = ? OR original_filename = ?
            """, (
                new_path,
                f"http://localhost:9000/reims-files/{new_path}",
                new_path,
                old_path,
                filename
            ))
            
            conn.commit()
            print(f"      ✓ Updated database records")
            
            # Delete old file (commented out for safety)
            # minio_client.remove_object("reims-files", old_path)
            # print(f"      ✓ Deleted old file")
            
            migration_log["migrations"].append({
                "old_path": f"reims-files/{old_path}",
                "new_path": f"reims-files/{new_path}",
                "property_id": property_id,
                "year": year,
                "status": "success"
            })
            
            migration_log["statistics"]["files_migrated"] += 1
            
        except Exception as e:
            print(f"      ✗ Error: {e}")
            migration_log["errors"].append({
                "file": old_path,
                "error": str(e)
            })
            migration_log["statistics"]["files_failed"] += 1
    
    # =========================================================================
    # SAVE MIGRATION LOG
    # =========================================================================
    log_filename = f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
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
        for error in migration_log["errors"]:
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
        migrate_storage()
    except Exception as e:
        print(f"\nERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()

