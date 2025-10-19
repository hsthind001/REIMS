"""
Enhanced REIMS Backend with MinIO Integration
Handles real file uploads and integrates with the complete processing pipeline
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import uuid
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import MinIO integration
try:
    import sys
    sys.path.append(str(Path(__file__).parent / "storage_service"))
    from client import minio_client
    MINIO_AVAILABLE = minio_client.is_available()
    logger.info(f"MinIO client available: {MINIO_AVAILABLE}")
except ImportError as e:
    logger.warning(f"MinIO client not available: {e}")
    MINIO_AVAILABLE = False
    minio_client = None

# Try to import database integration
try:
    sys.path.append(str(Path(__file__).parent / "backend"))
    from database import SessionLocal, Document, ProcessingJob
    DATABASE_AVAILABLE = True
    logger.info("Database integration available")
except ImportError as e:
    logger.warning(f"Database not available: {e}")
    DATABASE_AVAILABLE = False
    SessionLocal = None

# Try to import queue system
try:
    sys.path.append(str(Path(__file__).parent / "queue_service"))
    from queue_manager import queue_manager
    QUEUE_AVAILABLE = True
    logger.info("Queue system available")
except ImportError as e:
    logger.warning(f"Queue system not available: {e}")
    QUEUE_AVAILABLE = False
    queue_manager = None

app = FastAPI(title="REIMS Enhanced Backend API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for fallback
stored_documents = []
stored_properties = []

def get_db_session():
    """Get database session if available"""
    if DATABASE_AVAILABLE and SessionLocal:
        return SessionLocal()
    return None

async def store_file_to_minio(file: UploadFile, document_id: str, property_id: str) -> Dict[str, Any]:
    """Store file to MinIO object storage"""
    try:
        if not MINIO_AVAILABLE:
            raise Exception("MinIO not available")
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Generate object path
        timestamp = datetime.utcnow()
        date_path = timestamp.strftime("%Y/%m/%d")
        object_name = f"{date_path}/{document_id}_{file.filename}"
        
        # Upload to MinIO
        from io import BytesIO
        data_stream = BytesIO(file_content)
        
        # Prepare metadata
        metadata = {
            "document_id": document_id,
            "property_id": property_id,
            "original_filename": file.filename,
            "upload_timestamp": timestamp.isoformat(),
            "file_size": str(file_size),
            "content_type": file.content_type or "application/octet-stream"
        }
        
        # Upload to primary bucket
        result = minio_client.client.put_object(
            bucket_name=minio_client.bucket_name,
            object_name=object_name,
            data=data_stream,
            length=file_size,
            content_type=file.content_type or "application/octet-stream",
            metadata=metadata
        )
        
        # Generate download URL
        download_url = minio_client.get_presigned_url(object_name)
        
        logger.info(f"File uploaded to MinIO: {object_name}")
        
        return {
            "storage_type": "minio",
            "object_name": object_name,
            "bucket_name": minio_client.bucket_name,
            "file_size": file_size,
            "download_url": download_url,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"Error uploading to MinIO: {e}")
        # Fallback to local storage
        return await store_file_locally(file, document_id, property_id)

async def store_file_locally(file: UploadFile, document_id: str, property_id: str) -> Dict[str, Any]:
    """Fallback: Store file locally"""
    try:
        # Reset file pointer
        await file.seek(0)
        
        # Create storage directory
        storage_dir = Path("storage")
        storage_dir.mkdir(exist_ok=True)
        
        # Generate filename
        stored_filename = f"{document_id}_{file.filename}"
        file_path = storage_dir / stored_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        file_size = len(content)
        
        # Store metadata separately
        metadata = {
            "document_id": document_id,
            "property_id": property_id,
            "original_filename": file.filename,
            "upload_timestamp": datetime.utcnow().isoformat(),
            "file_size": file_size,
            "content_type": file.content_type or "application/octet-stream"
        }
        
        metadata_file = storage_dir / f"{document_id}_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"File stored locally: {file_path}")
        
        return {
            "storage_type": "local",
            "file_path": str(file_path),
            "stored_filename": stored_filename,
            "file_size": file_size,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"Error storing file locally: {e}")
        raise Exception(f"Failed to store file: {str(e)}")

async def store_to_database(document_info: Dict[str, Any]) -> Optional[str]:
    """Store document info to database"""
    if not DATABASE_AVAILABLE:
        return None
    
    try:
        db = get_db_session()
        if not db:
            return None
        
        doc = Document(
            document_id=document_info["document_id"],
            original_filename=document_info["original_filename"],
            stored_filename=document_info.get("stored_filename", document_info["original_filename"]),
            property_id=document_info["property_id"],
            file_size=document_info["file_size"],
            content_type=document_info["content_type"],
            file_path=document_info.get("file_path", ""),
            upload_timestamp=datetime.fromisoformat(document_info["upload_timestamp"]),
            status="uploaded"
        )
        
        db.add(doc)
        db.commit()
        db.refresh(doc)
        db.close()
        
        logger.info(f"Document stored in database: {doc.document_id}")
        return str(doc.id)
        
    except Exception as e:
        logger.error(f"Error storing to database: {e}")
        return None

async def queue_processing_job(document_info: Dict[str, Any]) -> Optional[str]:
    """Queue document for AI processing"""
    if not QUEUE_AVAILABLE:
        return None
    
    try:
        job_data = {
            "document_id": document_info["document_id"],
            "file_path": document_info.get("file_path") or document_info.get("object_name"),
            "property_id": document_info["property_id"],
            "original_filename": document_info["original_filename"],
            "options": {
                "enable_ai": True,
                "enable_backup": True,
                "priority": "normal"
            }
        }
        
        job_id = queue_manager.enqueue_job(
            queue_name="document_processing",
            job_type="document_processing",
            job_data=job_data
        )
        
        logger.info(f"Processing job queued: {job_id}")
        return job_id
        
    except Exception as e:
        logger.error(f"Error queuing processing job: {e}")
        return None

@app.get("/health")
async def health_check():
    """Enhanced health check with system status"""
    return {
        "status": "healthy",
        "services": {
            "minio": MINIO_AVAILABLE,
            "database": DATABASE_AVAILABLE,
            "queue": QUEUE_AVAILABLE
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    return {
        "message": "REIMS Enhanced Backend API",
        "version": "2.0.0",
        "features": ["MinIO Integration", "Database Storage", "AI Processing Queue"]
    }

@app.post("/api/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    property_id: str = Form(...)
):
    """Enhanced document upload with MinIO integration"""
    
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Generate document ID
    document_id = str(uuid.uuid4())
    
    try:
        # Store file (MinIO or local fallback)
        storage_result = await store_file_to_minio(file, document_id, property_id)
        
        # Prepare document information
        document_info = {
            "document_id": document_id,
            "original_filename": file.filename,
            "property_id": property_id,
            "file_size": storage_result["file_size"],
            "content_type": file.content_type or "application/octet-stream",
            "upload_timestamp": datetime.utcnow().isoformat(),
            "storage_type": storage_result["storage_type"]
        }
        
        # Add storage-specific info
        if storage_result["storage_type"] == "minio":
            document_info.update({
                "object_name": storage_result["object_name"],
                "bucket_name": storage_result["bucket_name"],
                "download_url": storage_result["download_url"]
            })
        else:
            document_info.update({
                "file_path": storage_result["file_path"],
                "stored_filename": storage_result["stored_filename"]
            })
        
        # Store to database (if available)
        db_id = await store_to_database(document_info)
        
        # Queue for processing (if available)
        job_id = await queue_processing_job(document_info)
        
        # Store in memory for immediate access
        stored_documents.append(document_info)
        
        # Response
        response = {
            "document_id": document_id,
            "filename": file.filename,
            "file_size": storage_result["file_size"],
            "status": "uploaded",
            "message": f"File uploaded successfully to {storage_result['storage_type']}",
            "storage_info": {
                "type": storage_result["storage_type"],
                "location": storage_result.get("object_name") or storage_result.get("file_path")
            }
        }
        
        if db_id:
            response["database_id"] = db_id
        
        if job_id:
            response["processing_job_id"] = job_id
            response["message"] += " and queued for AI processing"
        
        logger.info(f"Document upload completed: {document_id}")
        return response
        
    except Exception as e:
        logger.error(f"Upload failed for {file.filename}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Upload failed: {str(e)}"
        )

@app.get("/api/documents")
async def get_documents():
    """Get uploaded documents list"""
    
    # Try to get from database first
    if DATABASE_AVAILABLE:
        try:
            db = get_db_session()
            if db:
                docs = db.query(Document).order_by(Document.upload_timestamp.desc()).all()
                db.close()
                
                return {
                    "documents": [
                        {
                            "document_id": doc.document_id,
                            "filename": doc.original_filename,
                            "property_id": doc.property_id,
                            "file_size": doc.file_size,
                            "upload_timestamp": doc.upload_timestamp.isoformat(),
                            "status": doc.status
                        }
                        for doc in docs
                    ],
                    "total": len(docs),
                    "source": "database"
                }
        except Exception as e:
            logger.error(f"Error getting documents from database: {e}")
    
    # Fallback to in-memory storage
    return {
        "documents": stored_documents,
        "total": len(stored_documents),
        "source": "memory"
    }

@app.get("/api/documents/{document_id}")
async def get_document_info(document_id: str):
    """Get specific document information"""
    
    # Try database first
    if DATABASE_AVAILABLE:
        try:
            db = get_db_session()
            if db:
                doc = db.query(Document).filter(Document.document_id == document_id).first()
                db.close()
                
                if doc:
                    info = {
                        "document_id": doc.document_id,
                        "filename": doc.original_filename,
                        "property_id": doc.property_id,
                        "file_size": doc.file_size,
                        "content_type": doc.content_type,
                        "upload_timestamp": doc.upload_timestamp.isoformat(),
                        "status": doc.status,
                        "source": "database"
                    }
                    
                    # Add MinIO download URL if available
                    if MINIO_AVAILABLE and doc.file_path:
                        try:
                            info["download_url"] = minio_client.get_presigned_url(doc.file_path)
                        except Exception:
                            pass
                    
                    return info
        except Exception as e:
            logger.error(f"Error getting document from database: {e}")
    
    # Fallback to memory
    for doc in stored_documents:
        if doc["document_id"] == document_id:
            return doc
    
    raise HTTPException(status_code=404, detail="Document not found")

@app.get("/api/storage/status")
async def get_storage_status():
    """Get storage system status"""
    
    status = {
        "minio": {
            "available": MINIO_AVAILABLE,
            "buckets": []
        },
        "database": {
            "available": DATABASE_AVAILABLE,
            "document_count": 0
        },
        "queue": {
            "available": QUEUE_AVAILABLE,
            "pending_jobs": 0
        }
    }
    
    # MinIO status
    if MINIO_AVAILABLE:
        try:
            buckets = minio_client.client.list_buckets()
            status["minio"]["buckets"] = [
                {
                    "name": bucket.name,
                    "creation_date": bucket.creation_date.isoformat()
                }
                for bucket in buckets
            ]
        except Exception as e:
            status["minio"]["error"] = str(e)
    
    # Database status
    if DATABASE_AVAILABLE:
        try:
            db = get_db_session()
            if db:
                count = db.query(Document).count()
                status["database"]["document_count"] = count
                db.close()
        except Exception as e:
            status["database"]["error"] = str(e)
    
    # Queue status
    if QUEUE_AVAILABLE:
        try:
            # This would get actual queue statistics
            status["queue"]["pending_jobs"] = 0  # Placeholder
        except Exception as e:
            status["queue"]["error"] = str(e)
    
    return status

# Existing API endpoints for compatibility
@app.get("/api/properties")
async def get_properties():
    return stored_properties

@app.get("/api/property/properties") 
async def get_property_properties():
    return stored_properties

@app.get("/api/property/tenants")
async def get_tenants():
    return []

@app.get("/api/property/leases")
async def get_leases():
    return []

@app.get("/api/property/maintenance")
async def get_maintenance():
    return []

@app.get("/api/analytics")
async def get_analytics():
    return {
        "total_documents": len(stored_documents),
        "total_properties": len(stored_properties),
        "processing_stats": {
            "uploaded": len(stored_documents),
            "processed": 0,
            "failed": 0
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)