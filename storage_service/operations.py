"""
Enhanced Storage Operations for REIMS
Comprehensive MinIO object storage with versioning, backup, and intelligent management
"""

from typing import List, Optional, Dict, Any, BinaryIO
from datetime import datetime, timedelta
import uuid
import json
import hashlib
import io
import logging
from pathlib import Path

from minio.error import S3Error
from fastapi import UploadFile
from client import minio_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedStorageOperations:
    """
    Advanced storage operations with versioning, backup, and intelligent management
    """
    
    def __init__(self):
        self.bucket_name = minio_client.bucket_name
        self.backup_bucket = f"{self.bucket_name}-backup"
        self.archive_bucket = f"{self.bucket_name}-archive"
        
        # Initialize backup and archive buckets
        self._ensure_buckets_exist()
    
    def _ensure_buckets_exist(self):
        """Ensure all required buckets exist"""
        try:
            buckets = [self.bucket_name, self.backup_bucket, self.archive_bucket]
            
            for bucket in buckets:
                if not minio_client.client.bucket_exists(bucket):
                    minio_client.client.make_bucket(bucket)
                    logger.info(f"Created bucket: {bucket}")
                    
                    # Set bucket lifecycle policy for archive bucket
                    if bucket == self.archive_bucket:
                        self._set_archive_lifecycle_policy(bucket)
                        
        except S3Error as e:
            logger.error(f"Error ensuring buckets exist: {e}")
    
    def _set_archive_lifecycle_policy(self, bucket: str):
        """Set lifecycle policy for archive bucket"""
        try:
            # This would typically set a policy to transition to cheaper storage
            # For now, we'll just log it
            logger.info(f"Archive lifecycle policy would be set for {bucket}")
        except Exception as e:
            logger.warning(f"Could not set lifecycle policy for {bucket}: {e}")
    
    def _calculate_file_hash(self, file_data: bytes) -> str:
        """Calculate SHA256 hash of file data"""
        return hashlib.sha256(file_data).hexdigest()
    
    def _generate_object_path(self, document_id: str, filename: str, version: int = 1) -> str:
        """Generate structured object path"""
        date_path = datetime.utcnow().strftime("%Y/%m/%d")
        if version > 1:
            name, ext = Path(filename).stem, Path(filename).suffix
            versioned_filename = f"{name}_v{version}{ext}"
        else:
            versioned_filename = filename
        
        return f"{date_path}/{document_id}/{versioned_filename}"
    
    async def store_document(self, file: UploadFile, metadata: Dict[str, Any], 
                           enable_versioning: bool = True, 
                           enable_backup: bool = True) -> Dict[str, Any]:
        """
        Store a document with advanced features
        """
        try:
            # Read file data
            file_data = await file.read()
            file_size = len(file_data)
            file_hash = self._calculate_file_hash(file_data)
            
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Check for duplicates based on hash
            existing_doc = await self._find_duplicate_by_hash(file_hash)
            if existing_doc:
                logger.info(f"Duplicate file detected: {file_hash}")
                return {
                    **existing_doc,
                    "is_duplicate": True,
                    "original_document_id": existing_doc["document_id"]
                }
            
            # Determine version number
            version = 1
            if enable_versioning:
                version = await self._get_next_version(file.filename, metadata.get("property_id"))
            
            # Generate object path
            object_path = self._generate_object_path(doc_id, file.filename, version)
            
            # Prepare comprehensive metadata
            storage_metadata = {
                "document_id": doc_id,
                "original_filename": file.filename,
                "content_type": file.content_type or "application/octet-stream",
                "file_size": file_size,
                "file_hash": file_hash,
                "version": version,
                "upload_timestamp": datetime.utcnow().isoformat(),
                "storage_path": object_path,
                "backup_enabled": enable_backup,
                "versioning_enabled": enable_versioning,
                **metadata
            }
            
            # Store file in primary bucket
            data_stream = io.BytesIO(file_data)
            result = minio_client.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
                data=data_stream,
                length=file_size,
                content_type=file.content_type,
                metadata=storage_metadata
            )
            
            # Create backup if enabled
            backup_path = None
            if enable_backup:
                backup_path = await self._create_backup(object_path, file_data, storage_metadata)
            
            # Store metadata document
            await self._store_metadata_document(doc_id, storage_metadata)
            
            # Generate access URLs
            download_url = minio_client.get_presigned_url(object_path)
            
            response = {
                "document_id": doc_id,
                "filename": file.filename,
                "object_path": object_path,
                "content_type": file.content_type,
                "file_size": file_size,
                "file_hash": file_hash,
                "version": version,
                "upload_timestamp": storage_metadata["upload_timestamp"],
                "download_url": download_url,
                "backup_path": backup_path,
                "metadata": storage_metadata,
                "is_duplicate": False
            }
            
            logger.info(f"Document stored successfully: {doc_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error storing document: {e}")
            raise Exception(f"Failed to store document: {str(e)}")
        finally:
            await file.close()
    
    async def _find_duplicate_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Find existing document with the same hash"""
        try:
            # Search for objects with matching hash in metadata
            objects = minio_client.client.list_objects(self.bucket_name, recursive=True)
            
            for obj in objects:
                try:
                    obj_stat = minio_client.client.stat_object(self.bucket_name, obj.object_name)
                    obj_metadata = obj_stat.metadata
                    
                    if obj_metadata.get("file_hash") == file_hash:
                        return {
                            "document_id": obj_metadata.get("document_id"),
                            "filename": obj_metadata.get("original_filename"),
                            "object_path": obj.object_name,
                            "content_type": obj_metadata.get("content_type"),
                            "file_size": int(obj_metadata.get("file_size", 0)),
                            "upload_timestamp": obj_metadata.get("upload_timestamp")
                        }
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            logger.warning(f"Error checking for duplicates: {e}")
            return None
    
    async def _get_next_version(self, filename: str, property_id: str) -> int:
        """Determine the next version number for a file"""
        try:
            # Search for existing versions of the same file for the same property
            objects = minio_client.client.list_objects(self.bucket_name, recursive=True)
            max_version = 0
            
            for obj in objects:
                try:
                    obj_stat = minio_client.client.stat_object(self.bucket_name, obj.object_name)
                    obj_metadata = obj_stat.metadata
                    
                    if (obj_metadata.get("original_filename") == filename and 
                        obj_metadata.get("property_id") == property_id):
                        version = int(obj_metadata.get("version", 1))
                        max_version = max(max_version, version)
                except Exception:
                    continue
            
            return max_version + 1
            
        except Exception as e:
            logger.warning(f"Error determining version: {e}")
            return 1
    
    async def _create_backup(self, object_path: str, file_data: bytes, metadata: Dict) -> str:
        """Create backup copy in backup bucket"""
        try:
            backup_path = f"backup/{object_path}"
            data_stream = io.BytesIO(file_data)
            
            minio_client.client.put_object(
                bucket_name=self.backup_bucket,
                object_name=backup_path,
                data=data_stream,
                length=len(file_data),
                content_type=metadata.get("content_type", "application/octet-stream"),
                metadata={**metadata, "backup_timestamp": datetime.utcnow().isoformat()}
            )
            
            logger.info(f"Backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    async def _store_metadata_document(self, doc_id: str, metadata: Dict):
        """Store metadata as a separate JSON document"""
        try:
            metadata_path = f"metadata/{doc_id}.json"
            metadata_json = json.dumps(metadata, indent=2).encode('utf-8')
            data_stream = io.BytesIO(metadata_json)
            
            minio_client.client.put_object(
                bucket_name=self.bucket_name,
                object_name=metadata_path,
                data=data_stream,
                length=len(metadata_json),
                content_type="application/json"
            )
            
        except Exception as e:
            logger.warning(f"Error storing metadata document: {e}")
    
    def get_document_info(self, document_id: str, include_versions: bool = False) -> Optional[Dict[str, Any]]:
        """Get comprehensive document information"""
        try:
            # Find the document
            objects = minio_client.client.list_objects(self.bucket_name, recursive=True)
            document_info = None
            all_versions = []
            
            for obj in objects:
                try:
                    obj_stat = minio_client.client.stat_object(self.bucket_name, obj.object_name)
                    obj_metadata = obj_stat.metadata
                    
                    if obj_metadata.get("document_id") == document_id:
                        doc_data = {
                            "document_id": document_id,
                            "filename": obj_metadata.get("original_filename"),
                            "object_path": obj.object_name,
                            "content_type": obj_metadata.get("content_type"),
                            "file_size": int(obj_metadata.get("file_size", 0)),
                            "file_hash": obj_metadata.get("file_hash"),
                            "version": int(obj_metadata.get("version", 1)),
                            "upload_timestamp": obj_metadata.get("upload_timestamp"),
                            "last_modified": obj_stat.last_modified.isoformat(),
                            "metadata": obj_metadata
                        }
                        
                        if include_versions:
                            all_versions.append(doc_data)
                        
                        # Keep the latest version as main document info
                        if not document_info or doc_data["version"] > document_info.get("version", 0):
                            document_info = doc_data
                            
                except Exception:
                    continue
            
            if document_info:
                if include_versions:
                    document_info["all_versions"] = sorted(all_versions, key=lambda x: x["version"], reverse=True)
                
                # Add download URL
                document_info["download_url"] = minio_client.get_presigned_url(document_info["object_path"])
                
                # Check backup status
                document_info["backup_available"] = self._check_backup_exists(document_info["object_path"])
            
            return document_info
            
        except Exception as e:
            logger.error(f"Error getting document info: {e}")
            return None
    
    def _check_backup_exists(self, object_path: str) -> bool:
        """Check if backup exists for the document"""
        try:
            backup_path = f"backup/{object_path}"
            minio_client.client.stat_object(self.backup_bucket, backup_path)
            return True
        except Exception:
            return False
    
    def list_documents(self, prefix: str = "", limit: int = 100, 
                      property_id: str = None) -> List[Dict[str, Any]]:
        """List documents with optional filtering"""
        try:
            objects = minio_client.client.list_objects(
                self.bucket_name, 
                prefix=prefix, 
                recursive=True
            )
            
            documents = []
            processed_docs = set()
            
            for obj in objects:
                if len(documents) >= limit:
                    break
                
                try:
                    # Skip metadata files
                    if obj.object_name.startswith("metadata/"):
                        continue
                    
                    obj_stat = minio_client.client.stat_object(self.bucket_name, obj.object_name)
                    obj_metadata = obj_stat.metadata
                    
                    doc_id = obj_metadata.get("document_id")
                    if doc_id in processed_docs:
                        continue
                    
                    # Filter by property_id if specified
                    if property_id and obj_metadata.get("property_id") != property_id:
                        continue
                    
                    documents.append({
                        "document_id": doc_id,
                        "filename": obj_metadata.get("original_filename"),
                        "object_path": obj.object_name,
                        "content_type": obj_metadata.get("content_type"),
                        "file_size": int(obj_metadata.get("file_size", 0)),
                        "version": int(obj_metadata.get("version", 1)),
                        "upload_timestamp": obj_metadata.get("upload_timestamp"),
                        "last_modified": obj_stat.last_modified.isoformat(),
                        "property_id": obj_metadata.get("property_id")
                    })
                    
                    processed_docs.add(doc_id)
                    
                except Exception:
                    continue
            
            # Sort by upload timestamp (newest first)
            documents.sort(key=lambda x: x.get("upload_timestamp", ""), reverse=True)
            return documents
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    def delete_document(self, document_id: str, delete_all_versions: bool = False) -> Dict[str, Any]:
        """Delete document with options for version management"""
        try:
            deleted_objects = []
            
            # Find all objects for this document
            objects = minio_client.client.list_objects(self.bucket_name, recursive=True)
            
            for obj in objects:
                try:
                    obj_stat = minio_client.client.stat_object(self.bucket_name, obj.object_name)
                    obj_metadata = obj_stat.metadata
                    
                    if obj_metadata.get("document_id") == document_id:
                        if delete_all_versions:
                            # Delete this version
                            minio_client.client.remove_object(self.bucket_name, obj.object_name)
                            deleted_objects.append(obj.object_name)
                        else:
                            # Only delete the latest version
                            # This is a simplified approach - in production you'd be more careful
                            pass
                            
                except Exception:
                    continue
            
            # Delete metadata document
            try:
                metadata_path = f"metadata/{document_id}.json"
                minio_client.client.remove_object(self.bucket_name, metadata_path)
                deleted_objects.append(metadata_path)
            except Exception:
                pass
            
            # Delete from backup if requested
            if delete_all_versions:
                self._delete_backups(document_id)
            
            return {
                "document_id": document_id,
                "deleted_objects": deleted_objects,
                "deleted_all_versions": delete_all_versions,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return {
                "document_id": document_id,
                "status": "error",
                "error": str(e)
            }
    
    def _delete_backups(self, document_id: str):
        """Delete backup copies of a document"""
        try:
            objects = minio_client.client.list_objects(self.backup_bucket, recursive=True)
            
            for obj in objects:
                try:
                    if document_id in obj.object_name:
                        minio_client.client.remove_object(self.backup_bucket, obj.object_name)
                except Exception:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error deleting backups: {e}")
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive storage statistics"""
        try:
            stats = {
                "primary_bucket": self._get_bucket_stats(self.bucket_name),
                "backup_bucket": self._get_bucket_stats(self.backup_bucket),
                "archive_bucket": self._get_bucket_stats(self.archive_bucket),
                "total_documents": 0,
                "total_storage_used": 0,
                "document_types": {},
                "property_distribution": {},
                "version_distribution": {}
            }
            
            # Analyze documents in primary bucket
            objects = minio_client.client.list_objects(self.bucket_name, recursive=True)
            processed_docs = set()
            
            for obj in objects:
                try:
                    if obj.object_name.startswith("metadata/"):
                        continue
                    
                    obj_stat = minio_client.client.stat_object(self.bucket_name, obj.object_name)
                    obj_metadata = obj_stat.metadata
                    
                    doc_id = obj_metadata.get("document_id")
                    if doc_id not in processed_docs:
                        stats["total_documents"] += 1
                        processed_docs.add(doc_id)
                    
                    stats["total_storage_used"] += obj_stat.size
                    
                    # Content type distribution
                    content_type = obj_metadata.get("content_type", "unknown")
                    stats["document_types"][content_type] = stats["document_types"].get(content_type, 0) + 1
                    
                    # Property distribution
                    property_id = obj_metadata.get("property_id", "unspecified")
                    stats["property_distribution"][property_id] = stats["property_distribution"].get(property_id, 0) + 1
                    
                    # Version distribution
                    version = obj_metadata.get("version", "1")
                    stats["version_distribution"][f"v{version}"] = stats["version_distribution"].get(f"v{version}", 0) + 1
                    
                except Exception:
                    continue
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage statistics: {e}")
            return {}
    
    def _get_bucket_stats(self, bucket_name: str) -> Dict[str, Any]:
        """Get statistics for a specific bucket"""
        try:
            objects = minio_client.client.list_objects(bucket_name, recursive=True)
            
            total_size = 0
            object_count = 0
            
            for obj in objects:
                total_size += obj.size
                object_count += 1
            
            return {
                "bucket_name": bucket_name,
                "object_count": object_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.warning(f"Error getting bucket stats for {bucket_name}: {e}")
            return {
                "bucket_name": bucket_name,
                "object_count": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0
            }

# Global enhanced storage operations instance
enhanced_storage_ops = EnhancedStorageOperations()