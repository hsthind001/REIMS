"""
Storage Integration API for REIMS Backend
Integrates the main application with the enhanced storage service
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import httpx
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/storage", tags=["storage"])

# Storage service configuration
STORAGE_SERVICE_URL = "http://localhost:8002"

class StorageConfig:
    """Configuration for storage service"""
    def __init__(self):
        self.base_url = STORAGE_SERVICE_URL
        self.timeout = 30.0
        self.retry_attempts = 3

storage_config = StorageConfig()

async def get_storage_client():
    """Get HTTP client for storage service"""
    return httpx.AsyncClient(
        base_url=storage_config.base_url,
        timeout=storage_config.timeout
    )

@router.post("/upload")
async def upload_to_storage(
    file: UploadFile = File(...),
    property_id: str = Form(...),
    metadata: Optional[str] = Form("{}"),
    enable_versioning: bool = Form(True),
    enable_backup: bool = Form(True)
):
    """
    Upload a file to the enhanced storage service
    """
    try:
        async with await get_storage_client() as client:
            # Prepare form data
            files = {"file": (file.filename, await file.read(), file.content_type)}
            data = {
                "property_id": property_id,
                "metadata": metadata,
                "enable_versioning": enable_versioning,
                "enable_backup": enable_backup
            }
            
            response = await client.post("/documents/upload", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Integrate with queue system for processing
                try:
                    import sys
                    from pathlib import Path
                    sys.path.append(str(Path(__file__).parent.parent.parent / "queue_service"))
                    from queue_manager import queue_manager
                    
                    # Queue document for AI processing
                    job_id = queue_manager.enqueue_job(
                        queue_name='document_processing',
                        job_type='document_processing',
                        job_data={
                            'document_id': result['data']['document_id'],
                            'file_path': result['data']['object_path'],
                            'storage_type': 'minio',
                            'property_id': property_id,
                            'options': {
                                'enable_ai': True,
                                'versioning': enable_versioning,
                                'backup': enable_backup
                            }
                        }
                    )
                    
                    result['data']['processing_job_id'] = job_id
                    
                except Exception as e:
                    logger.warning(f"Could not queue for processing: {e}")
                
                return result
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Storage service error: {response.text}"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Storage service connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Storage service unavailable"
        )
    except Exception as e:
        logger.error(f"Storage upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
async def get_document_from_storage(
    document_id: str,
    include_versions: bool = False
):
    """
    Get document information from storage service
    """
    try:
        async with await get_storage_client() as client:
            params = {"include_versions": include_versions}
            response = await client.get(f"/documents/{document_id}", params=params)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Document not found in storage")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Storage service error: {response.text}"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Storage service connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Storage service unavailable"
        )

@router.get("/documents")
async def list_documents_from_storage(
    limit: int = 100,
    prefix: str = "",
    property_id: Optional[str] = None
):
    """
    List documents from storage service
    """
    try:
        async with await get_storage_client() as client:
            params = {
                "limit": limit,
                "prefix": prefix
            }
            if property_id:
                params["property_id"] = property_id
            
            response = await client.get("/documents", params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Storage service error: {response.text}"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Storage service connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Storage service unavailable"
        )

@router.delete("/documents/{document_id}")
async def delete_document_from_storage(
    document_id: str,
    delete_all_versions: bool = False,
    force_delete: bool = False
):
    """
    Delete document from storage service
    """
    try:
        async with await get_storage_client() as client:
            params = {
                "delete_all_versions": delete_all_versions,
                "force_delete": force_delete
            }
            
            response = await client.delete(f"/documents/{document_id}", params=params)
            
            if response.status_code == 200:
                result = response.json()
                
                # Queue cleanup tasks
                try:
                    import sys
                    from pathlib import Path
                    sys.path.append(str(Path(__file__).parent.parent.parent / "queue_service"))
                    from queue_manager import queue_manager
                    
                    # Queue cleanup job
                    queue_manager.enqueue_job(
                        queue_name='notifications',
                        job_type='notification',
                        job_data={
                            'type': 'document_deleted',
                            'document_id': document_id,
                            'delete_details': result['data']
                        }
                    )
                    
                except Exception as e:
                    logger.warning(f"Could not queue cleanup notification: {e}")
                
                return result
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Document not found in storage")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Storage service error: {response.text}"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Storage service connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Storage service unavailable"
        )

@router.get("/statistics")
async def get_storage_statistics():
    """
    Get storage statistics and analytics
    """
    try:
        async with await get_storage_client() as client:
            response = await client.get("/storage/statistics")
            
            if response.status_code == 200:
                stats = response.json()
                
                # Enhance with additional analytics
                enhanced_stats = {
                    **stats,
                    "service_status": "connected",
                    "last_updated": "2024-01-01T00:00:00Z"  # Would be actual timestamp
                }
                
                return enhanced_stats
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Storage service error: {response.text}"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Storage service connection error: {e}")
        # Return fallback stats
        return {
            "status": "error",
            "service_status": "disconnected",
            "error": "Storage service unavailable",
            "data": {
                "total_documents": 0,
                "total_storage_used": 0,
                "primary_bucket": {"object_count": 0, "total_size_mb": 0},
                "backup_bucket": {"object_count": 0, "total_size_mb": 0}
            }
        }

@router.post("/backup/{document_id}")
async def create_document_backup(document_id: str):
    """
    Create backup for a specific document
    """
    try:
        async with await get_storage_client() as client:
            response = await client.post(f"/storage/backup/{document_id}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Document not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Storage service error: {response.text}"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Storage service connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Storage service unavailable"
        )

@router.post("/archive")
async def archive_old_documents(
    days_old: int = 90,
    dry_run: bool = True
):
    """
    Archive documents older than specified days
    """
    try:
        async with await get_storage_client() as client:
            params = {
                "days_old": days_old,
                "dry_run": dry_run
            }
            
            response = await client.post("/storage/archive", params=params)
            
            if response.status_code == 200:
                result = response.json()
                
                # Queue archive notification if not dry run
                if not dry_run:
                    try:
                        import sys
                        from pathlib import Path
                        sys.path.append(str(Path(__file__).parent.parent.parent / "queue_service"))
                        from queue_manager import queue_manager
                        
                        queue_manager.enqueue_job(
                            queue_name='notifications',
                            job_type='notification',
                            job_data={
                                'type': 'documents_archived',
                                'archive_details': result['data']
                            }
                        )
                        
                    except Exception as e:
                        logger.warning(f"Could not queue archive notification: {e}")
                
                return result
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Storage service error: {response.text}"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Storage service connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Storage service unavailable"
        )

@router.get("/health")
async def storage_integration_health():
    """
    Health check for storage integration
    """
    try:
        async with await get_storage_client() as client:
            response = await client.get("/storage/health")
            
            if response.status_code == 200:
                storage_health = response.json()
                
                return {
                    "storage_integration": "healthy",
                    "storage_service": storage_health,
                    "connection": "active"
                }
            else:
                return {
                    "storage_integration": "degraded",
                    "storage_service": "error",
                    "connection": "failed",
                    "error": response.text
                }
                
    except httpx.RequestError as e:
        logger.error(f"Storage service health check failed: {e}")
        return {
            "storage_integration": "unhealthy",
            "storage_service": "unreachable",
            "connection": "failed",
            "error": str(e)
        }