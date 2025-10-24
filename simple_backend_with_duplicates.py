from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import uuid
import json
import time
import logging
import redis
from rq import Queue
from rq.job import Retry
from datetime import datetime
from pathlib import Path

# Database integration
try:
    import sys
    sys.path.append(str(Path(__file__).parent / "backend"))
    from database import get_db, Document, create_tables, SessionLocal
    from sqlalchemy.orm import Session
    from sqlalchemy import text
    DATABASE_AVAILABLE = True
    print("[OK] Database integration available")
    
    # Ensure tables exist
    create_tables()
    
except Exception as e:
    print(f"[WARN] Database not available: {e}")
    DATABASE_AVAILABLE = False

# MinIO integration
try:
    from minio import Minio
    from minio.error import S3Error
    
    # Initialize MinIO client
    minio_client = Minio(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    
    # Ensure bucket exists
    bucket_name = "reims-files"
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
    
    MINIO_AVAILABLE = True
    print("[OK] MinIO client initialized successfully")
    
except Exception as e:
    print(f"[WARN] MinIO not available: {e}")
    MINIO_AVAILABLE = False
    minio_client = None
    bucket_name = None

# RQ Queue integration
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.ping()  # Test connection
    rq_queue = Queue('document-processing', connection=redis_client)
    REDIS_AVAILABLE = True
    print("[OK] RQ Queue initialized successfully")
except Exception as e:
    print(f"[WARN] Redis/RQ not available: {e}")
    REDIS_AVAILABLE = False
    redis_client = None
    rq_queue = None

# Configure logging
logging.basicConfig(filename='simple_backend_app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create a simple FastAPI app with CORS
app = FastAPI(title="REIMS Simple API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data for testing
mock_documents = []
mock_properties = []

# MinIO bucket organization structure
BUCKET_PATHS = {
    "balance_sheet": "Financial Statements/{year}/Balance Sheets/",
    "income_statement": "Financial Statements/{year}/Income Statements/",
    "cash_flow_statement": "Financial Statements/{year}/Cash Flow Statements/",
    "rent_roll": "Financial Statements/{year}/Rent Rolls/",
    "other": "Financial Statements/{year}/Other/"
}

def extract_year_from_filename(filename: str) -> str:
    """Extract year from filename (e.g., 'ESP 2024 Balance Sheet.pdf' -> '2024')"""
    import re
    # Look for 4-digit year in filename
    match = re.search(r'\b(20\d{2})\b', filename)
    if match:
        return match.group(1)
    # Default to current year if not found
    from datetime import datetime
    return str(datetime.now().year)

def detect_document_type_from_filename(filename: str) -> str:
    """
    Auto-detect document type from filename
    Examples:
    - 'ESP 2024 Balance Sheet.pdf' -> 'balance_sheet'
    - 'ESP 2024 Income Statement.pdf' -> 'income_statement'
    - 'ESP 2024 Cash Flow Statement.pdf' -> 'cash_flow_statement'
    - 'ESP April 2025 Rent Roll.pdf' -> 'rent_roll'
    """
    filename_lower = filename.lower()
    
    # Check for balance sheet
    if 'balance sheet' in filename_lower or 'balance-sheet' in filename_lower:
        return 'balance_sheet'
    
    # Check for income statement
    if 'income statement' in filename_lower or 'income-statement' in filename_lower:
        return 'income_statement'
    
    # Check for cash flow statement
    if 'cash flow' in filename_lower or 'cashflow' in filename_lower or 'cash-flow' in filename_lower:
        return 'cash_flow_statement'
    
    # Check for rent roll
    if 'rent roll' in filename_lower or 'rent-roll' in filename_lower or 'rentroll' in filename_lower:
        return 'rent_roll'
    
    # Default to other
    return 'other'

def get_minio_path(document_type: str, filename: str) -> str:
    """Generate MinIO path based on document type and year from filename"""
    year = extract_year_from_filename(filename)
    base_path = BUCKET_PATHS.get(document_type, BUCKET_PATHS["other"])
    return base_path.format(year=year) + filename

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/test-status/{document_id}")
async def test_status(document_id: str):
    return {"document_id": document_id, "message": "test endpoint working"}

@app.get("/api/documents/{document_id}/status")
async def get_document_status(document_id: str):
    """
    Get real-time document processing status
    
    Returns:
        - status: queued, processing, completed, failed
        - extracted_data: available when completed
        - error: available when failed
        - timestamps: created_at, completed_at
    """
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get database session
        db = SessionLocal()
        logger.info(f"Looking for document_id: {document_id}")
        
        # Get document from database
        document = db.execute(
            text("SELECT document_id, original_filename, status, upload_timestamp, file_size, property_id FROM documents WHERE document_id = :doc_id"),
            {"doc_id": document_id}
        ).fetchone()
        
        logger.info(f"Document query result: {document}")
        
        if not document:
            logger.warning(f"Document {document_id} not found in database")
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get processing job info
        job_info = db.execute(
            text("SELECT job_id, status, created_at, completed_at FROM processing_jobs WHERE document_id = :doc_id ORDER BY created_at DESC LIMIT 1"),
            {"doc_id": document_id}
        ).fetchone()
        
        # Get extracted data if completed
        extracted_data = None
        if document[2] == 'completed':
            data_records = db.execute(
                text("SELECT data_type, extracted_content FROM extracted_data WHERE document_id = :doc_id"),
                {"doc_id": document_id}
            ).fetchall()
            
            if data_records:
                extracted_data = [
                    {"type": rec[0], "content": rec[1]} 
                    for rec in data_records
                ]
        
        return {
            "document_id": document[0],
            "filename": document[1],
            "status": document[2],
            "upload_timestamp": document[3],
            "file_size": document[4],
            "property_id": document[5],
            "job_id": job_info[0] if job_info else None,
            "job_status": job_info[1] if job_info else None,
            "created_at": job_info[2] if job_info else None,
            "completed_at": job_info[3] if job_info else None,
            "extracted_data": extracted_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'db' in locals():
            db.close()

@app.get("/")
async def root():
    return {"message": "REIMS Backend API is running"}

@app.get("/api/documents")
async def get_documents(db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    """Get all documents from database or mock data"""
    if DATABASE_AVAILABLE and db:
        try:
            documents = db.query(Document).order_by(Document.upload_timestamp.desc()).all()
            
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
        except Exception as e:
            print(f"ERROR Database query failed: {e}")
            # Fall back to mock data
    
    # Fallback to mock data
    return {"documents": mock_documents, "total": len(mock_documents), "source": "mock_data"}

@app.get("/api/properties")
async def get_properties():
    if DATABASE_AVAILABLE:
        try:
            import sqlite3
            conn = sqlite3.connect("reims.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, address, city, state, square_footage, 
                       purchase_price, current_market_value, monthly_rent, 
                       year_built, property_type, status, annual_noi, created_at,
                       total_units, occupied_units, occupancy_rate
                FROM properties
            """)
            properties = []
            for row in cursor.fetchall():
                # Calculate occupancy rate from stores data if available
                occupancy_rate = 0.95  # Default fallback
                # Row indices: [14]=total_units, [15]=occupied_units, [16]=occupancy_rate
                if len(row) > 16 and row[16] and row[16] > 0:  # occupancy_rate column exists and > 0
                    occupancy_rate = row[16]  # Already stored as decimal (0.84 = 84%)
                    print(f"[DEBUG] Property {row[0]} ({row[1]}): Using DB occupancy_rate = {row[16]} -> {occupancy_rate}")
                elif len(row) > 14 and row[14] and row[15] and row[14] > 0:  # Use total_units and occupied_units
                    occupancy_rate = row[15] / row[14]
                    print(f"[DEBUG] Property {row[0]} ({row[1]}): Calculated occupancy_rate = {row[15]}/{row[14]} -> {occupancy_rate}")
                else:
                    occupancy_rate = 0.95  # Default fallback
                    print(f"[DEBUG] Property {row[0]} ({row[1]}): Using default occupancy_rate = {occupancy_rate}")
                
                properties.append({
                    "id": row[0],
                    "name": row[1],
                    "address": row[2],
                    "city": row[3],
                    "state": row[4],
                    "square_footage": row[5],
                    "purchase_price": row[6],
                    "current_market_value": row[7],
                    "monthly_rent": row[8],
                    "year_built": row[9],
                    "property_type": row[10],
                    "status": row[11],
                    "annual_noi": row[12],
                    "created_at": row[13],
                    "total_sqft": row[5],
                    "square_footage": row[5],
                    "acquisition_cost": row[6],
                    "current_value": row[7],
                    "loan_balance": 0,
                    "noi": row[12] if row[12] else (row[8] * 12 if row[8] else 0),
                    "dscr": 1.5,
                    "occupancy_rate": occupancy_rate,
                    "has_active_alerts": False,
                    "units": 1
                })
            conn.close()
            return {
                "success": True,
                "properties": properties,
                "total": len(properties),
                "skip": 0,
                "limit": 20
            }
        except Exception as e:
            print(f"Database error: {e}")
            return mock_properties
    return mock_properties

@app.get("/api/properties/{property_id}")
async def get_property_by_id(property_id: int):
    """Get a single property by ID"""
    if DATABASE_AVAILABLE:
        try:
            import sqlite3
            conn = sqlite3.connect("reims.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, address, city, state, square_footage, 
                       purchase_price, current_market_value, monthly_rent, 
                       year_built, property_type, status, annual_noi, created_at,
                       total_units, occupied_units, occupancy_rate
                FROM properties
                WHERE id = ?
            """, (property_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row is None:
                raise HTTPException(status_code=404, detail=f"Property {property_id} not found")
            
            # Calculate occupancy rate from stores data if available
            occupancy_rate = 0.95  # Default fallback
            # Row indices: [14]=total_units, [15]=occupied_units, [16]=occupancy_rate
            if len(row) > 16 and row[16] and row[16] > 0:  # occupancy_rate column exists and > 0
                occupancy_rate = row[16]  # Already stored as decimal (0.84 = 84%)
                print(f"[DEBUG] Property {row[0]} ({row[1]}): Using DB occupancy_rate = {row[16]} -> {occupancy_rate}")
            elif len(row) > 14 and row[14] and row[15] and row[14] > 0:  # Use total_units and occupied_units
                occupancy_rate = row[15] / row[14]
                print(f"[DEBUG] Property {row[0]} ({row[1]}): Calculated occupancy_rate = {row[15]}/{row[14]} -> {occupancy_rate}")
            else:
                occupancy_rate = 0.95  # Default fallback
                print(f"[DEBUG] Property {row[0]} ({row[1]}): Using default occupancy_rate = {occupancy_rate}")
            
            return {
                "id": row[0],
                "name": row[1],
                "address": row[2],
                "city": row[3],
                "state": row[4],
                "square_footage": row[5],
                "purchase_price": row[6],
                "current_market_value": row[7],
                "monthly_rent": row[8],
                "year_built": row[9],
                "property_type": row[10],
                "status": row[11],
                "annual_noi": row[12],
                "created_at": row[13],
                "noi": row[12] if row[12] else (row[8] * 12 if row[8] else 0),
                "occupancy_rate": occupancy_rate
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"Database error: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    raise HTTPException(status_code=503, detail="Database not available")

@app.get("/api/property/properties")
async def get_property_properties():
    return mock_properties

@app.get("/api/property/tenants")
async def get_tenants():
    return []

@app.get("/api/property/leases")
async def get_leases():
    return []

@app.get("/api/property/maintenance")
async def get_maintenance():
    return []

@app.get("/api/analytics")
async def get_analytics(db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    """Get analytics from database or mock data"""
    if DATABASE_AVAILABLE and db:
        try:
            total_docs = db.query(Document).count()
            minio_docs = db.query(Document).filter(Document.storage_type.in_(["minio", "local_and_minio"])).count()
            
            # Get documents by property
            properties = db.query(Document.property_id).distinct().all()
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
        except Exception as e:
            print(f"ERROR Database analytics failed: {e}")
    
    # Fallback to mock data
    return {
        "total_documents": len(mock_documents),
        "total_properties": len(mock_properties),
        "processing_stats": {
            "uploaded": 0,
            "processed": 0,
            "failed": 0
        },
        "source": "mock_data"
    }

@app.get("/api/kpis/financial")
async def get_financial_kpis():
    """Get Core Financial KPIs - Phase 1 Implementation"""
    try:
        # Connect directly to SQLite to get proper financial data
        import sqlite3
        conn = sqlite3.connect('reims.db')
        cursor = conn.cursor()
        
        # Total Portfolio Value
        cursor.execute('SELECT SUM(current_market_value) FROM properties WHERE current_market_value IS NOT NULL;')
        total_portfolio_value = cursor.fetchone()[0] or 0
        
        # Total Properties Count
        cursor.execute('SELECT COUNT(*) FROM properties;')
        total_properties = cursor.fetchone()[0] or 0
        
        # Monthly Rental Income
        cursor.execute('SELECT SUM(monthly_rent) FROM properties WHERE monthly_rent IS NOT NULL;')
        monthly_rental_income = cursor.fetchone()[0] or 0
        
        # Occupancy Rate (based on status)
        cursor.execute('SELECT COUNT(*) FROM properties WHERE status = "occupied";')
        occupied_properties = cursor.fetchone()[0] or 0
        occupancy_rate = (occupied_properties / total_properties * 100) if total_properties > 0 else 0
        
        # Additional metrics for context
        cursor.execute('SELECT COUNT(*) FROM properties WHERE status = "available";')
        available_properties = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT AVG(monthly_rent) FROM properties WHERE monthly_rent IS NOT NULL;')
        avg_monthly_rent = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT property_type, COUNT(*) FROM properties GROUP BY property_type;')
        property_types = cursor.fetchall()
        
        conn.close()
        
        return {
            "status": "success",
            "source": "database",
            "timestamp": datetime.now().isoformat(),
            "core_kpis": {
                "total_portfolio_value": {
                    "value": total_portfolio_value,
                    "formatted": f"${total_portfolio_value:,.0f}",
                    "currency": "USD"
                },
                "total_properties": {
                    "value": total_properties,
                    "occupied": occupied_properties,
                    "available": available_properties
                },
                "monthly_rental_income": {
                    "value": monthly_rental_income,
                    "formatted": f"${monthly_rental_income:,.0f}",
                    "currency": "USD"
                },
                "occupancy_rate": {
                    "value": occupancy_rate,
                    "formatted": f"{occupancy_rate:.1f}%",
                    "occupied_units": occupied_properties,
                    "total_units": total_properties
                }
            },
            "additional_metrics": {
                "average_monthly_rent": {
                    "value": avg_monthly_rent,
                    "formatted": f"${avg_monthly_rent:,.0f}"
                },
                "property_type_distribution": {
                    prop_type: count for prop_type, count in property_types
                }
            }
        }
        
    except Exception as e:
        print(f"ERROR Financial KPIs calculation failed: {e}")
        # Return mock data as fallback
        return {
            "status": "error_fallback",
            "source": "mock_data",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "core_kpis": {
                "total_portfolio_value": {
                    "value": 47800000,
                    "formatted": "$47,800,000",
                    "currency": "USD"
                },
                "total_properties": {
                    "value": 184,
                    "occupied": 174,
                    "available": 10
                },
                "monthly_rental_income": {
                    "value": 1200000,
                    "formatted": "$1,200,000",
                    "currency": "USD"
                },
                "occupancy_rate": {
                    "value": 94.6,
                    "formatted": "94.6%",
                    "occupied_units": 174,
                    "total_units": 184
                }
            },
            "additional_metrics": {
                "average_monthly_rent": {
                    "value": 6500,
                    "formatted": "$6,500"
                },
                "property_type_distribution": {
                    "residential": 120,
                    "commercial": 45,
                    "industrial": 19
                }
            }
        }

@app.get("/api/documents/property/{property_id}")
async def get_documents_by_property(property_id: str, db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    """Get all documents for a specific property"""
    if DATABASE_AVAILABLE and db:
        try:
            documents = db.query(Document).filter(Document.property_id == property_id).order_by(Document.upload_timestamp.desc()).all()
            
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
        except Exception as e:
            print(f"ERROR Database query failed: {e}")
            return {"error": str(e)}, 500
    
    # Fallback to filtering mock data
    filtered_docs = [doc for doc in mock_documents if doc.get("property_id") == property_id]
    return {
        "documents": filtered_docs, 
        "total": len(filtered_docs),
        "property_id": property_id,
        "source": "mock_data"
    }

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...), 
    property_id: Optional[str] = Form(None),
    document_type: str = Form("financial_statement"),
    db: Session = Depends(get_db) if DATABASE_AVAILABLE else None
):
    """
    Enhanced document upload with MinIO integration and database storage
    
    Args:
        file: The uploaded file
        property_id: Optional property ID. If not provided, auto-generated
        document_type: Type of document being uploaded
        db: Database session
        
    Returns:
        Upload status with document ID and storage locations
    """
    document_id = str(uuid.uuid4())
    
    try:
        # 1. VALIDATION: Check file is valid
        if not file.filename:
            raise HTTPException(status_code=400, detail="Invalid file: No filename provided")
        
        # Validate file extension
        allowed_extensions = {'.pdf', '.xlsx', '.xls', '.csv'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # 2. PROPERTY ID: Generate or validate
        if property_id:
            # Validate provided property_id exists (if database available)
            if DATABASE_AVAILABLE and db:
                try:
                    result = db.execute(
                        text("SELECT id FROM properties WHERE id = :prop_id OR property_code = :prop_id"),
                        {"prop_id": property_id}
                    ).fetchone()
                    
                    if not result:
                        logger.warning(f"Property ID {property_id} not found, creating auto-generated ID")
                        property_id = f"PROP-{uuid.uuid4().hex[:12].upper()}"
                    else:
                        logger.info(f"Using existing property_id: {property_id}")
                except Exception as e:
                    logger.warning(f"Could not validate property_id {property_id}: {e}, using auto-generated")
                    property_id = f"PROP-{uuid.uuid4().hex[:12].upper()}"
        else:
            # Auto-generate UUID-based property_id (collision-resistant)
            property_id = f"PROP-{uuid.uuid4().hex[:12].upper()}"
            logger.info(f"Auto-generated property_id: {property_id}")
        
        # 3. READ FILE CONTENT
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size (50MB max)
        MAX_FILE_SIZE = 50 * 1024 * 1024
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        logger.info(
            f"Upload started - property_id: {property_id}, "
            f"filename: {file.filename}, size: {file_size} bytes"
        )
        
        # 4. STORE LOCALLY
        storage_dir = Path("storage")
        storage_dir.mkdir(exist_ok=True)
        
        # Use original filename only (no UUID prefix)
        stored_filename = file.filename
        file_path = storage_dir / stored_filename
        
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        logger.info(f"File stored locally: {file_path}")
        
        # 5. SAVE METADATA
        metadata = {
            "document_id": document_id,
            "original_filename": file.filename,
            "property_id": property_id,
            "file_size": file_size,
            "content_type": file.content_type or "application/octet-stream",
            "document_type": document_type,
            "upload_timestamp": datetime.now().isoformat(),
            "storage_path": str(file_path),
            "status": "uploaded"
        }
        
        metadata_file = storage_dir / f"{document_id}_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        # 6. UPLOAD TO MINIO
        minio_status = "local_only"
        minio_url = None
        minio_upload_time = None
        object_name = None
        
        if MINIO_AVAILABLE:
            try:
                # Upload to MinIO
                # Auto-detect document type from filename if not properly set
                if document_type not in BUCKET_PATHS or document_type == 'financial_statement':
                    detected_type = detect_document_type_from_filename(file.filename)
                    logger.info(f"Auto-detected document type: {document_type} -> {detected_type}")
                    document_type = detected_type
                
                # Use new bucket organization structure
                object_name = get_minio_path(document_type, stored_filename)
                print(f"DEBUG: document_type={document_type}, stored_filename={stored_filename}, object_name={object_name}")
                
                # Reset file position for MinIO upload
                with open(file_path, "rb") as f:
                    minio_client.put_object(
                        bucket_name,
                        object_name,
                        f,
                        length=file_size,
                        content_type=file.content_type or "application/octet-stream"
                    )
                
                minio_status = "uploaded_to_minio"
                minio_url = f"minio://{bucket_name}/{object_name}"
                minio_upload_time = datetime.now()
                
                logger.info(f"File uploaded to MinIO: {minio_url}")
                
                # Update metadata with MinIO info
                metadata["minio_bucket"] = bucket_name
                metadata["minio_object_name"] = object_name
                metadata["minio_url"] = minio_url
                metadata["storage_type"] = "local_and_minio"
                metadata["minio_upload_timestamp"] = minio_upload_time.isoformat()
                
                # Save updated metadata
                with open(metadata_file, "w") as f:
                    json.dump(metadata, f, indent=2)
                    
            except Exception as e:
                logger.error(f"MinIO upload failed: {e}", exc_info=True)
                minio_status = f"minio_error: {str(e)}"
        else:
            logger.warning("MinIO not available, storing locally only")
        
        # 7. STORE IN DATABASE
        db_status = "no_database"
        if DATABASE_AVAILABLE and db:
            try:
                # Create database record
                db_document = Document(
                    document_id=document_id,
                    original_filename=file.filename,
                    stored_filename=stored_filename,
                    property_id=property_id,
                    file_size=file_size,
                    content_type=file.content_type or "application/octet-stream",
                    file_path=str(file_path),
                    upload_timestamp=datetime.now(),
                    status="uploaded",
                    minio_bucket=bucket_name if MINIO_AVAILABLE and minio_status == "uploaded_to_minio" else None,
                    minio_object_name=object_name if MINIO_AVAILABLE and minio_status == "uploaded_to_minio" else None,
                    minio_url=minio_url,
                    storage_type="local_and_minio" if MINIO_AVAILABLE and minio_status == "uploaded_to_minio" else "local",
                    minio_upload_timestamp=minio_upload_time
                )
                
                db.add(db_document)
                db.commit()
                db.refresh(db_document)
                
                db_status = "stored_in_database"
                logger.info(f"Document stored in database with ID: {document_id}")
                
            except Exception as e:
                logger.error(f"Database storage failed: {e}", exc_info=True)
                db_status = f"database_error: {str(e)}"
                if db:
                    db.rollback()
        
        # 8. QUEUE FOR PROCESSING WITH RQ
        queue_status = "no_queue"
        job_id = None
        if REDIS_AVAILABLE and rq_queue:
            try:
                # Import the worker's process function
                import sys
                sys.path.append('queue_service')
                from simple_worker import process_document
                
                # Prepare metadata in expected format
                # Convert Windows path to Unix path for container
                container_file_path = str(file_path).replace('\\', '/')
                
                job_metadata = {
                    'file_path': container_file_path,
                    'property_id': property_id,
                    'document_type': document_type,
                    'original_filename': file.filename,
                    'minio_bucket': bucket_name if MINIO_AVAILABLE else None,
                    'minio_object_name': object_name if MINIO_AVAILABLE else None
                }
                
                # Enqueue job using RQ with timeout and retry
                job = rq_queue.enqueue(
                    process_document,
                    document_id,
                    job_metadata,
                    job_timeout='10m',  # ✅ 10-minute timeout
                    result_ttl=86400,    # Keep results for 24 hours
                    failure_ttl=604800,  # Keep failed jobs for 7 days
                    retry=Retry(max=3, interval=[60, 300, 900])  # ✅ Retry 3 times with backoff
                )
                
                job_id = job.id
                
                # Update document status to queued
                if DATABASE_AVAILABLE and db:
                    try:
                        db_document.status = "queued"
                        
                        # Create processing job record
                        from backend.database import ProcessingJob
                        db_job = ProcessingJob(
                            job_id=job_id,
                            document_id=document_id,
                            status="queued"
                        )
                        db.add(db_job)
                        db.commit()
                    except Exception as e:
                        logger.warning(f"Failed to update document status: {e}")
                
                queue_status = "queued"
                logger.info(f"Document queued for processing with RQ job ID: {job_id}")
                
            except Exception as e:
                logger.error(f"Failed to queue document: {e}", exc_info=True)
                queue_status = f"queue_error: {str(e)}"
        
        mock_document = {
            "document_id": document_id,
            "original_filename": file.filename,
            "property_id": property_id,
            "file_size": file_size,
            "upload_timestamp": datetime.now().isoformat(),
            "status": "queued" if queue_status == "queued" else "uploaded",
            "storage_path": str(file_path),
            "minio_status": minio_status,
            "minio_url": minio_url if MINIO_AVAILABLE else None,
            "queue_status": queue_status,
            "job_id": job_id
        }
        
        mock_documents.append(mock_document)
        
        # 9. RETURN SUCCESS RESPONSE
        return {
            "data": {
                "document_id": document_id,
                "filename": file.filename,
                "file_size": file_size,
                "status": "queued" if queue_status == "queued" else "uploaded",
                "property_id": property_id,  # Include generated/validated property_id
                "storage_location": str(file_path),
                "minio_location": minio_url if MINIO_AVAILABLE else None,
                "database_status": db_status,
                "queue_status": queue_status,
                "job_id": job_id,
                "message": (
                    f"File uploaded successfully and stored in storage/"
                    f"{' and MinIO bucket ' + bucket_name if MINIO_AVAILABLE and minio_status == 'uploaded_to_minio' else ''}"
                    f"{' and database' if db_status == 'stored_in_database' else ''}"
                ),
                "workflow": {
                    "step_1": "OK File received from frontend",
                    "step_2": "OK Stored locally in storage/",
                    "step_3": "OK Metadata saved as JSON",
                    "step_4": f"OK MinIO integration: {minio_status}" if minio_status == 'uploaded_to_minio' else f"FAIL MinIO integration: {minio_status}",
                    "step_5": f"OK Database storage: {db_status}" if db_status == 'stored_in_database' else f"FAIL Database storage: {db_status}",
                    "step_6": f"OK Queued for processing: {queue_status}" if queue_status == 'queued' else f"FAIL Queue: {queue_status}",
                    "step_7": "OK Ready for worker processing"
                }
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)# Year-based Financial Data Endpoints

@app.get("/api/properties/{property_id}/financials")
async def get_property_financials_by_year(property_id: int, year: Optional[int] = None):
    """Get financial data for a specific property and year"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        import sqlite3
        conn = sqlite3.connect("reims.db")
        cursor = conn.cursor()
        
        if year:
            cursor.execute("""
                SELECT year, current_market_value, monthly_rent, annual_noi, 
                       occupancy_rate, total_units, occupied_units, data_source
                FROM property_financials_history 
                WHERE property_id = ? AND year = ?
                ORDER BY year DESC
            """, (property_id, year))
        else:
            cursor.execute("""
                SELECT year, current_market_value, monthly_rent, annual_noi, 
                       occupancy_rate, total_units, occupied_units, data_source
                FROM property_financials_history 
                WHERE property_id = ?
                ORDER BY year DESC
            """, (property_id,))
        
        records = cursor.fetchall()
        conn.close()
        
        if not records:
            raise HTTPException(status_code=404, detail=f"No financial data found for property {property_id}")
        
        financial_data = []
        for record in records:
            financial_data.append({
                "year": record[0],
                "current_market_value": record[1],
                "monthly_rent": record[2],
                "annual_noi": record[3],
                "occupancy_rate": record[4],
                "total_units": record[5],
                "occupied_units": record[6],
                "data_source": record[7]
            })
        
        return {
            "property_id": property_id,
            "financial_data": financial_data,
            "total_records": len(financial_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting financial data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/properties/{property_id}/financials/compare")
async def compare_property_financials(property_id: int, years: str):
    """Compare financial data across multiple years for a property"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        year_list = [int(y.strip()) for y in years.split(',')]
        
        import sqlite3
        conn = sqlite3.connect("reims.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM properties WHERE id = ?", (property_id,))
        property_name = cursor.fetchone()
        if not property_name:
            raise HTTPException(status_code=404, detail=f"Property {property_id} not found")
        
        placeholders = ','.join(['?' for _ in year_list])
        cursor.execute(f"""
            SELECT year, current_market_value, monthly_rent, annual_noi, 
                   occupancy_rate, total_units, occupied_units, data_source
            FROM property_financials_history 
            WHERE property_id = ? AND year IN ({placeholders})
            ORDER BY year ASC
        """, [property_id] + year_list)
        
        records = cursor.fetchall()
        conn.close()
        
        if not records:
            raise HTTPException(status_code=404, detail=f"No financial data found for property {property_id} in years {years}")
        
        comparison_data = []
        previous_values = {}
        
        for record in records:
            year = record[0]
            current_values = {
                "year": year,
                "current_market_value": record[1],
                "monthly_rent": record[2],
                "annual_noi": record[3],
                "occupancy_rate": record[4],
                "total_units": record[5],
                "occupied_units": record[6],
                "data_source": record[7],
                "changes": {}
            }
            
            if previous_values:
                for key in ['current_market_value', 'monthly_rent', 'annual_noi', 'occupancy_rate']:
                    key_index = ['current_market_value', 'monthly_rent', 'annual_noi', 'occupancy_rate'].index(key) + 1
                    if previous_values[key] is not None and record[key_index] is not None:
                        old_val = previous_values[key]
                        new_val = record[key_index]
                        if old_val != 0:
                            change_pct = ((new_val - old_val) / old_val) * 100
                            current_values["changes"][key] = {
                                "percentage_change": round(change_pct, 2),
                                "absolute_change": new_val - old_val
                            }
            
            comparison_data.append(current_values)
            previous_values = {
                "current_market_value": record[1],
                "monthly_rent": record[2],
                "annual_noi": record[3],
                "occupancy_rate": record[4]
            }
        
        return {
            "property_id": property_id,
            "property_name": property_name[0],
            "comparison_data": comparison_data,
            "years_compared": year_list,
            "total_records": len(comparison_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing financial data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

def extract_year_from_filename(filename):
    """Extract year from filename"""
    import re
    year_match = re.search(r'\b(20\d{2})\b', filename)
    return int(year_match.group(1)) if year_match else None

# Year-based Financial Data Endpoints

@app.get("/api/properties/{property_id}/financials")
async def get_property_financials_by_year(property_id: int, year: Optional[int] = None):
    """Get financial data for a specific property and year"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        import sqlite3
        conn = sqlite3.connect("reims.db")
        cursor = conn.cursor()
        
        if year:
            cursor.execute("""
                SELECT year, current_market_value, monthly_rent, annual_noi, 
                       occupancy_rate, total_units, occupied_units, data_source
                FROM property_financials_history 
                WHERE property_id = ? AND year = ?
                ORDER BY year DESC
            """, (property_id, year))
        else:
            cursor.execute("""
                SELECT year, current_market_value, monthly_rent, annual_noi, 
                       occupancy_rate, total_units, occupied_units, data_source
                FROM property_financials_history 
                WHERE property_id = ?
                ORDER BY year DESC
            """, (property_id,))
        
        records = cursor.fetchall()
        conn.close()
        
        if not records:
            raise HTTPException(status_code=404, detail=f"No financial data found for property {property_id}")
        
        financial_data = []
        for record in records:
            financial_data.append({
                "year": record[0],
                "current_market_value": record[1],
                "monthly_rent": record[2],
                "annual_noi": record[3],
                "occupancy_rate": record[4],
                "total_units": record[5],
                "occupied_units": record[6],
                "data_source": record[7]
            })
        
        return {
            "property_id": property_id,
            "financial_data": financial_data,
            "total_records": len(financial_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting financial data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/properties/{property_id}/financials/compare")
async def compare_property_financials(property_id: int, years: str):
    """Compare financial data across multiple years for a property"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        year_list = [int(y.strip()) for y in years.split(',')]
        
        import sqlite3
        conn = sqlite3.connect("reims.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM properties WHERE id = ?", (property_id,))
        property_name = cursor.fetchone()
        if not property_name:
            raise HTTPException(status_code=404, detail=f"Property {property_id} not found")
        
        placeholders = ','.join(['?' for _ in year_list])
        cursor.execute(f"""
            SELECT year, current_market_value, monthly_rent, annual_noi, 
                   occupancy_rate, total_units, occupied_units, data_source
            FROM property_financials_history 
            WHERE property_id = ? AND year IN ({placeholders})
            ORDER BY year ASC
        """, [property_id] + year_list)
        
        records = cursor.fetchall()
        conn.close()
        
        if not records:
            raise HTTPException(status_code=404, detail=f"No financial data found for property {property_id} in years {years}")
        
        comparison_data = []
        previous_values = {}
        
        for record in records:
            year = record[0]
            current_values = {
                "year": year,
                "current_market_value": record[1],
                "monthly_rent": record[2],
                "annual_noi": record[3],
                "occupancy_rate": record[4],
                "total_units": record[5],
                "occupied_units": record[6],
                "data_source": record[7],
                "changes": {}
            }
            
            if previous_values:
                for key in ['current_market_value', 'monthly_rent', 'annual_noi', 'occupancy_rate']:
                    key_index = ['current_market_value', 'monthly_rent', 'annual_noi', 'occupancy_rate'].index(key) + 1
                    if previous_values[key] is not None and record[key_index] is not None:
                        old_val = previous_values[key]
                        new_val = record[key_index]
                        if old_val != 0:
                            change_pct = ((new_val - old_val) / old_val) * 100
                            current_values["changes"][key] = {
                                "percentage_change": round(change_pct, 2),
                                "absolute_change": new_val - old_val
                            }
            
            comparison_data.append(current_values)
            previous_values = {
                "current_market_value": record[1],
                "monthly_rent": record[2],
                "annual_noi": record[3],
                "occupancy_rate": record[4]
            }
        
        return {
            "property_id": property_id,
            "property_name": property_name[0],
            "comparison_data": comparison_data,
            "years_compared": year_list,
            "total_records": len(comparison_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing financial data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

def extract_year_from_filename(filename):
    """Extract year from filename"""
    import re
    year_match = re.search(r'\b(20\d{2})\b', filename)
    return int(year_match.group(1)) if year_match else None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
