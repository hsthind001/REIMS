"""
REIMS Nightly Batch Scheduler Service
Automated scheduling for anomaly detection and maintenance tasks
"""

import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from ..database import get_db
from .anomaly_detection import PropertyAnomalyService, NightlyAnomalyJob
from .audit_log import get_audit_logger
from ..models.enhanced_schema import EnhancedProperty

logger = logging.getLogger(__name__)

class SchedulerService:
    """Nightly batch job scheduler for automated tasks"""
    
    def __init__(self, db: Session):
        self.db = db
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Configure nightly anomaly detection (2 AM daily)
            self.scheduler.add_job(
                self._run_nightly_anomaly_detection,
                trigger=CronTrigger(hour=2, minute=0),
                id='nightly_anomaly_detection',
                name='Nightly Anomaly Detection',
                replace_existing=True,
                misfire_grace_time=3600  # 1 hour grace period
            )
            
            # Configure daily cleanup (3 AM daily)
            self.scheduler.add_job(
                self._run_daily_cleanup,
                trigger=CronTrigger(hour=3, minute=0),
                id='daily_cleanup',
                name='Daily Cleanup Tasks',
                replace_existing=True,
                misfire_grace_time=3600
            )
            
            # Configure weekly reports (Sunday 6 AM)
            self.scheduler.add_job(
                self._run_weekly_reports,
                trigger=CronTrigger(day_of_week='sun', hour=6, minute=0),
                id='weekly_reports',
                name='Weekly Performance Reports',
                replace_existing=True,
                misfire_grace_time=7200
            )
            
            # Configure health check monitoring (every 5 minutes)
            self.scheduler.add_job(
                self._run_health_monitoring,
                trigger='interval',
                minutes=5,
                id='health_monitoring',
                name='Health Check Monitoring',
                replace_existing=True
            )
            
            # Start the scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info("✅ Scheduler started successfully with 4 jobs configured")
            logger.info("   • Nightly Anomaly Detection: Daily at 2:00 AM")
            logger.info("   • Daily Cleanup: Daily at 3:00 AM")
            logger.info("   • Weekly Reports: Sundays at 6:00 AM")
            logger.info("   • Health Monitoring: Every 5 minutes")
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            raise
    
    async def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("✅ Scheduler stopped successfully")
        except Exception as e:
            logger.error(f"❌ Failed to stop scheduler: {e}")
    
    async def _run_nightly_anomaly_detection(self):
        """Run nightly anomaly detection for all properties"""
        logger.info("🔄 Starting nightly anomaly detection...")
        
        try:
            # Get audit logger and anomaly service
            audit_logger = get_audit_logger(self.db)
            nightly_job = NightlyAnomalyJob(self.db, audit_logger)
            
            # Run anomaly detection
            await nightly_job.run_nightly_analysis()
            
            logger.info("✅ Nightly anomaly detection completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Nightly anomaly detection failed: {e}")
    
    async def _run_daily_cleanup(self):
        """Run daily cleanup tasks"""
        logger.info("🔄 Starting daily cleanup tasks...")
        
        try:
            from ..models.enhanced_schema import AuditLog
            from datetime import timedelta
            
            # Clean up old audit logs (older than 90 days)
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            old_logs = self.db.query(AuditLog).filter(
                AuditLog.timestamp < cutoff_date
            ).delete()
            
            self.db.commit()
            
            logger.info(f"✅ Daily cleanup completed: {old_logs} old audit logs removed")
            
        except Exception as e:
            logger.error(f"❌ Daily cleanup failed: {e}")
            self.db.rollback()
    
    async def _run_weekly_reports(self):
        """Generate weekly performance reports"""
        logger.info("🔄 Generating weekly performance reports...")
        
        try:
            from .analytics_engine import AnalyticsEngine
            from .audit_log import get_audit_logger
            
            audit_logger = get_audit_logger(self.db)
            analytics_engine = AnalyticsEngine(self.db, audit_logger)
            
            # Generate portfolio analytics report
            portfolio_report = await analytics_engine.get_portfolio_analytics()
            
            # Log report generation
            await audit_logger.log_event(
                action="WEEKLY_REPORT_GENERATED",
                details={
                    "report_type": "portfolio_analytics",
                    "report_date": datetime.utcnow().isoformat(),
                    "properties_analyzed": portfolio_report.get('portfolio_summary', {}).get('total_properties', 0)
                }
            )
            
            logger.info("✅ Weekly reports generated successfully")
            
        except Exception as e:
            logger.error(f"❌ Weekly report generation failed: {e}")
    
    async def _run_health_monitoring(self):
        """Run periodic health monitoring"""
        try:
            from .monitoring import MonitoringService
            
            monitoring_service = MonitoringService(self.db)
            health_status = await monitoring_service.get_health_status()
            
            # Log if system is unhealthy
            if health_status.get('status') != 'healthy':
                logger.warning(f"⚠️ System health degraded: {health_status.get('status')}")
                
                # Check for critical issues
                from .monitoring import AlertingService
                alerting_service = AlertingService(self.db)
                alerts = await alerting_service.check_thresholds()
                
                # Send alerts for critical issues
                for alert in alerts:
                    if alert.get('severity') == 'critical':
                        await alerting_service.send_alert(alert)
            
        except Exception as e:
            logger.error(f"❌ Health monitoring check failed: {e}")
    
    def get_status(self):
        """Get scheduler status and job information"""
        if not self.is_running:
            return {
                "status": "stopped",
                "jobs": []
            }
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "status": "running",
            "jobs": jobs,
            "job_count": len(jobs)
        }

# Global scheduler instance
_scheduler_instance = None

def get_scheduler(db: Session) -> SchedulerService:
    """Get or create scheduler instance"""
    global _scheduler_instance
    
    if _scheduler_instance is None:
        _scheduler_instance = SchedulerService(db)
    
    return _scheduler_instance

async def start_scheduler(db: Session):
    """Start the global scheduler"""
    scheduler = get_scheduler(db)
    await scheduler.start()

async def stop_scheduler():
    """Stop the global scheduler"""
    global _scheduler_instance
    
    if _scheduler_instance:
        await _scheduler_instance.stop()
        _scheduler_instance = None

