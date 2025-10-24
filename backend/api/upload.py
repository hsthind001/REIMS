from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
import uuid
import os
from pathlib import Path
import json
from datetime import datetime
import sys
from sqlalchemy.orm import Session
from typing import Optional

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../queue_service"))

from database import get_db, Document, ProcessingJob, ExtractedData
from utils.filename_parser import parse_filename

router = APIRouter()

UPLOAD_DIR = "storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".csv"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def get_queue_client():
    """Get queue client with error handling"""
    try:
        # Import the new queue manager
        sys.path.append(os.path.join(os.path.dirname(__file__), "../../queue_service"))
        from queue_manager import queue_manager, JobPriority
        return queue_manager
    except Exception as e:
        print(f"Warning: Queue service unavailable: {e}")
        return None

@router.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...), 
    property_id: str = Form(...),
    property_name: Optional[str] = Form(None),
    document_year: Optional[int] = Form(None),
    document_type: Optional[str] = Form(None),
    document_period: Optional[str] = Form("Annual"),
    db: Session = Depends(get_db)
):
    # Validate file type
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Generate document ID and save file
    doc_id = str(uuid.uuid4())
    timestamp = datetime.utcnow()
    safe_filename = f"{doc_id}_{Path(file.filename).stem}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Parse filename for metadata if not provided
    parsed_metadata = parse_filename(file.filename)
    
    # Use provided values or fall back to parsed values
    final_property_name = property_name or parsed_metadata.get("property_name")
    final_document_year = document_year or parsed_metadata.get("document_year")
    final_document_type = document_type or parsed_metadata.get("document_type")
    final_document_period = document_period if document_period != "Annual" else parsed_metadata.get("document_period", "Annual")
    
    print(f"📄 Upload: {file.filename}")
    print(f"   Property: {final_property_name} (Year: {final_document_year})")
    print(f"   Type: {final_document_type} ({final_document_period})")
    
    # Save file to local storage
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Try to upload to MinIO as well
    minio_bucket = None
    minio_object_name = None
    minio_url = None
    storage_type = "local"
    
    try:
        from minio import Minio
        from dotenv import load_dotenv
        load_dotenv()
        
        minio_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        minio_access = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        minio_secret = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        bucket_name = os.getenv("MINIO_BUCKET_NAME", "reims-files")
        
        client = Minio(
            minio_endpoint,
            access_key=minio_access,
            secret_key=minio_secret,
            secure=False
        )
        
        # Ensure bucket exists
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
        
        # Extract year from metadata
        year = final_document_year or datetime.utcnow().year
        
        # Determine document subtype based on content analysis
        def get_document_subtype(filename, doc_type):
            """Analyze filename and document type to determine subtype folder"""
            filename_lower = filename.lower()
            
            # For financial statements, determine specific type
            if doc_type == 'financial_statement' or 'financial' in str(doc_type).lower():
                if 'balance' in filename_lower and 'sheet' in filename_lower:
                    return 'Balance Sheets'
                elif 'cash' in filename_lower and 'flow' in filename_lower:
                    return 'Cash Flow Statements'
                elif 'income' in filename_lower and 'statement' in filename_lower:
                    return 'Income Statements'
                elif 'rent' in filename_lower and 'roll' in filename_lower:
                    return 'Rent Rolls'
                else:
                    return 'Other Financial Documents'
            elif doc_type == 'rent_roll' or 'rent' in filename_lower:
                return 'Rent Rolls'
            else:
                return 'Other Documents'
        
        doc_subtype = get_document_subtype(file.filename, final_document_type or 'other')
        
        # Use original filename (no document_id prefix)
        # Build document-type-first path: Financial Statements/{year}/{subtype}/{filename}
        minio_object_name = f"Financial Statements/{year}/{doc_subtype}/{file.filename}"
        
        from io import BytesIO
        client.put_object(
            bucket_name,
            minio_object_name,
            BytesIO(content),
            len(content),
            content_type=file.content_type or "application/octet-stream"
        )
        
        minio_bucket = bucket_name
        minio_url = f"http://{minio_endpoint}/{bucket_name}/{minio_object_name}"
        storage_type = "local_and_minio"
        
        print(f"File uploaded to MinIO: {minio_url}")
        
    except Exception as e:
        print(f"MinIO upload failed (continuing with local only): {e}")
        # Continue with local storage only
    
    # Create database record with new metadata fields
    db_document = Document(
        document_id=doc_id,
        original_filename=file.filename,
        stored_filename=safe_filename,
        property_id=property_id,
        file_size=len(content),
        content_type=file.content_type or "application/octet-stream",
        file_path=file_path,
        upload_timestamp=timestamp,
        status="uploaded",
        minio_bucket=minio_bucket,
        minio_object_name=minio_object_name,
        minio_url=minio_url,
        storage_type=storage_type,
        minio_upload_timestamp=timestamp if minio_bucket else None,
        # NEW: Document metadata
        property_name=final_property_name,
        document_year=final_document_year,
        document_type=final_document_type,
        document_period=final_document_period
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Also write to financial_documents table for dual-table sync
    try:
        from sqlalchemy import text
        db.execute(
            text("""
                INSERT INTO financial_documents (
                    id, property_id, file_path, file_name, document_type,
                    property_name, document_year, document_period,
                    status, upload_date
                ) VALUES (
                    :document_id, :property_id, :file_path, :file_name, :document_type,
                    :property_name, :document_year, :document_period,
                    'uploaded', datetime('now')
                )
            """),
            {
                "document_id": doc_id,
                "property_id": property_id,
                "file_path": minio_object_name if minio_bucket else file_path,
                "file_name": file.filename,
                "document_type": final_document_type or "other",
                "property_name": final_property_name,
                "document_year": final_document_year,
                "document_period": final_document_period
            }
        )
        db.commit()
        print(f"SUCCESS: Document also saved to financial_documents table for sync")
    except Exception as e:
        # Log warning but don't fail the request
        print(f"WARNING: Failed to sync to financial_documents table: {e}")
    
    # Create metadata for legacy compatibility
    metadata = {
        "document_id": doc_id,
        "original_filename": file.filename,
        "stored_filename": safe_filename,
        "property_id": property_id,
        "file_size": len(content),
        "content_type": file.content_type or "application/octet-stream",
        "upload_timestamp": timestamp.isoformat(),
        "status": "uploaded",
        "file_path": file_path
    }
    
    # Try to queue for processing with new queue system
    job_id = None
    queue_client = get_queue_client()
    if queue_client:
        try:
            # Use new queue system
            job_id = queue_client.enqueue_job(
                queue_name='document_processing',
                job_type='document_processing',
                job_data={
                    'document_id': doc_id,
                    'file_path': file_path,
                    'options': {
                        'enable_ai': True,
                        'property_id': property_id
                    }
                },
                priority='normal'
            )
            
            # Create processing job record
            db_job = ProcessingJob(
                job_id=job_id,
                document_id=doc_id,
                status="queued"
            )
            db.add(db_job)
            
            # Update document status
            db_document.status = "queued"
            db.commit()
            
        except Exception as e:
            print(f"Failed to queue document for processing: {e}")
            # Continue without queuing
    
    # Save metadata file for legacy compatibility
    metadata_path = os.path.join(UPLOAD_DIR, f"{doc_id}_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    response = {
        "document_id": doc_id,
        "filename": file.filename,
        "property_id": property_id,
        "file_size": len(content),
        "status": db_document.status,
        "upload_timestamp": timestamp.isoformat(),
        # NEW: Include metadata in response
        "property_name": final_property_name,
        "document_year": final_document_year,
        "document_type": final_document_type,
        "document_period": final_document_period
    }
    
    if job_id:
        response["job_id"] = job_id
    
    return response

@router.get("/api/documents/{document_id}")
async def get_document_info(document_id: str, db: Session = Depends(get_db)):
    """Get document information by ID"""
    # Get from database first
    db_document = db.query(Document).filter(Document.document_id == document_id).first()
    
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get processing job info if exists
    processing_job = db.query(ProcessingJob).filter(ProcessingJob.document_id == document_id).first()
    
    result = {
        "document_id": db_document.document_id,
        "original_filename": db_document.original_filename,
        "stored_filename": db_document.stored_filename,
        "property_id": db_document.property_id,
        "file_size": db_document.file_size,
        "content_type": db_document.content_type,
        "upload_timestamp": db_document.upload_timestamp.isoformat(),
        "status": db_document.status
    }
    
    if processing_job:
        result["job_id"] = processing_job.job_id
        result["job_status"] = processing_job.status
        
        # Get live job status from queue if available
        queue_client = get_queue_client()
        if queue_client and processing_job.job_id:
            try:
                job_status = queue_client.get_job_status(processing_job.job_id)
                result["live_job_status"] = job_status
            except Exception as e:
                result["job_status_error"] = str(e)
    
    return result

@router.get("/api/documents")
async def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents"""
    documents = db.query(Document).order_by(Document.upload_timestamp.desc()).all()
    
    result_documents = []
    for doc in documents:
        doc_data = {
            "document_id": doc.document_id,
            "original_filename": doc.original_filename,
            "property_id": doc.property_id,
            "file_size": doc.file_size,
            "content_type": doc.content_type,
            "upload_timestamp": doc.upload_timestamp.isoformat(),
            "status": doc.status
        }
        
        # Add job info if exists
        processing_job = db.query(ProcessingJob).filter(ProcessingJob.document_id == doc.document_id).first()
        if processing_job:
            doc_data["job_id"] = processing_job.job_id
            doc_data["job_status"] = processing_job.status
        
        result_documents.append(doc_data)
    
    return {"documents": result_documents, "count": len(result_documents)}

@router.get("/api/queue/status")
async def get_queue_status():
    """Get current queue status"""
    queue_client = get_queue_client()
    if not queue_client:
        raise HTTPException(status_code=503, detail="Queue service unavailable")
    
    try:
        return queue_client.get_queue_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get queue status: {str(e)}")

@router.get("/api/documents/{document_id}/processed")
async def get_processed_data(document_id: str, db: Session = Depends(get_db)):
    """Get processed data for a document"""
    # Get from database first
    db_document = db.query(Document).filter(Document.document_id == document_id).first()
    
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get extracted data from database
    extracted_data = db.query(ExtractedData).filter(ExtractedData.document_id == document_id).all()
    
    result = {
        "document_id": document_id,
        "processed": len(extracted_data) > 0,
        "data": []
    }
    
    if extracted_data:
        # Convert database records to list format
        for record in extracted_data:
            data_item = {
                "id": record.id,
                "data_type": record.data_type,
                "extracted_content": record.extracted_content,
                "analysis_results": record.analysis_results or {},
                "property_indicators": record.property_indicators or {},
                "extraction_timestamp": record.extraction_timestamp.isoformat()
            }
            result["data"].append(data_item)
    else:
        # Fall back to file system if no database records (for backwards compatibility)
        processed_file = os.path.join("queue_service/processed_data", f"{document_id}_processed.json")
        
        if os.path.exists(processed_file):
            try:
                with open(processed_file, "r") as f:
                    file_data = json.load(f)
                result["processed"] = True
                result["data"] = file_data
            except Exception as e:
                pass  # Keep empty data if file read fails
    
    return result

@router.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a specific job"""
    queue_client = get_queue_client()
    if not queue_client:
        raise HTTPException(status_code=503, detail="Queue service unavailable")
    
    try:
        return queue_client.get_job_status(job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")
