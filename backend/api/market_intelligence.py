"""
REIMS Market Intelligence API
Market analysis, tenant recommendations, and anomaly detection endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from ..database import get_db
from ..models.enhanced_schema import User
from ..services.auth import require_analyst, get_current_user
from ..services.market_intelligence import MarketIntelligenceAgent
from ..services.anomaly_detection import PropertyAnomalyService, NightlyAnomalyJob
from ..services.audit_log import get_audit_logger, AuditLogger

router = APIRouter(prefix="/market", tags=["market-intelligence"])

# Pydantic models
class LocationAnalysisRequest(BaseModel):
    address: str
    city: str
    state: str
    property_type: str = "commercial"

class LocationAnalysisResponse(BaseModel):
    location: str
    property_type: str
    analysis: str
    market_data: Dict[str, Any]
    demographic_data: Dict[str, Any]
    nearby_properties: List[Dict[str, Any]]
    confidence: float
    generated_at: str

class TenantRecommendationRequest(BaseModel):
    property_id: str
    available_sqft: float
    current_tenants: List[str]

class TenantRecommendationResponse(BaseModel):
    property_id: str
    available_sqft: float
    recommendations: List[Dict[str, Any]]
    confidence: float
    generated_at: str

class AnomalyResponse(BaseModel):
    id: str
    metric_name: str
    timestamp: datetime
    value: float
    z_score: Optional[float]
    cusum_value: Optional[float]
    detection_method: str
    confidence: float
    trend_direction: Optional[str]
    created_at: datetime

class AnomalyStatisticsResponse(BaseModel):
    total_anomalies: int
    by_method: Dict[str, int]
    by_metric: Dict[str, int]
    by_confidence: Dict[str, int]
    date_range: Dict[str, datetime]

# Dependency injection
def get_market_agent(db: Session = Depends(get_db), audit_logger: AuditLogger = Depends(get_audit_logger)) -> MarketIntelligenceAgent:
    return MarketIntelligenceAgent(db, audit_logger)

def get_anomaly_service(db: Session = Depends(get_db), audit_logger: AuditLogger = Depends(get_audit_logger)) -> PropertyAnomalyService:
    return PropertyAnomalyService(db, audit_logger)

@router.post("/analyze-location", response_model=LocationAnalysisResponse)
async def analyze_location(
    request: LocationAnalysisRequest,
    current_user: User = Depends(require_analyst),
    market_agent: MarketIntelligenceAgent = Depends(get_market_agent)
):
    """Analyze market intelligence for a location"""
    
    try:
        analysis_result = await market_agent.analyze_location(
            address=request.address,
            city=request.city,
            state=request.state,
            property_type=request.property_type
        )
        
        if "error" in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result["error"])
        
        return LocationAnalysisResponse(
            location=analysis_result["location"],
            property_type=analysis_result["property_type"],
            analysis=analysis_result["analysis"],
            market_data=analysis_result["market_data"],
            demographic_data=analysis_result["demographic_data"],
            nearby_properties=analysis_result["nearby_properties"],
            confidence=analysis_result["confidence"],
            generated_at=analysis_result["generated_at"].isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing location: {str(e)}")

@router.post("/recommend-tenants", response_model=TenantRecommendationResponse)
async def recommend_tenants(
    request: TenantRecommendationRequest,
    current_user: User = Depends(require_analyst),
    market_agent: MarketIntelligenceAgent = Depends(get_market_agent)
):
    """Get AI tenant recommendations for vacant space"""
    
    try:
        recommendations_result = await market_agent.recommend_tenants(
            property_id=request.property_id,
            available_sqft=request.available_sqft,
            current_tenants=request.current_tenants,
            location_data=None  # Will be fetched if needed
        )
        
        if "error" in recommendations_result:
            raise HTTPException(status_code=500, detail=recommendations_result["error"])
        
        return TenantRecommendationResponse(
            property_id=recommendations_result["property_id"],
            available_sqft=recommendations_result["available_sqft"],
            recommendations=recommendations_result["recommendations"],
            confidence=recommendations_result["confidence"],
            generated_at=recommendations_result["generated_at"].isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating tenant recommendations: {str(e)}")

@router.get("/anomalies/{property_id}", response_model=List[AnomalyResponse])
async def get_property_anomalies(
    property_id: str,
    days_back: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_analyst),
    anomaly_service: PropertyAnomalyService = Depends(get_anomaly_service)
):
    """Get anomalies for a property"""
    
    try:
        anomalies = await anomaly_service.get_property_anomalies(
            property_id=property_id,
            days_back=days_back
        )
        
        return [
            AnomalyResponse(
                id=anomaly["id"],
                metric_name=anomaly["metric_name"],
                timestamp=anomaly["timestamp"],
                value=anomaly["value"],
                z_score=anomaly["z_score"],
                cusum_value=anomaly["cusum_value"],
                detection_method=anomaly["detection_method"],
                confidence=anomaly["confidence"],
                trend_direction=anomaly["trend_direction"],
                created_at=anomaly["created_at"]
            )
            for anomaly in anomalies
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving anomalies: {str(e)}")

@router.get("/anomalies/statistics", response_model=AnomalyStatisticsResponse)
async def get_anomaly_statistics(
    property_id: Optional[str] = Query(None),
    days_back: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_analyst),
    anomaly_service: PropertyAnomalyService = Depends(get_anomaly_service)
):
    """Get anomaly statistics"""
    
    try:
        statistics = await anomaly_service.get_anomaly_statistics(
            property_id=property_id,
            days_back=days_back
        )
        
        return AnomalyStatisticsResponse(
            total_anomalies=statistics["total_anomalies"],
            by_method=statistics["by_method"],
            by_metric=statistics["by_metric"],
            by_confidence=statistics["by_confidence"],
            date_range=statistics["date_range"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving anomaly statistics: {str(e)}")

@router.post("/analyze-property/{property_id}")
async def analyze_property_anomalies(
    property_id: str,
    current_user: User = Depends(require_analyst),
    anomaly_service: PropertyAnomalyService = Depends(get_anomaly_service)
):
    """Manually trigger anomaly analysis for a property"""
    
    try:
        anomalies = await anomaly_service.analyze_property(property_id)
        
        return {
            "property_id": property_id,
            "anomalies_found": len(anomalies),
            "analysis_completed": datetime.utcnow(),
            "anomalies": [
                {
                    "metric_name": anomaly["metric_name"],
                    "value": anomaly["value"],
                    "detection_method": anomaly["detection_method"],
                    "confidence": anomaly["confidence"]
                }
                for anomaly in anomalies
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing property anomalies: {str(e)}")

@router.post("/run-nightly-analysis")
async def run_nightly_anomaly_analysis(
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db),
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """Run nightly anomaly detection for all properties"""
    
    try:
        # Create nightly job
        nightly_job = NightlyAnomalyJob(db, audit_logger)
        
        # Run analysis
        await nightly_job.run_nightly_analysis()
        
        return {
            "status": "completed",
            "message": "Nightly anomaly analysis completed successfully",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running nightly analysis: {str(e)}")

@router.get("/market-analysis/{property_id}")
async def get_property_market_analysis(
    property_id: str,
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """Get market analysis for a property"""
    
    try:
        from ..models.enhanced_schema import MarketAnalysis
        
        # Get recent market analysis
        analyses = db.query(MarketAnalysis).filter(
            MarketAnalysis.property_id == property_id,
            MarketAnalysis.analysis_type.in_(["location_analysis", "tenant_recommendations"])
        ).order_by(MarketAnalysis.analyzed_at.desc()).limit(5).all()
        
        return [
            {
                "id": str(analysis.id),
                "analysis_type": analysis.analysis_type,
                "analysis_data": analysis.analysis_data,
                "confidence_score": float(analysis.confidence_score),
                "analyzed_at": analysis.analyzed_at
            }
            for analysis in analyses
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving market analysis: {str(e)}")

@router.get("/dashboard")
async def get_market_dashboard(
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """Get market intelligence dashboard data"""
    
    try:
        from ..models.enhanced_schema import MarketAnalysis, Anomaly
        
        # Get recent analyses
        recent_analyses = db.query(MarketAnalysis).filter(
            MarketAnalysis.analyzed_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        # Get recent anomalies
        recent_anomalies = db.query(Anomaly).filter(
            Anomaly.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Get analysis types breakdown
        analysis_types = db.query(
            MarketAnalysis.analysis_type,
            db.func.count(MarketAnalysis.id)
        ).group_by(MarketAnalysis.analysis_type).all()
        
        return {
            "recent_analyses": recent_analyses,
            "recent_anomalies": recent_anomalies,
            "analysis_types": {
                analysis_type: count for analysis_type, count in analysis_types
            },
            "dashboard_updated": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard data: {str(e)}")
