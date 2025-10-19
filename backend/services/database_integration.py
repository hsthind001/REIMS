"""
Database Integration Service for REIMS
Handles storage of processed document data into structured database
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# Database models
try:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent / "backend"))
    
    from database import Document, ProcessingJob, ExtractedData, Property, Analytics, SessionLocal
except ImportError as e:
    print(f"Warning: Database models not available: {e}")
    SessionLocal = None

logger = logging.getLogger(__name__)

class DatabaseIntegrationService:
    """Service for integrating processed document data with the database"""
    
    def __init__(self):
        self.session_factory = SessionLocal
    
    def store_document_metadata(self, document_info: Dict[str, Any]) -> str:
        """Store basic document metadata"""
        if not self.session_factory:
            logger.warning("Database not available")
            return "db_unavailable"
        
        try:
            with self.session_factory() as session:
                doc = Document(
                    document_id=document_info.get("document_id"),
                    original_filename=document_info.get("original_filename"),
                    stored_filename=document_info.get("stored_filename", document_info.get("original_filename")),
                    property_id=document_info.get("property_id", "general"),
                    file_size=document_info.get("file_size", 0),
                    content_type=document_info.get("content_type", "application/octet-stream"),
                    file_path=document_info.get("file_path", ""),
                    upload_timestamp=datetime.fromisoformat(document_info.get("upload_timestamp", datetime.utcnow().isoformat())),
                    status=document_info.get("status", "uploaded")
                )
                
                session.add(doc)
                session.commit()
                logger.info(f"Document metadata stored: {doc.document_id}")
                return doc.document_id
                
        except Exception as e:
            logger.error(f"Error storing document metadata: {e}")
            return None
    
    def store_processing_job(self, job_info: Dict[str, Any]) -> str:
        """Store processing job information"""
        if not self.session_factory:
            return "db_unavailable"
        
        try:
            with self.session_factory() as session:
                job = ProcessingJob(
                    job_id=job_info.get("job_id"),
                    document_id=job_info.get("document_id"),
                    status=job_info.get("status", "queued"),
                    created_at=datetime.utcnow(),
                    processing_result=job_info.get("processing_result")
                )
                
                session.add(job)
                session.commit()
                logger.info(f"Processing job stored: {job.job_id}")
                return job.job_id
                
        except Exception as e:
            logger.error(f"Error storing processing job: {e}")
            return None
    
    def store_extracted_data(self, extraction_result: Dict[str, Any]) -> str:
        """Store AI-extracted data in structured format"""
        if not self.session_factory:
            return "db_unavailable"
        
        try:
            with self.session_factory() as session:
                # Determine data type and metrics
                content_type = extraction_result.get("content_type", "unknown")
                extracted_content = extraction_result.get("extracted_data", {})
                analysis_results = extraction_result.get("analysis", {})
                
                # Extract specific metrics based on content type
                row_count = None
                column_count = None
                sheet_count = None
                page_count = None
                word_count = None
                
                if content_type == "csv":
                    row_count = analysis_results.get("row_count")
                    column_count = analysis_results.get("column_count")
                elif content_type == "excel":
                    sheet_count = extraction_result.get("sheet_count")
                elif content_type == "pdf":
                    page_count = analysis_results.get("page_count")
                    word_count = analysis_results.get("total_words")
                
                extracted_data = ExtractedData(
                    document_id=extraction_result.get("document_id"),
                    data_type=content_type,
                    extracted_content=extracted_content,
                    analysis_results=analysis_results,
                    property_indicators=extraction_result.get("property_indicators", {}),
                    extraction_timestamp=datetime.utcnow(),
                    row_count=row_count,
                    column_count=column_count,
                    sheet_count=sheet_count,
                    page_count=page_count,
                    word_count=word_count
                )
                
                session.add(extracted_data)
                session.commit()
                logger.info(f"Extracted data stored for document: {extracted_data.document_id}")
                return str(extracted_data.id)
                
        except Exception as e:
            logger.error(f"Error storing extracted data: {e}")
            return None
    
    def create_or_update_property(self, property_data: Dict[str, Any]) -> str:
        """Create or update property master record"""
        if not self.session_factory:
            return "db_unavailable"
        
        try:
            with self.session_factory() as session:
                property_id = property_data.get("property_id")
                
                # Check if property already exists
                existing_property = session.query(Property).filter(
                    Property.property_id == property_id
                ).first()
                
                if existing_property:
                    # Update existing property
                    if property_data.get("address"):
                        existing_property.address = property_data["address"]
                    if property_data.get("property_type"):
                        existing_property.property_type = property_data["property_type"]
                    if property_data.get("value"):
                        existing_property.value = property_data["value"]
                    
                    # Merge metadata
                    existing_metadata = existing_property.property_metadata or {}
                    new_metadata = property_data.get("metadata", {})
                    existing_metadata.update(new_metadata)
                    existing_property.property_metadata = existing_metadata
                    existing_property.updated_at = datetime.utcnow()
                    
                    logger.info(f"Property updated: {property_id}")
                    property_record = existing_property
                else:
                    # Create new property
                    property_record = Property(
                        property_id=property_id,
                        address=property_data.get("address"),
                        property_type=property_data.get("property_type"),
                        value=property_data.get("value"),
                        property_metadata=property_data.get("metadata", {}),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(property_record)
                    logger.info(f"New property created: {property_id}")
                
                session.commit()
                return property_record.property_id
                
        except Exception as e:
            logger.error(f"Error creating/updating property: {e}")
            return None
    
    def store_analytics_metrics(self, metrics: List[Dict[str, Any]]) -> int:
        """Store analytics metrics"""
        if not self.session_factory:
            return 0
        
        stored_count = 0
        
        try:
            with self.session_factory() as session:
                for metric in metrics:
                    analytics_record = Analytics(
                        metric_name=metric.get("name"),
                        metric_value=metric.get("value"),
                        metric_date=datetime.fromisoformat(metric.get("date", datetime.utcnow().isoformat())),
                        dimensions=metric.get("dimensions", {})
                    )
                    session.add(analytics_record)
                    stored_count += 1
                
                session.commit()
                logger.info(f"Stored {stored_count} analytics metrics")
                
        except Exception as e:
            logger.error(f"Error storing analytics metrics: {e}")
        
        return stored_count
    
    def process_and_store_document_complete(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Complete processing pipeline - store all data from AI processing"""
        if not self.session_factory:
            return {"status": "error", "message": "Database not available"}
        
        try:
            document_id = processing_result.get("document_id")
            results = {"document_id": document_id, "stored_records": {}}
            
            # 1. Store extracted data
            if "specialized_analysis" in processing_result:
                for agent_name, agent_result in processing_result["specialized_analysis"].items():
                    if "extracted_data" in agent_result:
                        extraction_id = self.store_extracted_data({
                            "document_id": document_id,
                            "content_type": processing_result.get("content_type"),
                            "extracted_data": agent_result["extracted_data"],
                            "analysis": agent_result.get("analysis", {}),
                            "property_indicators": agent_result.get("property_indicators", {})
                        })
                        results["stored_records"][f"{agent_name}_extraction"] = extraction_id
            
            # 2. Process property data if available
            synthesis = processing_result.get("synthesis", {})
            property_details = synthesis.get("property_details", {})
            
            if property_details:
                # Extract property information
                property_data = {
                    "property_id": processing_result.get("metadata", {}).get("property_id", document_id),
                    "metadata": {
                        "source_document": document_id,
                        "extraction_timestamp": datetime.utcnow().isoformat(),
                        "ai_extracted": True
                    }
                }
                
                # Add extracted property attributes
                if "addresses" in property_details:
                    addresses = property_details["addresses"].get("values", [])
                    if addresses:
                        property_data["address"] = addresses[0]
                
                if "property_values" in property_details:
                    values = property_details["property_values"].get("values", [])
                    if values:
                        property_data["value"] = values[0]
                
                if "property_type" in property_details:
                    types = property_details["property_type"].get("values", [])
                    if types:
                        property_data["property_type"] = types[0]
                
                # Add additional metadata
                for key, data in property_details.items():
                    if isinstance(data, dict) and "primary_value" in data:
                        property_data["metadata"][key] = data["primary_value"]
                
                property_id = self.create_or_update_property(property_data)
                results["stored_records"]["property"] = property_id
            
            # 3. Generate and store analytics metrics
            metrics = []
            
            # Document processing metrics
            metrics.append({
                "name": "document_processed",
                "value": 1,
                "date": datetime.utcnow().isoformat(),
                "dimensions": {
                    "document_type": synthesis.get("document_type", "unknown"),
                    "confidence": synthesis.get("confidence", 0.0),
                    "completeness": synthesis.get("completeness_score", 0.0)
                }
            })
            
            # Financial metrics if available
            financial_metrics = synthesis.get("financial_metrics", {})
            for metric_name, metric_data in financial_metrics.items():
                if isinstance(metric_data, dict) and "primary_value" in metric_data:
                    metrics.append({
                        "name": f"financial_{metric_name}",
                        "value": metric_data["primary_value"],
                        "date": datetime.utcnow().isoformat(),
                        "dimensions": {
                            "document_id": document_id,
                            "currency": metric_data.get("currency", "USD")
                        }
                    })
            
            # Property metrics if available
            for metric_name, metric_data in property_details.items():
                if isinstance(metric_data, dict) and "primary_value" in metric_data:
                    if isinstance(metric_data["primary_value"], (int, float)):
                        metrics.append({
                            "name": f"property_{metric_name}",
                            "value": metric_data["primary_value"],
                            "date": datetime.utcnow().isoformat(),
                            "dimensions": {
                                "document_id": document_id,
                                "property_id": property_data.get("property_id", "unknown")
                            }
                        })
            
            analytics_count = self.store_analytics_metrics(metrics)
            results["stored_records"]["analytics_metrics"] = analytics_count
            
            # 4. Update processing job status
            job_info = {
                "job_id": f"ai_processing_{document_id}",
                "document_id": document_id,
                "status": "completed",
                "processing_result": {
                    "ai_analysis": processing_result,
                    "database_storage": results
                }
            }
            job_id = self.store_processing_job(job_info)
            results["stored_records"]["processing_job"] = job_id
            
            results["status"] = "success"
            results["message"] = f"Complete processing stored for document {document_id}"
            
            logger.info(f"Complete document processing stored: {document_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error in complete processing storage: {e}")
            return {
                "status": "error", 
                "message": str(e),
                "document_id": processing_result.get("document_id")
            }
    
    def get_document_analytics(self, property_id: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics dashboard data"""
        if not self.session_factory:
            return {"error": "Database not available"}
        
        try:
            with self.session_factory() as session:
                # Basic counts
                total_documents = session.query(Document).count()
                total_properties = session.query(Property).count()
                total_extractions = session.query(ExtractedData).count()
                
                # Recent activity
                recent_docs = session.query(Document).order_by(
                    Document.upload_timestamp.desc()
                ).limit(5).all()
                
                # Property values if available
                properties_with_values = session.query(Property).filter(
                    Property.value.isnot(None)
                ).all()
                
                total_value = sum(p.value for p in properties_with_values if p.value)
                avg_value = total_value / len(properties_with_values) if properties_with_values else 0
                
                return {
                    "total_documents": total_documents,
                    "total_properties": total_properties,
                    "total_extractions": total_extractions,
                    "total_portfolio_value": total_value,
                    "average_property_value": avg_value,
                    "recent_documents": [
                        {
                            "document_id": doc.document_id,
                            "filename": doc.original_filename,
                            "upload_date": doc.upload_timestamp.isoformat(),
                            "status": doc.status
                        }
                        for doc in recent_docs
                    ],
                    "properties_analyzed": len(properties_with_values)
                }
                
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": str(e)}

# Global service instance
db_integration_service = DatabaseIntegrationService()