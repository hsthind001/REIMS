from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration - SQLite Only
# Using SQLite for simplicity and reliability
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reims.db")

# Create SQLite engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

print(f"[DATABASE] OK Using SQLite: {DATABASE_URL}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(String, unique=True, index=True, nullable=False)
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False)
    property_id = Column(String, index=True, nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="uploaded")
    
    # MinIO Storage Integration
    minio_bucket = Column(String, nullable=True)
    minio_object_name = Column(String, nullable=True)
    minio_url = Column(String, nullable=True)
    storage_type = Column(String, default="local")  # local, minio, local_and_minio
    minio_upload_timestamp = Column(DateTime, nullable=True)
    
    # Document Metadata (NEW)
    property_name = Column(String(255), index=True, nullable=True)  # Actual property name (e.g., "Empire State Plaza")
    document_year = Column(Integer, index=True, nullable=True)  # Financial year (e.g., 2024)
    document_type = Column(String(100), nullable=True)  # Document type (e.g., "Income Statement")
    document_period = Column(String(50), default="Annual")  # Period (Annual, Q1, Q2, Q3, Q4, etc.)
    
    # Relationships
    processing_jobs = relationship("ProcessingJob", back_populates="document")
    extracted_data = relationship("ExtractedData", back_populates="document")

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(String, unique=True, index=True, nullable=False)
    document_id = Column(String, ForeignKey("documents.document_id"), nullable=False)
    status = Column(String, default="queued")  # queued, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    processing_result = Column(JSON, nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="processing_jobs")

class ExtractedData(Base):
    __tablename__ = "extracted_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(String, ForeignKey("documents.document_id"), nullable=False)
    data_type = Column(String, nullable=False)  # csv, excel, pdf
    extracted_content = Column(JSON, nullable=False)
    analysis_results = Column(JSON, nullable=True)
    property_indicators = Column(JSON, nullable=True)
    extraction_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Specific fields for different data types
    row_count = Column(Integer, nullable=True)  # For CSV/Excel
    column_count = Column(Integer, nullable=True)  # For CSV/Excel
    sheet_count = Column(Integer, nullable=True)  # For Excel
    page_count = Column(Integer, nullable=True)  # For PDF
    word_count = Column(Integer, nullable=True)  # For PDF
    
    # Relationships
    document = relationship("Document", back_populates="extracted_data")

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(String, unique=True, index=True, nullable=False)
    address = Column(String, nullable=True)
    property_type = Column(String, nullable=True)  # residential, commercial, etc.
    value = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional property metadata (renamed to avoid conflict)
    property_metadata = Column(JSON, nullable=True)

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_date = Column(DateTime, default=datetime.utcnow)
    dimensions = Column(JSON, nullable=True)  # Additional categorization data

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Create tables automatically
create_tables()

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!")