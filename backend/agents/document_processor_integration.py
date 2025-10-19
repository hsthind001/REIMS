"""
Document Processing Integration Module
Connects AI orchestrator with REIMS backend API
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessorIntegration:
    """
    Integrates AI document processing with the REIMS backend
    Handles database updates and API responses
    """
    
    def __init__(self, db_path: str = "reims.db"):
        self.db_path = db_path
        self.storage_path = Path("storage")
        self.storage_path.mkdir(exist_ok=True)
        
        # Initialize database with processed_data table if not exists
        self._init_processed_data_table()
    
    def _init_processed_data_table(self):
        """Initialize the processed_data table for storing AI analysis results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    processing_status TEXT NOT NULL DEFAULT 'pending',
                    document_type TEXT,
                    confidence_score REAL,
                    extracted_data TEXT,  -- JSON blob
                    insights TEXT,        -- JSON blob
                    processing_time_seconds REAL,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Processed data table initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing processed_data table: {e}")
    
    async def process_document_with_ai(self, document_id: str) -> Dict[str, Any]:
        """
        Process a document using AI orchestrator and update database
        """
        try:
            # Get document info from database
            document_info = self._get_document_info(document_id)
            if not document_info:
                return {
                    "status": "error",
                    "message": f"Document {document_id} not found"
                }
            
            # Get file path
            file_path = self.storage_path / f"{document_id}_{document_info['filename']}"
            
            if not file_path.exists():
                return {
                    "status": "error",
                    "message": f"File not found: {file_path}"
                }
            
            # Update status to processing
            self._update_processing_status(document_id, "processing")
            
            # Prepare metadata
            metadata = {
                "document_id": document_id,
                "filename": document_info['filename'],
                "file_size": document_info.get('file_size', 0),
                "upload_date": document_info.get('upload_date'),
                "property_id": document_info.get('property_id')
            }
            
            # Process with AI orchestrator (simulated for now)
            ai_result = await self._simulate_ai_processing(str(file_path), metadata)
            
            # Save results to database
            self._save_processing_results(document_id, ai_result)
            
            return {
                "status": "success",
                "document_id": document_id,
                "processing_result": ai_result
            }
            
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {e}")
            self._update_processing_status(document_id, "error", str(e))
            
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _simulate_ai_processing(self, file_path: str, metadata: Dict) -> Dict[str, Any]:
        """
        Simulate AI processing - will be replaced with actual AI orchestrator
        """
        file_extension = Path(file_path).suffix.lower()
        
        # Simulate different processing results based on file type
        if file_extension == '.pdf':
            return {
                "document_id": metadata["document_id"],
                "processing_status": "success",
                "processing_time_seconds": 2.5,
                "content_type": "pdf",
                "classification": {
                    "primary_classification": "financial_statement",
                    "confidence_score": 0.85,
                    "secondary_classifications": ["income_statement", "cash_flow"]
                },
                "specialized_analysis": {
                    "financial_statement_agent": {
                        "agent": "financial_statement_agent",
                        "extracted_data": {
                            "revenue": {"primary_value": 250000, "currency": "USD", "period": "annual"},
                            "expenses": {"primary_value": 180000, "currency": "USD", "period": "annual"},
                            "net_income": {"primary_value": 70000, "currency": "USD", "period": "annual"},
                            "assets": {"primary_value": 850000, "currency": "USD"},
                            "liabilities": {"primary_value": 320000, "currency": "USD"}
                        },
                        "validation": {
                            "is_valid": True,
                            "confidence_score": 0.82,
                            "validation_errors": []
                        }
                    }
                },
                "synthesis": {
                    "document_type": "financial_statement",
                    "confidence": 0.85,
                    "financial_metrics": {
                        "revenue": {"primary_value": 250000, "currency": "USD", "period": "annual"},
                        "expenses": {"primary_value": 180000, "currency": "USD", "period": "annual"},
                        "net_income": {"primary_value": 70000, "currency": "USD", "period": "annual"}
                    },
                    "property_details": {},
                    "completeness_score": 0.75,
                    "cross_agent_insights": []
                },
                "insights": {
                    "summary": "Financial statement classified with 85% confidence. Data extraction achieved 75% completeness.",
                    "key_findings": ["Financial data successfully extracted and analyzed"],
                    "recommendations": ["High-quality extraction achieved - suitable for automated processing"],
                    "risk_factors": [],
                    "opportunities": ["Financial metrics available for profitability analysis"]
                }
            }
        
        elif file_extension in ['.csv', '.xlsx']:
            return {
                "document_id": metadata["document_id"],
                "processing_status": "success",
                "processing_time_seconds": 1.8,
                "content_type": "tabular",
                "classification": {
                    "primary_classification": "property_data",
                    "confidence_score": 0.78,
                    "secondary_classifications": ["property_listing", "valuation_data"]
                },
                "specialized_analysis": {
                    "property_data_agent": {
                        "agent": "property_data_agent",
                        "extracted_data": {
                            "addresses": [
                                {"street": "123 Main St", "city": "Springfield", "state": "IL", "zip": "62701"}
                            ],
                            "property_values": {"primary_value": 320000, "currency": "USD"},
                            "square_footage": {"value": 1850, "unit": "sqft"},
                            "bedrooms": {"count": 3},
                            "bathrooms": {"count": 2},
                            "property_type": {"type": "Single Family Home"},
                            "price_per_sqft": {"value": 173, "currency": "USD"}
                        },
                        "validation": {
                            "is_valid": True,
                            "confidence_score": 0.75,
                            "validation_errors": []
                        }
                    }
                },
                "synthesis": {
                    "document_type": "property_data",
                    "confidence": 0.78,
                    "financial_metrics": {},
                    "property_details": {
                        "addresses": [
                            {"street": "123 Main St", "city": "Springfield", "state": "IL", "zip": "62701"}
                        ],
                        "property_values": {"primary_value": 320000, "currency": "USD"},
                        "square_footage": {"value": 1850, "unit": "sqft"}
                    },
                    "completeness_score": 0.85,
                    "cross_agent_insights": []
                },
                "insights": {
                    "summary": "Property data classified with 78% confidence. Data extraction achieved 85% completeness.",
                    "key_findings": ["Property characteristics and valuation data identified"],
                    "recommendations": ["High-quality extraction achieved - suitable for automated processing"],
                    "risk_factors": [],
                    "opportunities": ["Property metrics available for market analysis"]
                }
            }
        
        else:
            return {
                "document_id": metadata["document_id"],
                "processing_status": "success",
                "processing_time_seconds": 0.5,
                "content_type": "unknown",
                "classification": {
                    "primary_classification": "unknown",
                    "confidence_score": 0.3,
                    "secondary_classifications": []
                },
                "specialized_analysis": {},
                "synthesis": {
                    "document_type": "unknown",
                    "confidence": 0.3,
                    "financial_metrics": {},
                    "property_details": {},
                    "completeness_score": 0.1
                },
                "insights": {
                    "summary": "Document type could not be determined with confidence.",
                    "key_findings": [],
                    "recommendations": ["Consider manual review due to low classification confidence"],
                    "risk_factors": ["Unknown document type - manual verification recommended"],
                    "opportunities": []
                }
            }
    
    def _get_document_info(self, document_id: str) -> Optional[Dict]:
        """Get document information from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, filename, file_size, upload_date, property_id
                FROM documents 
                WHERE id = ?
            """, (document_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "id": row[0],
                    "filename": row[1],
                    "file_size": row[2],
                    "upload_date": row[3],
                    "property_id": row[4]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting document info: {e}")
            return None
    
    def _update_processing_status(self, document_id: str, status: str, error_message: str = None):
        """Update processing status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if record exists
            cursor.execute("""
                SELECT id FROM processed_data WHERE document_id = ?
            """, (document_id,))
            
            if cursor.fetchone():
                # Update existing record
                cursor.execute("""
                    UPDATE processed_data 
                    SET processing_status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE document_id = ?
                """, (status, error_message, document_id))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO processed_data (document_id, processing_status, error_message)
                    VALUES (?, ?, ?)
                """, (document_id, status, error_message))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating processing status: {e}")
    
    def _save_processing_results(self, document_id: str, ai_result: Dict):
        """Save AI processing results to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract key information
            status = ai_result.get("processing_status", "unknown")
            document_type = ai_result.get("classification", {}).get("primary_classification", "unknown")
            confidence = ai_result.get("classification", {}).get("confidence_score", 0.0)
            processing_time = ai_result.get("processing_time_seconds", 0.0)
            
            # Convert complex data to JSON
            extracted_data = json.dumps(ai_result.get("synthesis", {}))
            insights = json.dumps(ai_result.get("insights", {}))
            
            # Check if record exists
            cursor.execute("""
                SELECT id FROM processed_data WHERE document_id = ?
            """, (document_id,))
            
            if cursor.fetchone():
                # Update existing record
                cursor.execute("""
                    UPDATE processed_data 
                    SET processing_status = ?, document_type = ?, confidence_score = ?,
                        extracted_data = ?, insights = ?, processing_time_seconds = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE document_id = ?
                """, (status, document_type, confidence, extracted_data, insights, 
                     processing_time, document_id))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO processed_data 
                    (document_id, processing_status, document_type, confidence_score,
                     extracted_data, insights, processing_time_seconds)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (document_id, status, document_type, confidence, extracted_data, 
                     insights, processing_time))
            
            conn.commit()
            conn.close()
            logger.info(f"Saved processing results for document {document_id}")
            
        except Exception as e:
            logger.error(f"Error saving processing results: {e}")
    
    def get_processed_data(self, document_id: str) -> Optional[Dict]:
        """Get processed data for a document"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT processing_status, document_type, confidence_score,
                       extracted_data, insights, processing_time_seconds,
                       error_message, created_at, updated_at
                FROM processed_data 
                WHERE document_id = ?
            """, (document_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                result = {
                    "processing_status": row[0],
                    "document_type": row[1],
                    "confidence_score": row[2],
                    "processing_time_seconds": row[5],
                    "error_message": row[6],
                    "created_at": row[7],
                    "updated_at": row[8]
                }
                
                # Parse JSON fields
                try:
                    result["extracted_data"] = json.loads(row[3]) if row[3] else {}
                    result["insights"] = json.loads(row[4]) if row[4] else {}
                except json.JSONDecodeError:
                    result["extracted_data"] = {}
                    result["insights"] = {}
                
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting processed data: {e}")
            return None
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get overall processing statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get basic statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_processed,
                    COUNT(CASE WHEN processing_status = 'success' THEN 1 END) as successful,
                    COUNT(CASE WHEN processing_status = 'error' THEN 1 END) as failed,
                    AVG(processing_time_seconds) as avg_processing_time,
                    AVG(confidence_score) as avg_confidence
                FROM processed_data
            """)
            
            stats = cursor.fetchone()
            
            # Get document type distribution
            cursor.execute("""
                SELECT document_type, COUNT(*) as count
                FROM processed_data
                WHERE processing_status = 'success'
                GROUP BY document_type
                ORDER BY count DESC
            """)
            
            type_distribution = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "total_processed": stats[0] or 0,
                "successful": stats[1] or 0,
                "failed": stats[2] or 0,
                "success_rate": (stats[1] / stats[0]) if stats[0] > 0 else 0.0,
                "average_processing_time": stats[3] or 0.0,
                "average_confidence": stats[4] or 0.0,
                "document_type_distribution": type_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting processing statistics: {e}")
            return {}

# Global processor instance
document_processor = DocumentProcessorIntegration()