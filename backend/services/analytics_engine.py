"""
REIMS Advanced Analytics Engine
Real-time metrics, KPI calculations, and performance analytics
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
import numpy as np
import pandas as pd

from ..models.enhanced_schema import (
    EnhancedProperty, FinancialDocument, ExtractedMetric, 
    Store, CommitteeAlert, WorkflowLock, AuditLog,
    MarketAnalysis, ExitStrategyAnalysis, Anomaly
)
from .audit_log import AuditLogger

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """Advanced analytics engine for real-time metrics and KPIs"""
    
    def __init__(self, db: Session, audit_logger: AuditLogger):
        self.db = db
        self.audit_logger = audit_logger
    
    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get comprehensive dashboard metrics"""
        
        try:
            # Get property metrics
            property_metrics = await self._get_property_metrics()
            
            # Get financial metrics
            financial_metrics = await self._get_financial_metrics()
            
            # Get alert metrics
            alert_metrics = await self._get_alert_metrics()
            
            # Get AI metrics
            ai_metrics = await self._get_ai_metrics()
            
            # Get performance metrics
            performance_metrics = await self._get_performance_metrics()
            
            return {
                'property_metrics': property_metrics,
                'financial_metrics': financial_metrics,
                'alert_metrics': alert_metrics,
                'ai_metrics': ai_metrics,
                'performance_metrics': performance_metrics,
                'generated_at': datetime.utcnow(),
                'dashboard_version': '4.1.0'
            }
            
        except Exception as e:
            logger.error(f"Error generating dashboard metrics: {e}")
            return {'error': str(e)}
    
    async def _get_property_metrics(self) -> Dict[str, Any]:
        """Get property-related metrics"""
        
        try:
            # Total properties
            total_properties = self.db.query(EnhancedProperty).count()
            
            # Properties by type
            properties_by_type = self.db.query(
                EnhancedProperty.property_type,
                func.count(EnhancedProperty.id)
            ).group_by(EnhancedProperty.property_type).all()
            
            # Total square footage
            total_sqft = self.db.query(func.sum(EnhancedProperty.total_sqft)).scalar() or 0
            
            # Properties with recent activity
            recent_activity = self.db.query(EnhancedProperty).join(
                FinancialDocument, EnhancedProperty.id == FinancialDocument.property_id
            ).filter(
                FinancialDocument.upload_date >= datetime.utcnow() - timedelta(days=30)
            ).count()
            
            # Store occupancy metrics
            total_stores = self.db.query(Store).count()
            occupied_stores = self.db.query(Store).filter(
                Store.status == 'occupied'
            ).count()
            
            occupancy_rate = (occupied_stores / total_stores) if total_stores > 0 else 0
            
            return {
                'total_properties': total_properties,
                'properties_by_type': {ptype: count for ptype, count in properties_by_type},
                'total_sqft': float(total_sqft) if total_sqft else 0,
                'recent_activity': recent_activity,
                'total_stores': total_stores,
                'occupied_stores': occupied_stores,
                'occupancy_rate': occupancy_rate
            }
            
        except Exception as e:
            logger.error(f"Error getting property metrics: {e}")
            return {}
    
    async def _get_financial_metrics(self) -> Dict[str, Any]:
        """Get financial performance metrics"""
        
        try:
            # Get latest financial metrics
            latest_metrics = self.db.query(ExtractedMetric).join(
                FinancialDocument, ExtractedMetric.document_id == FinancialDocument.id
            ).filter(
                FinancialDocument.upload_date >= datetime.utcnow() - timedelta(days=90)
            ).all()
            
            # Calculate aggregate metrics
            metrics_data = {}
            for metric in latest_metrics:
                metric_name = metric.metric_name
                if metric_name not in metrics_data:
                    metrics_data[metric_name] = []
                metrics_data[metric_name].append(float(metric.metric_value))
            
            # Calculate averages and totals
            financial_summary = {}
            for metric_name, values in metrics_data.items():
                if values:
                    financial_summary[metric_name] = {
                        'average': np.mean(values),
                        'median': np.median(values),
                        'min': np.min(values),
                        'max': np.max(values),
                        'count': len(values)
                    }
            
            # Calculate portfolio-level metrics
            total_noi = sum([data['average'] for name, data in financial_summary.items() if 'noi' in name.lower()])
            avg_cap_rate = np.mean([data['average'] for name, data in financial_summary.items() if 'cap_rate' in name.lower()]) if any('cap_rate' in name.lower() for name in financial_summary.keys()) else 0.07
            avg_occupancy = np.mean([data['average'] for name, data in financial_summary.items() if 'occupancy' in name.lower()]) if any('occupancy' in name.lower() for name in financial_summary.keys()) else 0.85
            
            # Calculate portfolio value
            portfolio_value = total_noi / avg_cap_rate if avg_cap_rate > 0 else 0
            
            return {
                'financial_summary': financial_summary,
                'portfolio_metrics': {
                    'total_noi': total_noi,
                    'avg_cap_rate': avg_cap_rate,
                    'avg_occupancy': avg_occupancy,
                    'portfolio_value': portfolio_value
                },
                'metrics_count': len(latest_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error getting financial metrics: {e}")
            return {}
    
    async def _get_alert_metrics(self) -> Dict[str, Any]:
        """Get alert and risk metrics"""
        
        try:
            # Recent alerts
            recent_alerts = self.db.query(CommitteeAlert).filter(
                CommitteeAlert.created_at >= datetime.utcnow() - timedelta(days=30)
            ).count()
            
            # Pending alerts
            pending_alerts = self.db.query(CommitteeAlert).filter(
                CommitteeAlert.status == 'pending'
            ).count()
            
            # Alerts by level
            alerts_by_level = self.db.query(
                CommitteeAlert.alert_level,
                func.count(CommitteeAlert.id)
            ).group_by(CommitteeAlert.alert_level).all()
            
            # Active workflow locks
            active_locks = self.db.query(WorkflowLock).filter(
                WorkflowLock.status == 'locked'
            ).count()
            
            # Recent anomalies
            recent_anomalies = self.db.query(Anomaly).filter(
                Anomaly.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            return {
                'recent_alerts': recent_alerts,
                'pending_alerts': pending_alerts,
                'alerts_by_level': {level: count for level, count in alerts_by_level},
                'active_locks': active_locks,
                'recent_anomalies': recent_anomalies
            }
            
        except Exception as e:
            logger.error(f"Error getting alert metrics: {e}")
            return {}
    
    async def _get_ai_metrics(self) -> Dict[str, Any]:
        """Get AI and machine learning metrics"""
        
        try:
            # Market analyses
            market_analyses = self.db.query(MarketAnalysis).filter(
                MarketAnalysis.analyzed_at >= datetime.utcnow() - timedelta(days=30)
            ).count()
            
            # Exit strategy analyses
            exit_analyses = self.db.query(ExitStrategyAnalysis).filter(
                ExitStrategyAnalysis.analysis_date >= datetime.utcnow() - timedelta(days=30)
            ).count()
            
            # AI confidence scores
            ai_confidence_scores = self.db.query(
                MarketAnalysis.confidence_score
            ).filter(
                MarketAnalysis.analyzed_at >= datetime.utcnow() - timedelta(days=30)
            ).all()
            
            avg_confidence = np.mean([float(score[0]) for score in ai_confidence_scores]) if ai_confidence_scores else 0
            
            # Analysis types breakdown
            analysis_types = self.db.query(
                MarketAnalysis.analysis_type,
                func.count(MarketAnalysis.id)
            ).group_by(MarketAnalysis.analysis_type).all()
            
            return {
                'market_analyses': market_analyses,
                'exit_analyses': exit_analyses,
                'avg_confidence': avg_confidence,
                'analysis_types': {atype: count for atype, count in analysis_types},
                'ai_utilization': {
                    'market_intelligence': market_analyses,
                    'exit_strategy': exit_analyses,
                    'total_ai_analyses': market_analyses + exit_analyses
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting AI metrics: {e}")
            return {}
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        
        try:
            # Document processing metrics
            total_documents = self.db.query(FinancialDocument).count()
            processed_documents = self.db.query(FinancialDocument).filter(
                FinancialDocument.processing_status == 'completed'
            ).count()
            
            processing_rate = (processed_documents / total_documents) if total_documents > 0 else 0
            
            # Recent activity
            recent_uploads = self.db.query(FinancialDocument).filter(
                FinancialDocument.upload_date >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            # User activity
            recent_audit_logs = self.db.query(AuditLog).filter(
                AuditLog.timestamp >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            # System health indicators
            system_health = {
                'database_connected': True,
                'processing_rate': processing_rate,
                'recent_activity': recent_uploads,
                'user_activity': recent_audit_logs
            }
            
            return {
                'total_documents': total_documents,
                'processed_documents': processed_documents,
                'processing_rate': processing_rate,
                'recent_uploads': recent_uploads,
                'user_activity': recent_audit_logs,
                'system_health': system_health
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    async def get_property_performance_trends(
        self, 
        property_id: str, 
        days_back: int = 90
    ) -> Dict[str, Any]:
        """Get performance trends for a specific property"""
        
        try:
            start_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get financial metrics over time
            metrics = self.db.query(ExtractedMetric).join(
                FinancialDocument, ExtractedMetric.document_id == FinancialDocument.id
            ).filter(
                FinancialDocument.property_id == property_id,
                ExtractedMetric.created_at >= start_date
            ).order_by(ExtractedMetric.created_at.asc()).all()
            
            # Organize by metric type and date
            trends_data = {}
            for metric in metrics:
                metric_name = metric.metric_name
                if metric_name not in trends_data:
                    trends_data[metric_name] = []
                
                trends_data[metric_name].append({
                    'date': metric.created_at,
                    'value': float(metric.metric_value),
                    'confidence': float(metric.confidence_score)
                })
            
            # Calculate trend analysis
            trend_analysis = {}
            for metric_name, data_points in trends_data.items():
                if len(data_points) >= 2:
                    values = [dp['value'] for dp in data_points]
                    dates = [dp['date'] for dp in data_points]
                    
                    # Calculate trend
                    trend_slope = np.polyfit(range(len(values)), values, 1)[0]
                    trend_direction = 'increasing' if trend_slope > 0 else 'decreasing' if trend_slope < 0 else 'stable'
                    
                    trend_analysis[metric_name] = {
                        'trend_direction': trend_direction,
                        'trend_slope': trend_slope,
                        'current_value': values[-1],
                        'previous_value': values[0],
                        'change_pct': ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0,
                        'data_points': len(data_points)
                    }
            
            return {
                'property_id': property_id,
                'trends_data': trends_data,
                'trend_analysis': trend_analysis,
                'analysis_period': {
                    'start_date': start_date,
                    'end_date': datetime.utcnow(),
                    'days_back': days_back
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting property performance trends: {e}")
            return {'error': str(e)}
    
    async def get_portfolio_analytics(self) -> Dict[str, Any]:
        """Get comprehensive portfolio analytics"""
        
        try:
            # Get all properties
            properties = self.db.query(EnhancedProperty).all()
            
            # Calculate portfolio metrics
            total_properties = len(properties)
            total_sqft = sum([float(p.total_sqft) for p in properties if p.total_sqft]) or 0
            
            # Get recent financial performance
            recent_metrics = self.db.query(ExtractedMetric).join(
                FinancialDocument, ExtractedMetric.document_id == FinancialDocument.id
            ).filter(
                FinancialDocument.upload_date >= datetime.utcnow() - timedelta(days=30)
            ).all()
            
            # Calculate portfolio performance
            portfolio_performance = {}
            for metric in recent_metrics:
                metric_name = metric.metric_name
                if metric_name not in portfolio_performance:
                    portfolio_performance[metric_name] = []
                portfolio_performance[metric_name].append(float(metric.metric_value))
            
            # Calculate portfolio averages
            portfolio_averages = {}
            for metric_name, values in portfolio_performance.items():
                if values:
                    portfolio_averages[metric_name] = {
                        'average': np.mean(values),
                        'median': np.median(values),
                        'std_dev': np.std(values),
                        'min': np.min(values),
                        'max': np.max(values)
                    }
            
            # Get exit strategy distribution
            exit_strategies = self.db.query(
                ExitStrategyAnalysis.recommended_strategy,
                func.count(ExitStrategyAnalysis.id)
            ).group_by(ExitStrategyAnalysis.recommended_strategy).all()
            
            return {
                'portfolio_summary': {
                    'total_properties': total_properties,
                    'total_sqft': total_sqft,
                    'avg_sqft_per_property': total_sqft / total_properties if total_properties > 0 else 0
                },
                'portfolio_performance': portfolio_averages,
                'exit_strategy_distribution': {strategy: count for strategy, count in exit_strategies},
                'analysis_date': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio analytics: {e}")
            return {'error': str(e)}
    
    async def get_kpi_dashboard(self) -> Dict[str, Any]:
        """Get KPI dashboard data"""
        
        try:
            # Key Performance Indicators
            kpis = {}
            
            # Financial KPIs
            financial_kpis = await self._calculate_financial_kpis()
            kpis.update(financial_kpis)
            
            # Operational KPIs
            operational_kpis = await self._calculate_operational_kpis()
            kpis.update(operational_kpis)
            
            # Risk KPIs
            risk_kpis = await self._calculate_risk_kpis()
            kpis.update(risk_kpis)
            
            # AI/ML KPIs
            ai_kpis = await self._calculate_ai_kpis()
            kpis.update(ai_kpis)
            
            return {
                'kpis': kpis,
                'dashboard_updated': datetime.utcnow(),
                'kpi_categories': {
                    'financial': list(financial_kpis.keys()),
                    'operational': list(operational_kpis.keys()),
                    'risk': list(risk_kpis.keys()),
                    'ai': list(ai_kpis.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting KPI dashboard: {e}")
            return {'error': str(e)}
    
    async def _calculate_financial_kpis(self) -> Dict[str, Any]:
        """Calculate financial KPIs"""
        
        try:
            # Get recent financial data
            recent_metrics = self.db.query(ExtractedMetric).join(
                FinancialDocument, ExtractedMetric.document_id == FinancialDocument.id
            ).filter(
                FinancialDocument.upload_date >= datetime.utcnow() - timedelta(days=30)
            ).all()
            
            # Calculate KPIs
            noi_values = [float(m.metric_value) for m in recent_metrics if 'noi' in m.metric_name.lower()]
            cap_rate_values = [float(m.metric_value) for m in recent_metrics if 'cap_rate' in m.metric_name.lower()]
            occupancy_values = [float(m.metric_value) for m in recent_metrics if 'occupancy' in m.metric_name.lower()]
            
            return {
                'total_noi': sum(noi_values) if noi_values else 0,
                'avg_cap_rate': np.mean(cap_rate_values) if cap_rate_values else 0,
                'avg_occupancy': np.mean(occupancy_values) if occupancy_values else 0,
                'portfolio_value': sum(noi_values) / np.mean(cap_rate_values) if noi_values and cap_rate_values else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating financial KPIs: {e}")
            return {}
    
    async def _calculate_operational_kpis(self) -> Dict[str, Any]:
        """Calculate operational KPIs"""
        
        try:
            # Document processing rate
            total_docs = self.db.query(FinancialDocument).count()
            processed_docs = self.db.query(FinancialDocument).filter(
                FinancialDocument.processing_status == 'completed'
            ).count()
            
            # Occupancy rate
            total_stores = self.db.query(Store).count()
            occupied_stores = self.db.query(Store).filter(Store.status == 'occupied').count()
            
            return {
                'document_processing_rate': (processed_docs / total_docs) if total_docs > 0 else 0,
                'occupancy_rate': (occupied_stores / total_stores) if total_stores > 0 else 0,
                'total_documents': total_docs,
                'total_stores': total_stores
            }
            
        except Exception as e:
            logger.error(f"Error calculating operational KPIs: {e}")
            return {}
    
    async def _calculate_risk_kpis(self) -> Dict[str, Any]:
        """Calculate risk KPIs"""
        
        try:
            # Active alerts
            active_alerts = self.db.query(CommitteeAlert).filter(
                CommitteeAlert.status == 'pending'
            ).count()
            
            # Recent anomalies
            recent_anomalies = self.db.query(Anomaly).filter(
                Anomaly.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            # Workflow locks
            active_locks = self.db.query(WorkflowLock).filter(
                WorkflowLock.status == 'locked'
            ).count()
            
            return {
                'active_alerts': active_alerts,
                'recent_anomalies': recent_anomalies,
                'active_locks': active_locks,
                'risk_score': min(100, (active_alerts * 10) + (recent_anomalies * 5) + (active_locks * 3))
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk KPIs: {e}")
            return {}
    
    async def _calculate_ai_kpis(self) -> Dict[str, Any]:
        """Calculate AI/ML KPIs"""
        
        try:
            # AI analyses
            market_analyses = self.db.query(MarketAnalysis).filter(
                MarketAnalysis.analyzed_at >= datetime.utcnow() - timedelta(days=30)
            ).count()
            
            exit_analyses = self.db.query(ExitStrategyAnalysis).filter(
                ExitStrategyAnalysis.analysis_date >= datetime.utcnow() - timedelta(days=30)
            ).count()
            
            # Average confidence
            confidence_scores = self.db.query(MarketAnalysis.confidence_score).filter(
                MarketAnalysis.analyzed_at >= datetime.utcnow() - timedelta(days=30)
            ).all()
            
            avg_confidence = np.mean([float(score[0]) for score in confidence_scores]) if confidence_scores else 0
            
            return {
                'ai_analyses_count': market_analyses + exit_analyses,
                'market_analyses': market_analyses,
                'exit_analyses': exit_analyses,
                'avg_confidence': avg_confidence,
                'ai_utilization_rate': (market_analyses + exit_analyses) / 30  # per day
            }
            
        except Exception as e:
            logger.error(f"Error calculating AI KPIs: {e}")
            return {}

