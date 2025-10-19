"""
Enhanced Storage Service API for REIMS
Provides comprehensive MinIO object storage with versioning, backup, and management features
"""

from fastapi import FastAPI, UploadFile, HTTPException, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any, List
import uvicorn
import json
import logging

from operations import enhanced_storage_ops

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="REIMS Enhanced Storage Service",
    description="Advanced object storage with versioning, backup, and intelligent management",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile,
    property_id: str = Form(...),
    metadata: Optional[str] = Form("{}"),
    enable_versioning: bool = Form(True),
    enable_backup: bool = Form(True)
):
    """
    Upload a document with advanced storage features
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        # Parse metadata JSON
        parsed_metadata = json.loads(metadata) if metadata else {}
        parsed_metadata["property_id"] = property_id
        
        result = await enhanced_storage_ops.store_document(
            file=file,
            metadata=parsed_metadata,
            enable_versioning=enable_versioning,
            enable_backup=enable_backup
        )
        
        return {
            "status": "success",
            "data": result
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata JSON")
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}")
async def get_document_info(
    document_id: str,
    include_versions: bool = Query(False)
):
    """
    Get comprehensive document information
    """
    try:
        info = enhanced_storage_ops.get_document_info(document_id, include_versions)
        
        if not info:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "status": "success",
            "data": info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents(
    limit: int = Query(100, le=1000),
    prefix: str = Query(""),
    property_id: Optional[str] = Query(None)
):
    """
    List documents with optional filtering
    """
    try:
        documents = enhanced_storage_ops.list_documents(
            prefix=prefix,
            limit=limit,
            property_id=property_id
        )
        
        return {
            "status": "success",
            "data": {
                "documents": documents,
                "count": len(documents),
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    delete_all_versions: bool = Query(False),
    force_delete: bool = Query(False)
):
    """
    Delete a document with version management options
    """
    try:
        if not force_delete:
            # Check if document exists
            info = enhanced_storage_ops.get_document_info(document_id)
            if not info:
                raise HTTPException(status_code=404, detail="Document not found")
        
        result = enhanced_storage_ops.delete_document(
            document_id=document_id,
            delete_all_versions=delete_all_versions
        )
        
        return {
            "status": "success",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/storage/statistics")
async def get_storage_statistics():
    """
    Get comprehensive storage statistics and analytics
    """
    try:
        stats = enhanced_storage_ops.get_storage_statistics()
        
        return {
            "status": "success",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Storage statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/storage/backup/{document_id}")
async def create_backup(document_id: str):
    """
    Manually create a backup for a specific document
    """
    try:
        # Get document info
        info = enhanced_storage_ops.get_document_info(document_id)
        if not info:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # This would trigger a manual backup process
        # For now, we'll return the current backup status
        
        return {
            "status": "success",
            "data": {
                "document_id": document_id,
                "backup_available": info.get("backup_available", False),
                "message": "Backup status checked"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backup creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/storage/archive")
async def archive_old_documents(
    days_old: int = Query(90, ge=1),
    dry_run: bool = Query(True)
):
    """
    Archive documents older than specified days
    """
    try:
        # This would implement archival logic
        # For now, we'll return a simulation
        
        return {
            "status": "success",
            "data": {
                "dry_run": dry_run,
                "days_old": days_old,
                "message": "Archival process would run here",
                "estimated_documents": 0,
                "estimated_savings_mb": 0
            }
        }
        
    except Exception as e:
        logger.error(f"Archive process error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/storage/health")
async def storage_health_check():
    """
    Health check for storage service
    """
    try:
        # Test basic storage operations
        from client import minio_client
        
        # Test bucket access
        buckets_status = {}
        test_buckets = [
            enhanced_storage_ops.bucket_name,
            enhanced_storage_ops.backup_bucket,
            enhanced_storage_ops.archive_bucket
        ]
        
        for bucket in test_buckets:
            try:
                exists = minio_client.client.bucket_exists(bucket)
                buckets_status[bucket] = "accessible" if exists else "not_found"
            except Exception as e:
                buckets_status[bucket] = f"error: {str(e)}"
        
        # Get basic stats
        stats = enhanced_storage_ops.get_storage_statistics()
        
        overall_status = "healthy" if all(
            status == "accessible" for status in buckets_status.values()
        ) else "degraded"
        
        return {
            "status": overall_status,
            "storage_service": "operational",
            "bucket_status": buckets_status,
            "basic_stats": {
                "total_documents": stats.get("total_documents", 0),
                "total_storage_mb": round(stats.get("total_storage_used", 0) / (1024 * 1024), 2)
            },
            "timestamp": "2024-01-01T00:00:00Z"  # Would be actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Storage health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

@app.get("/storage/buckets")
async def list_buckets():
    """
    List all storage buckets and their status
    """
    try:
        from client import minio_client
        
        buckets = minio_client.client.list_buckets()
        bucket_info = []
        
        for bucket in buckets:
            bucket_stats = enhanced_storage_ops._get_bucket_stats(bucket.name)
            bucket_info.append({
                "name": bucket.name,
                "creation_date": bucket.creation_date.isoformat(),
                "object_count": bucket_stats.get("object_count", 0),
                "total_size_mb": bucket_stats.get("total_size_mb", 0)
            })
        
        return {
            "status": "success",
            "data": {
                "buckets": bucket_info,
                "total_buckets": len(bucket_info)
            }
        }
        
    except Exception as e:
        logger.error(f"List buckets error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8002, reload=True)