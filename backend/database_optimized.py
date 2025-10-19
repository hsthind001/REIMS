"""
REIMS Database Module - Optimized
High-performance database setup with SQLAlchemy and SQLite optimizations
"""

import os
import logging
from pathlib import Path
from typing import Generator

# Configure logging
logger = logging.getLogger(__name__)

try:
    from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, event
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.pool import StaticPool
    from datetime import datetime
    
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    logger.warning("SQLAlchemy not available - using SQLite fallback")
    SQLALCHEMY_AVAILABLE = False

# Database configuration
DATABASE_URL = "sqlite:///./reims.db"
Base = declarative_base() if SQLALCHEMY_AVAILABLE else None

# SQLite optimizations
SQLITE_PRAGMAS = {
    "journal_mode": "WAL",
    "synchronous": "NORMAL", 
    "cache_size": 10000,
    "temp_store": "MEMORY",
    "mmap_size": 268435456,  # 256MB
    "optimize": None
}

if SQLALCHEMY_AVAILABLE:
    # Create optimized engine
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
            "timeout": 30
        },
        echo=False  # Set to True for SQL debugging
    )
    
    # Configure SQLite pragmas
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        for pragma, value in SQLITE_PRAGMAS.items():
            if value is not None:
                cursor.execute(f"PRAGMA {pragma}={value}")
            else:
                cursor.execute(f"PRAGMA {pragma}")
        cursor.close()
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None

# Document model for core functionality
if SQLALCHEMY_AVAILABLE:
    class Document(Base):
        __tablename__ = "documents"
        
        id = Column(Integer, primary_key=True, index=True)
        document_id = Column(String(255), unique=True, index=True, nullable=False)
        original_filename = Column(String(500), nullable=False)
        stored_filename = Column(String(500), nullable=False)
        property_id = Column(String(100), index=True)
        file_size = Column(Integer)
        content_type = Column(String(100))
        file_path = Column(String(1000))
        upload_timestamp = Column(DateTime, default=datetime.utcnow)
        status = Column(String(50), default="uploaded", index=True)
        processing_status = Column(String(50), default="pending")
        extracted_data = Column(Text)
        ai_insights = Column(Text)
        created_at = Column(DateTime, default=datetime.utcnow)

def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI
    Provides SQLAlchemy session with automatic cleanup
    """
    if not SQLALCHEMY_AVAILABLE or not SessionLocal:
        raise RuntimeError("Database not available - SQLAlchemy not installed")
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_database():
    """
    Initialize database with optimized settings
    Creates tables and applies performance optimizations
    """
    try:
        if SQLALCHEMY_AVAILABLE and engine:
            logger.info("Initializing database with SQLAlchemy...")
            
            # Create tables
            Base.metadata.create_all(bind=engine)
            
            # Verify connection
            with SessionLocal() as db:
                from sqlalchemy import text
                db.execute(text("SELECT 1"))
            
            logger.info("✅ Database initialized successfully with SQLAlchemy")
            return True
        else:
            # Fallback to direct SQLite
            logger.info("Initializing database with direct SQLite...")
            import sqlite3
            
            conn = sqlite3.connect("reims.db", timeout=30.0)
            
            # Apply pragmas
            for pragma, value in SQLITE_PRAGMAS.items():
                if value is not None:
                    conn.execute(f"PRAGMA {pragma}={value}")
                else:
                    conn.execute(f"PRAGMA {pragma}")
            
            # Create basic documents table
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
            
            # Create performance indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_documents_id ON documents(document_id)",
                "CREATE INDEX IF NOT EXISTS idx_documents_property ON documents(property_id)",
                "CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status)",
                "CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at)"
            ]
            
            for index_sql in indexes:
                conn.execute(index_sql)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Database initialized successfully with SQLite fallback")
            return True
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

def get_database_stats():
    """Get database performance statistics"""
    try:
        if SQLALCHEMY_AVAILABLE and SessionLocal:
            with SessionLocal() as db:
                result = db.execute("SELECT COUNT(*) FROM documents").fetchone()
                doc_count = result[0] if result else 0
        else:
            import sqlite3
            conn = sqlite3.connect("reims.db")
            cursor = conn.execute("SELECT COUNT(*) FROM documents")
            doc_count = cursor.fetchone()[0]
            conn.close()
        
        return {
            "document_count": doc_count,
            "database_type": "SQLAlchemy" if SQLALCHEMY_AVAILABLE else "Direct SQLite",
            "status": "healthy"
        }
    except Exception as e:
        logger.error(f"Database stats error: {e}")
        return {
            "document_count": 0,
            "database_type": "Error",
            "status": "error",
            "error": str(e)
        }

def optimize_database():
    """Run database optimization commands"""
    try:
        if SQLALCHEMY_AVAILABLE and engine:
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("PRAGMA optimize"))
                conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
        else:
            import sqlite3
            conn = sqlite3.connect("reims.db")
            conn.execute("PRAGMA optimize")
            conn.execute("VACUUM")
            conn.close()
        
        logger.info("Database optimization completed")
        return True
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        return False

def get_session():
    """Get database session context manager"""
    if not SQLALCHEMY_AVAILABLE or not SessionLocal:
        raise RuntimeError("Database not available")
    
    return SessionLocal()

# Initialize database on module import
if __name__ != "__main__":
    init_database()