"""
REIMS Alert System & Committee Approval Workflow
Implements risk alerts with DSCR/occupancy monitoring and committee approval
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from decimal import Decimal
import asyncio
import logging

from ..models.enhanced_schema import (
    EnhancedProperty, Store, CommitteeAlert, WorkflowLock, 
    AlertLevel, AlertStatus, WorkflowLockStatus, User
)
from .audit_log import AuditLogger, AuditEventType

logger = logging.getLogger(__name__)

class AlertEngine:
    """Main alert engine for risk monitoring"""
    
    def __init__(self, db: Session, audit_logger: AuditLogger):
        self.db = db
        self.audit_logger = audit_logger
        
        # Alert thresholds
        self.thresholds = {
            'dscr_critical': Decimal('1.25'),
            'dscr_warning': Decimal('1.30'),
            'occupancy_critical': Decimal('0.80'),
            'occupancy_warning': Decimal('0.85'),
            'revenue_decline_critical': Decimal('0.15'),  # 15% decline
            'revenue_decline_warning': Decimal('0.10')   # 10% decline
        }
    
    async def check_property_metrics(self, property_id: str) -> List[Dict[str, Any]]:
        """Check all metrics for a property and create alerts"""
        alerts = []
        
        try:
            # Get property with stores
            property_obj = self.db.query(EnhancedProperty).filter(
                EnhancedProperty.id == property_id
            ).first()
            
            if not property_obj:
                logger.warning(f"Property {property_id} not found")
                return alerts
            
            # Check DSCR
            dscr_alerts = await self._check_dscr(property_obj)
            alerts.extend(dscr_alerts)
            
            # Check Occupancy
            occupancy_alerts = await self._check_occupancy(property_obj)
            alerts.extend(occupancy_alerts)
            
            # Check Revenue trends
            revenue_alerts = await self._check_revenue_trends(property_obj)
            alerts.extend(revenue_alerts)
            
            # Send notifications for new alerts
            for alert in alerts:
                if alert.get('is_new', False):
                    await self._send_notification(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking property metrics for {property_id}: {e}")
            return []
    
    async def _check_dscr(self, property_obj: EnhancedProperty) -> List[Dict[str, Any]]:
        """Check DSCR metrics and create alerts if needed"""
        alerts = []
        
        try:
            # Get latest DSCR from extracted metrics
            from ..models.enhanced_schema import ExtractedMetric, FinancialDocument
            
            latest_dscr = self.db.query(ExtractedMetric).join(
                FinancialDocument, ExtractedMetric.document_id == FinancialDocument.id
            ).filter(
                FinancialDocument.property_id == property_obj.id,
                ExtractedMetric.metric_name == 'dscr'
            ).order_by(ExtractedMetric.created_at.desc()).first()
            
            if not latest_dscr:
                return alerts
            
            dscr_value = latest_dscr.metric_value
            
            # Check against thresholds
            if dscr_value < self.thresholds['dscr_critical']:
                alert = await self._create_alert(
                    property_obj=property_obj,
                    metric='dscr',
                    value=dscr_value,
                    threshold=self.thresholds['dscr_critical'],
                    level=AlertLevel.CRITICAL,
                    committee='Finance Sub-Committee'
                )
                alerts.append(alert)
                
                # Lock workflow
                await self._lock_workflow(property_obj.id, alert['alert_id'])
                
            elif dscr_value < self.thresholds['dscr_warning']:
                alert = await self._create_alert(
                    property_obj=property_obj,
                    metric='dscr',
                    value=dscr_value,
                    threshold=self.thresholds['dscr_warning'],
                    level=AlertLevel.WARNING,
                    committee='Finance Sub-Committee'
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error checking DSCR for property {property_obj.id}: {e}")
        
        return alerts
    
    async def _check_occupancy(self, property_obj: EnhancedProperty) -> List[Dict[str, Any]]:
        """Check occupancy metrics and create alerts if needed"""
        alerts = []
        
        try:
            # Calculate occupancy rate
            stores = self.db.query(Store).filter(Store.property_id == property_obj.id).all()
            
            if not stores:
                return alerts
            
            total_units = len(stores)
            occupied_units = len([s for s in stores if s.status.value == 'occupied'])
            occupancy_rate = Decimal(occupied_units) / Decimal(total_units)
            
            # Check against thresholds
            if occupancy_rate < self.thresholds['occupancy_critical']:
                alert = await self._create_alert(
                    property_obj=property_obj,
                    metric='occupancy',
                    value=occupancy_rate,
                    threshold=self.thresholds['occupancy_critical'],
                    level=AlertLevel.CRITICAL,
                    committee='Occupancy Sub-Committee'
                )
                alerts.append(alert)
                
                # Lock workflow
                await self._lock_workflow(property_obj.id, alert['alert_id'])
                
            elif occupancy_rate < self.thresholds['occupancy_warning']:
                alert = await self._create_alert(
                    property_obj=property_obj,
                    metric='occupancy',
                    value=occupancy_rate,
                    threshold=self.thresholds['occupancy_warning'],
                    level=AlertLevel.WARNING,
                    committee='Occupancy Sub-Committee'
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error checking occupancy for property {property_obj.id}: {e}")
        
        return alerts
    
    async def _check_revenue_trends(self, property_obj: EnhancedProperty) -> List[Dict[str, Any]]:
        """Check revenue trends and create alerts if needed"""
        alerts = []
        
        try:
            # Get revenue metrics from last 3 months
            from ..models.enhanced_schema import ExtractedMetric, FinancialDocument
            
            three_months_ago = datetime.utcnow() - timedelta(days=90)
            
            revenue_metrics = self.db.query(ExtractedMetric).join(
                FinancialDocument, ExtractedMetric.document_id == FinancialDocument.id
            ).filter(
                FinancialDocument.property_id == property_obj.id,
                ExtractedMetric.metric_name.in_(['gross_revenue', 'total_revenue']),
                ExtractedMetric.created_at >= three_months_ago
            ).order_by(ExtractedMetric.created_at.desc()).all()
            
            if len(revenue_metrics) < 2:
                return alerts
            
            # Calculate trend
            recent_revenue = revenue_metrics[0].metric_value
            previous_revenue = revenue_metrics[-1].metric_value
            
            if previous_revenue > 0:
                decline_rate = (previous_revenue - recent_revenue) / previous_revenue
                
                if decline_rate >= self.thresholds['revenue_decline_critical']:
                    alert = await self._create_alert(
                        property_obj=property_obj,
                        metric='revenue_decline',
                        value=decline_rate,
                        threshold=self.thresholds['revenue_decline_critical'],
                        level=AlertLevel.CRITICAL,
                        committee='Finance Sub-Committee'
                    )
                    alerts.append(alert)
                    
                elif decline_rate >= self.thresholds['revenue_decline_warning']:
                    alert = await self._create_alert(
                        property_obj=property_obj,
                        metric='revenue_decline',
                        value=decline_rate,
                        threshold=self.thresholds['revenue_decline_warning'],
                        level=AlertLevel.WARNING,
                        committee='Finance Sub-Committee'
                    )
                    alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error checking revenue trends for property {property_obj.id}: {e}")
        
        return alerts
    
    async def _create_alert(
        self,
        property_obj: EnhancedProperty,
        metric: str,
        value: Decimal,
        threshold: Decimal,
        level: AlertLevel,
        committee: str
    ) -> Dict[str, Any]:
        """Create a new alert"""
        
        # Check if similar alert already exists
        existing_alert = self.db.query(CommitteeAlert).filter(
            CommitteeAlert.property_id == property_obj.id,
            CommitteeAlert.metric == metric,
            CommitteeAlert.status == AlertStatus.PENDING
        ).first()
        
        if existing_alert:
            # Update existing alert
            existing_alert.value = value
            existing_alert.threshold = threshold
            existing_alert.level = level
            existing_alert.committee = committee
            self.db.commit()
            
            return {
                'alert_id': str(existing_alert.id),
                'is_new': False,
                'alert': existing_alert
            }
        
        # Create new alert
        alert = CommitteeAlert(
            property_id=property_obj.id,
            metric=metric,
            value=value,
            threshold=threshold,
            level=level,
            committee=committee,
            status=AlertStatus.PENDING
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        # Log audit event
        await self.audit_logger.log_event(
            action=AuditEventType.ALERT_CREATED.value,
            br_id="BR-003",
            property_id=str(property_obj.id),
            details={
                "alert_id": str(alert.id),
                "metric": metric,
                "value": float(value),
                "threshold": float(threshold),
                "level": level.value,
                "committee": committee
            }
        )
        
        return {
            'alert_id': str(alert.id),
            'is_new': True,
            'alert': alert
        }
    
    async def _lock_workflow(self, property_id: str, alert_id: str):
        """Lock workflow for critical alerts"""
        
        # Check if workflow is already locked
        existing_lock = self.db.query(WorkflowLock).filter(
            WorkflowLock.property_id == property_id,
            WorkflowLock.status == WorkflowLockStatus.LOCKED
        ).first()
        
        if existing_lock:
            return
        
        # Create workflow lock
        lock = WorkflowLock(
            property_id=property_id,
            alert_id=alert_id,
            status=WorkflowLockStatus.LOCKED
        )
        
        self.db.add(lock)
        self.db.commit()
        
        # Log audit event
        await self.audit_logger.log_event(
            action=AuditEventType.WORKFLOW_LOCK.value,
            br_id="BR-003",
            property_id=property_id,
            details={
                "alert_id": alert_id,
                "lock_reason": "Critical alert triggered"
            }
        )
    
    async def _send_notification(self, alert_data: Dict[str, Any]):
        """Send notification for new alert"""
        # TODO: Implement notification service (email, Slack, etc.)
        logger.info(f"Alert notification: {alert_data}")
    
    async def approve_alert(
        self,
        alert_id: str,
        user_id: str,
        decision: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Approve or reject an alert"""
        
        alert = self.db.query(CommitteeAlert).filter(
            CommitteeAlert.id == alert_id
        ).first()
        
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")
        
        if alert.status != AlertStatus.PENDING:
            raise ValueError(f"Alert {alert_id} is not pending")
        
        # Update alert status
        alert.status = AlertStatus.APPROVED if decision == 'approved' else AlertStatus.REJECTED
        alert.approved_by = user_id
        alert.approved_at = datetime.utcnow()
        alert.notes = notes
        
        self.db.commit()
        
        # If approved, unlock workflow
        if decision == 'approved':
            await self._unlock_workflow(alert.property_id, alert_id)
        
        # Log audit event
        await self.audit_logger.log_alert_decision(
            user_id=user_id,
            alert_id=alert_id,
            property_id=str(alert.property_id),
            decision=decision,
            notes=notes
        )
        
        return {
            'alert_id': alert_id,
            'status': alert.status.value,
            'approved_by': user_id,
            'approved_at': alert.approved_at,
            'notes': notes
        }
    
    async def _unlock_workflow(self, property_id: str, alert_id: str):
        """Unlock workflow after alert approval"""
        
        lock = self.db.query(WorkflowLock).filter(
            WorkflowLock.property_id == property_id,
            WorkflowLock.alert_id == alert_id,
            WorkflowLock.status == WorkflowLockStatus.LOCKED
        ).first()
        
        if lock:
            lock.status = WorkflowLockStatus.UNLOCKED
            lock.unlocked_at = datetime.utcnow()
            self.db.commit()
            
            # Log audit event
            await self.audit_logger.log_event(
                action=AuditEventType.WORKFLOW_UNLOCK.value,
                br_id="BR-003",
                property_id=property_id,
                details={
                    "alert_id": alert_id,
                    "unlock_reason": "Alert approved"
                }
            )
    
    async def get_pending_alerts(
        self,
        committee: Optional[str] = None,
        property_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get pending alerts for committee approval"""
        
        query = self.db.query(CommitteeAlert).filter(
            CommitteeAlert.status == AlertStatus.PENDING
        )
        
        if committee:
            query = query.filter(CommitteeAlert.committee == committee)
        
        if property_id:
            query = query.filter(CommitteeAlert.property_id == property_id)
        
        alerts = query.all()
        
        return [
            {
                'id': str(alert.id),
                'property_id': str(alert.property_id),
                'metric': alert.metric,
                'value': float(alert.value),
                'threshold': float(alert.threshold),
                'level': alert.level.value,
                'committee': alert.committee,
                'status': alert.status.value,
                'created_at': alert.created_at,
                'property_name': self._get_property_name(alert.property_id)
            }
            for alert in alerts
        ]
    
    def _get_property_name(self, property_id: str) -> str:
        """Get property name for display"""
        property_obj = self.db.query(EnhancedProperty).filter(
            EnhancedProperty.id == property_id
        ).first()
        
        return property_obj.name if property_obj else "Unknown Property"

# Committee Approval Service
class CommitteeApprovalService:
    """Service for committee approval workflow"""
    
    def __init__(self, db: Session, audit_logger: AuditLogger):
        self.db = db
        self.audit_logger = audit_logger
        self.alert_engine = AlertEngine(db, audit_logger)
    
    async def get_committee_dashboard(self, committee: str) -> Dict[str, Any]:
        """Get dashboard data for committee"""
        
        # Get pending alerts
        pending_alerts = await self.alert_engine.get_pending_alerts(committee=committee)
        
        # Get recent decisions
        recent_decisions = self.db.query(CommitteeAlert).filter(
            CommitteeAlert.committee == committee,
            CommitteeAlert.status != AlertStatus.PENDING,
            CommitteeAlert.approved_at >= datetime.utcnow() - timedelta(days=30)
        ).order_by(CommitteeAlert.approved_at.desc()).limit(10).all()
        
        # Get workflow locks
        workflow_locks = self.db.query(WorkflowLock).filter(
            WorkflowLock.status == WorkflowLockStatus.LOCKED
        ).all()
        
        return {
            'committee': committee,
            'pending_alerts': pending_alerts,
            'recent_decisions': [
                {
                    'id': str(alert.id),
                    'property_id': str(alert.property_id),
                    'metric': alert.metric,
                    'decision': alert.status.value,
                    'approved_at': alert.approved_at,
                    'notes': alert.notes
                }
                for alert in recent_decisions
            ],
            'active_locks': len(workflow_locks),
            'total_pending': len(pending_alerts)
        }
    
    async def process_alert_decision(
        self,
        alert_id: str,
        user_id: str,
        decision: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process committee decision on alert"""
        
        return await self.alert_engine.approve_alert(
            alert_id=alert_id,
            user_id=user_id,
            decision=decision,
            notes=notes
        )
