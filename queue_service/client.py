from redis import Redis
from rq import Queue
from rq.job import Job
from dotenv import load_dotenv
import os
from typing import Optional

# Load environment variables
load_dotenv()

class QueueClient:
    def __init__(self):
        self.redis_conn = Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD", ""),
            decode_responses=False,  # Don't decode responses automatically
            socket_connect_timeout=5,  # Add timeouts for better error handling
            socket_timeout=5
        )
        
        # Verify Redis connection
        try:
            self.redis_conn.ping()
        except Exception as e:
            raise Exception(f"Failed to connect to Redis: {str(e)}")
        
        # Create the main processing queue
        self.queue = Queue(
            name=os.getenv("QUEUE_NAME", "document-processing"),
            connection=self.redis_conn,
            is_async=True,
            default_timeout='10m'  # Default job timeout
        )

    def enqueue_document(self, document_id: str, metadata: dict) -> str:
        """
        Add a document to the processing queue
        Returns the job ID
        """
        from simple_worker import process_document
        
        job = self.queue.enqueue(
            process_document,
            args=(document_id, metadata),
            job_timeout='10m',  # Maximum job runtime
            result_ttl=24*60*60,  # Keep successful job results for 24 hours
            failure_ttl=7*24*60*60  # Keep failed jobs for 7 days
        )
        return job.id

    def get_job_status(self, job_id: str) -> dict:
        """
        Get the current status and result of a job
        """
        try:
            job = Job.fetch(job_id, connection=self.redis_conn)
            
            if not job:
                return {"status": "not_found"}
            
            status = {
                "job_id": job.id,
                "status": job.get_status(),
                "queue_name": job.origin,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "enqueued_at": job.enqueued_at.isoformat() if job.enqueued_at else None,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "ended_at": job.ended_at.isoformat() if job.ended_at else None,
                "execution_time": job.ended_at - job.started_at if job.ended_at and job.started_at else None
            }
            
            if job.is_finished:
                status["result"] = job.result
            elif job.is_failed:
                status["error"] = str(job.exc_info)
                status["error_details"] = {
                    "type": job._exc_info.__class__.__name__ if job._exc_info else None,
                    "message": str(job._exc_info) if job._exc_info else None
                }
                
            return status
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to fetch job status: {str(e)}"
            }

    def get_queue_info(self) -> dict:
        """
        Get information about the current state of the queue
        """
        return {
            "queued_jobs": self.queue.count,
            "started_jobs": len(self.queue.started_job_registry),
            "deferred_jobs": len(self.queue.deferred_job_registry),
            "finished_jobs": len(self.queue.finished_job_registry),
            "failed_jobs": len(self.queue.failed_job_registry)
        }

# Create a singleton instance
queue_client = QueueClient()