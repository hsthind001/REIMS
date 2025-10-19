"""
REIMS Anomaly Detection Service
Statistical anomaly detection using Z-score and CUSUM methods
"""

import numpy as np
from scipy import stats
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from decimal import Decimal
import logging
import asyncio

from ..models.enhanced_schema import (
    EnhancedProperty, ExtractedMetric, Anomaly, FinancialDocument
)
from .audit_log import AuditLogger

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Statistical anomaly detection using Z-score and CUSUM methods"""
    
    def __init__(self, z_threshold: float = 2.0, cusum_threshold: float = 5.0):
        self.z_threshold = z_threshold
        self.cusum_threshold = cusum_threshold
    
    def detect_zscore_anomalies(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies using z-score method"""
        
        if len(values) < 3:
            return []
        
        try:
            values_array = np.array(values)
            mean = np.mean(values_array)
            std = np.std(values_array)
            
            if std == 0:
                return []
            
            z_scores = np.abs((values_array - mean) / std)
            anomalies = []
            
            for idx, z_score in enumerate(z_scores):
                if z_score >= self.z_threshold:
                    anomalies.append({
                        'metric_name': metric_name,
                        'timestamp': timestamps[idx],
                        'value': values[idx],
                        'z_score': float(z_score),
                        'mean': float(mean),
                        'std': float(std),
                        'detection_method': 'z-score',
                        'confidence': min(z_score / 3.0, 0.99)
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error in z-score detection: {e}")
            return []
    
    def detect_cusum_trends(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime]
    ) -> List[Dict[str, Any]]:
        """Detect trend shifts using CUSUM"""
        
        if len(values) < 5:
            return []
        
        try:
            values_array = np.array(values)
            mean = np.mean(values_array)
            
            # Calculate CUSUM
            cusum_pos = np.zeros(len(values))
            cusum_neg = np.zeros(len(values))
            
            for i in range(1, len(values)):
                cusum_pos[i] = max(0, cusum_pos[i-1] + values[i] - mean)
                cusum_neg[i] = min(0, cusum_neg[i-1] + values[i] - mean)
            
            anomalies = []
            
            for idx in range(len(values)):
                if (abs(cusum_pos[idx]) > self.cusum_threshold or 
                    abs(cusum_neg[idx]) > self.cusum_threshold):
                    
                    cusum_value = max(abs(cusum_pos[idx]), abs(cusum_neg[idx]))
                    trend_direction = 'upward' if cusum_pos[idx] > abs(cusum_neg[idx]) else 'downward'
                    
                    anomalies.append({
                        'metric_name': metric_name,
                        'timestamp': timestamps[idx],
                        'value': values[idx],
                        'cusum_value': float(cusum_value),
                        'detection_method': 'cusum',
                        'trend_direction': trend_direction,
                        'confidence': min(cusum_value / 10.0, 0.99)
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error in CUSUM detection: {e}")
            return []

class PropertyAnomalyService:
    """Service for property-specific anomaly detection"""
    
    def __init__(self, db: Session, audit_logger: AuditLogger):
        self.db = db
        self.audit_logger = audit_logger
        self.detector = AnomalyDetector()
    
    async def analyze_property(
        self,
        property_id: str,
        property_class: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Analyze all metrics for a property and detect anomalies"""
        
        try:
            # Get historical data for the property
            metrics_data = await self._get_metric_history(property_id, lookback_months=12)
            
            if not metrics_data:
                logger.warning(f"No metric data found for property {property_id}")
                return []
            
            all_anomalies = []
            
            # Analyze each metric
            for metric_name, data in metrics_data.items():
                if len(data) < 3:  # Need at least 3 data points
                    continue
                
                values = [d['value'] for d in data]
                timestamps = [d['timestamp'] for d in data]
                
                # Z-score detection
                z_anomalies = self.detector.detect_zscore_anomalies(
                    metric_name, values, timestamps
                )
                
                # CUSUM detection
                cusum_anomalies = self.detector.detect_cusum_trends(
                    metric_name, values, timestamps
                )
                
                # Combine anomalies
                metric_anomalies = z_anomalies + cusum_anomalies
                
                # Store anomalies in database
                for anomaly in metric_anomalies:
                    await self._store_anomaly(property_id, anomaly)
                
                all_anomalies.extend(metric_anomalies)
            
            # Log analysis completion
            await self.audit_logger.log_event(
                action="ANOMALY_ANALYSIS",
                property_id=property_id,
                details={
                    "anomalies_found": len(all_anomalies),
                    "metrics_analyzed": len(metrics_data),
                    "property_class": property_class
                }
            )
            
            return all_anomalies
            
        except Exception as e:
            logger.error(f"Error analyzing property {property_id}: {e}")
            return []
    
    async def _get_metric_history(
        self,
        property_id: str,
        lookback_months: int = 12
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get historical metric data for a property"""
        
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=lookback_months * 30)
            
            # Get metrics from database
            metrics = self.db.query(ExtractedMetric).join(
                FinancialDocument, ExtractedMetric.document_id == FinancialDocument.id
            ).filter(
                FinancialDocument.property_id == property_id,
                ExtractedMetric.created_at >= start_date
            ).order_by(ExtractedMetric.created_at.asc()).all()
            
            # Group by metric name
            metrics_data = {}
            for metric in metrics:
                metric_name = metric.metric_name
                if metric_name not in metrics_data:
                    metrics_data[metric_name] = []
                
                metrics_data[metric_name].append({
                    'value': float(metric.metric_value),
                    'timestamp': metric.created_at,
                    'confidence': float(metric.confidence_score)
                })
            
            return metrics_data
            
        except Exception as e:
            logger.error(f"Error getting metric history: {e}")
            return {}
    
    async def _store_anomaly(self, property_id: str, anomaly: Dict[str, Any]):
        """Store anomaly in database"""
        
        try:
            anomaly_record = Anomaly(
                property_id=property_id,
                metric_name=anomaly['metric_name'],
                timestamp=anomaly['timestamp'],
                value=anomaly['value'],
                z_score=anomaly.get('z_score'),
                cusum_value=anomaly.get('cusum_value'),
                detection_method=anomaly['detection_method'],
                confidence=anomaly['confidence'],
                trend_direction=anomaly.get('trend_direction')
            )
            
            self.db.add(anomaly_record)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error storing anomaly: {e}")
    
    async def get_property_anomalies(
        self,
        property_id: str,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Get recent anomalies for a property"""
        
        try:
            start_date = datetime.utcnow() - timedelta(days=days_back)
            
            anomalies = self.db.query(Anomaly).filter(
                Anomaly.property_id == property_id,
                Anomaly.created_at >= start_date
            ).order_by(Anomaly.created_at.desc()).all()
            
            return [
                {
                    'id': str(anomaly.id),
                    'metric_name': anomaly.metric_name,
                    'timestamp': anomaly.timestamp,
                    'value': float(anomaly.value),
                    'z_score': float(anomaly.z_score) if anomaly.z_score else None,
                    'cusum_value': float(anomaly.cusum_value) if anomaly.cusum_value else None,
                    'detection_method': anomaly.detection_method,
                    'confidence': float(anomaly.confidence),
                    'trend_direction': anomaly.trend_direction,
                    'created_at': anomaly.created_at
                }
                for anomaly in anomalies
            ]
            
        except Exception as e:
            logger.error(f"Error getting property anomalies: {e}")
            return []
    
    async def get_anomaly_statistics(
        self,
        property_id: Optional[str] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get anomaly statistics"""
        
        try:
            start_date = datetime.utcnow() - timedelta(days=days_back)
            
            query = self.db.query(Anomaly).filter(Anomaly.created_at >= start_date)
            
            if property_id:
                query = query.filter(Anomaly.property_id == property_id)
            
            anomalies = query.all()
            
            if not anomalies:
                return {
                    'total_anomalies': 0,
                    'by_method': {},
                    'by_metric': {},
                    'by_confidence': {'high': 0, 'medium': 0, 'low': 0}
                }
            
            # Calculate statistics
            by_method = {}
            by_metric = {}
            by_confidence = {'high': 0, 'medium': 0, 'low': 0}
            
            for anomaly in anomalies:
                # By method
                method = anomaly.detection_method
                by_method[method] = by_method.get(method, 0) + 1
                
                # By metric
                metric = anomaly.metric_name
                by_metric[metric] = by_metric.get(metric, 0) + 1
                
                # By confidence
                confidence = float(anomaly.confidence)
                if confidence >= 0.8:
                    by_confidence['high'] += 1
                elif confidence >= 0.6:
                    by_confidence['medium'] += 1
                else:
                    by_confidence['low'] += 1
            
            return {
                'total_anomalies': len(anomalies),
                'by_method': by_method,
                'by_metric': by_metric,
                'by_confidence': by_confidence,
                'date_range': {
                    'start': start_date,
                    'end': datetime.utcnow()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting anomaly statistics: {e}")
            return {}

class NightlyAnomalyJob:
    """Nightly batch job for anomaly detection"""
    
    def __init__(self, db: Session, audit_logger: AuditLogger):
        self.db = db
        self.audit_logger = audit_logger
        self.anomaly_service = PropertyAnomalyService(db, audit_logger)
    
    async def run_nightly_analysis(self):
        """Run nightly anomaly detection for all properties"""
        
        logger.info("Starting nightly anomaly detection")
        
        try:
            # Get all active properties
            properties = self.db.query(EnhancedProperty).all()
            
            total_anomalies = 0
            properties_analyzed = 0
            
            for property_obj in properties:
                try:
                    anomalies = await self.anomaly_service.analyze_property(
                        str(property_obj.id),
                        property_obj.property_class
                    )
                    
                    total_anomalies += len(anomalies)
                    properties_analyzed += 1
                    
                    if anomalies:
                        logger.info(f"Found {len(anomalies)} anomalies for property {property_obj.name}")
                        
                        # Send notification for critical anomalies
                        critical_anomalies = [
                            a for a in anomalies 
                            if a.get('confidence', 0) >= 0.8
                        ]
                        
                        if critical_anomalies:
                            await self._send_anomaly_notification(
                                property_obj, critical_anomalies
                            )
                
                except Exception as e:
                    logger.error(f"Error analyzing property {property_obj.id}: {e}")
            
            # Log completion
            await self.audit_logger.log_event(
                action="NIGHTLY_ANOMALY_ANALYSIS",
                details={
                    "properties_analyzed": properties_analyzed,
                    "total_anomalies": total_anomalies,
                    "analysis_date": datetime.utcnow()
                }
            )
            
            logger.info(f"Completed nightly anomaly detection: {total_anomalies} anomalies found across {properties_analyzed} properties")
            
        except Exception as e:
            logger.error(f"Error in nightly anomaly detection: {e}")
    
    async def _send_anomaly_notification(
        self,
        property_obj: EnhancedProperty,
        anomalies: List[Dict[str, Any]]
    ):
        """Send notification for critical anomalies"""
        
        # TODO: Implement notification service (email, Slack, etc.)
        logger.info(f"Critical anomalies detected for {property_obj.name}: {len(anomalies)} anomalies")
        
        for anomaly in anomalies:
            logger.info(f"  - {anomaly['metric_name']}: {anomaly['value']} (confidence: {anomaly['confidence']})")
