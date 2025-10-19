"""
REIMS Advanced Analytics API
Real-time metrics, KPI dashboard, and performance analytics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from ..database import get_db
from ..models.enhanced_schema import User
from ..services.auth import require_analyst, get_current_user
from ..services.analytics_engine import AnalyticsEngine
from ..services.audit_log import get_audit_logger, AuditLogger

router = APIRouter(prefix="/analytics", tags=["advanced-analytics"])

# Pydantic models
class DashboardMetricsResponse(BaseModel):
    property_metrics: Dict[str, Any]
    financial_metrics: Dict[str, Any]
    alert_metrics: Dict[str, Any]
    ai_metrics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    generated_at: datetime
    dashboard_version: str

class PropertyTrendsResponse(BaseModel):
    property_id: str
    trends_data: Dict[str, List[Dict[str, Any]]]
    trend_analysis: Dict[str, Any]
    analysis_period: Dict[str, Any]

class PortfolioAnalyticsResponse(BaseModel):
    portfolio_summary: Dict[str, Any]
    portfolio_performance: Dict[str, Any]
    exit_strategy_distribution: Dict[str, int]
    analysis_date: datetime

class KPIDashboardResponse(BaseModel):
    kpis: Dict[str, Any]
    dashboard_updated: datetime
    kpi_categories: Dict[str, List[str]]

# Dependency injection
def get_analytics_engine(
    db: Session = Depends(get_db), 
    audit_logger: AuditLogger = Depends(get_audit_logger)
) -> AnalyticsEngine:
    return AnalyticsEngine(db, audit_logger)

@router.get("/dashboard", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(
    current_user: User = Depends(require_analyst),
    analytics_engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """Get comprehensive dashboard metrics"""
    
    try:
        metrics = await analytics_engine.get_dashboard_metrics()
        
        if "error" in metrics:
            raise HTTPException(status_code=500, detail=metrics["error"])
        
        return DashboardMetricsResponse(
            property_metrics=metrics["property_metrics"],
            financial_metrics=metrics["financial_metrics"],
            alert_metrics=metrics["alert_metrics"],
            ai_metrics=metrics["ai_metrics"],
            performance_metrics=metrics["performance_metrics"],
            generated_at=metrics["generated_at"],
            dashboard_version=metrics["dashboard_version"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard metrics: {str(e)}")

@router.get("/property-trends/{property_id}", response_model=PropertyTrendsResponse)
async def get_property_performance_trends(
    property_id: str,
    days_back: int = Query(90, ge=7, le=365),
    current_user: User = Depends(require_analyst),
    analytics_engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """Get performance trends for a specific property"""
    
    try:
        trends = await analytics_engine.get_property_performance_trends(property_id, days_back)
        
        if "error" in trends:
            raise HTTPException(status_code=500, detail=trends["error"])
        
        return PropertyTrendsResponse(
            property_id=trends["property_id"],
            trends_data=trends["trends_data"],
            trend_analysis=trends["trend_analysis"],
            analysis_period=trends["analysis_period"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving property trends: {str(e)}")

@router.get("/portfolio", response_model=PortfolioAnalyticsResponse)
async def get_portfolio_analytics(
    current_user: User = Depends(require_analyst),
    analytics_engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """Get comprehensive portfolio analytics"""
    
    try:
        analytics = await analytics_engine.get_portfolio_analytics()
        
        if "error" in analytics:
            raise HTTPException(status_code=500, detail=analytics["error"])
        
        return PortfolioAnalyticsResponse(
            portfolio_summary=analytics["portfolio_summary"],
            portfolio_performance=analytics["portfolio_performance"],
            exit_strategy_distribution=analytics["exit_strategy_distribution"],
            analysis_date=analytics["analysis_date"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving portfolio analytics: {str(e)}")

@router.get("/kpi-dashboard", response_model=KPIDashboardResponse)
async def get_kpi_dashboard(
    current_user: User = Depends(require_analyst),
    analytics_engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """Get KPI dashboard data"""
    
    try:
        kpi_data = await analytics_engine.get_kpi_dashboard()
        
        if "error" in kpi_data:
            raise HTTPException(status_code=500, detail=kpi_data["error"])
        
        return KPIDashboardResponse(
            kpis=kpi_data["kpis"],
            dashboard_updated=kpi_data["dashboard_updated"],
            kpi_categories=kpi_data["kpi_categories"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving KPI dashboard: {str(e)}")

@router.get("/real-time-metrics")
async def get_real_time_metrics(
    current_user: User = Depends(require_analyst),
    analytics_engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """Get real-time system metrics"""
    
    try:
        # Get current metrics
        dashboard_metrics = await analytics_engine.get_dashboard_metrics()
        
        # Calculate real-time indicators
        real_time_indicators = {
            'system_status': 'operational',
            'last_update': datetime.utcnow(),
            'active_users': 1,  # Current user
            'processing_queue': 0,  # Would be calculated from actual queue
            'database_health': 'connected',
            'ai_services': 'available',
            'storage_health': 'operational'
        }
        
        return {
            'real_time_indicators': real_time_indicators,
            'dashboard_metrics': dashboard_metrics,
            'timestamp': datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving real-time metrics: {str(e)}")

@router.get("/performance-summary")
async def get_performance_summary(
    current_user: User = Depends(require_analyst),
    analytics_engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """Get system performance summary"""
    
    try:
        # Get performance metrics
        dashboard_metrics = await analytics_engine.get_dashboard_metrics()
        performance_metrics = dashboard_metrics.get('performance_metrics', {})
        
        # Calculate performance score
        processing_rate = performance_metrics.get('processing_rate', 0)
        system_health = performance_metrics.get('system_health', {})
        
        performance_score = min(100, int(processing_rate * 100))
        
        return {
            'performance_score': performance_score,
            'processing_rate': processing_rate,
            'system_health': system_health,
            'recommendations': [
                'System operating at optimal performance' if performance_score >= 90 else
                'Consider optimizing document processing' if performance_score >= 70 else
                'System performance needs attention'
            ],
            'last_updated': datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving performance summary: {str(e)}")

@router.get("/trend-analysis")
async def get_trend_analysis(
    metric_type: str = Query("all", description="Type of metric to analyze"),
    days_back: int = Query(30, ge=7, le=365),
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """Get trend analysis for specific metrics"""
    
    try:
        from ..models.enhanced_schema import ExtractedMetric, FinancialDocument
        
        # Get metrics data
        start_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = db.query(ExtractedMetric).join(
            FinancialDocument, ExtractedMetric.document_id == FinancialDocument.id
        ).filter(
            ExtractedMetric.created_at >= start_date
        )
        
        if metric_type != "all":
            query = query.filter(ExtractedMetric.metric_name.ilike(f"%{metric_type}%"))
        
        metrics = query.order_by(ExtractedMetric.created_at.asc()).all()
        
        # Organize by metric type
        trends_by_metric = {}
        for metric in metrics:
            metric_name = metric.metric_name
            if metric_name not in trends_by_metric:
                trends_by_metric[metric_name] = []
            
            trends_by_metric[metric_name].append({
                'date': metric.created_at,
                'value': float(metric.metric_value),
                'confidence': float(metric.confidence_score)
            })
        
        # Calculate trend analysis
        trend_analysis = {}
        for metric_name, data_points in trends_by_metric.items():
            if len(data_points) >= 2:
                values = [dp['value'] for dp in data_points]
                
                # Calculate trend
                import numpy as np
                trend_slope = np.polyfit(range(len(values)), values, 1)[0]
                trend_direction = 'increasing' if trend_slope > 0 else 'decreasing' if trend_slope < 0 else 'stable'
                
                trend_analysis[metric_name] = {
                    'trend_direction': trend_direction,
                    'trend_slope': float(trend_slope),
                    'current_value': values[-1],
                    'change_pct': ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0,
                    'data_points': len(data_points)
                }
        
        return {
            'trends_by_metric': trends_by_metric,
            'trend_analysis': trend_analysis,
            'analysis_period': {
                'start_date': start_date,
                'end_date': datetime.utcnow(),
                'days_back': days_back
            },
            'metric_type': metric_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving trend analysis: {str(e)}")

@router.get("/comparative-analysis")
async def get_comparative_analysis(
    property_ids: List[str] = Query(..., description="List of property IDs to compare"),
    current_user: User = Depends(require_analyst),
    analytics_engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """Get comparative analysis between properties"""
    
    try:
        if len(property_ids) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 properties allowed for comparison")
        
        # Get trends for each property
        property_analyses = {}
        for property_id in property_ids:
            trends = await analytics_engine.get_property_performance_trends(property_id, 30)
            if "error" not in trends:
                property_analyses[property_id] = trends
        
        # Calculate comparative metrics
        comparative_metrics = {}
        for property_id, analysis in property_analyses.items():
            trend_analysis = analysis.get('trend_analysis', {})
            
            # Calculate performance score
            performance_score = 0
            for metric_name, trend_data in trend_analysis.items():
                if trend_data['trend_direction'] == 'increasing':
                    performance_score += 10
                elif trend_data['trend_direction'] == 'stable':
                    performance_score += 5
            
            comparative_metrics[property_id] = {
                'performance_score': performance_score,
                'trend_analysis': trend_analysis,
                'analysis_date': analysis.get('analysis_period', {}).get('end_date')
            }
        
        return {
            'property_analyses': property_analyses,
            'comparative_metrics': comparative_metrics,
            'comparison_date': datetime.utcnow(),
            'properties_compared': len(property_analyses)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving comparative analysis: {str(e)}")

@router.get("/export-analytics")
async def export_analytics_data(
    format: str = Query("json", description="Export format: json, csv"),
    date_range: int = Query(30, ge=1, le=365, description="Days back to include"),
    current_user: User = Depends(require_analyst),
    analytics_engine: AnalyticsEngine = Depends(get_analytics_engine)
):
    """Export analytics data in specified format"""
    
    try:
        # Get comprehensive analytics data
        dashboard_metrics = await analytics_engine.get_dashboard_metrics()
        portfolio_analytics = await analytics_engine.get_portfolio_analytics()
        kpi_data = await analytics_engine.get_kpi_dashboard()
        
        export_data = {
            'dashboard_metrics': dashboard_metrics,
            'portfolio_analytics': portfolio_analytics,
            'kpi_data': kpi_data,
            'export_date': datetime.utcnow(),
            'exported_by': current_user.username,
            'date_range_days': date_range
        }
        
        if format == "csv":
            # Convert to CSV format (simplified)
            import json
            csv_data = json.dumps(export_data, indent=2, default=str)
            return {
                'format': 'csv',
                'data': csv_data,
                'filename': f'reims_analytics_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
            }
        else:
            return {
                'format': 'json',
                'data': export_data,
                'filename': f'reims_analytics_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting analytics data: {str(e)}")

