"""
REIMS Database Configuration - SQLite Only
Provides database session management and connection pooling
Configured for SQLite for simplicity and reliability
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Load environment variables from .env file
load_dotenv()

# Database URL from environment - defaults to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reims.db")

# Confirm we're using SQLite
if DATABASE_URL.startswith("sqlite"):
    print(f"[DATABASE] OK Using SQLite: {DATABASE_URL}")
    
    # Create optimized SQLite engine
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for SQL query logging
    )
    
    # Configure SQLite optimizations for better performance
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Enable SQLite optimizations"""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        cursor.execute("PRAGMA synchronous=NORMAL")  # Faster writes
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")  # In-memory temp tables
        cursor.execute("PRAGMA foreign_keys=ON")  # Enforce foreign keys
        cursor.close()
    
    print("[DATABASE] OK SQLite optimizations enabled")
else:
    # User configured PostgreSQL - respect their choice
    print(f"[DATABASE] Using PostgreSQL: {DATABASE_URL}")
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False
    )

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    
    Yields:
        Session: SQLAlchemy database session
        
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Creates all tables defined by SQLAlchemy models.
    """
    Base.metadata.create_all(bind=engine)
    print("SUCCESS: Database tables initialized")


def close_db():
    """
    Close database connections.
    Call this when shutting down the application.
    """
    engine.dispose()
    print("SUCCESS: Database connections closed")


# SQLite-specific optimization
if "sqlite" in DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Enable SQLite optimizations"""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()

