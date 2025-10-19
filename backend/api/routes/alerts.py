"""
Alerts API Routes
Handles committee alerts, approvals, and statistics
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from backend.api.database import get_db

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


# Request models
class ApproveAlertRequest(BaseModel):
    decision: str = "approved"
    user_id: str
    notes: Optional[str] = None


class RejectAlertRequest(BaseModel):
    decision: str = "rejected"
    user_id: str
    reason: str
    notes: Optional[str] = None


@router.get("")
async def get_alerts(
    status: Optional[str] = "pending",
    level: Optional[str] = None,
    committee: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get alerts list with filters
    
    Query Parameters:
    - status: Filter by status ('pending', 'approved', 'rejected')
    - level: Filter by level ('critical', 'warning', 'info')
    - committee: Filter by committee name
    - limit: Maximum number of alerts to return
    
    Returns:
    - alerts: List of alert objects
    - total: Total count
    """
    
    try:
        where_conditions = []
        params = {"limit": limit}
        
        if status:
            where_conditions.append("ca.status = :status")
            params["status"] = status
        
        if level:
            where_conditions.append("ca.level = :level")
            params["level"] = level
        
        if committee:
            where_conditions.append("ca.committee = :committee")
            params["committee"] = committee
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Main query
        results = db.execute(
            text(f"""
                SELECT 
                    ca.id,
                    ca.property_id,
                    p.name as property_name,
                    ca.alert_type,
                    ca.value,
                    ca.threshold,
                    ca.level,
                    ca.committee,
                    ca.status,
                    ca.created_at,
                    ca.approved_at,
                    ca.approved_by,
                    ca.notes,
                    -- Generate description
                    CASE ca.alert_type
                        WHEN 'dscr_low' THEN 'DSCR has fallen below the required threshold of ' || ca.threshold::text
                        WHEN 'occupancy_low' THEN 'Occupancy rate has dropped below ' || (ca.threshold * 100)::text || '%'
                        WHEN 'anomaly_detected' THEN 'Statistical anomaly detected (Z-score: ' || ca.value::text || ')'
                        ELSE 'Alert triggered'
                    END as description
                FROM committee_alerts ca
                JOIN properties p ON p.id = ca.property_id
                {where_clause}
                ORDER BY 
                    CASE ca.level
                        WHEN 'critical' THEN 1
                        WHEN 'warning' THEN 2
                        WHEN 'info' THEN 3
                    END,
                    ca.created_at DESC
                LIMIT :limit
            """),
            params
        ).fetchall()
        
        # Format alerts
        alerts = []
        for row in results:
            alerts.append({
                "id": row.id,
                "property_id": row.property_id,
                "property_name": row.property_name,
                "alert_type": row.alert_type,
                "value": float(row.value) if row.value is not None else None,
                "threshold": float(row.threshold) if row.threshold is not None else None,
                "level": row.level,
                "committee": row.committee,
                "status": row.status,
                "description": row.description,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "approved_at": row.approved_at.isoformat() if row.approved_at else None,
                "approved_by": row.approved_by,
                "notes": row.notes,
            })
        
        return {
            "success": True,
            "data": {
                "alerts": alerts,
                "total": len(alerts)
            }
        }
        
    except Exception as e:
        print(f"Alerts query error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch alerts: {str(e)}"
        )


