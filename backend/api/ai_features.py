"""
REIMS AI Features API
Document summarization, AI chat, and market intelligence endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging

from ..database import get_db
from ..models.enhanced_schema import User, FinancialDocument, MarketAnalysis
from ..services.auth import require_analyst, get_current_user
from ..services.llm_service import llm_service
from ..services.audit_log import get_audit_logger, AuditLogger
from ..services.alert_system import AlertEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])

# Pydantic models
class SummarizeRequest(BaseModel):
    document_id: str
    document_type: str  # lease, offering_memorandum, financial_statement

class SummarizeResponse(BaseModel):
    document_id: str
    summary: str
    confidence: float
    model: str
    generated_at: str
    machine_generated: bool

class ChatRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    model: str
    timestamp: str
    confidence: float

class MarketAnalysisRequest(BaseModel):
    location: str
    property_type: str = "commercial"

class MarketAnalysisResponse(BaseModel):
    analysis: str
    location: str
    property_type: str
    model: str
    generated_at: str
    confidence: float

# Dependency injection
def get_llm_service():
    return llm_service

@router.post("/summarize/{document_id}", response_model=SummarizeResponse)
async def summarize_document(
    document_id: str,
    document_type: str = Form(...),
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db),
    llm_service = Depends(get_llm_service),
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """Generate AI summary of document using local LLM"""
    
    try:
        # Get document from database
        document = db.query(FinancialDocument).filter(
            FinancialDocument.id == document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Read document content
        document_path = Path(document.file_path)
        if not document_path.exists():
            raise HTTPException(status_code=404, detail="Document file not found")
        
        # Extract text based on file type
        document_text = await _extract_document_text(document_path)
        
        if not document_text:
            raise HTTPException(status_code=400, detail="Could not extract text from document")
        
        # Generate summary using LLM
        summary_result = await llm_service.summarize_document(
            document_text=document_text,
            document_type=document_type,
            property_id=str(document.property_id)
        )
        
        if "error" in summary_result:
            raise HTTPException(status_code=500, detail=summary_result["error"])
        
        # Store summary in database
        from ..models.enhanced_schema import MarketAnalysis
        market_analysis = MarketAnalysis(
            property_id=document.property_id,
            analysis_type="document_summary",
            analysis_data={
                "summary": summary_result["summary"],
                "document_type": document_type,
                "document_id": document_id
            },
            confidence_score=summary_result["confidence"]
        )
        db.add(market_analysis)
        db.commit()
        
        # Log audit event
        await audit_logger.log_ai_summarization(
            user_id=str(current_user.id),
            document_id=document_id,
            property_id=str(document.property_id),
            confidence=summary_result["confidence"],
            model_used=summary_result["model"]
        )
        
        return SummarizeResponse(
            document_id=document_id,
            summary=summary_result["summary"],
            confidence=summary_result["confidence"],
            model=summary_result["model"],
            generated_at=summary_result["generated_at"].isoformat(),
            machine_generated=summary_result["machine_generated"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in document summarization: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_request: ChatRequest,
    current_user: User = Depends(require_analyst),
    llm_service = Depends(get_llm_service),
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """Chat with AI assistant for REIMS data"""
    
    try:
        # Generate AI response
        chat_result = await llm_service.chat_with_ai(
            query=chat_request.query,
            context=chat_request.context
        )
        
        if "error" in chat_result:
            raise HTTPException(status_code=500, detail=chat_result["error"])
        
        # Log audit event
        await audit_logger.log_event(
            action="AI_CHAT",
            user_id=str(current_user.id),
            details={
                "query": chat_request.query,
                "response_length": len(chat_result["response"]),
                "model": chat_result["model"]
            }
        )
        
        return ChatResponse(
            response=chat_result["response"],
            model=chat_result["model"],
            timestamp=chat_result["timestamp"].isoformat(),
            confidence=chat_result["confidence"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@router.post("/market-analysis", response_model=MarketAnalysisResponse)
async def analyze_market_intelligence(
    analysis_request: MarketAnalysisRequest,
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db),
    llm_service = Depends(get_llm_service),
    audit_logger: AuditLogger = Depends(get_audit_logger)
):
    """Analyze market intelligence for a location"""
    
    try:
        # Generate market analysis using LLM
        analysis_result = await llm_service.analyze_market_intelligence(
            location=analysis_request.location,
            property_type=analysis_request.property_type
        )
        
        if "error" in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result["error"])
        
        # Store analysis in database
        market_analysis = MarketAnalysis(
            property_id=None,  # General market analysis
            analysis_type="market_intelligence",
            analysis_data={
                "location": analysis_request.location,
                "property_type": analysis_request.property_type,
                "analysis": analysis_result["analysis"]
            },
            confidence_score=analysis_result["confidence"]
        )
        db.add(market_analysis)
        db.commit()
        
        # Log audit event
        await audit_logger.log_event(
            action="MARKET_ANALYSIS",
            user_id=str(current_user.id),
            details={
                "location": analysis_request.location,
                "property_type": analysis_request.property_type,
                "model": analysis_result["model"]
            }
        )
        
        return MarketAnalysisResponse(
            analysis=analysis_result["analysis"],
            location=analysis_result["location"],
            property_type=analysis_result["property_type"],
            model=analysis_result["model"],
            generated_at=analysis_result["generated_at"].isoformat(),
            confidence=analysis_result["confidence"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in market analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating market analysis: {str(e)}")

@router.get("/status")
async def get_ai_status(
    current_user: User = Depends(get_current_user),
    llm_service = Depends(get_llm_service)
):
    """Get AI service status and capabilities"""
    
    return {
        "llm_available": llm_service.is_available,
        "model": llm_service.model_name,
        "capabilities": [
            "Document Summarization",
            "AI Chat Assistant",
            "Market Intelligence Analysis",
            "Tenant Recommendations",
            "Risk Assessment"
        ],
        "supported_document_types": [
            "lease",
            "offering_memorandum", 
            "financial_statement",
            "property_report"
        ],
        "status": "operational" if llm_service.is_available else "unavailable"
    }

@router.get("/models")
async def get_available_models(
    current_user: User = Depends(get_current_user),
    llm_service = Depends(get_llm_service)
):
    """Get available LLM models"""
    
    try:
        if llm_service.is_available:
            models = llm_service.ollama_client.list()
            return {
                "available_models": [model['name'] for model in models['models']],
                "current_model": llm_service.model_name,
                "status": "connected"
            }
        else:
            return {
                "available_models": [],
                "current_model": llm_service.model_name,
                "status": "disconnected",
                "error": "Ollama service not available"
            }
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return {
            "available_models": [],
            "current_model": llm_service.model_name,
            "status": "error",
            "error": str(e)
        }

# Helper functions
async def _extract_document_text(document_path: Path) -> str:
    """Extract text from document based on file type"""
    
    try:
        if document_path.suffix.lower() == '.pdf':
            return await _extract_pdf_text(document_path)
        elif document_path.suffix.lower() in ['.txt', '.md']:
            return document_path.read_text(encoding='utf-8')
        else:
            # For other file types, try to read as text
            try:
                return document_path.read_text(encoding='utf-8')
            except:
                return f"Document content extraction not supported for {document_path.suffix} files"
    except Exception as e:
        logger.error(f"Error extracting text from {document_path}: {e}")
        return ""

async def _extract_pdf_text(document_path: Path) -> str:
    """Extract text from PDF document"""
    
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(document_path))
        text = ""
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()
        
        doc.close()
        return text
    except ImportError:
        logger.warning("PyMuPDF not available for PDF text extraction")
        return "PDF text extraction requires PyMuPDF library"
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return f"Error extracting PDF text: {str(e)}"
