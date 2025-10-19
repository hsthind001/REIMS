#!/usr/bin/env python3
"""
Test the database integration directly without the web server
"""
import sys
import os
import uuid
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

def test_database():
    print("Testing database integration...")
    
    try:
        # Import database components
        from database import SessionLocal, Document, ProcessingJob, ExtractedData, create_tables
        print("✓ Database imports successful")
        
        # Create tables
        create_tables()
        print("✓ Database tables created")
        
        # Test database session
        db = SessionLocal()
        try:
            # Test creating a document record
            test_doc_id = str(uuid.uuid4())
            test_document = Document(
                document_id=test_doc_id,
                original_filename="test_document.pdf",
                stored_filename=f"{test_doc_id}_test_document.pdf",
                property_id="TEST_PROPERTY_001",
                file_size=1024,
                content_type="application/pdf",
                file_path=f"/storage/{test_doc_id}_test_document.pdf",
                status="uploaded"
            )
            db.add(test_document)
            db.commit()
            print(f"✓ Created test document: {test_doc_id}")
            
            # Test creating a processing job
            test_job = ProcessingJob(
                document_id=test_doc_id,
                job_id=f"job_{uuid.uuid4()}",
                status="queued"
            )
            db.add(test_job)
            db.commit()
            print("✓ Created test processing job")
            
            # Test creating extracted data
            test_data = ExtractedData(
                document_id=test_doc_id,
                data_type="financial_data",
                extracted_content={"revenue": 100000, "expenses": 50000},
                analysis_results={"extracted_at": datetime.utcnow().isoformat()}
            )
            db.add(test_data)
            db.commit()
            print("✓ Created test extracted data")
            
            # Test querying data
            documents = db.query(Document).all()
            jobs = db.query(ProcessingJob).all()
            data_records = db.query(ExtractedData).all()
            
            print(f"✓ Database queries successful:")
            print(f"  - Documents: {len(documents)}")
            print(f"  - Processing Jobs: {len(jobs)}")
            print(f"  - Extracted Data Records: {len(data_records)}")
            
            # Test the upload API functions
            print("\nTesting upload API database functions...")
            sys.path.append(os.path.join(os.path.dirname(__file__), "backend", "api"))
            
            # Test queue client
            from upload import get_queue_client
            queue_client = get_queue_client()
            if queue_client:
                print("✓ Queue client available")
            else:
                print("⚠ Queue client not available (expected if Redis not running)")
                
            print("\n✓ All database tests completed successfully!")
            return True
            
        except Exception as e:
            print(f"✗ Database operation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database()
    if success:
        print("\n🎉 Database integration is working correctly!")
    else:
        print("\n❌ Database integration has issues!")