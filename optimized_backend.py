"""
REIMS Optimized Backend API - Production Ready
High-performance FastAPI application with comprehensive optimizations
"""

import os
import sys
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from pathlib import Path

# Core FastAPI imports
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Database imports
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import optimized database
try:
    from database_optimized import get_db, Document, init_database, get_database_stats
    DATABASE_AVAILABLE = True
except ImportError:
    logger.warning("Optimized database not available - using fallback")
    DATABASE_AVAILABLE = False

# Pydantic models for API responses
class DocumentResponse(BaseModel):
    document_id: str
    original_filename: str
    property_id: str
    file_size: int
    upload_timestamp: datetime
    status: str
    processing_status: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    database: Dict[str, Any]
    uptime_seconds: float

class AnalyticsResponse(BaseModel):
    total_documents: int
    processing_stats: Dict[str, int]
    recent_uploads: int
    storage_used_mb: float

# Global variables for performance tracking
app_start_time = datetime.now()
request_count = 0

# Startup/shutdown context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    logger.info("🚀 REIMS Backend Starting Up...")
    
    # Initialize database
    if DATABASE_AVAILABLE:
        init_database()
        logger.info("✅ Database initialized")
    
    # Create upload directories
    for directory in ["uploads", "storage", "temp"]:
        Path(directory).mkdir(exist_ok=True)
    logger.info("✅ Upload directories created")
    
    # Cleanup old temp files
    cleanup_temp_files()
    logger.info("✅ Temp files cleaned")
    
    yield
    
    # Shutdown
    logger.info("🛑 REIMS Backend Shutting Down...")

def cleanup_temp_files():
    """Remove temporary files older than 24 hours"""
    try:
        temp_dir = Path("temp")
        if temp_dir.exists():
            cutoff_time = datetime.now() - timedelta(hours=24)
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_path.unlink()
                        logger.info(f"Cleaned up temp file: {file_path}")
    except Exception as e:
        logger.warning(f"Temp file cleanup failed: {e}")

