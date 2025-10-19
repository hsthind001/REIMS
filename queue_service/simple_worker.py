import time
import sys
import json
import os
from rq import Worker, Queue
from redis import Redis
from redis.exceptions import ConnectionError, TimeoutError
from dotenv import load_dotenv
import logging
from document_processor import document_processor

# Add database imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
try:
    from database import SessionLocal, ProcessingJob, ExtractedData
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Database imports failed: {e}")
    DATABASE_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def process_document(document_id: str, metadata: dict) -> dict:
    """
    Process a document from the queue using the document processor
    """
    logger.info(f"Started processing document {document_id}")
    
    try:
        file_path = metadata.get('file_path')
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Process the document
        result = document_processor.process(file_path, metadata)
        
        # Add job metadata
        result.update({
            "document_id": document_id,
            "original_metadata": metadata,
            "job_completed_at": time.time()
        })
        
        # Save processed data to file (for backwards compatibility)
        output_dir = "processed_data"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"{document_id}_processed.json")
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        result["output_file"] = output_file
        
        # Save to database if available
        if DATABASE_AVAILABLE:
            try:
                db = SessionLocal()
                try:
                    # ✅ UPDATE DOCUMENT STATUS TO COMPLETED
                    from sqlalchemy import text
                    db.execute(
                        text("UPDATE documents SET status = 'completed' WHERE document_id = :doc_id"),
                        {"doc_id": document_id}
                    )
                    
                    # Update processing job status
                    job = db.query(ProcessingJob).filter(ProcessingJob.document_id == document_id).first()
                    if job:
                        job.status = "completed"
                        job.result_data = result
                        job.completed_at = time.time()
                    
                    # Save extracted data
                    extracted_data = result.get('extracted_data', [])
                    if isinstance(extracted_data, list):
                        for data_item in extracted_data:
                            db_record = ExtractedData(
                                document_id=document_id,
                                data_type=data_item.get('type', 'unknown'),
                                extracted_content=data_item.get('data', {}),
                                analysis_results=data_item.get('analysis', {}),
                                property_indicators=data_item.get('property_indicators', {})
                            )
                            db.add(db_record)
                    
                    db.commit()
                    logger.info(f"Saved processed data to database for document {document_id}")
                    
                except Exception as db_error:
                    db.rollback()
                    logger.error(f"Database save failed for document {document_id}: {db_error}")
                finally:
                    db.close()
                    
            except Exception as e:
                logger.error(f"Database connection failed for document {document_id}: {e}")
        
        logger.info(f"Successfully processed document {document_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        error_result = {
            "document_id": document_id,
            "status": "error",
            "error": str(e),
            "job_completed_at": time.time()
        }
        
        # ✅ UPDATE STATUS TO FAILED ON ERROR
        if DATABASE_AVAILABLE:
            try:
                db = SessionLocal()
                try:
                    # Update document status to failed
                    from sqlalchemy import text
                    db.execute(
                        text("UPDATE documents SET status = 'failed' WHERE document_id = :doc_id"),
                        {"doc_id": document_id}
                    )
                    
                    # Update processing job status
                    job = db.query(ProcessingJob).filter(ProcessingJob.document_id == document_id).first()
                    if job:
                        job.status = "failed"
                        job.error_message = str(e)
                        job.completed_at = time.time()
                    db.commit()
                except Exception as db_error:
                    db.rollback()
                    logger.error(f"Failed to update failed status: {db_error}")
                finally:
                    db.close()
            except Exception as db_conn_error:
                logger.error(f"Database connection failed for failed status update: {db_conn_error}")
        
        return error_result

def setup_redis(max_retries=3, retry_delay=2):
    """Set up Redis connection with retries"""
    retries = 0
    last_error = None
    
    while retries < max_retries:
        try:
            redis_conn = Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                password=os.getenv("REDIS_PASSWORD", ""),
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            redis_conn.ping()
            logger.info(f"Successfully connected to Redis at {redis_conn.connection_pool.connection_kwargs['host']}:{redis_conn.connection_pool.connection_kwargs['port']}")
            return redis_conn
            
        except ConnectionError as e:
            last_error = e
            retries += 1
            logger.warning(f"Redis connection attempt {retries}/{max_retries} failed: {str(e)}")
            if retries < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                
        except TimeoutError as e:
            last_error = e
            retries += 1
            logger.warning(f"Redis connection timeout on attempt {retries}/{max_retries}: {str(e)}")
            if retries < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {str(e)}")
            raise
            
    logger.error(f"Failed to connect to Redis after {max_retries} attempts: {str(last_error)}")
    raise last_error

if __name__ == '__main__':
    try:
        # Set up Redis connection
        redis_conn = setup_redis()

        # Get queue name from environment
        queue_name = os.getenv("QUEUE_NAME", "document-processing")
        logger.info(f"Using queue: {queue_name}")

        # Create queue
        queue = Queue(queue_name, connection=redis_conn)

        # Set up worker with custom name
        worker_name = f"document_worker.{os.getpid()}"
        worker = Worker([queue], connection=redis_conn, name=worker_name)
        logger.info(f"Starting worker {worker_name}")

        # Start processing jobs (Windows-compatible settings)
        worker.work(
            logging_level=logging.INFO,
            burst=False
        )

    except KeyboardInterrupt:
        logger.info("Shutting down worker gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)