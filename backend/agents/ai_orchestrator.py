"""
AI Orchestrator for REIMS Document Processing
Coordinates multiple AI agents and provides intelligent document analysis
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import asyncio
from pathlib import Path

# Import document processing components
from document_agents import agent_registry, DocumentProcessingAgent
import pandas as pd
import fitz  # PyMuPDF

class DocumentAIOrchestrator:
    """
    Main orchestrator for AI-powered document processing
    Coordinates multiple agents and provides comprehensive analysis
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ai_orchestrator")
        self.agent_registry = agent_registry
        
        # Processing statistics
        self.stats = {
            "total_documents_processed": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "processing_time_total": 0.0
        }
    
    async def process_document(self, file_path: str, metadata: Dict) -> Dict[str, Any]:
        """
        Main document processing pipeline
        Returns comprehensive analysis from all relevant agents
        """
        start_time = datetime.utcnow()
        self.logger.info(f"Starting AI processing for document: {file_path}")
        
        try:
            # Step 1: Load and preprocess document
            content, content_type = await self._load_document(file_path)
            
            # Step 2: Run classification agent first
            classification_result = await self._classify_document(content, metadata)
            
            # Step 3: Select and run appropriate specialized agents
            specialized_results = await self._run_specialized_agents(
                content, metadata, classification_result
            )
            
            # Step 4: Combine and synthesize results
            synthesis_result = await self._synthesize_results(
                classification_result, specialized_results, metadata
            )
            
            # Step 5: Generate insights and recommendations
            insights = await self._generate_insights(synthesis_result)
            
            # Update statistics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.stats["total_documents_processed"] += 1
            self.stats["successful_extractions"] += 1
            self.stats["processing_time_total"] += processing_time
            
            return {
                "document_id": metadata.get("document_id", "unknown"),
                "processing_status": "success",
                "processing_time_seconds": processing_time,
                "content_type": content_type,
                "classification": classification_result,
                "specialized_analysis": specialized_results,
                "synthesis": synthesis_result,
                "insights": insights,
                "metadata": metadata,
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing document {file_path}: {e}")
            self.stats["failed_extractions"] += 1
            
            return {
                "document_id": metadata.get("document_id", "unknown"),
                "processing_status": "error",
                "error": str(e),
                "metadata": metadata,
                "timestamp": start_time.isoformat()
            }
    
    async def _load_document(self, file_path: str) -> Tuple[Any, str]:
        """Load document content based on file type"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return await self._load_pdf(file_path), "pdf"
        elif file_extension in ['.xlsx', '.xls']:
            return await self._load_excel(file_path), "excel"
        elif file_extension == '.csv':
            return await self._load_csv(file_path), "csv"
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    async def _load_pdf(self, file_path: str) -> str:
        """Load PDF content as text"""
        doc = fitz.open(file_path)
        text_content = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content += page.get_text() + "\n"
        
        doc.close()
        return text_content
    
    async def _load_excel(self, file_path: str) -> pd.DataFrame:
        """Load Excel content as DataFrame"""
        # Try to read the first sheet
        df = pd.read_excel(file_path, sheet_name=0)
        return df
    
    async def _load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV content as DataFrame"""
        # Try different encodings
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                return df
            except UnicodeDecodeError:
                continue
        
        raise ValueError("Could not read CSV file with any supported encoding")
    
    async def _classify_document(self, content: Any, metadata: Dict) -> Dict[str, Any]:
        """Run document classification"""
        classification_agent = self.agent_registry.get_agent("document_classification_agent")
        
        if classification_agent:
            return classification_agent.process(content, metadata)
        else:
            return {
                "primary_classification": "unknown",
                "confidence_score": 0.0,
                "error": "Classification agent not available"
            }
    
    async def _run_specialized_agents(self, content: Any, metadata: Dict, 
                                    classification_result: Dict) -> Dict[str, Any]:
        """Run specialized agents based on document classification"""
        results = {}
        
        primary_type = classification_result.get("primary_classification", "unknown")
        confidence = classification_result.get("confidence_score", 0.0)
        
        # Determine which agents to run based on classification
        agents_to_run = []
        
        if primary_type in ["financial_statement", "financial_data"] or confidence < 0.7:
            # Always run financial agent for financial docs or low confidence
            agents_to_run.append("financial_statement_agent")
        
        if primary_type in ["property_listing", "property_data", "appraisal_report"] or confidence < 0.7:
            # Always run property agent for property docs or low confidence
            agents_to_run.append("property_data_agent")
        
        # If confidence is very low, run all agents
        if confidence < 0.5:
            agents_to_run = list(self.agent_registry.get_all_agents().keys())
            agents_to_run.remove("document_classification_agent")  # Already ran this
        
        # Run selected agents
        for agent_name in agents_to_run:
            agent = self.agent_registry.get_agent(agent_name)
            if agent:
                try:
                    result = agent.process(content, metadata)
                    results[agent_name] = result
                except Exception as e:
                    self.logger.error(f"Error running agent {agent_name}: {e}")
                    results[agent_name] = {
                        "agent": agent_name,
                        "error": str(e),
                        "processing_timestamp": datetime.utcnow().isoformat()
                    }
        
        return results
    
    async def _synthesize_results(self, classification: Dict, specialized: Dict, 
                                metadata: Dict) -> Dict[str, Any]:
        """Synthesize results from all agents into a comprehensive analysis"""
        synthesis = {
            "document_type": classification.get("primary_classification", "unknown"),
            "confidence": classification.get("confidence_score", 0.0),
            "extracted_entities": {},
            "financial_metrics": {},
            "property_details": {},
            "key_insights": [],
            "data_quality": self._assess_data_quality(specialized),
            "completeness_score": 0.0
        }
        
        # Extract and consolidate data from all agents
        for agent_name, result in specialized.items():
            if "error" in result:
                continue
            
            extracted_data = result.get("extracted_data", {})
            
            if agent_name == "financial_statement_agent":
                synthesis["financial_metrics"].update(extracted_data)
                
                # Add financial insights
                if "revenue" in extracted_data and "expenses" in extracted_data:
                    synthesis["key_insights"].append({
                        "type": "financial",
                        "insight": "Revenue and expense data available for profitability analysis",
                        "confidence": result.get("validation", {}).get("confidence_score", 0.0)
                    })
            
            elif agent_name == "property_data_agent":
                synthesis["property_details"].update(extracted_data)
                
                # Add property insights
                if "property_values" in extracted_data and "square_footage" in extracted_data:
                    synthesis["key_insights"].append({
                        "type": "property",
                        "insight": "Property valuation and size data available for price analysis",
                        "confidence": result.get("validation", {}).get("confidence_score", 0.0)
                    })
        
        # Calculate overall completeness score
        total_fields = 0
        populated_fields = 0
        
        for category in [synthesis["financial_metrics"], synthesis["property_details"]]:
            for field, value in category.items():
                total_fields += 1
                if value:
                    populated_fields += 1
        
        synthesis["completeness_score"] = populated_fields / total_fields if total_fields > 0 else 0.0
        
        # Generate cross-agent insights
        synthesis["cross_agent_insights"] = self._generate_cross_agent_insights(synthesis)
        
        return synthesis
    
    def _assess_data_quality(self, specialized_results: Dict) -> Dict[str, Any]:
        """Assess the quality of extracted data"""
        quality_metrics = {
            "overall_confidence": 0.0,
            "agent_success_rate": 0.0,
            "validation_issues": [],
            "data_consistency": "unknown"
        }
        
        successful_agents = 0
        total_confidence = 0.0
        total_agents = len(specialized_results)
        
        for agent_name, result in specialized_results.items():
            if "error" not in result:
                successful_agents += 1
                validation = result.get("validation", {})
                confidence = validation.get("confidence_score", 0.0)
                total_confidence += confidence
                
                # Check for validation issues
                if not validation.get("is_valid", True):
                    errors = validation.get("validation_errors", [])
                    quality_metrics["validation_issues"].extend(errors)
        
        if total_agents > 0:
            quality_metrics["agent_success_rate"] = successful_agents / total_agents
            quality_metrics["overall_confidence"] = total_confidence / total_agents
        
        # Determine data consistency
        if quality_metrics["overall_confidence"] > 0.8:
            quality_metrics["data_consistency"] = "high"
        elif quality_metrics["overall_confidence"] > 0.5:
            quality_metrics["data_consistency"] = "medium"
        else:
            quality_metrics["data_consistency"] = "low"
        
        return quality_metrics
    
    def _generate_cross_agent_insights(self, synthesis: Dict) -> List[Dict]:
        """Generate insights by analyzing results across multiple agents"""
        insights = []
        
        financial = synthesis.get("financial_metrics", {})
        property_details = synthesis.get("property_details", {})
        
        # Cross-validation insights
        if financial and property_details:
            insights.append({
                "type": "cross_validation",
                "insight": "Both financial and property data detected - comprehensive analysis possible",
                "confidence": 0.8
            })
        
        # Investment analysis insights
        if "revenue" in financial and "property_values" in property_details:
            try:
                revenue = financial["revenue"].get("primary_value", 0)
                property_value = property_details["property_values"].get("primary_value", 0)
                
                if revenue > 0 and property_value > 0:
                    roi = (revenue / property_value) * 100
                    insights.append({
                        "type": "investment_analysis",
                        "insight": f"Estimated ROI: {roi:.2f}% based on annual revenue vs property value",
                        "confidence": 0.7,
                        "calculation": f"Revenue ${revenue:,.0f} / Property Value ${property_value:,.0f}"
                    })
            except (KeyError, TypeError, ZeroDivisionError):
                pass
        
        # Market analysis insights
        if "price_per_sqft" in property_details:
            price_per_sqft = property_details["price_per_sqft"].get("value", 0)
            if price_per_sqft > 0:
                if price_per_sqft > 200:
                    market_segment = "premium"
                elif price_per_sqft > 100:
                    market_segment = "mid-market"
                else:
                    market_segment = "affordable"
                
                insights.append({
                    "type": "market_analysis",
                    "insight": f"Property appears to be in {market_segment} market segment (${price_per_sqft:.0f}/sqft)",
                    "confidence": 0.6
                })
        
        return insights
    
    async def _generate_insights(self, synthesis: Dict) -> Dict[str, Any]:
        """Generate high-level insights and recommendations"""
        insights = {
            "summary": "",
            "key_findings": [],
            "recommendations": [],
            "risk_factors": [],
            "opportunities": []
        }
        
        document_type = synthesis.get("document_type", "unknown")
        confidence = synthesis.get("confidence", 0.0)
        completeness = synthesis.get("completeness_score", 0.0)
        
        # Generate summary
        insights["summary"] = f"Document classified as {document_type} with {confidence:.1%} confidence. Data extraction achieved {completeness:.1%} completeness."
        
        # Key findings
        if synthesis.get("financial_metrics"):
            insights["key_findings"].append("Financial data successfully extracted and analyzed")
        
        if synthesis.get("property_details"):
            insights["key_findings"].append("Property characteristics and valuation data identified")
        
        # Recommendations based on document type and quality
        if confidence < 0.7:
            insights["recommendations"].append("Consider manual review due to low classification confidence")
        
        if completeness < 0.5:
            insights["recommendations"].append("Data extraction incomplete - additional processing may be needed")
        
        # Risk factors
        if synthesis.get("data_quality", {}).get("validation_issues"):
            insights["risk_factors"].append("Data validation issues detected - verify accuracy")
        
        # Opportunities
        if confidence > 0.8 and completeness > 0.7:
            insights["opportunities"].append("High-quality extraction achieved - suitable for automated processing")
        
        if synthesis.get("cross_agent_insights"):
            insights["opportunities"].append("Multi-dimensional analysis possible with available data")
        
        return insights
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        avg_time = (self.stats["processing_time_total"] / 
                   max(self.stats["total_documents_processed"], 1))
        
        return {
            **self.stats,
            "average_processing_time": avg_time,
            "success_rate": (self.stats["successful_extractions"] / 
                           max(self.stats["total_documents_processed"], 1))
        }
    
    def reset_stats(self):
        """Reset processing statistics"""
        self.stats = {
            "total_documents_processed": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "processing_time_total": 0.0
        }

# Global orchestrator instance
ai_orchestrator = DocumentAIOrchestrator()