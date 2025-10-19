"""
REIMS Audit Logging Service
Comprehensive audit trail with BR-ID linkage
"""

from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import json
import uuid

from ..models.enhanced_schema import AuditLog, User
from ..database import get_db

class AuditEventType(Enum):
    """Audit event types for comprehensive tracking"""
    # Document Management
    DOCUMENT_UPLOAD = "document_upload"
    DOCUMENT_DELETE = "document_delete"
    DOCUMENT_PROCESS = "document_process"
    
    # Data Extraction
    DATA_EXTRACTION = "data_extraction"
    METRIC_EXTRACTION = "metric_extraction"
    
    # Property Management
    PROPERTY_CREATE = "property_create"
    PROPERTY_UPDATE = "property_update"
    PROPERTY_DELETE = "property_delete"
    
    # Store Management
    STORE_CREATE = "store_create"
    STORE_UPDATE = "store_update"
    STORE_DELETE = "store_delete"
    
    # Alert System
    ALERT_CREATED = "alert_created"
    ALERT_DECISION = "alert_decision"
    ALERT_ESCALATION = "alert_escalation"
    
    # Workflow Management
    WORKFLOW_LOCK = "workflow_lock"
    WORKFLOW_UNLOCK = "workflow_unlock"
    
    # AI Features
    AI_SUMMARIZATION = "ai_summarization"
    AI_ANALYSIS = "ai_analysis"
    AI_RECOMMENDATION = "ai_recommendation"
    
    # Exit Strategy
    EXIT_ANALYSIS = "exit_strategy_analysis"
    EXIT_RECOMMENDATION = "exit_recommendation"
    
    # User Management
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    
    # Data Export
    DATA_EXPORT = "data_export"
    AUDIT_EXPORT = "audit_export"
    
    # System Events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIGURATION_CHANGE = "configuration_change"

