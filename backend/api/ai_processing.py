"""
AI Processing API endpoints for REIMS
Handles document processing with AI agents
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

import logging

# Import the document processor integration
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "agents"))

logger = logging.getLogger(__name__)

try:
    from document_processor_integration import document_processor
    DOCUMENT_PROCESSOR_AVAILABLE = True
except ImportError:
    logger.warning("Document processor not available - running in standalone mode")
    DOCUMENT_PROCESSOR_AVAILABLE = False
    document_processor = None

router = APIRouter(prefix="/ai", tags=["ai"])

class ProcessDocumentRequest(BaseModel):
    document_id: str
    priority: Optional[str] = "normal"

class ProcessingStatusResponse(BaseModel):
    document_id: str
    status: str
    message: Optional[str] = None

@router.post("/process/{document_id}")
async def process_document(document_id: str, background_tasks: BackgroundTasks):
    """
    Start AI processing for a document
    Processing runs in the background
    """
    try:
        # Add processing task to background
        background_tasks.add_task(
            document_processor.process_document_with_ai,
            document_id
        )
        
        return {
            "status": "processing_started",
            "document_id": document_id,
            "message": "Document processing started in background"
        }
        
    except Exception as e:
        logger.error(f"Error starting document processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/process/{document_id}/status")
async def get_processing_status(document_id: str):
    """
    Get processing status and results for a document
    """
    try:
        processed_data = document_processor.get_processed_data(document_id)
        
        if not processed_data:
            return {
                "status": "not_processed",
                "document_id": document_id,
                "message": "Document has not been processed yet"
            }
        
        return {
            "status": processed_data.get("processing_status", "unknown"),
            "document_id": document_id,
            "document_type": processed_data.get("document_type"),
            "confidence_score": processed_data.get("confidence_score"),
            "processing_time_seconds": processed_data.get("processing_time_seconds"),
            "error_message": processed_data.get("error_message"),
            "created_at": processed_data.get("created_at"),
            "updated_at": processed_data.get("updated_at")
        }
        
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/processed-data/{document_id}")
async def get_processed_data(document_id: str):
    """
    Get detailed processed data and insights for a document
    """
    try:
        processed_data = document_processor.get_processed_data(document_id)
        
        if not processed_data:
            raise HTTPException(status_code=404, detail="No processed data found for this document")
        
        if processed_data.get("processing_status") != "success":
            return {
                "status": processed_data.get("processing_status", "unknown"),
                "error_message": processed_data.get("error_message"),
                "document_id": document_id
            }
        
        # Return comprehensive processed data
        return {
            "document_id": document_id,
            "status": "success",
            "document_type": processed_data.get("document_type"),
            "confidence_score": processed_data.get("confidence_score"),
            "extracted_data": processed_data.get("extracted_data", {}),
            "insights": processed_data.get("insights", {}),
            "processing_time_seconds": processed_data.get("processing_time_seconds"),
            "created_at": processed_data.get("created_at"),
            "updated_at": processed_data.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processed data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-all")
async def process_all_documents(background_tasks: BackgroundTasks):
    """
    Start AI processing for all unprocessed documents
    """
    try:
        # Get all documents that haven't been processed
        import sqlite3
        
        conn = sqlite3.connect("reims.db")
        cursor = conn.cursor()
        
        # Find documents without processing records
        cursor.execute("""
            SELECT d.id 
            FROM documents d
            LEFT JOIN processed_data pd ON d.id = pd.document_id
            WHERE pd.document_id IS NULL
        """)
        
        unprocessed_docs = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Add processing tasks for all unprocessed documents
        for doc_id in unprocessed_docs:
            background_tasks.add_task(
                document_processor.process_document_with_ai,
                doc_id
            )
        
        return {
            "status": "batch_processing_started",
            "documents_queued": len(unprocessed_docs),
            "document_ids": unprocessed_docs,
            "message": f"Started processing {len(unprocessed_docs)} documents"
        }
        
    except Exception as e:
        logger.error(f"Error starting batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/processing-stats")
async def get_processing_analytics():
    """
    Get analytics about AI processing performance
    """
    try:
        stats = document_processor.get_processing_statistics()
        
        return {
            "processing_statistics": stats,
            "performance_metrics": {
                "total_processed": stats.get("total_processed", 0),
                "success_rate": stats.get("success_rate", 0.0),
                "average_processing_time": stats.get("average_processing_time", 0.0),
                "average_confidence": stats.get("average_confidence", 0.0)
            },
            "document_type_distribution": stats.get("document_type_distribution", {}),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error getting processing analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/extraction-summary")
async def get_extraction_summary():
    """
    Get summary of data extraction across all processed documents
    """
    try:
        import sqlite3
        import json
        
        conn = sqlite3.connect("reims.db")
        cursor = conn.cursor()
        
        # Get all successful extractions
        cursor.execute("""
            SELECT document_type, extracted_data, confidence_score
            FROM processed_data
            WHERE processing_status = 'success'
            AND extracted_data IS NOT NULL
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Analyze extracted data
        financial_docs = 0
        property_docs = 0
        total_revenue = 0
        total_property_value = 0
        confidence_scores = []
        
        for row in rows:
            doc_type, extracted_json, confidence = row
            confidence_scores.append(confidence or 0)
            
            try:
                extracted_data = json.loads(extracted_json) if extracted_json else {}
                
                if doc_type == "financial_statement":
                    financial_docs += 1
                    financial_metrics = extracted_data.get("financial_metrics", {})
                    revenue = financial_metrics.get("revenue", {})
                    if isinstance(revenue, dict) and "primary_value" in revenue:
                        total_revenue += revenue["primary_value"]
                
                elif doc_type == "property_data":
                    property_docs += 1
                    property_details = extracted_data.get("property_details", {})
                    prop_values = property_details.get("property_values", {})
                    if isinstance(prop_values, dict) and "primary_value" in prop_values:
                        total_property_value += prop_values["primary_value"]
                        
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        return {
            "summary": {
                "total_documents_analyzed": len(rows),
                "financial_documents": financial_docs,
                "property_documents": property_docs,
                "average_confidence": round(avg_confidence, 3)
            },
            "financial_summary": {
                "total_revenue_extracted": total_revenue,
                "financial_documents_count": financial_docs
            },
            "property_summary": {
                "total_property_value_extracted": total_property_value,
                "property_documents_count": property_docs
            },
            "confidence_distribution": {
                "high_confidence": len([c for c in confidence_scores if c > 0.8]),
                "medium_confidence": len([c for c in confidence_scores if 0.5 <= c <= 0.8]),
                "low_confidence": len([c for c in confidence_scores if c < 0.5])
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error getting extraction summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def ai_health_check():
    """
    Health check for AI processing system
    """
    try:
        # Basic health checks
        health_status = {
            "ai_processing": "healthy",
            "database_connection": "unknown",
            "agent_registry": "unknown"
        }
        
        # Test database connection
        try:
            stats = document_processor.get_processing_statistics()
            health_status["database_connection"] = "healthy"
        except Exception:
            health_status["database_connection"] = "unhealthy"
        
        # Test agent registry (simulated)
        try:
            # This would test the actual AI orchestrator when implemented
            health_status["agent_registry"] = "healthy"
        except Exception:
            health_status["agent_registry"] = "unhealthy"
        
        overall_status = "healthy" if all(
            status == "healthy" for status in health_status.values()
        ) else "degraded"
        
        return {
            "status": overall_status,
            "components": health_status,
            "timestamp": "2024-01-01T00:00:00Z"  # Would be actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Error in AI health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }