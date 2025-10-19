"""
REIMS Monitoring API
Health checks, metrics, and system monitoring endpoints
"""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from ..database import get_db
from ..models.enhanced_schema import User
from ..services.auth import require_analyst, get_current_user
from ..services.monitoring import MonitoringService, AlertingService

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# Dependency injection
def get_monitoring_service(db: Session = Depends(get_db)) -> MonitoringService:
    return MonitoringService(db)

def get_alerting_service(db: Session = Depends(get_db)) -> AlertingService:
    return AlertingService(db)

@router.get("/health")
async def health_check(
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
):
    """Comprehensive health check endpoint"""
    
    health_status = await monitoring_service.get_health_status()
    
    # Return appropriate status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return Response(
        content=str(health_status),
        status_code=status_code,
        media_type="application/json"
    )

@router.get("/health/live")
async def liveness_probe():
    """Kubernetes liveness probe"""
    return {"status": "alive", "timestamp": datetime.utcnow()}

@router.get("/health/ready")
async def readiness_probe(
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
):
    """Kubernetes readiness probe"""
    
    health_status = await monitoring_service.get_health_status()
    
    if health_status['status'] == 'healthy':
        return {"status": "ready", "timestamp": datetime.utcnow()}
    else:
        return Response(
            content='{"status": "not_ready"}',
            status_code=503,
            media_type="application/json"
        )

@router.get("/metrics")
async def get_prometheus_metrics(
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
):
    """Prometheus metrics endpoint"""
    
    metrics = await monitoring_service.get_metrics()
    
    return Response(
        content=metrics.get('metrics', ''),
        media_type=metrics.get('content_type', 'text/plain')
    )

@router.get("/system-info")
async def get_system_info(
    current_user: User = Depends(require_analyst),
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
):
    """Get detailed system information"""
    
    return await monitoring_service.get_system_info()

@router.get("/performance-report")
async def get_performance_report(
    current_user: User = Depends(require_analyst),
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
):
    """Get comprehensive performance report"""
    
    return await monitoring_service.get_performance_report()

@router.get("/alerts")
async def get_system_alerts(
    current_user: User = Depends(require_analyst),
    alerting_service: AlertingService = Depends(get_alerting_service)
):
    """Get current system alerts"""
    
    alerts = await alerting_service.check_thresholds()
    
    return {
        'alerts': alerts,
        'alert_count': len(alerts),
        'critical_count': len([a for a in alerts if a.get('severity') == 'critical']),
        'warning_count': len([a for a in alerts if a.get('severity') == 'warning']),
        'timestamp': datetime.utcnow()
    }

@router.get("/status")
async def get_system_status(
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
):
    """Get quick system status"""
    
    health_status = await monitoring_service.get_health_status()
    
    return {
        'status': health_status['status'],
        'uptime_seconds': health_status.get('uptime_seconds', 0),
        'version': health_status.get('version', '4.1.0'),
        'timestamp': datetime.utcnow()
    }

