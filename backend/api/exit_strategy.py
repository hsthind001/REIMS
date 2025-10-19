"""
REIMS Exit Strategy API
Financial modeling and exit strategy analysis endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models.enhanced_schema import User
from ..services.auth import require_analyst, get_current_user
from ..services.exit_strategy import ExitStrategyAnalyzer
from ..services.audit_log import get_audit_logger, AuditLogger

router = APIRouter(prefix="/exit-strategy", tags=["exit-strategy"])

# Pydantic models
class ExitStrategyResponse(BaseModel):
    property_id: str
    analysis_date: datetime
    scenarios: Dict[str, Any]
    recommendation: Dict[str, Any]
    confidence: float
    market_conditions: Dict[str, Any]
    property_metrics: Dict[str, Any]

class AnalysisHistoryResponse(BaseModel):
    id: str
    analysis_date: datetime
    recommended_strategy: str
    confidence_score: float
    analysis_data: Dict[str, Any]
    scenarios_data: Dict[str, Any]

class PortfolioAnalysisResponse(BaseModel):
    portfolio_analyses: List[Dict[str, Any]]
    strategy_distribution: Dict[str, int]
    average_confidence: float
    total_equity: float
    total_value: float
    analysis_count: int

class ScenarioComparisonResponse(BaseModel):
    property_id: str
    scenarios: Dict[str, Any]
    recommendation: Dict[str, Any]
    comparison_metrics: Dict[str, Any]

# Dependency injection
def get_exit_analyzer(
    db: Session = Depends(get_db), 
    audit_logger: AuditLogger = Depends(get_audit_logger)
) -> ExitStrategyAnalyzer:
    return ExitStrategyAnalyzer(db, audit_logger)

@router.get("/analyze/{property_id}", response_model=ExitStrategyResponse)
async def analyze_property_exit_strategy(
    property_id: str,
    current_user: User = Depends(require_analyst),
    exit_analyzer: ExitStrategyAnalyzer = Depends(get_exit_analyzer)
):
    """Get comprehensive exit strategy analysis for a property"""
    
    try:
        analysis_result = await exit_analyzer.analyze_property(property_id)
        
        if "error" in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result["error"])
        
        return ExitStrategyResponse(
            property_id=analysis_result["property_id"],
            analysis_date=analysis_result["analysis_date"],
            scenarios=analysis_result["scenarios"],
            recommendation=analysis_result["recommendation"],
            confidence=analysis_result["confidence"],
            market_conditions=analysis_result["market_conditions"],
            property_metrics=analysis_result["property_metrics"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing exit strategy: {str(e)}")

@router.get("/history/{property_id}", response_model=List[AnalysisHistoryResponse])
async def get_analysis_history(
    property_id: str,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_analyst),
    exit_analyzer: ExitStrategyAnalyzer = Depends(get_exit_analyzer)
):
    """Get historical exit strategy analyses for a property"""
    
    try:
        history = await exit_analyzer.get_property_analysis_history(property_id, limit)
        
        return [
            AnalysisHistoryResponse(
                id=analysis["id"],
                analysis_date=analysis["analysis_date"],
                recommended_strategy=analysis["recommended_strategy"],
                confidence_score=analysis["confidence_score"],
                analysis_data=analysis["analysis_data"],
                scenarios_data=analysis["scenarios_data"]
            )
            for analysis in history
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis history: {str(e)}")

@router.post("/portfolio", response_model=PortfolioAnalysisResponse)
async def analyze_portfolio_exit_strategies(
    property_ids: List[str],
    current_user: User = Depends(require_analyst),
    exit_analyzer: ExitStrategyAnalyzer = Depends(get_exit_analyzer)
):
    """Get portfolio-level exit strategy analysis"""
    
    try:
        if len(property_ids) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 properties allowed for portfolio analysis")
        
        portfolio_analysis = await exit_analyzer.get_portfolio_analysis(property_ids)
        
        if "error" in portfolio_analysis:
            raise HTTPException(status_code=500, detail=portfolio_analysis["error"])
        
        return PortfolioAnalysisResponse(
            portfolio_analyses=portfolio_analysis["portfolio_analyses"],
            strategy_distribution=portfolio_analysis["strategy_distribution"],
            average_confidence=portfolio_analysis["average_confidence"],
            total_equity=portfolio_analysis["total_equity"],
            total_value=portfolio_analysis["total_value"],
            analysis_count=portfolio_analysis["analysis_count"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing portfolio: {str(e)}")

@router.get("/scenario-comparison/{property_id}", response_model=ScenarioComparisonResponse)
async def get_scenario_comparison(
    property_id: str,
    current_user: User = Depends(require_analyst),
    exit_analyzer: ExitStrategyAnalyzer = Depends(get_exit_analyzer)
):
    """Get detailed scenario comparison for a property"""
    
    try:
        analysis_result = await exit_analyzer.analyze_property(property_id)
        
        if "error" in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result["error"])
        
        scenarios = analysis_result["scenarios"]
        
        # Calculate comparison metrics
        comparison_metrics = {
            "irr_comparison": {
                "hold": scenarios["hold"].get("irr", 0),
                "refinance": scenarios["refinance"].get("annual_savings", 0) / 1000000,  # Convert to millions
                "sale": scenarios["sale"].get("annualized_return", 0)
            },
            "cash_flow_comparison": {
                "hold": scenarios["hold"].get("total_return", 0),
                "refinance": scenarios["refinance"].get("cash_out", 0),
                "sale": scenarios["sale"].get("net_proceeds", 0)
            },
            "risk_assessment": {
                "hold": len(scenarios["hold"].get("risk_factors", [])),
                "refinance": len(scenarios["refinance"].get("risk_factors", [])),
                "sale": len(scenarios["sale"].get("risk_factors", []))
            }
        }
        
        return ScenarioComparisonResponse(
            property_id=property_id,
            scenarios=scenarios,
            recommendation=analysis_result["recommendation"],
            comparison_metrics=comparison_metrics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating scenario comparison: {str(e)}")

@router.get("/dashboard")
async def get_exit_strategy_dashboard(
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """Get exit strategy dashboard data"""
    
    try:
        from ..models.enhanced_schema import ExitStrategyAnalysis, EnhancedProperty
        
        # Get recent analyses
        recent_analyses = db.query(ExitStrategyAnalysis).filter(
            ExitStrategyAnalysis.analysis_date >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        # Get strategy distribution
        strategy_distribution = db.query(
            ExitStrategyAnalysis.recommended_strategy,
            db.func.count(ExitStrategyAnalysis.id)
        ).group_by(ExitStrategyAnalysis.recommended_strategy).all()
        
        # Get average confidence
        avg_confidence = db.query(
            db.func.avg(ExitStrategyAnalysis.confidence_score)
        ).filter(
            ExitStrategyAnalysis.analysis_date >= datetime.utcnow() - timedelta(days=30)
        ).scalar() or 0
        
        # Get properties with recent analyses
        properties_with_analyses = db.query(EnhancedProperty).join(
            ExitStrategyAnalysis, EnhancedProperty.id == ExitStrategyAnalysis.property_id
        ).filter(
            ExitStrategyAnalysis.analysis_date >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        return {
            "recent_analyses": recent_analyses,
            "strategy_distribution": {
                strategy: count for strategy, count in strategy_distribution
            },
            "average_confidence": float(avg_confidence),
            "properties_analyzed": properties_with_analyses,
            "dashboard_updated": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard data: {str(e)}")

@router.get("/metrics/{property_id}")
async def get_property_financial_metrics(
    property_id: str,
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """Get key financial metrics for exit strategy analysis"""
    
    try:
        from ..models.enhanced_schema import EnhancedProperty, ExtractedMetric, FinancialDocument
        
        # Get property
        property_obj = db.query(EnhancedProperty).filter(
            EnhancedProperty.id == property_id
        ).first()
        
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Get latest metrics
        latest_metrics = db.query(ExtractedMetric).join(
            FinancialDocument, ExtractedMetric.document_id == FinancialDocument.id
        ).filter(
            FinancialDocument.property_id == property_id
        ).order_by(ExtractedMetric.created_at.desc()).limit(20).all()
        
        # Organize metrics by type
        metrics_by_type = {}
        for metric in latest_metrics:
            metric_type = metric.metric_name
            if metric_type not in metrics_by_type:
                metrics_by_type[metric_type] = []
            metrics_by_type[metric_type].append({
                "value": float(metric.metric_value),
                "confidence": float(metric.confidence_score),
                "date": metric.created_at
            })
        
        # Calculate key metrics
        noi = metrics_by_type.get('noi', [{}])[0].get('value', 0)
        cap_rate = metrics_by_type.get('cap_rate', [{}])[0].get('value', 0.07)
        occupancy = metrics_by_type.get('occupancy_rate', [{}])[0].get('value', 0.85)
        dscr = metrics_by_type.get('dscr', [{}])[0].get('value', 1.5)
        
        # Calculate derived metrics
        estimated_value = noi / cap_rate if cap_rate > 0 else 0
        loan_balance = estimated_value * 0.7  # Assume 70% LTV
        equity = estimated_value - loan_balance
        
        return {
            "property_id": property_id,
            "property_name": property_obj.name,
            "key_metrics": {
                "noi": noi,
                "cap_rate": cap_rate,
                "occupancy": occupancy,
                "dscr": dscr,
                "estimated_value": estimated_value,
                "loan_balance": loan_balance,
                "equity": equity
            },
            "metrics_by_type": metrics_by_type,
            "analysis_ready": noi > 0 and cap_rate > 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving financial metrics: {str(e)}")

@router.post("/batch-analyze")
async def batch_analyze_properties(
    property_ids: List[str],
    current_user: User = Depends(require_analyst),
    exit_analyzer: ExitStrategyAnalyzer = Depends(get_exit_analyzer)
):
    """Batch analyze multiple properties for exit strategies"""
    
    try:
        if len(property_ids) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 properties allowed for batch analysis")
        
        results = []
        errors = []
        
        for property_id in property_ids:
            try:
                analysis = await exit_analyzer.analyze_property(property_id)
                if "error" not in analysis:
                    results.append(analysis)
                else:
                    errors.append({"property_id": property_id, "error": analysis["error"]})
            except Exception as e:
                errors.append({"property_id": property_id, "error": str(e)})
        
        return {
            "successful_analyses": len(results),
            "failed_analyses": len(errors),
            "results": results,
            "errors": errors,
            "batch_completed": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch analysis: {str(e)}")
