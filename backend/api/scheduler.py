"""
REIMS Scheduler API
Manage and monitor scheduled jobs
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..models.enhanced_schema import User
from ..services.auth import require_analyst, get_current_user
from ..services.scheduler import get_scheduler

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

@router.get("/status")
async def get_scheduler_status(
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """Get scheduler status and job information"""
    
    scheduler = get_scheduler(db)
    status = scheduler.get_status()
    
    return {
        **status,
        "timestamp": datetime.utcnow()
    }

@router.post("/start")
async def start_scheduler(
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """Start the scheduler"""
    
    try:
        scheduler = get_scheduler(db)
        await scheduler.start()
        
        return {
            "status": "success",
            "message": "Scheduler started successfully",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")

@router.post("/stop")
async def stop_scheduler_endpoint(
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """Stop the scheduler"""
    
    try:
        scheduler = get_scheduler(db)
        await scheduler.stop()
        
        return {
            "status": "success",
            "message": "Scheduler stopped successfully",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")

@router.get("/jobs")
async def list_scheduled_jobs(
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """List all scheduled jobs"""
    
    scheduler = get_scheduler(db)
    status = scheduler.get_status()
    
    return {
        "jobs": status.get("jobs", []),
        "job_count": status.get("job_count", 0),
        "scheduler_status": status.get("status"),
        "timestamp": datetime.utcnow()
    }


















