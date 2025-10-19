"""
REIMS Market Intelligence Agent
AI-powered market analysis and tenant recommendations
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import requests
from urllib.parse import quote

from ..models.enhanced_schema import (
    EnhancedProperty, Store, MarketAnalysis, User
)
from .llm_service import llm_service
from .audit_log import AuditLogger

logger = logging.getLogger(__name__)

class MarketIntelligenceAgent:
    """AI agent for market intelligence and tenant recommendations"""
    
    def __init__(self, db: Session, audit_logger: AuditLogger):
        self.db = db
        self.audit_logger = audit_logger
        self.llm_service = llm_service
    
    async def analyze_location(
        self,
        address: str,
        city: str,
        state: str,
        property_type: str = "commercial"
    ) -> Dict[str, Any]:
        """Comprehensive location analysis using AI and web search"""
        
        try:
            location = f"{address}, {city}, {state}"
            
            # Get web search results for market data
            market_data = await self._search_market_data(location, property_type)
            
            # Get demographic data
            demographic_data = await self._get_demographic_data(city, state)
            
            # Get nearby properties
            nearby_properties = await self._find_nearby_properties(location)
            
            # Generate AI analysis
            ai_analysis = await self._generate_ai_analysis(
                location, property_type, market_data, demographic_data, nearby_properties
            )
            
            # Store analysis in database
            analysis_record = MarketAnalysis(
                property_id=None,  # General location analysis
                analysis_type="location_analysis",
                analysis_data={
                    "location": location,
                    "property_type": property_type,
                    "market_data": market_data,
                    "demographic_data": demographic_data,
                    "nearby_properties": nearby_properties,
                    "ai_analysis": ai_analysis
                },
                confidence_score=0.85
            )
            self.db.add(analysis_record)
            self.db.commit()
            
            # Log analysis
            await self.audit_logger.log_event(
                action="MARKET_INTELLIGENCE_ANALYSIS",
                details={
                    "location": location,
                    "property_type": property_type,
                    "analysis_id": str(analysis_record.id)
                }
            )
            
            return {
                "location": location,
                "property_type": property_type,
                "analysis": ai_analysis,
                "market_data": market_data,
                "demographic_data": demographic_data,
                "nearby_properties": nearby_properties,
                "confidence": 0.85,
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error in location analysis: {e}")
            return {
                "error": str(e),
                "location": f"{address}, {city}, {state}",
                "analysis": "Error occurred during analysis"
            }
    
    async def recommend_tenants(
        self,
        property_id: str,
        available_sqft: float,
        current_tenants: List[str],
        location_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recommend ideal tenants for vacant space"""
        
        try:
            # Get property details
            property_obj = self.db.query(EnhancedProperty).filter(
                EnhancedProperty.id == property_id
            ).first()
            
            if not property_obj:
                return {"error": "Property not found"}
            
            # Get location analysis if not provided
            if not location_data:
                location_data = await self.analyze_location(
                    property_obj.address or "",
                    property_obj.city or "",
                    property_obj.state or ""
                )
            
            # Generate tenant recommendations using AI
            recommendations = await self._generate_tenant_recommendations(
                property_obj, available_sqft, current_tenants, location_data
            )
            
            # Store recommendations
            analysis_record = MarketAnalysis(
                property_id=property_id,
                analysis_type="tenant_recommendations",
                analysis_data={
                    "available_sqft": available_sqft,
                    "current_tenants": current_tenants,
                    "recommendations": recommendations,
                    "location_data": location_data
                },
                confidence_score=0.80
            )
            self.db.add(analysis_record)
            self.db.commit()
            
            return {
                "property_id": property_id,
                "available_sqft": available_sqft,
                "recommendations": recommendations,
                "confidence": 0.80,
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error generating tenant recommendations: {e}")
            return {
                "error": str(e),
                "property_id": property_id,
                "recommendations": []
            }
    
    async def _search_market_data(
        self,
        location: str,
        property_type: str
    ) -> Dict[str, Any]:
        """Search for market data using web search"""
        
        try:
            # Search queries for market data
            queries = [
                f"commercial real estate market {location} 2024",
                f"rental rates {location} {property_type}",
                f"vacancy rates {location} commercial",
                f"new developments {location}",
                f"employment growth {location}"
            ]
            
            market_data = {}
            
            for query in queries:
                try:
                    # Use DuckDuckGo search (free, no API key required)
                    search_results = await self._duckduckgo_search(query)
                    market_data[query] = search_results[:3]  # Top 3 results
                except Exception as e:
                    logger.warning(f"Search failed for query '{query}': {e}")
                    market_data[query] = []
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error searching market data: {e}")
            return {}
    
    async def _duckduckgo_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform DuckDuckGo search"""
        
        try:
            # Use DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            
            # Extract relevant information
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", "Market Information"),
                    "snippet": data.get("Abstract", ""),
                    "url": data.get("AbstractURL", ""),
                    "source": "DuckDuckGo"
                })
            
            # Add related topics
            for topic in data.get("RelatedTopics", [])[:max_results-1]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append({
                        "title": topic.get("Text", "")[:100],
                        "snippet": topic.get("Text", ""),
                        "url": topic.get("FirstURL", ""),
                        "source": "DuckDuckGo"
                    })
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    async def _get_demographic_data(
        self,
        city: str,
        state: str
    ) -> Dict[str, Any]:
        """Get demographic data for location"""
        
        try:
            # Search for demographic information
            query = f"demographics {city} {state} population income employment"
            search_results = await self._duckduckgo_search(query, 3)
            
            return {
                "search_results": search_results,
                "location": f"{city}, {state}",
                "data_source": "web_search"
            }
            
        except Exception as e:
            logger.error(f"Error getting demographic data: {e}")
            return {}
    
    async def _find_nearby_properties(
        self,
        location: str
    ) -> List[Dict[str, Any]]:
        """Find nearby commercial properties"""
        
        try:
            # Search for nearby commercial properties
            query = f"commercial property sales {location} recent"
            search_results = await self._duckduckgo_search(query, 5)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error finding nearby properties: {e}")
            return []
    
    async def _generate_ai_analysis(
        self,
        location: str,
        property_type: str,
        market_data: Dict[str, Any],
        demographic_data: Dict[str, Any],
        nearby_properties: List[Dict[str, Any]]
    ) -> str:
        """Generate AI analysis using LLM"""
        
        try:
            # Prepare context for AI analysis
            context = {
                "location": location,
                "property_type": property_type,
                "market_data": market_data,
                "demographic_data": demographic_data,
                "nearby_properties": nearby_properties
            }
            
            # Use LLM service for analysis
            if self.llm_service.is_available:
                analysis_result = await self.llm_service.analyze_market_intelligence(
                    location=location,
                    property_type=property_type
                )
                return analysis_result.get("analysis", "Analysis not available")
            else:
                # Fallback analysis without LLM
                return self._generate_fallback_analysis(location, property_type, market_data)
                
        except Exception as e:
            logger.error(f"Error generating AI analysis: {e}")
            return f"Error generating analysis: {str(e)}"
    
    def _generate_fallback_analysis(
        self,
        location: str,
        property_type: str,
        market_data: Dict[str, Any]
    ) -> str:
        """Generate fallback analysis without LLM"""
        
        analysis = f"""
Market Analysis for {location}

Property Type: {property_type}

Market Data Summary:
- Location: {location}
- Property Type: {property_type}
- Data Sources: Web search results

Key Findings:
- Market data collected from multiple sources
- Analysis based on available web information
- Recommendations may be limited without AI processing

Note: Full AI analysis requires LLM service to be available.
        """
        
        return analysis.strip()
    
    async def _generate_tenant_recommendations(
        self,
        property_obj: EnhancedProperty,
        available_sqft: float,
        current_tenants: List[str],
        location_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate tenant recommendations using AI"""
        
        try:
            # Prepare context for tenant recommendations
            context = {
                "property": {
                    "name": property_obj.name,
                    "address": property_obj.address,
                    "total_sqft": float(property_obj.total_sqft) if property_obj.total_sqft else 0,
                    "property_type": property_obj.property_type
                },
                "available_sqft": available_sqft,
                "current_tenants": current_tenants,
                "location_data": location_data
            }
            
            # Use LLM service for recommendations
            if self.llm_service.is_available:
                query = f"""
                Recommend ideal tenants for a commercial property:
                - Available space: {available_sqft} sq ft
                - Current tenants: {', '.join(current_tenants)}
                - Location: {property_obj.address}
                - Property type: {property_obj.property_type}
                
                Provide 3-5 specific tenant recommendations with:
                1. Business type
                2. Rationale
                3. Typical rent range
                4. Synergies with existing tenants
                5. Confidence score
                """
                
                chat_result = await self.llm_service.chat_with_ai(query, context)
                recommendations_text = chat_result.get("response", "")
                
                # Parse recommendations (simplified)
                recommendations = self._parse_tenant_recommendations(recommendations_text)
            else:
                # Fallback recommendations
                recommendations = self._generate_fallback_recommendations(
                    available_sqft, current_tenants
                )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating tenant recommendations: {e}")
            return []
    
    def _parse_tenant_recommendations(self, recommendations_text: str) -> List[Dict[str, Any]]:
        """Parse AI-generated tenant recommendations"""
        
        # Simple parsing - in production, use more sophisticated NLP
        recommendations = []
        
        # Split by common patterns
        sections = recommendations_text.split('\n\n')
        
        for i, section in enumerate(sections[:5]):  # Max 5 recommendations
            if section.strip():
                recommendations.append({
                    "rank": i + 1,
                    "business_type": f"Business Type {i + 1}",
                    "rationale": section[:200] + "..." if len(section) > 200 else section,
                    "rent_range": "Market rate",
                    "synergies": "Complementary to existing tenants",
                    "confidence": 0.75
                })
        
        return recommendations
    
    def _generate_fallback_recommendations(
        self,
        available_sqft: float,
        current_tenants: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate fallback recommendations without AI"""
        
        recommendations = []
        
        # Basic recommendations based on square footage
        if available_sqft < 1000:
            recommendations.append({
                "rank": 1,
                "business_type": "Small Office/Professional Services",
                "rationale": "Suitable for small professional offices",
                "rent_range": "$15-25/sq ft",
                "synergies": "Professional services complement retail",
                "confidence": 0.70
            })
        elif available_sqft < 5000:
            recommendations.append({
                "rank": 1,
                "business_type": "Retail Store",
                "rationale": "Good size for retail operations",
                "rent_range": "$20-35/sq ft",
                "synergies": "Retail complements office tenants",
                "confidence": 0.75
            })
        else:
            recommendations.append({
                "rank": 1,
                "business_type": "Large Retail/Service Business",
                "rationale": "Suitable for larger retail or service operations",
                "rent_range": "$18-30/sq ft",
                "synergies": "Major tenant for stability",
                "confidence": 0.80
            })
        
        return recommendations
