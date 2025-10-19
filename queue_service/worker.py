"""
Enhanced Background Worker for REIMS Document Processing
Integrates with Redis queue system and AI processing
"""

import asyncio
import logging
import time
import signal
import sys
from typing import Dict, Any
from pathlib import Path

# Add backend path to import modules
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from queue_manager import queue_manager, JobStatus
from document_processor import DocumentProcessor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedDocumentWorker:
    """
    Enhanced worker that processes documents using queue system
    """
    
    def __init__(self, worker_id: str = None):
        self.worker_id = worker_id or f"worker_{int(time.time())}"
        self.processor = DocumentProcessor()
        self.running = False
        self.stats = {
            'jobs_processed': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'start_time': None
        }
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def start(self, queue_names: list = None):
        """
        Start the worker to process jobs from specified queues
        """
        if queue_names is None:
            queue_names = ['document_processing_queue', 'ai_analysis', 'notifications']
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        logger.info(f"Worker {self.worker_id} starting to process queues: {queue_names}")
        
        while self.running:
            job_processed = False
            
            # Check each queue for jobs
            for queue_name in queue_names:
                job = queue_manager.dequeue_job(queue_name, self.worker_id)
                
                if job:
                    job_processed = True
                    await self._process_job(job)
                    break
            
            if not job_processed:
                # No jobs available, sleep briefly
                await asyncio.sleep(1)
        
        logger.info(f"Worker {self.worker_id} stopped. Stats: {self.stats}")
    
    async def _process_job(self, job: Dict[str, Any]):
        """
        Process a single job
        """
        job_id = job['job_id']
        job_type = job['job_type']
        job_data = job['job_data']
        
        logger.info(f"Processing job {job_id} of type {job_type}")
        
        try:
            self.stats['jobs_processed'] += 1
            
            # Route job to appropriate handler
            if job_type == 'document_processing':
                result = await self._process_document_job(job_data)
            elif job_type == 'ai_analysis':
                result = await self._process_ai_analysis_job(job_data)
            elif job_type == 'notification':
                result = await self._process_notification_job(job_data)
            elif job_type == 'batch_processing':
                result = await self._process_batch_job(job_data)
            else:
                raise ValueError(f"Unknown job type: {job_type}")
            
            # Mark job as completed
            queue_manager.complete_job(job_id, result)
            self.stats['jobs_completed'] += 1
            
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            error_message = f"Error processing job {job_id}: {str(e)}"
            logger.error(error_message)
            
            # Mark job as failed (with retry)
            queue_manager.fail_job(job_id, error_message, retry=True)
            self.stats['jobs_failed'] += 1
    
    async def _process_document_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document processing job
        """
        document_id = job_data.get('document_id')
        file_path = job_data.get('file_path')
        processing_options = job_data.get('options', {})
        
        if not document_id or not file_path:
            raise ValueError("Missing required fields: document_id and file_path")
        
        # Simulate document processing for now
        await asyncio.sleep(2)  # Simulate processing time
        
        result = {
            'status': 'processed',
            'document_id': document_id,
            'file_path': file_path,
            'processing_time': 2.0,
            'timestamp': time.time()
        }
        
        # If AI processing is enabled, queue AI analysis
        if processing_options.get('enable_ai', True):
            ai_job_id = queue_manager.enqueue_job(
                queue_name='ai_analysis',
                job_type='ai_analysis',
                job_data={
                    'document_id': document_id,
                    'file_path': file_path,
                    'processing_result': result
                }
            )
            result['ai_job_id'] = ai_job_id
        
        return result
    
    async def _process_ai_analysis_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an AI analysis job
        """
        document_id = job_data.get('document_id')
        file_path = job_data.get('file_path')
        
        if not document_id or not file_path:
            raise ValueError("Missing required fields: document_id and file_path")
        
        # Import AI processing components
        try:
            sys.path.append(str(Path(__file__).parent.parent / "backend" / "agents"))
            from document_processor_integration import document_processor
            
            # Process document with AI
            result = await document_processor.process_document_with_ai(document_id)
            
            # Queue notification if processing was successful
            if result.get('status') == 'success':
                queue_manager.enqueue_job(
                    queue_name='notifications',
                    job_type='notification',
                    job_data={
                        'type': 'ai_processing_complete',
                        'document_id': document_id,
                        'result_summary': result.get('processing_result', {})
                    }
                )
            
            return result
            
        except ImportError as e:
            logger.warning(f"AI processing not available: {e}")
            return {
                'status': 'skipped',
                'message': 'AI processing not available',
                'document_id': document_id
            }
    
    async def _process_notification_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a notification job
        """
        notification_type = job_data.get('type')
        document_id = job_data.get('document_id')
        
        logger.info(f"Processing notification: {notification_type} for document {document_id}")
        
        # Here you would implement actual notification logic
        # For now, just log the notification
        
        if notification_type == 'ai_processing_complete':
            result_summary = job_data.get('result_summary', {})
            logger.info(f"AI processing completed for document {document_id}: {result_summary}")
        
        elif notification_type == 'processing_error':
            error_message = job_data.get('error_message', 'Unknown error')
            logger.error(f"Processing error for document {document_id}: {error_message}")
        
        elif notification_type == 'batch_processing_complete':
            processed_count = job_data.get('processed_count', 0)
            logger.info(f"Batch processing completed: {processed_count} documents processed")
        
        return {
            'status': 'sent',
            'notification_type': notification_type,
            'timestamp': time.time()
        }
    
    async def _process_batch_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a batch processing job
        """
        document_ids = job_data.get('document_ids', [])
        options = job_data.get('options', {})
        
        if not document_ids:
            raise ValueError("No document IDs provided for batch processing")
        
        results = []
        processed_count = 0
        
        for document_id in document_ids:
            try:
                # Queue individual document processing job
                job_id = queue_manager.enqueue_job(
                    queue_name='document_processing',
                    job_type='document_processing',
                    job_data={
                        'document_id': document_id,
                        'file_path': f"storage/{document_id}_*",  # Placeholder
                        'options': options
                    }
                )
                
                results.append({
                    'document_id': document_id,
                    'job_id': job_id,
                    'status': 'queued'
                })
                processed_count += 1
                
            except Exception as e:
                results.append({
                    'document_id': document_id,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Queue completion notification
        queue_manager.enqueue_job(
            queue_name='notifications',
            job_type='notification',
            job_data={
                'type': 'batch_processing_complete',
                'processed_count': processed_count,
                'total_count': len(document_ids)
            }
        )
        
        return {
            'processed_count': processed_count,
            'total_count': len(document_ids),
            'results': results
        }

async def main():
    """
    Main entry point for the worker
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='REIMS Document Processing Worker')
    parser.add_argument('--worker-id', help='Worker ID', default=None)
    parser.add_argument('--queues', help='Comma-separated list of queues to process', 
                       default='document_processing,ai_analysis,notifications')
    
    args = parser.parse_args()
    
    queue_names = [q.strip() for q in args.queues.split(',')]
    
    worker = EnhancedDocumentWorker(worker_id=args.worker_id)
    
    try:
        await worker.start(queue_names)
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    except Exception as e:
        logger.error(f"Worker error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())