"""
Documents API Routes
Handles document upload, storage, and processing status
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import uuid
from datetime import datetime
import redis
import json
import io
import sys
import os

# Add path for filename parser
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.api.database import get_db
from backend.api.dependencies import get_redis_client, get_minio_client
from backend.utils.filename_parser import parse_filename

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("/test-dependencies")
async def test_dependencies(
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    minio_client = Depends(get_minio_client)
):
    """Test if all dependencies are working"""
    return {
        "success": True,
        "dependencies": {
            "database": db is not None,
            "redis": redis_client is not None,
            "minio": minio_client is not None
        }
    }


# Allowed file types
ALLOWED_EXTENSIONS = {
    'application/pdf',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv',
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def find_or_create_property(db: Session, property_name: str) -> int:
    """
    Find existing property by name or create new one
    
    Args:
        db: Database session
        property_name: Property name from filename
        
    Returns:
        property_id: Existing or newly created property ID
    """
    if not property_name:
        return None
    
    # Normalize name for matching
    normalized_name = property_name.strip().lower()
    
    # Check if property exists (case-insensitive)
    result = db.execute(
        text("SELECT id FROM properties WHERE LOWER(name) = :name"),
        {"name": normalized_name}
    ).fetchone()
    
    if result:
        print(f"   ✓ Found existing property: {property_name} (ID: {result[0]})")
        return result[0]
    
    # Property doesn't exist - create it
    print(f"   ⚡ Creating new property: {property_name}")
    
    # Get next available ID
    max_id_result = db.execute(text("SELECT MAX(id) FROM properties")).fetchone()
    new_id = (max_id_result[0] or 0) + 1
    
    # Generate property code
    property_code = f"PROP{new_id:03d}"
    
    # Insert new property with defaults
    db.execute(
        text("""
            INSERT INTO properties (
                id, property_code, name, address, city, state, zip_code, country,
                property_type, status, current_market_value, monthly_rent,
                year_built, created_at
            ) VALUES (
                :id, :property_code, :name, :address, :city, :state, :zip_code, :country,
                'commercial', 'active', 0, 0, 2024, datetime('now')
            )
        """),
        {
            "id": new_id,
            "property_code": property_code,
            "name": property_name,
            "address": f"{property_name}, Location TBD",
            "city": "Unknown",
            "state": "NY",
            "zip_code": "00000",
            "country": "USA"
        }
    )
    db.commit()
    
    print(f"   ✓ Created property ID: {new_id} (Code: {property_code})")
    return new_id


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    property_id: Optional[str] = Form(None),  # Make optional for auto-creation
    document_type: str = Form(...),
    property_name: Optional[str] = Form(None),
    document_year: Optional[int] = Form(None),
    document_period: Optional[str] = Form("Annual"),
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    minio_client = Depends(get_minio_client)
):
    """
    Upload a financial document
    
    Form Parameters:
    - file: Document file (PDF, Excel, CSV)
    - property_id: Property UUID
    - document_type: Type of document (offering_memo, rent_roll, financial_statement, etc.)
    - property_name: (Optional) Property name - auto-extracted from filename if not provided
    - document_year: (Optional) Document year - auto-extracted from filename if not provided
    - document_period: (Optional) Period (Annual, Q1, Q2, etc.) - auto-extracted from filename if not provided
    
    Returns:
    - document_id: UUID of uploaded document
    - status: 'queued' (ready for processing)
    """
    
    # Parse filename for metadata if not provided
    parsed_metadata = parse_filename(file.filename)
    
    # Use provided values or fall back to parsed values
    final_property_name = property_name or parsed_metadata.get("property_name")
    final_document_year = document_year or parsed_metadata.get("document_year")
    final_document_type = document_type  # Keep user-provided type, but could enhance
    final_document_period = document_period if document_period != "Annual" else parsed_metadata.get("document_period", "Annual")
    
    # Auto-determine property_id if not provided
    if not property_id and final_property_name:
        property_id = find_or_create_property(db, final_property_name)
    elif not property_id:
        raise HTTPException(
            status_code=400,
            detail="property_id or filename with property name required"
        )
    
    print(f"\nDEBUG: Upload endpoint called")
    print(f"   File: {file.filename}")
    print(f"   Property ID: {property_id}")
    print(f"   Property Name: {final_property_name} (parsed: {parsed_metadata.get('property_name')})")
    print(f"   Year: {final_document_year} (parsed: {parsed_metadata.get('document_year')})")
    print(f"   Document Type: {final_document_type}")
    print(f"   Period: {final_document_period}")
    print(f"   MinIO available: {minio_client is not None}")
    print(f"   Redis available: {redis_client is not None}")
    
    try:
        # Check if MinIO is available
        if minio_client is None:
            raise HTTPException(
                status_code=503,
                detail="File storage service (MinIO) is not available"
            )
        
        # Validate file type
        if file.content_type not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: PDF, Excel, CSV"
            )
        
        # Validate file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: 50MB"
            )
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Extract year from metadata
        year = final_document_year or datetime.utcnow().year
        
        # Determine document subtype based on content analysis
        def get_document_subtype(filename, doc_type):
            """Analyze filename and document type to determine subtype folder"""
            filename_lower = filename.lower()
            
            # For financial statements, determine specific type
            if doc_type == 'financial_statement' or 'financial' in doc_type.lower():
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
        
        doc_subtype = get_document_subtype(file.filename, document_type)
        
        # Use original filename (no document_id prefix)
        original_filename = file.filename
        
        # Build new document-type-first path: Financial Statements/{year}/{subtype}/{filename}
        file_path = f"Financial Statements/{year}/{doc_subtype}/{original_filename}"
        
        # Upload to MinIO
        try:
            from io import BytesIO
            minio_client.put_object(
                bucket_name="reims-files",
                object_name=file_path,
                data=BytesIO(file_content),
                length=len(file_content),
                content_type=file.content_type
            )
            print(f"SUCCESS: File uploaded to MinIO: {file_path}")
        except Exception as e:
            print(f"ERROR: MinIO upload error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file to storage: {str(e)}"
            )
        
        # Store metadata in database (with new metadata fields)
        try:
            db.execute(
                text("""
                    INSERT INTO financial_documents (
                        id,
                        property_id,
                        file_path,
                        file_name,
                        document_type,
                        property_name,
                        document_year,
                        document_period,
                        status,
                        upload_date
                    ) VALUES (
                        :document_id,
                        :property_id,
                        :file_path,
                        :file_name,
                        :document_type,
                        :property_name,
                        :document_year,
                        :document_period,
                        'queued',
                        datetime('now')
                    )
                """),
                {
                    "document_id": document_id,
                    "property_id": property_id,
                    "file_path": file_path,
                    "file_name": file.filename,
                    "document_type": document_type,
                    "property_name": final_property_name,
                    "document_year": final_document_year,
                    "document_period": final_document_period
                }
            )
            # Also write to documents table for backward compatibility and dual-table sync
            try:
                db.execute(
                    text("""
                        INSERT INTO documents (
                            id, document_id, original_filename, stored_filename,
                            property_id, file_size, content_type, file_path,
                            upload_timestamp, status, minio_bucket, minio_object_name,
                            minio_url, storage_type, property_name, document_year,
                            document_type, document_period
                        ) VALUES (
                            :id, :document_id, :original_filename, :stored_filename,
                            :property_id, :file_size, :content_type, :file_path,
                            datetime('now'), 'uploaded', 'reims-files', :minio_object_name,
                            :minio_url, 'minio', :property_name, :document_year,
                            :document_type, :document_period
                        )
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "document_id": document_id,
                        "original_filename": file.filename,
                        "stored_filename": file.filename,  # Use original filename, no prefix
                        "property_id": str(property_id),
                        "file_size": len(file_content),
                        "content_type": file.content_type,
                        "file_path": file_path,
                        "minio_object_name": file_path,
                        "minio_url": f"http://localhost:9000/reims-files/{file_path}",
                        "property_name": final_property_name,
                        "document_year": final_document_year,
                        "document_type": document_type,
                        "document_period": final_document_period
                    }
                )
                print(f"SUCCESS: Document also saved to documents table for sync")
            except Exception as e:
                # Log warning but don't fail the request
                print(f"WARNING: Failed to sync to documents table: {e}")
            
            db.commit()
            print(f"SUCCESS: Document metadata saved: {document_id}")
            print(f"         Property: {final_property_name}, Year: {final_document_year}, Period: {final_document_period}")
        except Exception as e:
            # Rollback and try to delete from MinIO
            print(f"ERROR: Database error: {str(e)}")
            db.rollback()
            try:
                if minio_client:
                    minio_client.remove_object("reims-files", file_path)
            except:
                pass
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save document metadata: {str(e)}"
            )
        
        # Add to processing queue
        try:
            if redis_client:
                queue_message = json.dumps({
                    "document_id": document_id,
                    "property_id": property_id,
                    "file_path": file_path,
                    "file_name": file.filename,
                    "document_type": document_type
                })
                redis_client.rpush("document_processing_queue", queue_message)
                print(f"SUCCESS: Document queued for processing: {document_id}")
            else:
                print(f"WARNING: Redis not available, document not queued")
        except Exception as e:
            print(f"WARNING: Failed to queue document for processing: {e}")
            # Don't fail the request, document is uploaded
        
        return {
            "success": True,
            "data": {
                "document_id": document_id,
                "status": "queued",
                "file_name": file.filename,
                "file_size": len(file_content),
                "upload_date": datetime.utcnow().isoformat(),
                # NEW: Include extracted metadata in response
                "property_name": final_property_name,
                "document_year": final_document_year,
                "document_type": final_document_type,
                "document_period": final_document_period
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: UPLOAD FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/{document_id}/status")
async def get_document_status(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get document processing status and extracted metrics
    
    Returns:
    - document_id: Document UUID
    - status: 'queued', 'processing', 'processed', or 'failed'
    - upload_date: When document was uploaded
    - processing_date: When processing completed (if processed)
    - error_message: Error details (if failed)
    - metrics: Extracted financial metrics (if processed)
    """
    
    try:
        # Get document info
        doc_result = db.execute(
            text("""
                SELECT 
                    id,
                    property_id,
                    file_name,
                    document_type,
                    status,
                    upload_date,
                    processing_date,
                    error_message
                FROM financial_documents
                WHERE id = :document_id
            """),
            {"document_id": document_id}
        ).fetchone()
        
        if not doc_result:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found"
            )
        
        # Get extracted metrics
        metrics_results = db.execute(
            text("""
                SELECT 
                    metric_name,
                    metric_value,
                    confidence_score,
                    extraction_method,
                    created_at
                FROM extracted_metrics
                WHERE document_id = :document_id
                ORDER BY created_at DESC
            """),
            {"document_id": document_id}
        ).fetchall()
        
        # Format metrics
        metrics = {}
        for row in metrics_results:
            metrics[row.metric_name] = {
                "value": float(row.metric_value),
                "confidence_score": float(row.confidence_score),
                "extraction_method": row.extraction_method
            }
        
        return {
            "success": True,
            "data": {
                "document_id": doc_result.id,
                "property_id": doc_result.property_id,
                "file_name": doc_result.file_name,
                "document_type": doc_result.document_type,
                "status": doc_result.status,
                "upload_date": str(doc_result.upload_date) if doc_result.upload_date else None,
                "processing_date": str(doc_result.processing_date) if doc_result.processing_date else None,
                "error_message": doc_result.error_message,
                "metrics": metrics if metrics else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch document status: {str(e)}"
        )


@router.get("")
async def list_documents(
    property_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List documents with optional filters
    """
    try:
        where_conditions = []
        params = {"limit": limit}
        
        if property_id:
            where_conditions.append("property_id = :property_id")
            params["property_id"] = property_id
        
        if status:
            where_conditions.append("status = :status")
            params["status"] = status
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        results = db.execute(
            text(f"""
                SELECT 
                    fd.id,
                    fd.property_id,
                    p.name as property_name,
                    fd.file_name,
                    fd.document_type,
                    fd.status,
                    fd.upload_date,
                    fd.processing_date
                FROM financial_documents fd
                LEFT JOIN properties p ON p.id = fd.property_id
                {where_clause}
                ORDER BY fd.upload_date DESC
                LIMIT :limit
            """),
            params
        ).fetchall()
        
        documents = []
        for row in results:
            documents.append({
                "id": row.id,
                "property_id": row.property_id,
                "property_name": row.property_name,
                "file_name": row.file_name,
                "document_type": row.document_type,
                "status": row.status,
                "upload_date": str(row.upload_date) if row.upload_date else None,
                "processing_date": str(row.processing_date) if row.processing_date else None,
            })
        
        return {
            "success": True,
            "data": {
                "documents": documents,
                "total": len(documents)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    db: Session = Depends(get_db),
    minio_client = Depends(get_minio_client)
):
    """
    Download a document file from MinIO storage
    """
    try:
        # Get document metadata from database
        doc_result = db.execute(
            text("""
                SELECT 
                    id,
                    file_path,
                    file_name,
                    document_type
                FROM financial_documents
                WHERE id = :document_id
            """),
            {"document_id": document_id}
        ).fetchone()
        
        if not doc_result:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found"
            )
        
        if not minio_client:
            raise HTTPException(
                status_code=503,
                detail="File storage service (MinIO) is not available"
            )
        
        # Get file from MinIO
        try:
            response = minio_client.get_object("reims-files", doc_result.file_path)
            file_data = response.read()
            response.close()
            response.release_conn()
            
            # Determine content type based on file extension
            file_ext = doc_result.file_name.split('.')[-1].lower()
            content_type_map = {
                'pdf': 'application/pdf',
                'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'xls': 'application/vnd.ms-excel',
                'csv': 'text/csv',
            }
            content_type = content_type_map.get(file_ext, 'application/octet-stream')
            
            # Return file as streaming response
            return StreamingResponse(
                io.BytesIO(file_data),
                media_type=content_type,
                headers={
                    "Content-Disposition": f"attachment; filename={doc_result.file_name}"
                }
            )
            
        except Exception as e:
            print(f"MinIO download error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to download file from storage: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download document: {str(e)}"
        )


@router.get("/{document_id}/view")
async def view_document(
    document_id: str,
    db: Session = Depends(get_db),
    minio_client = Depends(get_minio_client)
):
    """
    View/preview a document file inline (opens in browser)
    """
    try:
        # Get document metadata from database
        doc_result = db.execute(
            text("""
                SELECT 
                    id,
                    file_path,
                    file_name,
                    document_type
                FROM financial_documents
                WHERE id = :document_id
            """),
            {"document_id": document_id}
        ).fetchone()
        
        if not doc_result:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found"
            )
        
        if not minio_client:
            raise HTTPException(
                status_code=503,
                detail="File storage service (MinIO) is not available"
            )
        
        # Get file from MinIO
        try:
            response = minio_client.get_object("reims-files", doc_result.file_path)
            file_data = response.read()
            response.close()
            response.release_conn()
            
            # Determine content type based on file extension
            file_ext = doc_result.file_name.split('.')[-1].lower()
            content_type_map = {
                'pdf': 'application/pdf',
                'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'xls': 'application/vnd.ms-excel',
                'csv': 'text/csv',
            }
            content_type = content_type_map.get(file_ext, 'application/octet-stream')
            
            # Return file as inline response (for viewing in browser)
            return StreamingResponse(
                io.BytesIO(file_data),
                media_type=content_type,
                headers={
                    "Content-Disposition": f"inline; filename={doc_result.file_name}"
                }
            )
            
        except Exception as e:
            print(f"MinIO view error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to view file from storage: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to view document: {str(e)}"
        )

