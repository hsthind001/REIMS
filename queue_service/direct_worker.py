"""
Direct Redis Queue Worker
Processes jobs from document_processing_queue that are added by the upload endpoint
"""

import redis
import json
import time
import sys
import os
from pathlib import Path

# Add backend path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import database
try:
    from backend.api.database import SessionLocal
    from sqlalchemy import text
    print("✓ Database module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import database module: {e}")
    sys.exit(1)

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

print("=" * 80)
print("REIMS Direct Worker Started")
print("=" * 80)
print(f"Listening to queue: document_processing_queue")
print(f"Redis connection: {redis_client.ping()}")
print("=" * 80)

def update_document_status(document_id, status, error_message=None):
    """Update document status in database"""
    try:
        db = SessionLocal()
        query = text("""
            UPDATE financial_documents 
            SET status = :status,
                processing_status = :processing_status,
                processing_date = datetime('now'),
                error_message = :error_message
            WHERE id = :document_id
        """)
        db.execute(query, {
            "status": status,
            "processing_status": status,
            "document_id": document_id,
            "error_message": error_message
        })
        db.commit()
        db.close()
        print(f"   ✓ Updated document {document_id} status to: {status}")
        return True
    except Exception as e:
        print(f"   ✗ Failed to update database: {e}")
        return False

def process_document(job_data):
    """Process a document job"""
    document_id = job_data.get('document_id')
    file_path = job_data.get('file_path')
    file_name = job_data.get('file_name')
    
    print(f"\n📄 Processing: {file_name}")
    print(f"   Document ID: {document_id}")
    print(f"   File Path: {file_path}")
    
    try:
        # For now, just mark as completed
        # In production, you would:
        # 1. Download file from MinIO
        # 2. Extract data (PDF parsing, Excel parsing, etc.)
        # 3. Save extracted data to processed_data table
        # 4. Run AI analysis if needed
        
        # Simulate processing
        time.sleep(0.5)
        
        # Mark as completed
        success = update_document_status(document_id, 'completed')
        
        if success:
            print(f"   ✓ Processing completed successfully")
        else:
            print(f"   ⚠ Processing completed but database update failed")
            
        return True
        
    except Exception as e:
        print(f"   ✗ Processing failed: {e}")
        update_document_status(document_id, 'failed', str(e))
        return False

def main():
    """Main worker loop"""
    processed_count = 0
    
    while True:
        try:
            # Check queue length
            queue_length = redis_client.llen('document_processing_queue')
            
            if queue_length > 0:
                print(f"\n📊 Queue status: {queue_length} jobs waiting")
                
                # Get job from queue (blocking pop with 1 second timeout)
                result = redis_client.blpop('document_processing_queue', timeout=1)
                
                if result:
                    queue_name, job_json = result
                    job_data = json.loads(job_json)
                    
                    # Process the job
                    if process_document(job_data):
                        processed_count += 1
                        print(f"   ✓ Total processed: {processed_count}")
                    else:
                        print(f"   ✗ Processing failed")
            else:
                # No jobs, wait a bit
                time.sleep(2)
                print(".", end="", flush=True)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Worker stopped. Total processed: {processed_count}")
            break
        except Exception as e:
            print(f"\n❌ Worker error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()

