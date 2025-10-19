"""
Redis-based Queue Manager for REIMS
Handles asynchronous document processing tasks
"""

import redis
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3

class QueueManager:
    """
    Redis-based queue manager for background job processing
    """
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                db=redis_db,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Connected to Redis successfully")
        except redis.ConnectionError:
            logger.warning("Redis not available - using in-memory fallback")
            self.redis_client = None
            self._memory_store = {}
            self._memory_queues = {
                'document_processing': [],
                'ai_analysis': [],
                'notifications': []
            }
    
    def enqueue_job(self, queue_name: str, job_type: str, job_data: Dict[str, Any], 
                    priority: JobPriority = JobPriority.NORMAL, 
                    delay_seconds: int = 0) -> str:
        """
        Add a job to the specified queue
        """
        job_id = str(uuid.uuid4())
        
        job = {
            'job_id': job_id,
            'job_type': job_type,
            'queue_name': queue_name,
            'job_data': job_data,
            'priority': priority.value,
            'status': JobStatus.PENDING.value,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'scheduled_at': (datetime.utcnow() + timedelta(seconds=delay_seconds)).isoformat(),
            'attempts': 0,
            'max_attempts': 3,
            'error_message': None,
            'result': None
        }
        
        if self.redis_client:
            # Store job details
            self.redis_client.hset(f"job:{job_id}", mapping=job)
            
            # Add to priority queue
            score = priority.value * 1000000 + int(datetime.utcnow().timestamp())
            if delay_seconds > 0:
                # Schedule for later
                self.redis_client.zadd(f"scheduled:{queue_name}", {job_id: score + delay_seconds})
            else:
                # Add to immediate processing queue
                self.redis_client.zadd(f"queue:{queue_name}", {job_id: score})
            
            logger.info(f"Job {job_id} enqueued to {queue_name}")
        else:
            # Memory fallback
            self._memory_store[job_id] = job
            if queue_name not in self._memory_queues:
                self._memory_queues[queue_name] = []
            self._memory_queues[queue_name].append(job_id)
            logger.info(f"Job {job_id} added to memory queue {queue_name}")
        
        return job_id
    
    def dequeue_job(self, queue_name: str, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the next job from the queue for processing
        """
        if self.redis_client:
            # Move scheduled jobs to active queue if their time has come
            self._process_scheduled_jobs(queue_name)
            
            # Get highest priority job
            jobs = self.redis_client.zrevrange(f"queue:{queue_name}", 0, 0, withscores=True)
            
            if jobs:
                job_id, score = jobs[0]
                
                # Remove from queue and mark as processing
                self.redis_client.zrem(f"queue:{queue_name}", job_id)
                self.redis_client.hset(f"job:{job_id}", mapping={
                    'status': JobStatus.PROCESSING.value,
                    'worker_id': worker_id,
                    'started_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                })
                
                # Get full job details
                job_data = self.redis_client.hgetall(f"job:{job_id}")
                if job_data:
                    job_data['job_data'] = json.loads(job_data.get('job_data', '{}'))
                    return job_data
        else:
            # Memory fallback
            if queue_name in self._memory_queues and self._memory_queues[queue_name]:
                job_id = self._memory_queues[queue_name].pop(0)
                job = self._memory_store.get(job_id)
                if job:
                    job['status'] = JobStatus.PROCESSING.value
                    job['worker_id'] = worker_id
                    job['started_at'] = datetime.utcnow().isoformat()
                    job['updated_at'] = datetime.utcnow().isoformat()
                    return job
        
        return None
    
    def complete_job(self, job_id: str, result: Dict[str, Any] = None):
        """
        Mark a job as completed
        """
        update_data = {
            'status': JobStatus.COMPLETED.value,
            'completed_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if result:
            update_data['result'] = json.dumps(result)
        
        if self.redis_client:
            self.redis_client.hset(f"job:{job_id}", mapping=update_data)
        else:
            job = self._memory_store.get(job_id)
            if job:
                job.update(update_data)
                if result:
                    job['result'] = result
        
        logger.info(f"Job {job_id} completed")
    
    def fail_job(self, job_id: str, error_message: str, retry: bool = True):
        """
        Mark a job as failed, optionally retry
        """
        if self.redis_client:
            job_data = self.redis_client.hgetall(f"job:{job_id}")
            attempts = int(job_data.get('attempts', 0)) + 1
            max_attempts = int(job_data.get('max_attempts', 3))
            
            update_data = {
                'attempts': attempts,
                'error_message': error_message,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if retry and attempts < max_attempts:
                # Retry with exponential backoff
                delay_seconds = 60 * (2 ** (attempts - 1))  # 1min, 2min, 4min...
                
                update_data['status'] = JobStatus.PENDING.value
                self.redis_client.hset(f"job:{job_id}", mapping=update_data)
                
                # Schedule retry
                score = int((datetime.utcnow() + timedelta(seconds=delay_seconds)).timestamp())
                self.redis_client.zadd(f"scheduled:{job_data['queue_name']}", {job_id: score})
                
                logger.info(f"Job {job_id} scheduled for retry in {delay_seconds} seconds")
            else:
                # Mark as permanently failed
                update_data['status'] = JobStatus.FAILED.value
                update_data['failed_at'] = datetime.utcnow().isoformat()
                self.redis_client.hset(f"job:{job_id}", mapping=update_data)
                
                logger.error(f"Job {job_id} permanently failed: {error_message}")
        else:
            # Memory fallback
            job = self._memory_store.get(job_id)
            if job:
                job['attempts'] = job.get('attempts', 0) + 1
                job['error_message'] = error_message
                job['updated_at'] = datetime.utcnow().isoformat()
                
                if not retry or job['attempts'] >= job.get('max_attempts', 3):
                    job['status'] = JobStatus.FAILED.value
                    job['failed_at'] = datetime.utcnow().isoformat()
                else:
                    job['status'] = JobStatus.PENDING.value
                    # For memory fallback, just re-add to queue
                    queue_name = job['queue_name']
                    if queue_name not in self._memory_queues:
                        self._memory_queues[queue_name] = []
                    self._memory_queues[queue_name].append(job_id)
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of a job
        """
        if self.redis_client:
            job_data = self.redis_client.hgetall(f"job:{job_id}")
            if job_data:
                # Parse JSON fields
                if 'job_data' in job_data:
                    job_data['job_data'] = json.loads(job_data['job_data'])
                if 'result' in job_data and job_data['result']:
                    job_data['result'] = json.loads(job_data['result'])
                return job_data
        else:
            return self._memory_store.get(job_id)
        
        return None
    
    def get_queue_stats(self, queue_name: str) -> Dict[str, int]:
        """
        Get statistics for a queue
        """
        stats = {
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'failed': 0,
            'scheduled': 0
        }
        
        if self.redis_client:
            stats['pending'] = self.redis_client.zcard(f"queue:{queue_name}")
            stats['scheduled'] = self.redis_client.zcard(f"scheduled:{queue_name}")
            
            # Count jobs by status (this is expensive, consider caching)
            job_keys = self.redis_client.keys("job:*")
            for job_key in job_keys:
                job_data = self.redis_client.hgetall(job_key)
                if job_data.get('queue_name') == queue_name:
                    status = job_data.get('status', 'unknown')
                    if status in stats:
                        stats[status] += 1
        else:
            # Memory fallback
            if queue_name in self._memory_queues:
                stats['pending'] = len(self._memory_queues[queue_name])
            
            for job_id, job in self._memory_store.items():
                if job.get('queue_name') == queue_name:
                    status = job.get('status', 'unknown')
                    if status in stats:
                        stats[status] += 1
        
        return stats
    
    def _process_scheduled_jobs(self, queue_name: str):
        """
        Move scheduled jobs to active queue if their time has come
        """
        if not self.redis_client:
            return
        
        current_time = int(datetime.utcnow().timestamp())
        
        # Get jobs that are ready to be processed
        ready_jobs = self.redis_client.zrangebyscore(
            f"scheduled:{queue_name}", 
            0, 
            current_time
        )
        
        for job_id in ready_jobs:
            # Move to active queue
            job_data = self.redis_client.hgetall(f"job:{job_id}")
            if job_data:
                priority = int(job_data.get('priority', JobPriority.NORMAL.value))
                score = priority * 1000000 + current_time
                
                self.redis_client.zadd(f"queue:{queue_name}", {job_id: score})
                self.redis_client.zrem(f"scheduled:{queue_name}", job_id)
    
    def cleanup_completed_jobs(self, older_than_hours: int = 24):
        """
        Clean up completed jobs older than specified hours
        """
        if not self.redis_client:
            return
        
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        cutoff_iso = cutoff_time.isoformat()
        
        job_keys = self.redis_client.keys("job:*")
        cleaned_count = 0
        
        for job_key in job_keys:
            job_data = self.redis_client.hgetall(job_key)
            
            if (job_data.get('status') in [JobStatus.COMPLETED.value, JobStatus.FAILED.value] and
                job_data.get('completed_at', job_data.get('failed_at', '')) < cutoff_iso):
                
                self.redis_client.delete(job_key)
                cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} old jobs")
        return cleaned_count

# Global queue manager instance
queue_manager = QueueManager()