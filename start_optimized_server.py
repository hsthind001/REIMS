#!/usr/bin/env python3
"""
REIMS Backend Server Startup
Optimized startup script with error handling and dependency checks
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check and install missing dependencies"""
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'pandas', 
        'requests', 'python-dotenv', 'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"Missing packages: {missing_packages}")
        logger.info("Installing missing dependencies...")
        try:
            import subprocess
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--user", *missing_packages
            ])
            logger.info("Dependencies installed successfully")
        except Exception as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    return True

def setup_database():
    """Initialize database with optimized settings"""
    try:
        import sqlite3
        from datetime import datetime
        
        db_path = "reims.db"
        logger.info(f"Setting up database: {db_path}")
        
        # Create optimized connection
        conn = sqlite3.connect(db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        
        # Basic documents table for core functionality
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT UNIQUE NOT NULL,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                property_id TEXT,
                file_size INTEGER,
                content_type TEXT,
                file_path TEXT,
                upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'uploaded',
                processing_status TEXT DEFAULT 'pending',
                extracted_data TEXT,
                ai_insights TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_id ON documents(document_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_property ON documents(property_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status)")
        
        conn.commit()
        conn.close()
        
        logger.info("Database setup completed")
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False

def create_upload_directory():
    """Create upload directory with proper permissions"""
    try:
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Also create storage directory
        storage_dir = Path("storage")
        storage_dir.mkdir(exist_ok=True)
        
        logger.info(f"Upload directories created: {upload_dir}, {storage_dir}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create directories: {e}")
        return False

def start_server():
    """Start the FastAPI server with optimized settings"""
    try:
        logger.info("Starting REIMS Backend Server...")
        
        # Import FastAPI components
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        # Create FastAPI app
        app = FastAPI(
            title="REIMS API",
            description="Real Estate Information Management System - Optimized",
            version="2.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Configure CORS for frontend
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Import routers with error handling
        routers_loaded = []
        
        try:
            from backend.api.upload import router as upload_router
            app.include_router(upload_router)
            routers_loaded.append("upload")
        except Exception as e:
            logger.warning(f"Upload router failed to load: {e}")
        
        try:
            from backend.api.analytics import router as analytics_router
            app.include_router(analytics_router)
            routers_loaded.append("analytics")
        except Exception as e:
            logger.warning(f"Analytics router failed to load: {e}")
        
        try:
            from backend.api.property_management import router as property_router
            app.include_router(property_router)
            routers_loaded.append("property_management")
        except Exception as e:
            logger.warning(f"Property management router failed to load: {e}")
        
        try:
            from backend.api.ai_processing import router as ai_router
            app.include_router(ai_router)
            routers_loaded.append("ai_processing")
        except Exception as e:
            logger.warning(f"AI processing router failed to load: {e}")
        
        # Add health check endpoint
        @app.get("/health")
        async def health_check():
            from datetime import datetime
            return {
                "status": "healthy",
                "service": "REIMS API v2.0",
                "routers_loaded": routers_loaded,
                "timestamp": datetime.now().isoformat()
            }
        
        @app.get("/")
        async def root():
            return {
                "message": "REIMS API is running",
                "version": "2.0.0",
                "docs": "/docs",
                "health": "/health"
            }
        
        # Start server with uvicorn
        import uvicorn
        logger.info(f"Server starting with routers: {routers_loaded}")
        logger.info("API Documentation: http://localhost:8000/docs")
        logger.info("Health Check: http://localhost:8000/health")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload for production
            access_log=True,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        return False

def main():
    """Main startup function"""
    logger.info("🚀 REIMS Backend Server - Optimized Startup")
    logger.info("=" * 50)
    
    # Step 1: Check dependencies
    logger.info("1. Checking dependencies...")
    if not check_dependencies():
        logger.error("❌ Dependency check failed")
        return 1
    
    # Step 2: Setup database
    logger.info("2. Setting up database...")
    if not setup_database():
        logger.error("❌ Database setup failed")
        return 1
    
    # Step 3: Create directories
    logger.info("3. Creating directories...")
    if not create_upload_directory():
        logger.error("❌ Directory creation failed")
        return 1
    
    # Step 4: Start server
    logger.info("4. Starting server...")
    logger.info("✅ All checks passed - starting REIMS server")
    start_server()
    
    return 0

if __name__ == "__main__":
    exit(main())