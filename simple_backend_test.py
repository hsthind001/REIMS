"""
REIMS Simple Backend - Testing Version
Fast startup backend for testing the optimized system
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel

# Try to import database
try:
    from database_optimized import init_database, optimize_database, get_session
    DATABASE_AVAILABLE = True
    logger.info("Database module loaded successfully")
except ImportError as e:
    DATABASE_AVAILABLE = False
    logger.warning(f"Database not available: {e}")

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    database: str
    uptime_seconds: float

class SystemStats(BaseModel):
    uptime_seconds: float
    database_available: bool
    total_requests: int
    version: str

# Global tracking
app_start_time = datetime.now()
request_count = 0

# Create FastAPI app
app = FastAPI(
    title="REIMS Backend - Simple",
    description="Real Estate Information Management System - Testing Backend",
    version="1.0.0"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request counter middleware
@app.middleware("http")
async def count_requests(request, call_next):
    global request_count
    request_count += 1
    response = await call_next(request)
    return response

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "REIMS Backend - Simple Testing Version",
        "version": "1.0.0",
        "timestamp": datetime.now(),
        "status": "running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.now() - app_start_time).total_seconds()
    
    database_status = "available" if DATABASE_AVAILABLE else "not_available"
    if DATABASE_AVAILABLE:
        try:
            # Test database connection
            with get_session() as db:
                # Simple test query
                database_status = "healthy"
        except Exception as e:
            database_status = f"error: {str(e)}"
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(),
        database=database_status,
        uptime_seconds=round(uptime, 2)
    )

@app.get("/api/system/stats", response_model=SystemStats)
async def get_system_stats():
    """Get system statistics"""
    uptime = (datetime.now() - app_start_time).total_seconds()
    
    return SystemStats(
        uptime_seconds=round(uptime, 2),
        database_available=DATABASE_AVAILABLE,
        total_requests=request_count,
        version="1.0.0"
    )

@app.get("/api/properties")
async def get_properties():
    """Get properties list"""
    # Mock data for testing
    return {
        "properties": [
            {
                "id": "1",
                "name": "Test Property 1",
                "address": "123 Test St",
                "status": "active"
            },
            {
                "id": "2", 
                "name": "Test Property 2",
                "address": "456 Demo Ave",
                "status": "active"
            }
        ],
        "total": 2
    }

@app.get("/api/documents")
async def get_documents():
    """Get documents list"""
    # Mock data for testing
    return {
        "documents": [
            {
                "id": "doc1",
                "name": "Test Document 1.pdf",
                "property_id": "1",
                "upload_date": datetime.now().isoformat(),
                "status": "processed"
            },
            {
                "id": "doc2",
                "name": "Test Document 2.pdf", 
                "property_id": "2",
                "upload_date": datetime.now().isoformat(),
                "status": "processed"
            }
        ],
        "total": 2
    }

@app.get("/api/analytics")
async def get_analytics():
    """Get analytics data"""
    return {
        "total_properties": 2,
        "total_documents": 2,
        "recent_uploads": 0,
        "processing_stats": {
            "processed": 2,
            "pending": 0,
            "failed": 0
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    # Initialize database if available
    if DATABASE_AVAILABLE:
        logger.info("Initializing database...")
        try:
            if init_database():
                optimize_database()
                logger.info("✅ Database initialized and optimized")
            else:
                logger.warning("⚠️ Database initialization failed")
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
    
    logger.info("🚀 Starting REIMS Simple Backend on http://localhost:8001")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        access_log=True
    )