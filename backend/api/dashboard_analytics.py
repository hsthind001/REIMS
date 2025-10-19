"""
REIMS Dashboard Analytics API
Comprehensive KPI endpoints for professional dashboard
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, distinct
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, date
import sys
import os
import json

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database import get_db, Document, ProcessingJob, ExtractedData, Analytics, Property
except ImportError:
    from backend.database import get_db, Document, ProcessingJob, ExtractedData, Analytics, Property

router = APIRouter()

@router.get("/api/dashboard/overview")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """Get comprehensive dashboard overview with all key metrics"""
    try:
        # Document metrics
        total_documents = db.query(Document).count()
        minio_stored = db.query(Document).filter(Document.minio_bucket.isnot(None)).count()
        recent_uploads = db.query(Document).filter(
            Document.upload_timestamp >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Processing metrics
        total_jobs = db.query(ProcessingJob).count()
        completed_jobs = db.query(ProcessingJob).filter(ProcessingJob.status == "completed").count()
        failed_jobs = db.query(ProcessingJob).filter(ProcessingJob.status == "failed").count()
        success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        # Storage metrics
        total_storage = db.query(func.sum(Document.file_size)).scalar() or 0
        avg_file_size = total_storage / total_documents if total_documents > 0 else 0
        
        # Property metrics
        try:
            total_properties = db.query(Property).count()
        except Exception:
            # Fallback if Property model doesn't match schema
            total_properties = 0
        
        try:
            unique_property_ids = db.query(distinct(Document.property_id)).count()
        except Exception:
            unique_property_ids = 0
        
        # File type distribution
        file_types = db.query(
            Document.content_type,
            func.count(Document.id).label('count')
        ).group_by(Document.content_type).all()
        
        # Recent activity (last 24 hours)
        today_uploads = db.query(Document).filter(
            Document.upload_timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Processing queue status
        queued_jobs = db.query(ProcessingJob).filter(ProcessingJob.status == "queued").count()
        processing_jobs = db.query(ProcessingJob).filter(ProcessingJob.status == "processing").count()
        
        return {
            "overview": {
                "total_documents": total_documents,
                "minio_stored_documents": minio_stored,
                "total_storage_bytes": int(total_storage),
                "average_file_size_bytes": int(avg_file_size),
                "unique_properties": unique_property_ids,
                "success_rate_percent": round(success_rate, 2)
            },
            "processing": {
                "total_jobs": total_jobs,
                "completed": completed_jobs,
                "failed": failed_jobs,
                "queued": queued_jobs,
                "processing": processing_jobs,
                "success_rate": round(success_rate, 2)
            },
            "activity": {
                "uploads_today": today_uploads,
                "uploads_this_week": recent_uploads
            },
            "file_types": [
                {"type": ft[0], "count": ft[1], "percentage": round(ft[1]/total_documents*100, 1)}
                for ft in file_types
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard overview failed: {str(e)}")

@router.get("/api/dashboard/financial")
async def get_financial_metrics(
    days: int = Query(30, description="Number of days for analysis"),
    db: Session = Depends(get_db)
):
    """Get financial performance metrics"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Calculate storage costs (simulated - $0.50 per GB per month)
        total_storage_gb = (db.query(func.sum(Document.file_size)).scalar() or 0) / (1024**3)
        monthly_storage_cost = total_storage_gb * 0.50
        
        # Processing costs (simulated - $0.10 per successful job)
        completed_jobs = db.query(ProcessingJob).filter(
            and_(
                ProcessingJob.status == "completed",
                ProcessingJob.completed_at >= cutoff_date
            )
        ).count()
        processing_costs = completed_jobs * 0.10
        
        # Upload trends for revenue calculation (simulated)
        daily_uploads = db.query(
            func.date(Document.upload_timestamp).label('date'),
            func.count(Document.id).label('count'),
            func.sum(Document.file_size).label('size')
        ).filter(
            Document.upload_timestamp >= cutoff_date
        ).group_by(func.date(Document.upload_timestamp)).all()
        
        # Calculate trend
        total_value = len(daily_uploads) * 100  # $100 per active day
        
        return {
            "summary": {
                "estimated_monthly_value": round(total_value, 2),
                "storage_costs": round(monthly_storage_cost, 2),
                "processing_costs": round(processing_costs, 2),
                "net_value": round(total_value - monthly_storage_cost - processing_costs, 2),
                "analysis_period_days": days
            },
            "metrics": {
                "total_storage_gb": round(total_storage_gb, 3),
                "completed_processing_jobs": completed_jobs,
                "cost_per_gb": 0.50,
                "cost_per_job": 0.10
            },
            "daily_activity": [
                {
                    "date": str(upload[0]),
                    "uploads": upload[1],
                    "size_bytes": upload[2] or 0,
                    "estimated_value": upload[1] * 5  # $5 per upload
                }
                for upload in daily_uploads
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Financial metrics failed: {str(e)}")

@router.get("/api/dashboard/performance")
async def get_performance_metrics(
    hours: int = Query(24, description="Number of hours for analysis"),
    db: Session = Depends(get_db)
):
    """Get system performance metrics"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Processing performance
        jobs_in_period = db.query(ProcessingJob).filter(
            ProcessingJob.created_at >= cutoff_time
        ).all()
        
        # Calculate average processing time
        completed_jobs_in_period = [
            job for job in jobs_in_period 
            if job.status == "completed" and job.started_at and job.completed_at
        ]
        
        avg_processing_time = 0
        if completed_jobs_in_period:
            total_time = sum(
                (job.completed_at - job.started_at).total_seconds()
                for job in completed_jobs_in_period
            )
            avg_processing_time = total_time / len(completed_jobs_in_period)
        
        # Upload performance
        uploads_in_period = db.query(Document).filter(
            Document.upload_timestamp >= cutoff_time
        ).count()
        
        # Error rates
        failed_jobs_in_period = len([job for job in jobs_in_period if job.status == "failed"])
        error_rate = (failed_jobs_in_period / len(jobs_in_period) * 100) if jobs_in_period else 0
        
        # Hourly breakdown
        hourly_stats = db.query(
            func.extract('hour', Document.upload_timestamp).label('hour'),
            func.count(Document.id).label('uploads')
        ).filter(
            Document.upload_timestamp >= cutoff_time
        ).group_by('hour').all()
        
        return {
            "performance": {
                "average_processing_time_seconds": round(avg_processing_time, 2),
                "uploads_per_hour": round(uploads_in_period / hours, 2),
                "error_rate_percent": round(error_rate, 2),
                "analysis_period_hours": hours
            },
            "current_period": {
                "total_uploads": uploads_in_period,
                "total_jobs": len(jobs_in_period),
                "completed_jobs": len(completed_jobs_in_period),
                "failed_jobs": failed_jobs_in_period
            },
            "hourly_distribution": [
                {"hour": int(hour), "uploads": count}
                for hour, count in hourly_stats
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance metrics failed: {str(e)}")

@router.get("/api/dashboard/properties")
async def get_property_analytics(db: Session = Depends(get_db)):
    """Get property-specific analytics"""
    try:
        # Property distribution
        property_stats = db.query(
            Document.property_id,
            func.count(Document.id).label('document_count'),
            func.sum(Document.file_size).label('total_size'),
            func.min(Document.upload_timestamp).label('first_upload'),
            func.max(Document.upload_timestamp).label('last_upload')
        ).group_by(Document.property_id).all()
        
        # Top properties by document count
        top_properties = sorted(property_stats, key=lambda x: x[1], reverse=True)[:10]
        
        # Property types (if available)
        property_types = db.query(Property.property_type, func.count(Property.id)).group_by(
            Property.property_type
        ).all()
        
        # Recent property activity
        recent_activity = db.query(
            Document.property_id,
            func.count(Document.id).label('uploads')
        ).filter(
            Document.upload_timestamp >= datetime.utcnow() - timedelta(days=7)
        ).group_by(Document.property_id).order_by(func.count(Document.id).desc()).limit(5).all()
        
        return {
            "summary": {
                "total_properties": len(property_stats),
                "total_documents": sum(stat[1] for stat in property_stats),
                "average_documents_per_property": round(
                    sum(stat[1] for stat in property_stats) / len(property_stats), 2
                ) if property_stats else 0
            },
            "top_properties": [
                {
                    "property_id": prop[0],
                    "document_count": prop[1],
                    "total_size_bytes": prop[2] or 0,
                    "first_upload": prop[3].isoformat() if prop[3] else None,
                    "last_upload": prop[4].isoformat() if prop[4] else None,
                    "activity_span_days": (prop[4] - prop[3]).days if prop[3] and prop[4] else 0
                }
                for prop in top_properties
            ],
            "property_types": [
                {"type": ptype[0] or "Unknown", "count": ptype[1]}
                for ptype in property_types
            ],
            "recent_activity": [
                {"property_id": activity[0], "recent_uploads": activity[1]}
                for activity in recent_activity
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Property analytics failed: {str(e)}")

@router.get("/api/dashboard/alerts")
async def get_system_alerts(db: Session = Depends(get_db)):
    """Get system alerts and warnings"""
    try:
        alerts = []
        
        # Check for failed jobs in last 24 hours
        recent_failures = db.query(ProcessingJob).filter(
            and_(
                ProcessingJob.status == "failed",
                ProcessingJob.created_at >= datetime.utcnow() - timedelta(hours=24)
            )
        ).count()
        
        if recent_failures > 0:
            alerts.append({
                "type": "error",
                "priority": "high",
                "title": "Processing Failures Detected",
                "message": f"{recent_failures} processing jobs failed in the last 24 hours",
                "count": recent_failures,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Check for old queued jobs
        old_queued = db.query(ProcessingJob).filter(
            and_(
                ProcessingJob.status == "queued",
                ProcessingJob.created_at <= datetime.utcnow() - timedelta(hours=1)
            )
        ).count()
        
        if old_queued > 0:
            alerts.append({
                "type": "warning",
                "priority": "medium",
                "title": "Stale Queue Items",
                "message": f"{old_queued} jobs have been queued for over 1 hour",
                "count": old_queued,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Check for large files
        large_files = db.query(Document).filter(
            Document.file_size > 10 * 1024 * 1024  # 10MB
        ).count()
        
        if large_files > 0:
            alerts.append({
                "type": "info",
                "priority": "low",
                "title": "Large Files Detected",
                "message": f"{large_files} files are larger than 10MB",
                "count": large_files,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Check storage utilization
        total_storage_mb = (db.query(func.sum(Document.file_size)).scalar() or 0) / (1024 * 1024)
        if total_storage_mb > 1000:  # 1GB threshold
            alerts.append({
                "type": "warning",
                "priority": "medium",
                "title": "High Storage Usage",
                "message": f"Total storage usage: {total_storage_mb:.1f} MB",
                "count": int(total_storage_mb),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return {
            "alerts": alerts,
            "alert_count": len(alerts),
            "last_checked": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System alerts failed: {str(e)}")

@router.get("/api/dashboard/trends")
async def get_trend_analysis(
    days: int = Query(30, description="Number of days for trend analysis"),
    db: Session = Depends(get_db)
):
    """Get trend analysis for key metrics"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Daily upload trends
        daily_trends = db.query(
            func.date(Document.upload_timestamp).label('date'),
            func.count(Document.id).label('uploads'),
            func.sum(Document.file_size).label('total_size'),
            func.avg(Document.file_size).label('avg_size')
        ).filter(
            Document.upload_timestamp >= cutoff_date
        ).group_by(func.date(Document.upload_timestamp)).order_by('date').all()
        
        # Processing success rate trends
        processing_trends = db.query(
            func.date(ProcessingJob.created_at).label('date'),
            func.count(ProcessingJob.id).label('total_jobs'),
            func.sum(func.case([(ProcessingJob.status == 'completed', 1)], else_=0)).label('completed'),
            func.sum(func.case([(ProcessingJob.status == 'failed', 1)], else_=0)).label('failed')
        ).filter(
            ProcessingJob.created_at >= cutoff_date
        ).group_by(func.date(ProcessingJob.created_at)).order_by('date').all()
        
        # Property activity trends
        property_trends = db.query(
            func.date(Document.upload_timestamp).label('date'),
            func.count(func.distinct(Document.property_id)).label('active_properties')
        ).filter(
            Document.upload_timestamp >= cutoff_date
        ).group_by(func.date(Document.upload_timestamp)).order_by('date').all()
        
        return {
            "analysis_period": {
                "days": days,
                "start_date": cutoff_date.date().isoformat(),
                "end_date": datetime.utcnow().date().isoformat()
            },
            "upload_trends": [
                {
                    "date": str(trend[0]),
                    "uploads": trend[1],
                    "total_size_bytes": trend[2] or 0,
                    "average_size_bytes": int(trend[3] or 0)
                }
                for trend in daily_trends
            ],
            "processing_trends": [
                {
                    "date": str(trend[0]),
                    "total_jobs": trend[1],
                    "completed": trend[2],
                    "failed": trend[3],
                    "success_rate": round((trend[2] / trend[1] * 100) if trend[1] > 0 else 0, 2)
                }
                for trend in processing_trends
            ],
            "property_activity": [
                {
                    "date": str(trend[0]),
                    "active_properties": trend[1]
                }
                for trend in property_trends
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")

@router.get("/api/dashboard/real-time")
async def get_real_time_metrics(db: Session = Depends(get_db)):
    """Get real-time system metrics"""
    try:
        now = datetime.utcnow()
        
        # Last hour activity
        last_hour = now - timedelta(hours=1)
        hour_uploads = db.query(Document).filter(Document.upload_timestamp >= last_hour).count()
        hour_jobs = db.query(ProcessingJob).filter(ProcessingJob.created_at >= last_hour).count()
        
        # Last 5 minutes activity
        last_5min = now - timedelta(minutes=5)
        recent_uploads = db.query(Document).filter(Document.upload_timestamp >= last_5min).count()
        recent_jobs = db.query(ProcessingJob).filter(ProcessingJob.created_at >= last_5min).count()
        
        # Current queue status
        queue_status = {
            "queued": db.query(ProcessingJob).filter(ProcessingJob.status == "queued").count(),
            "processing": db.query(ProcessingJob).filter(ProcessingJob.status == "processing").count()
        }
        
        # Latest uploads
        latest_uploads = db.query(Document).order_by(
            Document.upload_timestamp.desc()
        ).limit(5).all()
        
        # Latest completed jobs
        latest_jobs = db.query(ProcessingJob).filter(
            ProcessingJob.status == "completed"
        ).order_by(ProcessingJob.completed_at.desc()).limit(5).all()
        
        return {
            "current_time": now.isoformat(),
            "activity": {
                "last_hour": {
                    "uploads": hour_uploads,
                    "jobs": hour_jobs
                },
                "last_5_minutes": {
                    "uploads": recent_uploads,
                    "jobs": recent_jobs
                }
            },
            "queue_status": queue_status,
            "latest_uploads": [
                {
                    "document_id": doc.document_id,
                    "filename": doc.original_filename,
                    "property_id": doc.property_id,
                    "file_size": doc.file_size,
                    "timestamp": doc.upload_timestamp.isoformat()
                }
                for doc in latest_uploads
            ],
            "latest_completions": [
                {
                    "job_id": job.job_id,
                    "document_id": job.document_id,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "processing_time_seconds": (
                        (job.completed_at - job.started_at).total_seconds()
                        if job.completed_at and job.started_at else None
                    )
                }
                for job in latest_jobs
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Real-time metrics failed: {str(e)}")