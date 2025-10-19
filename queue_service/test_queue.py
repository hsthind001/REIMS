from client import queue_client
import asyncio
import time
import uuid
from datetime import datetime

async def test_queue():
    """Test the queue service functionality"""
    try:
        print(f"\n=== Queue Service Tests ({datetime.now().isoformat()}) ===\n")
        
        print("1. Testing Redis connection...")
        queue_info = queue_client.get_queue_info()
        print("Queue info:", queue_info)
        print("✓ Redis connection successful")

        # Test document enqueueing
        print("\n2. Testing document enqueueing...")
        test_doc_id = str(uuid.uuid4())
        test_metadata = {
            "filename": "test.pdf",
            "content_type": "application/pdf",
            "size": 1024,
            "test_id": str(uuid.uuid4())
        }
        
        job_id = queue_client.enqueue_document(test_doc_id, test_metadata)
        print(f"Job ID: {job_id}")
        assert job_id is not None, "Job ID should not be None"
        print("✓ Document enqueued successfully")

        # Test job status retrieval
        print("\n3. Testing job status retrieval...")
        status = queue_client.get_job_status(job_id)
        print("Initial status:", status)
        assert status.get("status") != "error", f"Error getting job status: {status.get('error')}"
        
        # Wait for job completion
        print("\nWaiting for job completion...")
        max_wait = 30  # Maximum wait time in seconds
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < max_wait:
            status = queue_client.get_job_status(job_id)
            current_status = status.get("status")
            
            # Only print status when it changes
            if current_status != last_status:
                print(f"Job status: {current_status}")
                last_status = current_status
            
            if current_status == "finished":
                print("\nJob result:", status.get("result"))
                break
            elif current_status == "failed":
                print("\nJob failed:", status.get("error"))
                break
                
            await asyncio.sleep(1)
        else:
            print("\nWarning: Job did not complete within timeout period")
            
        print("\nFinal job details:", status)
        assert status.get("status") != "error", f"Error in final status: {status.get('error')}"
        
        # Test queue metrics
        print("\n4. Testing queue metrics...")
        metrics = queue_client.get_queue_info()
        print("Queue metrics:", metrics)
        
        print("\n✓ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise
    finally:
        print("\n=== Test run completed ===\n")

if __name__ == "__main__":
    asyncio.run(test_queue())