class AuditLogger:
    """Comprehensive audit logging service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def log_event(
        self,
        action: str,
        user_id: Optional[str] = None,
        br_id: Optional[str] = None,
        property_id: Optional[str] = None,
        document_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """Log audit event with full traceability"""
        
        event_id = str(uuid.uuid4())
        
        audit_entry = AuditLog(
            id=event_id,
            action=action,
            user_id=user_id,
            br_id=br_id,
            property_id=property_id,
            document_id=document_id,
            details=json.dumps(details) if details else None,
            ip_address=ip_address,
            timestamp=datetime.utcnow(),
            session_id=session_id
        )
        
        self.db.add(audit_entry)
        self.db.commit()
        
        return event_id
    
    async def log_document_upload(
        self,
        user_id: str,
        document_id: str,
        property_id: str,
        filename: str,
        file_size: int,
        ip_address: Optional[str] = None
    ) -> str:
        """Log document upload event"""
        return await self.log_event(
            action=AuditEventType.DOCUMENT_UPLOAD.value,
            user_id=user_id,
            br_id="BR-001",
            property_id=property_id,
            document_id=document_id,
            details={
                "filename": filename,
                "file_size": file_size,
                "event_type": "document_upload"
            },
            ip_address=ip_address
        )
    
    async def log_alert_decision(
        self,
        user_id: str,
        alert_id: str,
        property_id: str,
        decision: str,
        notes: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> str:
        """Log alert decision event"""
        return await self.log_event(
            action=AuditEventType.ALERT_DECISION.value,
            user_id=user_id,
            br_id="BR-003",
            property_id=property_id,
            details={
                "alert_id": alert_id,
                "decision": decision,
                "notes": notes,
                "event_type": "alert_decision"
            },
            ip_address=ip_address
        )
    
    async def log_ai_summarization(
        self,
        user_id: str,
        document_id: str,
        property_id: str,
        confidence: float,
        model_used: str,
        ip_address: Optional[str] = None
    ) -> str:
        """Log AI summarization event"""
        return await self.log_event(
            action=AuditEventType.AI_SUMMARIZATION.value,
            user_id=user_id,
            br_id="BR-012",
            property_id=property_id,
            document_id=document_id,
            details={
                "confidence": confidence,
                "model_used": model_used,
                "event_type": "ai_summarization"
            },
            ip_address=ip_address
        )
    
    async def log_exit_analysis(
        self,
        user_id: str,
        property_id: str,
        recommendation: str,
        confidence: float,
        ip_address: Optional[str] = None
    ) -> str:
        """Log exit strategy analysis event"""
        return await self.log_event(
            action=AuditEventType.EXIT_ANALYSIS.value,
            user_id=user_id,
            br_id="BR-004",
            property_id=property_id,
            details={
                "recommendation": recommendation,
                "confidence": confidence,
                "event_type": "exit_analysis"
            },
            ip_address=ip_address
        )
    
    async def log_user_login(
        self,
        user_id: str,
        username: str,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """Log user login event"""
        return await self.log_event(
            action=AuditEventType.USER_LOGIN.value,
            user_id=user_id,
            details={
                "username": username,
                "event_type": "user_login"
            },
            ip_address=ip_address,
            session_id=session_id
        )
    
    async def get_lineage(
        self,
        document_id: Optional[str] = None,
        property_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get complete audit trail for document or property"""
        
        query = self.db.query(AuditLog).join(User, AuditLog.user_id == User.id, isouter=True)
        
        if document_id:
            query = query.filter(
                (AuditLog.document_id == document_id) |
                (AuditLog.details.like(f'%"document_id":"{document_id}"%'))
            )
        
        if property_id:
            query = query.filter(AuditLog.property_id == property_id)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        results = query.order_by(AuditLog.timestamp.asc()).all()
        
        return [
            {
                "id": str(log.id),
                "action": log.action,
                "user_id": str(log.user_id) if log.user_id else None,
                "username": log.user.username if log.user else None,
                "br_id": log.br_id,
                "property_id": str(log.property_id) if log.property_id else None,
                "document_id": str(log.document_id) if log.document_id else None,
                "details": json.loads(log.details) if log.details else None,
                "ip_address": log.ip_address,
                "timestamp": log.timestamp,
                "session_id": log.session_id
            }
            for log in results
        ]
    
    async def export_audit_bundle(
        self,
        property_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Export audit bundle for regulators/lenders (BR-007)"""
        
        # Get all related audit logs
        audit_logs = await self.get_lineage(
            property_id=property_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get all related documents
        from ..models.enhanced_schema import FinancialDocument
        documents = self.db.query(FinancialDocument).filter(
            FinancialDocument.property_id == property_id,
            FinancialDocument.upload_date.between(start_date, end_date)
        ).all()
        
        # Get all related alerts
        from ..models.enhanced_schema import CommitteeAlert
        alerts = self.db.query(CommitteeAlert).filter(
            CommitteeAlert.property_id == property_id,
            CommitteeAlert.created_at.between(start_date, end_date)
        ).all()
        
        # Compile bundle
        bundle = {
            "property_id": property_id,
            "export_date": datetime.utcnow(),
            "period": {
                "start": start_date,
                "end": end_date
            },
            "audit_logs": audit_logs,
            "documents": [
                {
                    "id": str(doc.id),
                    "document_type": doc.document_type,
                    "upload_date": doc.upload_date,
                    "processing_status": doc.processing_status
                }
                for doc in documents
            ],
            "alerts": [
                {
                    "id": str(alert.id),
                    "metric": alert.metric,
                    "value": float(alert.value),
                    "threshold": float(alert.threshold),
                    "level": alert.level.value,
                    "committee": alert.committee,
                    "status": alert.status.value,
                    "created_at": alert.created_at
                }
                for alert in alerts
            ],
            "lineage": audit_logs
        }
        
        return bundle

# Global audit logger instance
def get_audit_logger(db: Session = Depends(get_db)) -> AuditLogger:
    """Get audit logger instance"""
    return AuditLogger(db)

# Middleware for automatic API request logging
from fastapi import Request
import time

async def audit_middleware(request: Request, call_next):
    """Audit all API requests"""
    start_time = time.time()
    
    # Extract user from token if available
    user_id = None
    if 'authorization' in request.headers:
        try:
            from ..services.auth import auth_service
            token = request.headers['authorization'].replace('Bearer ', '')
            payload = auth_service.verify_token(token)
            user_id = payload.get('user_id')
        except:
            pass
    
    # Process request
    response = await call_next(request)
    
    # Log request
    processing_time = time.time() - start_time
    
    # Get audit logger
    db = next(get_db())
    audit_logger = AuditLogger(db)
    
    await audit_logger.log_event(
        action=f"API_{request.method}_{request.url.path}",
        user_id=user_id,
        details={
            "method": request.method,
            "path": str(request.url.path),
            "query_params": dict(request.query_params),
            "status_code": response.status_code,
            "processing_time": processing_time
        },
        ip_address=request.client.host
    )
    
    return response
