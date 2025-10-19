from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List
from datetime import datetime, timedelta
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database import get_db, Document, ProcessingJob, ExtractedData, Analytics

router = APIRouter()

@router.get("/api/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get overall analytics overview"""
    try:
        # Basic counts
        total_documents = db.query(Document).count()
        total_jobs = db.query(ProcessingJob).count()
        total_extracted_records = db.query(ExtractedData).count()
        
        # Job status breakdown
        job_status_counts = db.query(
            ProcessingJob.status, 
            func.count(ProcessingJob.id)
        ).group_by(ProcessingJob.status).all()
        
        # Document status breakdown
        doc_status_counts = db.query(
            Document.status,
            func.count(Document.id)
        ).group_by(Document.status).all()
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_documents = db.query(Document).filter(
            Document.upload_timestamp >= week_ago
        ).count()
        
        # File type breakdown
        file_type_counts = db.query(
            Document.content_type,
            func.count(Document.id)
        ).group_by(Document.content_type).all()
        
        # Property breakdown
        property_counts = db.query(
            Document.property_id,
            func.count(Document.id)
        ).group_by(Document.property_id).all()
        
        return {
            "overview": {
                "total_documents": total_documents,
                "total_jobs": total_jobs,
                "total_extracted_records": total_extracted_records,
                "recent_documents_7d": recent_documents
            },
            "job_status": [{"status": status, "count": count} for status, count in job_status_counts],
            "document_status": [{"status": status, "count": count} for status, count in doc_status_counts],
            "file_types": [{"type": content_type, "count": count} for content_type, count in file_type_counts],
            "properties": [{"property_id": prop_id, "count": count} for prop_id, count in property_counts[:10]]  # Top 10
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics overview failed: {str(e)}")

@router.get("/api/analytics/documents")
async def get_document_analytics(
    property_id: Optional[str] = Query(None),
    days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """Get document analytics with optional filtering"""
    try:
        # Base query
        base_query = db.query(Document)
        
        # Apply filters
        if property_id:
            base_query = base_query.filter(Document.property_id == property_id)
        
        # Date range filter
        if days > 0:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            base_query = base_query.filter(Document.upload_timestamp >= cutoff_date)
        
        # Get documents
        documents = base_query.order_by(Document.upload_timestamp.desc()).all()
        
        # Calculate statistics
        total_size = sum(doc.file_size for doc in documents)
        avg_size = total_size / len(documents) if documents else 0
        
        # Daily upload counts
        daily_counts = db.query(
            func.date(Document.upload_timestamp).label('date'),
            func.count(Document.id).label('count')
        ).filter(
            Document.upload_timestamp >= datetime.utcnow() - timedelta(days=days)
        )
        
        if property_id:
            daily_counts = daily_counts.filter(Document.property_id == property_id)
            
        daily_counts = daily_counts.group_by(
            func.date(Document.upload_timestamp)
        ).order_by('date').all()
        
        return {
            "summary": {
                "total_documents": len(documents),
                "total_size_bytes": total_size,
                "average_size_bytes": int(avg_size),
                "date_range_days": days,
                "property_filter": property_id
            },
            "daily_uploads": [
                {"date": str(date), "count": count} 
                for date, count in daily_counts
            ],
            "recent_documents": [
                {
                    "document_id": doc.document_id,
                    "filename": doc.original_filename,
                    "property_id": doc.property_id,
                    "file_size": doc.file_size,
                    "upload_timestamp": doc.upload_timestamp.isoformat(),
                    "status": doc.status
                }
                for doc in documents[:20]  # Latest 20
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analytics failed: {str(e)}")

@router.get("/api/analytics/processing")
async def get_processing_analytics(
    days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """Get processing job analytics"""
    try:
        # Date range filter
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Job status breakdown
        job_status_counts = db.query(
            ProcessingJob.status,
            func.count(ProcessingJob.id)
        ).filter(
            ProcessingJob.created_at >= cutoff_date
        ).group_by(ProcessingJob.status).all()
        
        # Success rate calculation
        total_jobs = db.query(ProcessingJob).filter(
            ProcessingJob.created_at >= cutoff_date
        ).count()
        
        completed_jobs = db.query(ProcessingJob).filter(
            and_(
                ProcessingJob.created_at >= cutoff_date,
                ProcessingJob.status == "completed"
            )
        ).count()
        
        success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        # Daily processing counts
        daily_processing = db.query(
            func.date(ProcessingJob.created_at).label('date'),
            ProcessingJob.status,
            func.count(ProcessingJob.id).label('count')
        ).filter(
            ProcessingJob.created_at >= cutoff_date
        ).group_by(
            func.date(ProcessingJob.created_at),
            ProcessingJob.status
        ).order_by('date').all()
        
        # Recent failed jobs
        failed_jobs = db.query(ProcessingJob).filter(
            and_(
                ProcessingJob.created_at >= cutoff_date,
                ProcessingJob.status == "failed"
            )
        ).order_by(ProcessingJob.created_at.desc()).limit(10).all()
        
        return {
            "summary": {
                "total_jobs": total_jobs,
                "completed_jobs": completed_jobs,
                "success_rate_percent": round(success_rate, 2),
                "date_range_days": days
            },
            "status_breakdown": [
                {"status": status, "count": count}
                for status, count in job_status_counts
            ],
            "daily_processing": [
                {"date": str(date), "status": status, "count": count}
                for date, status, count in daily_processing
            ],
            "recent_failures": [
                {
                    "job_id": job.job_id,
                    "document_id": job.document_id,
                    "created_at": job.created_at.isoformat(),
                    "error_message": job.error_message
                }
                for job in failed_jobs
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing analytics failed: {str(e)}")

@router.get("/api/analytics/data-insights")
async def get_data_insights(
    property_id: Optional[str] = Query(None),
    data_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get insights from extracted data"""
    try:
        # Base query for extracted data
        base_query = db.query(ExtractedData)
        
        # Apply filters
        if property_id:
            base_query = base_query.join(Document).filter(Document.property_id == property_id)
        
        if data_type:
            base_query = base_query.filter(ExtractedData.data_type == data_type)
        
        # Get data
        extracted_data = base_query.all()
        
        # Data type breakdown
        data_type_counts = db.query(
            ExtractedData.data_type,
            func.count(ExtractedData.id)
        ).group_by(ExtractedData.data_type).all()
        
        # Recent extractions
        recent_extractions = db.query(ExtractedData).order_by(
            ExtractedData.extraction_timestamp.desc()
        ).limit(10).all()
        
        return {
            "summary": {
                "total_extracted_records": len(extracted_data),
                "property_filter": property_id,
                "data_type_filter": data_type
            },
            "data_type_breakdown": [
                {"data_type": dtype, "count": count}
                for dtype, count in data_type_counts
            ],
            "recent_extractions": [
                {
                    "id": str(record.id),
                    "document_id": record.document_id,
                    "data_type": record.data_type,
                    "extraction_timestamp": record.extraction_timestamp.isoformat(),
                    "row_count": record.row_count,
                    "column_count": record.column_count
                }
                for record in recent_extractions
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data insights failed: {str(e)}")