@router.get("/stats")
async def get_alert_stats(db: Session = Depends(get_db)):
    """
    Get alert statistics
    
    Returns:
    - total_pending: Count of pending alerts
    - total_approved: Count of approved alerts
    - total_rejected: Count of rejected alerts
    - by_level: Breakdown by level
    - by_committee: Breakdown by committee
    - avg_response_time_hours: Average time to decision
    - oldest_pending_days: Age of oldest pending alert
    """
    
    try:
        # Get aggregate statistics
        result = db.execute(
            text("""
                SELECT 
                    COUNT(*) FILTER (WHERE status = 'pending') as total_pending,
                    COUNT(*) FILTER (WHERE status = 'approved') as total_approved,
                    COUNT(*) FILTER (WHERE status = 'rejected') as total_rejected,
                    COUNT(*) FILTER (WHERE level = 'critical' AND status = 'pending') as critical_pending,
                    COUNT(*) FILTER (WHERE level = 'warning' AND status = 'pending') as warning_pending,
                    COUNT(*) FILTER (WHERE level = 'info' AND status = 'pending') as info_pending,
                    AVG(
                        EXTRACT(EPOCH FROM (approved_at - created_at)) / 3600
                    ) FILTER (WHERE approved_at IS NOT NULL) as avg_response_time_hours,
                    MAX(
                        EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400
                    ) FILTER (WHERE status = 'pending') as oldest_pending_days
                FROM committee_alerts
            """)
        ).fetchone()
        
        # Get by committee
        committee_results = db.execute(
            text("""
                SELECT 
                    committee,
                    COUNT(*) as count
                FROM committee_alerts
                WHERE status = 'pending'
                GROUP BY committee
            """)
        ).fetchall()
        
        by_committee = {}
        for row in committee_results:
            by_committee[row.committee] = row.count
        
        return {
            "success": True,
            "data": {
                "total_pending": result.total_pending or 0,
                "total_approved": result.total_approved or 0,
                "total_rejected": result.total_rejected or 0,
                "by_level": {
                    "critical": result.critical_pending or 0,
                    "warning": result.warning_pending or 0,
                    "info": result.info_pending or 0,
                },
                "by_committee": by_committee,
                "avg_response_time_hours": round(float(result.avg_response_time_hours or 0), 2),
                "oldest_pending_days": round(float(result.oldest_pending_days or 0), 1),
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch alert stats: {str(e)}"
        )


@router.post("/{alert_id}/approve")
async def approve_alert(
    alert_id: str,
    request: ApproveAlertRequest,
    db: Session = Depends(get_db)
):
    """
    Approve an alert
    
    Request Body:
    - user_id: User ID making the decision
    - notes: Optional notes
    
    Actions:
    1. Update alert status to 'approved'
    2. Unlock workflow
    3. Update property alert flag
    4. Log audit event
    """
    
    try:
        # Check if alert exists and is pending
        alert_check = db.execute(
            text("""
                SELECT property_id, status
                FROM committee_alerts
                WHERE id = :alert_id
            """),
            {"alert_id": alert_id}
        ).fetchone()
        
        if not alert_check:
            raise HTTPException(
                status_code=404,
                detail=f"Alert {alert_id} not found"
            )
        
        if alert_check.status != 'pending':
            raise HTTPException(
                status_code=400,
                detail=f"Alert is already {alert_check.status}"
            )
        
        property_id = alert_check.property_id
        
        # Update alert
        db.execute(
            text("""
                UPDATE committee_alerts
                SET 
                    status = 'approved',
                    approved_by = :user_id,
                    approved_at = NOW(),
                    notes = :notes
                WHERE id = :alert_id
            """),
            {
                "alert_id": alert_id,
                "user_id": request.user_id,
                "notes": request.notes
            }
        )
        
        # Unlock workflow
        db.execute(
            text("""
                UPDATE workflow_locks
                SET 
                    status = 'unlocked',
                    unlocked_at = NOW()
                WHERE alert_id = :alert_id
            """),
            {"alert_id": alert_id}
        )
        
        # Update property alert flag
        db.execute(
            text("""
                UPDATE properties
                SET has_active_alerts = EXISTS(
                    SELECT 1 FROM committee_alerts
                    WHERE property_id = :property_id AND status = 'pending'
                )
                WHERE id = :property_id
            """),
            {"property_id": property_id}
        )
        
        # Log audit event
        db.execute(
            text("""
                INSERT INTO audit_log (
                    action,
                    user_id,
                    br_id,
                    alert_id,
                    property_id,
                    details,
                    timestamp
                ) VALUES (
                    'ALERT_DECISION',
                    :user_id,
                    'BR-003',
                    :alert_id,
                    :property_id,
                    :details,
                    NOW()
                )
            """),
            {
                "user_id": request.user_id,
                "alert_id": alert_id,
                "property_id": property_id,
                "details": f'{{"decision": "approved", "notes": "{request.notes or ""}"}}'
            }
        )
        
        db.commit()
        
        return {
            "success": True,
            "data": {
                "alert_id": alert_id,
                "status": "approved",
                "approved_at": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to approve alert: {str(e)}"
        )


@router.post("/{alert_id}/reject")
async def reject_alert(
    alert_id: str,
    request: RejectAlertRequest,
    db: Session = Depends(get_db)
):
    """
    Reject an alert
    
    Request Body:
    - user_id: User ID making the decision
    - reason: Reason for rejection (required)
    - notes: Optional additional notes
    
    Actions:
    1. Update alert status to 'rejected'
    2. Unlock workflow
    3. Update property alert flag
    4. Log audit event
    """
    
    try:
        # Check if alert exists and is pending
        alert_check = db.execute(
            text("""
                SELECT property_id, status
                FROM committee_alerts
                WHERE id = :alert_id
            """),
            {"alert_id": alert_id}
        ).fetchone()
        
        if not alert_check:
            raise HTTPException(
                status_code=404,
                detail=f"Alert {alert_id} not found"
            )
        
        if alert_check.status != 'pending':
            raise HTTPException(
                status_code=400,
                detail=f"Alert is already {alert_check.status}"
            )
        
        property_id = alert_check.property_id
        
        # Combine reason and notes
        full_notes = f"Reason: {request.reason}"
        if request.notes:
            full_notes += f"\nNotes: {request.notes}"
        
        # Update alert
        db.execute(
            text("""
                UPDATE committee_alerts
                SET 
                    status = 'rejected',
                    approved_by = :user_id,
                    approved_at = NOW(),
                    notes = :notes
                WHERE id = :alert_id
            """),
            {
                "alert_id": alert_id,
                "user_id": request.user_id,
                "notes": full_notes
            }
        )
        
        # Unlock workflow
        db.execute(
            text("""
                UPDATE workflow_locks
                SET 
                    status = 'unlocked',
                    unlocked_at = NOW()
                WHERE alert_id = :alert_id
            """),
            {"alert_id": alert_id}
        )
        
        # Update property alert flag
        db.execute(
            text("""
                UPDATE properties
                SET has_active_alerts = EXISTS(
                    SELECT 1 FROM committee_alerts
                    WHERE property_id = :property_id AND status = 'pending'
                )
                WHERE id = :property_id
            """),
            {"property_id": property_id}
        )
        
        # Log audit event
        db.execute(
            text("""
                INSERT INTO audit_log (
                    action,
                    user_id,
                    br_id,
                    alert_id,
                    property_id,
                    details,
                    timestamp
                ) VALUES (
                    'ALERT_DECISION',
                    :user_id,
                    'BR-003',
                    :alert_id,
                    :property_id,
                    :details,
                    NOW()
                )
            """),
            {
                "user_id": request.user_id,
                "alert_id": alert_id,
                "property_id": property_id,
                "details": f'{{"decision": "rejected", "reason": "{request.reason}", "notes": "{request.notes or ""}"}}'
            }
        )
        
        db.commit()
        
        return {
            "success": True,
            "data": {
                "alert_id": alert_id,
                "status": "rejected",
                "approved_at": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reject alert: {str(e)}"
        )


@router.get("/property/{property_id}")
async def get_property_alerts(
    property_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get alert history for a specific property
    
    Returns alerts for the specified property, including resolution time
    """
    
    try:
        results = db.execute(
            text("""
                SELECT 
                    ca.id,
                    ca.alert_type,
                    ca.value,
                    ca.threshold,
                    ca.level,
                    ca.committee,
                    ca.status,
                    ca.created_at,
                    ca.approved_at,
                    ca.approved_by,
                    ca.notes,
                    -- Calculate resolution time
                    CASE 
                        WHEN ca.approved_at IS NOT NULL 
                        THEN EXTRACT(EPOCH FROM (ca.approved_at - ca.created_at)) / 3600
                        ELSE NULL
                    END as resolution_time_hours,
                    -- Generate description
                    CASE ca.alert_type
                        WHEN 'dscr_low' THEN 'DSCR below threshold'
                        WHEN 'occupancy_low' THEN 'Low occupancy rate'
                        WHEN 'anomaly_detected' THEN 'Statistical anomaly'
                        ELSE 'Alert'
                    END as description
                FROM committee_alerts ca
                WHERE ca.property_id = :property_id
                ORDER BY ca.created_at DESC
                LIMIT :limit
            """),
            {
                "property_id": property_id,
                "limit": limit
            }
        ).fetchall()
        
        alerts = []
        for row in results:
            alerts.append({
                "id": row.id,
                "alert_type": row.alert_type,
                "value": float(row.value) if row.value is not None else None,
                "threshold": float(row.threshold) if row.threshold is not None else None,
                "level": row.level,
                "committee": row.committee,
                "status": row.status,
                "description": row.description,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "approved_at": row.approved_at.isoformat() if row.approved_at else None,
                "approved_by": row.approved_by,
                "notes": row.notes,
                "resolution_time_hours": round(float(row.resolution_time_hours), 2) if row.resolution_time_hours else None,
            })
        
        return {
            "success": True,
            "data": {
                "property_id": property_id,
                "alerts": alerts,
                "total": len(alerts)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch property alerts: {str(e)}"
        )

