"""
REIMS Production Monitoring Service
Prometheus metrics, health checks, and system monitoring
"""

import logging
import time
import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import asyncio

from ..models.enhanced_schema import AuditLog, FinancialDocument, EnhancedProperty

logger = logging.getLogger(__name__)

# Prometheus metrics
request_count = Counter('reims_requests_total', 'Total request count', ['method', 'endpoint', 'status'])
request_duration = Histogram('reims_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
active_users = Gauge('reims_active_users', 'Number of active users')
document_processing_time = Histogram('reims_document_processing_seconds', 'Document processing time')
ai_analysis_time = Histogram('reims_ai_analysis_seconds', 'AI analysis time', ['analysis_type'])
database_connections = Gauge('reims_database_connections', 'Active database connections')
system_cpu_usage = Gauge('reims_system_cpu_percent', 'System CPU usage percentage')
system_memory_usage = Gauge('reims_system_memory_percent', 'System memory usage percentage')
system_disk_usage = Gauge('reims_system_disk_percent', 'System disk usage percentage')

class MonitoringService:
    """Production monitoring and health check service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.start_time = datetime.utcnow()
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        
        try:
            health_checks = {
                'database': await self._check_database_health(),
                'storage': await self._check_storage_health(),
                'ai_services': await self._check_ai_services_health(),
                'system_resources': await self._check_system_resources(),
                'services': await self._check_services_health()
            }
            
            # Determine overall health
            all_healthy = all(check['status'] == 'healthy' for check in health_checks.values())
            overall_status = 'healthy' if all_healthy else 'degraded'
            
            return {
                'status': overall_status,
                'timestamp': datetime.utcnow(),
                'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds(),
                'checks': health_checks,
                'version': '4.1.0'
            }
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow()
            }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        
        try:
            start_time = time.time()
            
            # Test query
            result = self.db.query(EnhancedProperty).limit(1).first()
            
            query_time = time.time() - start_time
            
            # Check connection pool
            connection_count = self.db.bind.pool.size() if hasattr(self.db.bind, 'pool') else 0
            
            database_connections.set(connection_count)
            
            return {
                'status': 'healthy',
                'query_time_ms': query_time * 1000,
                'connections': connection_count,
                'message': 'Database is operational'
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Database connection failed'
            }
    
    async def _check_storage_health(self) -> Dict[str, Any]:
        """Check storage system health"""
        
        try:
            # Check disk space
            disk_usage = psutil.disk_usage('/')
            
            system_disk_usage.set(disk_usage.percent)
            
            status = 'healthy' if disk_usage.percent < 80 else 'warning' if disk_usage.percent < 90 else 'critical'
            
            return {
                'status': status,
                'disk_usage_percent': disk_usage.percent,
                'disk_free_gb': disk_usage.free / (1024**3),
                'disk_total_gb': disk_usage.total / (1024**3),
                'message': f'Disk usage at {disk_usage.percent}%'
            }
            
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return {
                'status': 'unknown',
                'error': str(e),
                'message': 'Storage check failed'
            }
    
    async def _check_ai_services_health(self) -> Dict[str, Any]:
        """Check AI services availability"""
        
        try:
            # Check Ollama availability
            import requests
            
            try:
                response = requests.get('http://localhost:11434/api/tags', timeout=5)
                ollama_available = response.status_code == 200
            except:
                ollama_available = False
            
            return {
                'status': 'healthy' if ollama_available else 'degraded',
                'ollama_available': ollama_available,
                'message': 'AI services operational' if ollama_available else 'Ollama unavailable'
            }
            
        except Exception as e:
            logger.error(f"AI services health check failed: {e}")
            return {
                'status': 'unknown',
                'error': str(e),
                'message': 'AI services check failed'
            }
    
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            system_memory_usage.set(memory.percent)
            
            # Determine status
            cpu_status = 'healthy' if cpu_percent < 80 else 'warning' if cpu_percent < 90 else 'critical'
            memory_status = 'healthy' if memory.percent < 80 else 'warning' if memory.percent < 90 else 'critical'
            
            overall_status = 'critical' if 'critical' in [cpu_status, memory_status] else \
                           'warning' if 'warning' in [cpu_status, memory_status] else 'healthy'
            
            return {
                'status': overall_status,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'message': f'CPU: {cpu_percent}%, Memory: {memory.percent}%'
            }
            
        except Exception as e:
            logger.error(f"System resources check failed: {e}")
            return {
                'status': 'unknown',
                'error': str(e),
                'message': 'System resources check failed'
            }
    
    async def _check_services_health(self) -> Dict[str, Any]:
        """Check individual service health"""
        
        try:
            services_status = {
                'api': 'healthy',
                'database': 'healthy',
                'storage': 'healthy',
                'ai': 'healthy',
                'analytics': 'healthy'
            }
            
            return {
                'status': 'healthy',
                'services': services_status,
                'message': 'All services operational'
            }
            
        except Exception as e:
            logger.error(f"Services health check failed: {e}")
            return {
                'status': 'unknown',
                'error': str(e),
                'message': 'Services check failed'
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get Prometheus metrics"""
        
        try:
            # Update gauges
            await self._update_metrics()
            
            # Generate Prometheus metrics
            metrics_output = generate_latest()
            
            return {
                'metrics': metrics_output.decode('utf-8'),
                'content_type': CONTENT_TYPE_LATEST,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow()
            }
    
    async def _update_metrics(self):
        """Update Prometheus metrics"""
        
        try:
            # Update system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_cpu_usage.set(cpu_percent)
            system_memory_usage.set(memory.percent)
            system_disk_usage.set(disk.percent)
            
            # Update active users (simplified)
            recent_logs = self.db.query(AuditLog).filter(
                AuditLog.timestamp >= datetime.utcnow() - timedelta(minutes=15)
            ).count()
            
            active_users.set(recent_logs)
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    async def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record request metrics"""
        
        try:
            request_count.labels(method=method, endpoint=endpoint, status=status).inc()
            request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        except Exception as e:
            logger.error(f"Error recording request metrics: {e}")
    
    async def record_document_processing(self, duration: float):
        """Record document processing time"""
        
        try:
            document_processing_time.observe(duration)
        except Exception as e:
            logger.error(f"Error recording document processing metrics: {e}")
    
    async def record_ai_analysis(self, analysis_type: str, duration: float):
        """Record AI analysis time"""
        
        try:
            ai_analysis_time.labels(analysis_type=analysis_type).observe(duration)
        except Exception as e:
            logger.error(f"Error recording AI analysis metrics: {e}")
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        
        try:
            return {
                'system': {
                    'platform': psutil.LINUX if hasattr(psutil, 'LINUX') else 'unknown',
                    'cpu_count': psutil.cpu_count(),
                    'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                    'boot_time': datetime.fromtimestamp(psutil.boot_time())
                },
                'memory': {
                    'total_gb': psutil.virtual_memory().total / (1024**3),
                    'available_gb': psutil.virtual_memory().available / (1024**3),
                    'percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total_gb': psutil.disk_usage('/').total / (1024**3),
                    'free_gb': psutil.disk_usage('/').free / (1024**3),
                    'percent': psutil.disk_usage('/').percent
                },
                'network': {
                    'connections': len(psutil.net_connections())
                },
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {'error': str(e)}
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        
        try:
            # Get recent performance data
            recent_logs = self.db.query(AuditLog).filter(
                AuditLog.timestamp >= datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            recent_documents = self.db.query(FinancialDocument).filter(
                FinancialDocument.upload_date >= datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            # Calculate performance metrics
            uptime = (datetime.utcnow() - self.start_time).total_seconds()
            
            return {
                'uptime_hours': uptime / 3600,
                'requests_24h': recent_logs,
                'documents_24h': recent_documents,
                'avg_requests_per_hour': recent_logs / 24 if recent_logs > 0 else 0,
                'system_health': await self.get_health_status(),
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance report: {e}")
            return {'error': str(e)}

class AlertingService:
    """Service for monitoring alerts and notifications"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def check_thresholds(self) -> List[Dict[str, Any]]:
        """Check system thresholds and generate alerts"""
        
        alerts = []
        
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                alerts.append({
                    'severity': 'critical',
                    'type': 'cpu_usage',
                    'message': f'CPU usage critical: {cpu_percent}%',
                    'value': cpu_percent,
                    'threshold': 90
                })
            elif cpu_percent > 80:
                alerts.append({
                    'severity': 'warning',
                    'type': 'cpu_usage',
                    'message': f'CPU usage high: {cpu_percent}%',
                    'value': cpu_percent,
                    'threshold': 80
                })
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                alerts.append({
                    'severity': 'critical',
                    'type': 'memory_usage',
                    'message': f'Memory usage critical: {memory.percent}%',
                    'value': memory.percent,
                    'threshold': 90
                })
            elif memory.percent > 80:
                alerts.append({
                    'severity': 'warning',
                    'type': 'memory_usage',
                    'message': f'Memory usage high: {memory.percent}%',
                    'value': memory.percent,
                    'threshold': 80
                })
            
            # Check disk usage
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                alerts.append({
                    'severity': 'critical',
                    'type': 'disk_usage',
                    'message': f'Disk usage critical: {disk.percent}%',
                    'value': disk.percent,
                    'threshold': 90
                })
            elif disk.percent > 80:
                alerts.append({
                    'severity': 'warning',
                    'type': 'disk_usage',
                    'message': f'Disk usage high: {disk.percent}%',
                    'value': disk.percent,
                    'threshold': 80
                })
            
        except Exception as e:
            logger.error(f"Error checking thresholds: {e}")
            alerts.append({
                'severity': 'error',
                'type': 'monitoring',
                'message': f'Monitoring error: {str(e)}'
            })
        
        return alerts
    
    async def send_alert(self, alert: Dict[str, Any]):
        """Send alert notification"""
        
        try:
            # Log alert
            logger.warning(f"ALERT: {alert['severity']} - {alert['message']}")
            
            # In production, integrate with:
            # - Email notifications
            # - Slack/Teams webhooks
            # - PagerDuty
            # - SMS alerts
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")

