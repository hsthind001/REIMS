from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import uuid
import json
from datetime import datetime
from pathlib import Path
import time
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RobustBackend:
    """Robust backend with dependency management and retry logic"""
    
    def __init__(self):
        self.app = FastAPI(title="REIMS Robust Backend API")
        self.database_available = False
        self.minio_available = False
        self.minio_client = None
        self.bucket_name = "reims-documents"
        self.mock_documents = []
        self.mock_properties = []
        
        # Setup CORS - UPDATED for frontend dependency
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",  # Frontend development server
                "http://localhost:3000",  # Alternative frontend port
                "http://127.0.0.1:5173",  # Alternative localhost format
                "http://127.0.0.1:3000"   # Alternative localhost format
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize connections with retries
        self._initialize_with_retries()
        
        # Setup routes
        self._setup_routes()
    
    def _initialize_with_retries(self):
        """Initialize database and MinIO connections with retry logic"""
        # Initialize database
        self._init_database()
        
        # Initialize MinIO
        self._init_minio()
    
    def _init_database(self, max_retries=5):
        """Initialize database connection with retries"""
        for attempt in range(max_retries):
            try:
                sys.path.append(str(Path(__file__).parent / "backend"))
                from database import get_db, Document, create_tables, SessionLocal
                from sqlalchemy.orm import Session
                
                # Ensure tables exist
                create_tables()
                
                # Test database connection
                db = SessionLocal()
                db.query(Document).first()
                db.close()
                
                self.database_available = True
                self.get_db = get_db
                self.Document = Document
                self.SessionLocal = SessionLocal
                self.Session = Session
                
                logger.info("✅ Database connection established")
                return True
                
            except Exception as e:
                logger.warning(f"Database init attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("❌ Database initialization failed after all retries")
                    self.database_available = False
                    return False
    
    def _init_minio(self, max_retries=5):
        """Initialize MinIO connection with retries"""
        for attempt in range(max_retries):
            try:
                from minio import Minio
                from minio.error import S3Error
                
                # Initialize MinIO client
                self.minio_client = Minio(
                    endpoint="localhost:9000",
                    access_key="minioadmin",
                    secret_key="minioadmin",
                    secure=False
                )
                
                # Test connection
                self.minio_client.list_buckets()
                
                # Ensure bucket exists
                if not self.minio_client.bucket_exists(self.bucket_name):
                    self.minio_client.make_bucket(self.bucket_name)
                    logger.info(f"Created bucket: {self.bucket_name}")
                
                self.minio_available = True
                logger.info("✅ MinIO connection established")
                return True
                
            except Exception as e:
                logger.warning(f"MinIO init attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("❌ MinIO initialization failed after all retries")
                    self.minio_available = False
                    self.minio_client = None
                    return False
    
    def _retry_database_operation(self, operation, max_retries=3):
        """Retry database operations with reconnection"""
        for attempt in range(max_retries):
            try:
                if not self.database_available:
                    self._init_database()
                
                if self.database_available:
                    return operation()
                else:
                    raise Exception("Database not available")
                    
            except Exception as e:
                logger.warning(f"Database operation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    # Try to reinitialize database connection
                    self._init_database()
                else:
                    logger.error("Database operation failed after all retries")
                    raise e
    
    def _retry_minio_operation(self, operation, max_retries=3):
        """Retry MinIO operations with reconnection"""
        for attempt in range(max_retries):
            try:
                if not self.minio_available:
                    self._init_minio()
                
                if self.minio_available:
                    return operation()
                else:
                    raise Exception("MinIO not available")
                    
            except Exception as e:
                logger.warning(f"MinIO operation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    # Try to reinitialize MinIO connection
                    self._init_minio()
                else:
                    logger.error("MinIO operation failed after all retries")
                    raise e
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "database": self.database_available,
                "minio": self.minio_available,
                "services": {
                    "database": "available" if self.database_available else "unavailable",
                    "minio": "available" if self.minio_available else "unavailable"
                }
            }
        
        @self.app.get("/")
        async def root():
            return {
                "message": "REIMS Robust Backend API is running",
                "timestamp": datetime.now().isoformat(),
                "database_status": "available" if self.database_available else "unavailable",
                "minio_status": "available" if self.minio_available else "unavailable"
            }
        
        @self.app.get("/api/documents")
        async def get_documents():
            """Get all documents with retry logic"""
            try:
                def db_operation():
                    db = self.SessionLocal()
                    try:
                        documents = db.query(self.Document).order_by(self.Document.upload_timestamp.desc()).all()
                        
                        document_list = []
                        for doc in documents:
                            document_list.append({
                                "document_id": doc.document_id,
                                "original_filename": doc.original_filename,
                                "property_id": doc.property_id,
                                "file_size": doc.file_size,
                                "content_type": doc.content_type,
                                "upload_timestamp": doc.upload_timestamp.isoformat() if doc.upload_timestamp else None,
                                "status": doc.status,
                                "storage_type": doc.storage_type,
                                "minio_bucket": doc.minio_bucket,
                                "minio_object_name": doc.minio_object_name,
                                "minio_url": doc.minio_url,
                                "minio_upload_timestamp": doc.minio_upload_timestamp.isoformat() if doc.minio_upload_timestamp else None
                            })
                        
                        return {
                            "documents": document_list, 
                            "total": len(document_list),
                            "source": "database"
                        }
                    finally:
                        db.close()
                
                if self.database_available:
                    return self._retry_database_operation(db_operation)
                
            except Exception as e:
                logger.error(f"Database documents query failed: {e}")
            
            # Fallback to mock data
            return {
                "documents": self.mock_documents, 
                "total": len(self.mock_documents), 
                "source": "mock_data"
            }
        
        @self.app.get("/api/analytics")
        async def get_analytics():
            """Get analytics with retry logic"""
            try:
                def db_operation():
                    db = self.SessionLocal()
                    try:
                        total_docs = db.query(self.Document).count()
                        minio_docs = db.query(self.Document).filter(
                            self.Document.storage_type.in_(["minio", "local_and_minio"])
                        ).count()
                        
                        # Get documents by property
                        properties = db.query(self.Document.property_id).distinct().all()
                        property_count = len(properties)
                        
                        return {
                            "total_documents": total_docs,
                            "total_properties": property_count,
                            "minio_stored_documents": minio_docs,
                            "processing_stats": {
                                "uploaded": total_docs,
                                "processed": 0,
                                "failed": 0
                            },
                            "source": "database"
                        }
                    finally:
                        db.close()
                
                if self.database_available:
                    return self._retry_database_operation(db_operation)
                
            except Exception as e:
                logger.error(f"Database analytics query failed: {e}")
            
            # Fallback to mock data
            return {
                "total_documents": len(self.mock_documents),
                "total_properties": len(self.mock_properties),
                "processing_stats": {
                    "uploaded": 0,
                    "processed": 0,
                    "failed": 0
                },
                "source": "mock_data"
            }
        
        @self.app.get("/api/properties")
        async def get_properties():
            return self.mock_properties
        
        @self.app.get("/api/property/properties")
        async def get_property_properties():
            return self.mock_properties
        
        @self.app.get("/api/property/tenants")
        async def get_tenants():
            return []
        
        @self.app.get("/api/property/leases")
        async def get_leases():
            return []
        
        @self.app.get("/api/property/maintenance")
        async def get_maintenance():
            return []
        
        @self.app.get("/api/documents/property/{property_id}")
        async def get_documents_by_property(property_id: str):
            """Get documents by property with retry logic"""
            try:
                def db_operation():
                    db = self.SessionLocal()
                    try:
                        documents = db.query(self.Document).filter(
                            self.Document.property_id == property_id
                        ).order_by(self.Document.upload_timestamp.desc()).all()
                        
                        document_list = []
                        for doc in documents:
                            document_list.append({
                                "document_id": doc.document_id,
                                "original_filename": doc.original_filename,
                                "property_id": doc.property_id,
                                "file_size": doc.file_size,
                                "content_type": doc.content_type,
                                "upload_timestamp": doc.upload_timestamp.isoformat() if doc.upload_timestamp else None,
                                "status": doc.status,
                                "storage_type": doc.storage_type,
                                "minio_bucket": doc.minio_bucket,
                                "minio_object_name": doc.minio_object_name,
                                "minio_url": doc.minio_url
                            })
                        
                        return {
                            "documents": document_list, 
                            "total": len(document_list),
                            "property_id": property_id,
                            "source": "database"
                        }
                    finally:
                        db.close()
                
                if self.database_available:
                    return self._retry_database_operation(db_operation)
                
            except Exception as e:
                logger.error(f"Database property query failed: {e}")
            
            # Fallback to filtering mock data
            filtered_docs = [doc for doc in self.mock_documents if doc.get("property_id") == property_id]
            return {
                "documents": filtered_docs, 
                "total": len(filtered_docs),
                "property_id": property_id,
                "source": "mock_data"
            }
        
        @self.app.post("/api/documents/upload")
        async def upload_document(file: UploadFile = File(...), property_id: str = Form(...)):
            """Enhanced document upload with robust error handling"""
            document_id = str(uuid.uuid4())
            
            try:
                # Read file content
                file_content = await file.read()
                file_size = len(file_content)
                
                # Store file in local storage first (always works)
                storage_dir = Path("storage")
                storage_dir.mkdir(exist_ok=True)
                
                stored_filename = f"{document_id}_{file.filename}"
                file_path = storage_dir / stored_filename
                
                with open(file_path, "wb") as buffer:
                    buffer.write(file_content)
                
                # Create metadata
                metadata = {
                    "document_id": document_id,
                    "original_filename": file.filename,
                    "property_id": property_id,
                    "file_size": file_size,
                    "content_type": file.content_type or "application/octet-stream",
                    "upload_timestamp": datetime.now().isoformat(),
                    "storage_path": str(file_path),
                    "status": "uploaded"
                }
                
                # Save metadata
                metadata_file = storage_dir / f"{document_id}_metadata.json"
                with open(metadata_file, "w") as f:
                    json.dump(metadata, f, indent=2)
                
                # Try MinIO upload with retry
                minio_status = "local_only"
                minio_url = None
                minio_upload_time = None
                object_name = None
                
                if self.minio_available:
                    try:
                        def minio_operation():
                            nonlocal object_name, minio_url, minio_upload_time
                            object_name = f"frontend-uploads/{property_id}/{stored_filename}"
                            
                            with open(file_path, "rb") as f:
                                self.minio_client.put_object(
                                    self.bucket_name,
                                    object_name,
                                    f,
                                    length=file_size,
                                    content_type=file.content_type or "application/octet-stream"
                                )
                            
                            minio_url = f"minio://{self.bucket_name}/{object_name}"
                            minio_upload_time = datetime.now()
                            return True
                        
                        self._retry_minio_operation(minio_operation)
                        minio_status = "uploaded_to_minio"
                        
                        # Update metadata
                        metadata.update({
                            "minio_bucket": self.bucket_name,
                            "minio_object_name": object_name,
                            "minio_url": minio_url,
                            "storage_type": "local_and_minio",
                            "minio_upload_timestamp": minio_upload_time.isoformat()
                        })
                        
                        with open(metadata_file, "w") as f:
                            json.dump(metadata, f, indent=2)
                        
                        logger.info(f"✅ File uploaded to MinIO: {object_name}")
                        
                    except Exception as e:
                        logger.error(f"MinIO upload failed: {e}")
                        minio_status = f"minio_error: {str(e)}"
                
                # Try database storage with retry
                db_status = "no_database"
                if self.database_available:
                    try:
                        def db_operation():
                            db = self.SessionLocal()
                            try:
                                db_document = self.Document(
                                    document_id=document_id,
                                    original_filename=file.filename,
                                    stored_filename=stored_filename,
                                    property_id=property_id,
                                    file_size=file_size,
                                    content_type=file.content_type or "application/octet-stream",
                                    file_path=str(file_path),
                                    upload_timestamp=datetime.now(),
                                    status="uploaded",
                                    minio_bucket=self.bucket_name if minio_status == "uploaded_to_minio" else None,
                                    minio_object_name=object_name if minio_status == "uploaded_to_minio" else None,
                                    minio_url=minio_url,
                                    storage_type="local_and_minio" if minio_status == "uploaded_to_minio" else "local",
                                    minio_upload_timestamp=minio_upload_time
                                )
                                
                                db.add(db_document)
                                db.commit()
                                db.refresh(db_document)
                                return True
                            except Exception as e:
                                db.rollback()
                                raise e
                            finally:
                                db.close()
                        
                        self._retry_database_operation(db_operation)
                        db_status = "stored_in_database"
                        logger.info(f"✅ Document stored in database with ID: {document_id}")
                        
                    except Exception as e:
                        logger.error(f"Database storage failed: {e}")
                        db_status = f"database_error: {str(e)}"
                
                # Add to mock data as backup
                mock_document = {
                    "document_id": document_id,
                    "original_filename": file.filename,
                    "property_id": property_id,
                    "file_size": file_size,
                    "upload_timestamp": datetime.now().isoformat(),
                    "status": "uploaded",
                    "storage_path": str(file_path),
                    "minio_status": minio_status,
                    "minio_url": minio_url
                }
                
                self.mock_documents.append(mock_document)
                
                return {
                    "document_id": document_id,
                    "filename": file.filename,
                    "file_size": file_size,
                    "status": "uploaded",
                    "storage_location": str(file_path),
                    "minio_location": minio_url,
                    "database_status": db_status,
                    "message": f"File uploaded successfully and stored locally" + 
                              (f" and in MinIO bucket '{self.bucket_name}'" if minio_status == "uploaded_to_minio" else "") +
                              (f" and database" if db_status == "stored_in_database" else ""),
                    "workflow": {
                        "step_1": "✅ File received from frontend",
                        "step_2": "✅ Stored locally in storage/",
                        "step_3": "✅ Metadata saved as JSON",
                        "step_4": f"{'✅' if minio_status == 'uploaded_to_minio' else '❌'} MinIO integration: {minio_status}",
                        "step_5": f"{'✅' if db_status == 'stored_in_database' else '❌'} Database storage: {db_status}",
                        "step_6": "✅ Ready for AI processing"
                    },
                    "service_status": {
                        "database": self.database_available,
                        "minio": self.minio_available
                    }
                }
                
            except Exception as e:
                logger.error(f"Upload failed: {e}")
                raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Create the robust backend instance
robust_backend = RobustBackend()
app = robust_backend.app

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting REIMS Robust Backend...")
    logger.info(f"Database available: {robust_backend.database_available}")
    logger.info(f"MinIO available: {robust_backend.minio_available}")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)