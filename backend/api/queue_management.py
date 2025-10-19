"""
Queue Management API for REIMS
Provides endpoints to manage background processing jobs
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import sys
from pathlib import Path

# Add queue service path
sys.path.append(str(Path(__file__).parent.parent.parent / "queue_service"))

from queue_manager import queue_manager, JobPriority

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/queue", tags=["queue"])

class JobRequest(BaseModel):
    job_type: str
    job_data: Dict[str, Any]
    priority: Optional[str] = "normal"
    delay_seconds: Optional[int] = 0

class BatchJobRequest(BaseModel):
    document_ids: List[str]
    options: Optional[Dict[str, Any]] = {}
    priority: Optional[str] = "normal"

@router.post("/jobs")
async def create_job(job_request: JobRequest):
    """
    Create a new background job
    """
    try:
        # Map priority string to enum
        priority_map = {
            'low': JobPriority.LOW,
            'normal': JobPriority.NORMAL,
            'high': JobPriority.HIGH,
            'urgent': JobPriority.URGENT
        }
        
        priority = priority_map.get(job_request.priority.lower(), JobPriority.NORMAL)
        
        # Determine queue based on job type
        queue_map = {
            'document_processing': 'document_processing',
            'ai_analysis': 'ai_analysis',
            'notification': 'notifications',
            'batch_processing': 'document_processing'
        }
        
        queue_name = queue_map.get(job_request.job_type, 'document_processing')
        
        # Create job
        job_id = queue_manager.enqueue_job(
            queue_name=queue_name,
            job_type=job_request.job_type,
            job_data=job_request.job_data,
            priority=priority,
            delay_seconds=job_request.delay_seconds
        )
        
        return {
            "status": "created",
            "job_id": job_id,
            "queue_name": queue_name,
            "priority": job_request.priority,
            "delay_seconds": job_request.delay_seconds
        }
        
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/batch/process-documents")
async def create_batch_processing_job(batch_request: BatchJobRequest):
    """
    Create a batch job to process multiple documents
    """
    try:
        priority_map = {
            'low': JobPriority.LOW,
            'normal': JobPriority.NORMAL,
            'high': JobPriority.HIGH,
            'urgent': JobPriority.URGENT
        }
        
        priority = priority_map.get(batch_request.priority.lower(), JobPriority.NORMAL)
        
        job_id = queue_manager.enqueue_job(
            queue_name='document_processing',
            job_type='batch_processing',
            job_data={
                'document_ids': batch_request.document_ids,
                'options': batch_request.options
            },
            priority=priority
        )
        
        return {
            "status": "created",
            "job_id": job_id,
            "document_count": len(batch_request.document_ids),
            "priority": batch_request.priority
        }
        
    except Exception as e:
        logger.error(f"Error creating batch job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status and details of a specific job
    """
    try:
        job_data = queue_manager.get_job_status(job_id)
        
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": job_id,
            "status": job_data.get("status"),
            "job_type": job_data.get("job_type"),
            "queue_name": job_data.get("queue_name"),
            "priority": job_data.get("priority"),
            "created_at": job_data.get("created_at"),
            "updated_at": job_data.get("updated_at"),
            "started_at": job_data.get("started_at"),
            "completed_at": job_data.get("completed_at"),
            "failed_at": job_data.get("failed_at"),
            "attempts": job_data.get("attempts", 0),
            "max_attempts": job_data.get("max_attempts", 3),
            "error_message": job_data.get("error_message"),
            "result": job_data.get("result"),
            "worker_id": job_data.get("worker_id")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queues/{queue_name}/stats")
async def get_queue_stats(queue_name: str):
    """
    Get statistics for a specific queue
    """
    try:
        stats = queue_manager.get_queue_stats(queue_name)
        
        return {
            "queue_name": queue_name,
            "statistics": stats,
            "total_jobs": sum(stats.values())
        }
        
    except Exception as e:
        logger.error(f"Error getting queue stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queues/stats")
async def get_all_queue_stats():
    """
    Get statistics for all queues
    """
    try:
        queue_names = ['document_processing', 'ai_analysis', 'notifications']
        all_stats = {}
        
        for queue_name in queue_names:
            stats = queue_manager.get_queue_stats(queue_name)
            all_stats[queue_name] = {
                "statistics": stats,
                "total_jobs": sum(stats.values())
            }
        
        return {
            "queues": all_stats,
            "summary": {
                "total_pending": sum(q["statistics"]["pending"] for q in all_stats.values()),
                "total_processing": sum(q["statistics"]["processing"] for q in all_stats.values()),
                "total_completed": sum(q["statistics"]["completed"] for q in all_stats.values()),
                "total_failed": sum(q["statistics"]["failed"] for q in all_stats.values())
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting all queue stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/queues/cleanup")
async def cleanup_completed_jobs(older_than_hours: int = 24):
    """
    Clean up completed jobs older than specified hours
    """
    try:
        cleaned_count = queue_manager.cleanup_completed_jobs(older_than_hours)
        
        return {
            "status": "completed",
            "cleaned_jobs": cleaned_count,
            "older_than_hours": older_than_hours
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """
    Cancel a pending job (not yet implemented in queue manager)
    """
    try:
        job_data = queue_manager.get_job_status(job_id)
        
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job_data.get("status") in ["completed", "failed", "cancelled"]:
            return {
                "status": "already_finished",
                "job_id": job_id,
                "current_status": job_data.get("status")
            }
        
        # For now, just return that cancellation is not supported
        # In a full implementation, you would remove from queue and mark as cancelled
        return {
            "status": "cancellation_not_implemented",
            "job_id": job_id,
            "message": "Job cancellation not yet implemented"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def queue_health_check():
    """
    Health check for queue system
    """
    try:
        # Test basic queue operations
        test_stats = queue_manager.get_queue_stats("document_processing")
        
        return {
            "status": "healthy",
            "queue_manager": "operational",
            "redis_connection": "available" if queue_manager.redis_client else "fallback_memory",
            "test_queue_stats": test_stats
        }
        
    except Exception as e:
        logger.error(f"Queue health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }