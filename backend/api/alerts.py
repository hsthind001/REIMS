"""
REIMS Alert Management API
Handles alert creation, committee approval, and workflow management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from ..database import get_db
from ..models.enhanced_schema import User, UserRole
from ..services.auth import require_supervisor, require_analyst, get_current_user
from ..services.alert_system import AlertEngine, CommitteeApprovalService
from ..services.audit_log import get_audit_logger, AuditLogger

router = APIRouter(prefix="/alerts", tags=["alerts"])

# Pydantic models
class AlertResponse(BaseModel):
    id: str
    property_id: str
    property_name: str
    metric: str
    value: float
    threshold: float
    level: str
    committee: str
    status: str
    created_at: datetime

class AlertDecisionRequest(BaseModel):
    decision: str  # 'approved' or 'rejected'
    notes: Optional[str] = None

class AlertDecisionResponse(BaseModel):
    alert_id: str
    status: str
    approved_by: str
    approved_at: datetime
    notes: Optional[str] = None

class CommitteeDashboardResponse(BaseModel):
    committee: str
    pending_alerts: List[AlertResponse]
    recent_decisions: List[Dict[str, Any]]
    active_locks: int
    total_pending: int

# Dependency injection
def get_alert_engine(db: Session = Depends(get_db), audit_logger: AuditLogger = Depends(get_audit_logger)) -> AlertEngine:
    return AlertEngine(db, audit_logger)

def get_committee_service(db: Session = Depends(get_db), audit_logger: AuditLogger = Depends(get_audit_logger)) -> CommitteeApprovalService:
    return CommitteeApprovalService(db, audit_logger)

@router.get("/pending", response_model=List[AlertResponse])
async def get_pending_alerts(
    committee: Optional[str] = Query(None, description="Filter by committee"),
    property_id: Optional[str] = Query(None, description="Filter by property"),
    current_user: User = Depends(require_analyst),
    alert_engine: AlertEngine = Depends(get_alert_engine)
):
    """Get alerts requiring committee approval"""
    try:
        alerts = await alert_engine.get_pending_alerts(committee=committee, property_id=property_id)
        
        return [
            AlertResponse(
                id=alert['id'],
                property_id=alert['property_id'],
                property_name=alert['property_name'],
                metric=alert['metric'],
                value=alert['value'],
                threshold=alert['threshold'],
                level=alert['level'],
                committee=alert['committee'],
                status=alert['status'],
                created_at=alert['created_at']
            )
            for alert in alerts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving pending alerts: {str(e)}")

@router.post("/{alert_id}/approve", response_model=AlertDecisionResponse)
async def approve_alert(
    alert_id: str,
    decision_request: AlertDecisionRequest,
    current_user: User = Depends(require_supervisor),
    alert_engine: AlertEngine = Depends(get_alert_engine)
):
    """Committee member approves/rejects alert"""
    try:
        if decision_request.decision not in ['approved', 'rejected']:
            raise HTTPException(status_code=400, detail="Decision must be 'approved' or 'rejected'")
        
        result = await alert_engine.approve_alert(
            alert_id=alert_id,
            user_id=str(current_user.id),
            decision=decision_request.decision,
            notes=decision_request.notes
        )
        
        return AlertDecisionResponse(
            alert_id=result['alert_id'],
            status=result['status'],
            approved_by=result['approved_by'],
            approved_at=result['approved_at'],
            notes=result['notes']
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing alert decision: {str(e)}")

@router.get("/committee/{committee}/dashboard", response_model=CommitteeDashboardResponse)
async def get_committee_dashboard(
    committee: str,
    current_user: User = Depends(require_analyst),
    committee_service: CommitteeApprovalService = Depends(get_committee_service)
):
    """Get committee dashboard with pending alerts and recent decisions"""
    try:
        dashboard_data = await committee_service.get_committee_dashboard(committee)
        
        return CommitteeDashboardResponse(
            committee=dashboard_data['committee'],
            pending_alerts=[
                AlertResponse(
                    id=alert['id'],
                    property_id=alert['property_id'],
                    property_name=alert['property_name'],
                    metric=alert['metric'],
                    value=alert['value'],
                    threshold=alert['threshold'],
                    level=alert['level'],
                    committee=alert['committee'],
                    status=alert['status'],
                    created_at=alert['created_at']
                )
                for alert in dashboard_data['pending_alerts']
            ],
            recent_decisions=dashboard_data['recent_decisions'],
            active_locks=dashboard_data['active_locks'],
            total_pending=dashboard_data['total_pending']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving committee dashboard: {str(e)}")

@router.post("/check-property/{property_id}")
async def check_property_metrics(
    property_id: str,
    current_user: User = Depends(require_analyst),
    alert_engine: AlertEngine = Depends(get_alert_engine)
):
    """Manually trigger metric check for a property"""
    try:
        alerts = await alert_engine.check_property_metrics(property_id)
        
        return {
            "property_id": property_id,
            "alerts_created": len([a for a in alerts if a.get('is_new', False)]),
            "alerts_updated": len([a for a in alerts if not a.get('is_new', False)]),
            "total_alerts": len(alerts),
            "alerts": [
                {
                    "alert_id": alert['alert_id'],
                    "is_new": alert['is_new'],
                    "metric": alert['alert'].metric,
                    "level": alert['alert'].level.value
                }
                for alert in alerts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking property metrics: {str(e)}")

@router.get("/workflow-locks")
async def get_workflow_locks(
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """Get all active workflow locks"""
    try:
        from ..models.enhanced_schema import WorkflowLock, WorkflowLockStatus, EnhancedProperty
        
        locks = db.query(WorkflowLock).join(
            EnhancedProperty, WorkflowLock.property_id == EnhancedProperty.id
        ).filter(
            WorkflowLock.status == WorkflowLockStatus.LOCKED
        ).all()
        
        return [
            {
                "lock_id": str(lock.id),
                "property_id": str(lock.property_id),
                "property_name": lock.property.name,
                "alert_id": str(lock.alert_id),
                "locked_at": lock.locked_at,
                "status": lock.status.value
            }
            for lock in locks
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving workflow locks: {str(e)}")

@router.post("/workflow-locks/{property_id}/unlock")
async def unlock_workflow(
    property_id: str,
    current_user: User = Depends(require_supervisor),
    alert_engine: AlertEngine = Depends(get_alert_engine)
):
    """Manually unlock workflow for a property (supervisor only)"""
    try:
        from ..models.enhanced_schema import WorkflowLock, WorkflowLockStatus
        
        # Find active lock
        lock = alert_engine.db.query(WorkflowLock).filter(
            WorkflowLock.property_id == property_id,
            WorkflowLock.status == WorkflowLockStatus.LOCKED
        ).first()
        
        if not lock:
            raise HTTPException(status_code=404, detail="No active workflow lock found for this property")
        
        # Unlock workflow
        await alert_engine._unlock_workflow(property_id, str(lock.alert_id))
        
        return {
            "property_id": property_id,
            "unlocked_at": datetime.utcnow(),
            "unlocked_by": str(current_user.id),
            "message": "Workflow unlocked successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unlocking workflow: {str(e)}")

@router.get("/statistics")
async def get_alert_statistics(
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """Get alert statistics for dashboard"""
    try:
        from ..models.enhanced_schema import CommitteeAlert, AlertStatus, AlertLevel
        
        # Total alerts by status
        status_counts = db.query(
            CommitteeAlert.status,
            db.func.count(CommitteeAlert.id)
        ).group_by(CommitteeAlert.status).all()
        
        # Alerts by level
        level_counts = db.query(
            CommitteeAlert.level,
            db.func.count(CommitteeAlert.id)
        ).group_by(CommitteeAlert.level).all()
        
        # Alerts by committee
        committee_counts = db.query(
            CommitteeAlert.committee,
            db.func.count(CommitteeAlert.id)
        ).group_by(CommitteeAlert.committee).all()
        
        # Recent alerts (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_alerts = db.query(CommitteeAlert).filter(
            CommitteeAlert.created_at >= thirty_days_ago
        ).count()
        
        return {
            "status_breakdown": {
                status.value: count for status, count in status_counts
            },
            "level_breakdown": {
                level.value: count for level, count in level_counts
            },
            "committee_breakdown": {
                committee: count for committee, count in committee_counts
            },
            "recent_alerts": recent_alerts,
            "total_alerts": sum(count for _, count in status_counts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alert statistics: {str(e)}")
