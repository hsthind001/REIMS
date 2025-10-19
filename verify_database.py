#!/usr/bin/env python3
"""
Verify database integration and check stored documents
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

def check_database():
    print("=== Database Integration Verification ===")
    
    db_path = "reims.db"
    if not Path(db_path).exists():
        print(f"❌ Database file {db_path} does not exist")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if documents table exists and has MinIO fields
        cursor.execute("PRAGMA table_info(documents)")
        columns = cursor.fetchall()
        
        print(f"✅ Database connected successfully")
        print(f"📋 Documents table has {len(columns)} columns:")
        
        minio_fields = []
        for col in columns:
            col_name = col[1]  # Column name is at index 1
            col_type = col[2]  # Column type is at index 2
            print(f"   - {col_name} ({col_type})")
            
            if 'minio' in col_name.lower():
                minio_fields.append(col_name)
        
        print(f"\n🗂️ MinIO-related fields found: {len(minio_fields)}")
        for field in minio_fields:
            print(f"   - {field}")
        
        # Check existing documents
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        print(f"\n📄 Total documents in database: {doc_count}")
        
        if doc_count > 0:
            # Get recent documents
            cursor.execute("""
                SELECT document_id, original_filename, property_id, 
                       storage_type, minio_bucket, minio_object_name, minio_url,
                       upload_timestamp, minio_upload_timestamp
                FROM documents 
                ORDER BY upload_timestamp DESC 
                LIMIT 5
            """)
            
            recent_docs = cursor.fetchall()
            print(f"\n📋 Recent documents:")
            for doc in recent_docs:
                print(f"   📄 {doc[1]} (Property: {doc[2]})")
                print(f"      ID: {doc[0]}")
                print(f"      Storage: {doc[3]}")
                if doc[4]:  # minio_bucket
                    print(f"      MinIO: {doc[4]}/{doc[5]}")
                print(f"      Uploaded: {doc[7]}")
                print()
        
        # Check MinIO integration status
        cursor.execute("SELECT COUNT(*) FROM documents WHERE storage_type = 'local_and_minio'")
        minio_count = cursor.fetchone()[0]
        print(f"🗄️ Documents stored in MinIO: {minio_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def create_test_record():
    print("\n=== Creating Test Database Record ===")
    
    try:
        # Import the database models
        import sys
        sys.path.append(str(Path(__file__).parent / "backend"))
        from database import SessionLocal, Document
        
        db = SessionLocal()
        
        # Create a test document record
        test_doc = Document(
            document_id="test-db-integration-001",
            original_filename="test_database_integration.txt",
            stored_filename="test-db-integration-001_test_database_integration.txt",
            property_id="TEST-DB-001",
            file_size=500,
            content_type="text/plain",
            file_path="storage/test-db-integration-001_test_database_integration.txt",
            upload_timestamp=datetime.now(),
            status="uploaded",
            minio_bucket="reims-documents",
            minio_object_name="frontend-uploads/TEST-DB-001/test-db-integration-001_test_database_integration.txt",
            minio_url="minio://reims-documents/frontend-uploads/TEST-DB-001/test-db-integration-001_test_database_integration.txt",
            storage_type="local_and_minio",
            minio_upload_timestamp=datetime.now()
        )
        
        db.add(test_doc)
        db.commit()
        db.refresh(test_doc)
        
        print(f"✅ Test record created successfully")
        print(f"   Document ID: {test_doc.document_id}")
        print(f"   Property ID: {test_doc.property_id}")
        print(f"   Storage Type: {test_doc.storage_type}")
        print(f"   MinIO URL: {test_doc.minio_url}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test record: {e}")
        return False

if __name__ == "__main__":
    if check_database():
        print("\n" + "="*50)
        create_test_record()
        print("\n" + "="*50)
        print("Re-checking database after test record...")
        check_database()
    else:
        print("Database verification failed")