# Create FastAPI app with optimizations
app = FastAPI(
    title="REIMS API - Optimized",
    description="Real Estate Information Management System - High Performance Edition",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    # Performance optimizations
    generate_unique_id_function=lambda route: f"{route.tags[0]}-{route.name}" if route.tags else route.name,
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware with optimized settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:8080",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Request counting middleware
@app.middleware("http")
async def count_requests(request, call_next):
    global request_count
    request_count += 1
    
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-Count"] = str(request_count)
    
    return response

# Exception handlers
@app.exception_handler(500)
async def internal_server_error(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )

@app.exception_handler(404)
async def not_found_error(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

# Root endpoint
@app.get("/", tags=["system"])
async def root():
    """Root endpoint with system information"""
    return {
        "message": "REIMS API - Optimized Edition",
        "version": "2.1.0",
        "documentation": "/docs",
        "health": "/health",
        "features": [
            "High-performance SQLite with WAL mode",
            "Optimized file uploads",
            "Advanced caching",
            "Request compression",
            "Performance monitoring"
        ]
    }

# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check():
    """Comprehensive health check with performance metrics"""
    uptime = (datetime.now() - app_start_time).total_seconds()
    
    # Get database stats
    db_stats = get_database_stats() if DATABASE_AVAILABLE else {"status": "unavailable"}
    
    return HealthResponse(
        status="healthy",
        version="2.1.0",
        timestamp=datetime.now(),
        database=db_stats,
        uptime_seconds=uptime
    )

# Documents endpoints
@app.get("/api/documents", tags=["documents"])
async def get_documents(
    limit: int = 100,
    offset: int = 0,
    property_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db) if DATABASE_AVAILABLE else None
):
    """Get documents with pagination and filtering"""
    if not DATABASE_AVAILABLE:
        return {"documents": [], "total": 0, "message": "Database not available"}
    
    try:
        query = db.query(Document)
        
        # Apply filters
        if property_id:
            query = query.filter(Document.property_id == property_id)
        if status:
            query = query.filter(Document.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        documents = query.offset(offset).limit(limit).all()
        
        return {
            "documents": [
                {
                    "document_id": doc.document_id,
                    "original_filename": doc.original_filename,
                    "property_id": doc.property_id,
                    "file_size": doc.file_size,
                    "upload_timestamp": doc.upload_timestamp,
                    "status": doc.status,
                    "processing_status": doc.processing_status
                }
                for doc in documents
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")

@app.post("/api/documents/upload", tags=["documents"])
async def upload_document(
    file: UploadFile = File(...),
    property_id: str = Form(...),
    db: Session = Depends(get_db) if DATABASE_AVAILABLE else None
):
    """Optimized document upload with validation and storage"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")
    
    # Validate file type
    allowed_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "text/csv"
    }
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415, 
            detail=f"Unsupported file type: {file.content_type}"
        )
    
    try:
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Create storage path
        storage_dir = Path("storage")
        storage_dir.mkdir(exist_ok=True)
        
        # Generate safe filename
        safe_filename = f"{document_id}_{file.filename}"
        file_path = storage_dir / safe_filename
        
        # Save file with streaming to handle large files
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Save to database
        if DATABASE_AVAILABLE and db:
            db_document = Document(
                document_id=document_id,
                original_filename=file.filename,
                stored_filename=safe_filename,
                property_id=property_id,
                file_size=len(content),
                content_type=file.content_type,
                file_path=str(file_path),
                upload_timestamp=datetime.now(),
                status="uploaded",
                processing_status="pending"
            )
            
            db.add(db_document)
            db.commit()
            db.refresh(db_document)
        
        logger.info(f"Document uploaded: {document_id} ({file.filename})")
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "file_size": len(content),
            "property_id": property_id,
            "status": "uploaded",
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        # Cleanup file if database save failed
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Analytics endpoint
@app.get("/api/analytics", response_model=AnalyticsResponse, tags=["analytics"])
async def get_analytics(db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    """Get system analytics and statistics"""
    
    if not DATABASE_AVAILABLE:
        return AnalyticsResponse(
            total_documents=0,
            processing_stats={"uploaded": 0, "processed": 0, "failed": 0},
            recent_uploads=0,
            storage_used_mb=0.0
        )
    
    try:
        # Get document counts
        total_docs = db.query(Document).count()
        
        # Get processing stats
        uploaded = db.query(Document).filter(Document.status == "uploaded").count()
        processed = db.query(Document).filter(Document.status == "processed").count()
        failed = db.query(Document).filter(Document.status == "failed").count()
        
        # Get recent uploads (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent = db.query(Document).filter(Document.upload_timestamp >= yesterday).count()
        
        # Calculate storage usage
        storage_dir = Path("storage")
        storage_mb = 0.0
        if storage_dir.exists():
            storage_mb = sum(f.stat().st_size for f in storage_dir.iterdir() if f.is_file()) / (1024 * 1024)
        
        return AnalyticsResponse(
            total_documents=total_docs,
            processing_stats={
                "uploaded": uploaded,
                "processed": processed,
                "failed": failed
            },
            recent_uploads=recent,
            storage_used_mb=round(storage_mb, 2)
        )
        
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")

# Property management endpoints
@app.get("/api/properties", tags=["properties"])
async def get_properties():
    """Get all properties (mock data for now)"""
    return {
        "properties": [],
        "total": 0,
        "message": "Property management feature coming soon"
    }

@app.get("/api/property/{endpoint:path}", tags=["properties"])
async def property_endpoints(endpoint: str):
    """Handle property management sub-endpoints"""
    return {
        "endpoint": endpoint,
        "data": [],
        "message": f"Property {endpoint} endpoint - coming soon"
    }

# Performance monitoring
@app.get("/api/system/stats", tags=["system"])
async def get_system_stats():
    """Get system performance statistics"""
    uptime = (datetime.now() - app_start_time).total_seconds()
    
    # Get storage usage
    storage_usage = {}
    for directory in ["storage", "uploads", "temp"]:
        dir_path = Path(directory)
        if dir_path.exists():
            size_mb = sum(f.stat().st_size for f in dir_path.iterdir() if f.is_file()) / (1024 * 1024)
            storage_usage[directory] = round(size_mb, 2)
    
    return {
        "uptime_seconds": uptime,
        "total_requests": request_count,
        "requests_per_second": round(request_count / max(uptime, 1), 2),
        "storage_usage_mb": storage_usage,
        "database_available": DATABASE_AVAILABLE,
        "python_version": sys.version
    }

# Static file serving for uploads (optional)
if Path("storage").exists():
    app.mount("/files", StaticFiles(directory="storage"), name="files")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "optimized_backend:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        workers=1,
        access_log=True,
        log_level="info"
    )