"""
REIMS LLM Service - Ollama Integration
Local LLM service for document summarization and AI features
"""

import ollama
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json
import re

logger = logging.getLogger(__name__)

class LLMService:
    """Local LLM service using Ollama for document processing"""
    
    def __init__(self, model_name: str = "phi3:mini"):
        self.model_name = model_name
        self.ollama_client = ollama
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200
        )
        self.is_available = self._check_ollama_availability()
    
    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is available and model is loaded"""
        try:
            # Test connection
            models = self.ollama_client.list()
            available_models = [model['name'] for model in models['models']]
            
            if self.model_name in available_models:
                logger.info(f"✅ Ollama model {self.model_name} is available")
                return True
            else:
                logger.warning(f"⚠️ Model {self.model_name} not found. Available: {available_models}")
                # Try to pull the model
                try:
                    self.ollama_client.pull(self.model_name)
                    logger.info(f"✅ Successfully pulled model {self.model_name}")
                    return True
                except Exception as e:
                    logger.error(f"❌ Failed to pull model {self.model_name}: {e}")
                    return False
        except Exception as e:
            logger.error(f"❌ Ollama not available: {e}")
            return False
    
    async def summarize_document(
        self, 
        document_text: str, 
        document_type: str,
        property_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Summarize lease or offering memorandum document"""
        
        if not self.is_available:
            return {
                "error": "LLM service not available",
                "summary": "LLM service is not available. Please check Ollama installation.",
                "confidence": 0.0
            }
        
        try:
            # Split long documents
            chunks = self.text_splitter.split_text(document_text)
            
            # Get appropriate prompt based on document type
            if document_type == "lease":
                prompt = self._get_lease_summary_prompt()
            elif document_type == "offering_memorandum":
                prompt = self._get_om_summary_prompt()
            else:
                prompt = self._get_general_summary_prompt()
            
            summaries = []
            
            # Process each chunk
            for i, chunk in enumerate(chunks):
                try:
                    response = self.ollama_client.chat(
                        model=self.model_name,
                        messages=[
                            {
                                'role': 'system',
                                'content': 'You are a commercial real estate analyst. Provide concise, accurate summaries with specific financial details.'
                            },
                            {
                                'role': 'user',
                                'content': f"{prompt}\n\n{chunk}"
                            }
                        ]
                    )
                    
                    summary = response['message']['content']
                    summaries.append(summary)
                    
                    logger.info(f"Processed chunk {i+1}/{len(chunks)} for {document_type}")
                    
                except Exception as e:
                    logger.error(f"Error processing chunk {i+1}: {e}")
                    summaries.append(f"Error processing chunk {i+1}: {str(e)}")
            
            # Combine chunk summaries
            final_summary = self._combine_summaries(summaries, document_type)
            
            # Calculate confidence based on consistency
            confidence = self._calculate_summary_confidence(summaries)
            
            return {
                'summary': final_summary,
                'confidence': confidence,
                'model': self.model_name,
                'generated_at': datetime.utcnow(),
                'machine_generated': True,
                'chunks_processed': len(chunks),
                'property_id': property_id
            }
            
        except Exception as e:
            logger.error(f"Error in document summarization: {e}")
            return {
                "error": str(e),
                "summary": "Error occurred during summarization",
                "confidence": 0.0
            }
    
    def _get_lease_summary_prompt(self) -> str:
        """Get prompt for lease document summarization"""
        return """Extract and summarize the following from this lease document:

1. **Tenant Information**:
   - Tenant name and business type
   - Lease term (start/end dates)
   - Monthly rent amount and any escalations
   - Security deposit and other fees

2. **Financial Terms**:
   - Base rent and any percentage rent
   - Common area maintenance (CAM) charges
   - Utilities included/excluded
   - Late fees and penalties

3. **Key Obligations**:
   - Tenant responsibilities
   - Landlord responsibilities
   - Maintenance obligations
   - Insurance requirements

4. **Special Provisions**:
   - Renewal options and terms
   - Assignment and subletting rights
   - Use restrictions
   - Any special clauses

Format as structured bullet points with specific financial figures."""
    
    def _get_om_summary_prompt(self) -> str:
        """Get prompt for offering memorandum summarization"""
        return """Extract and summarize the following from this offering memorandum:

1. **Property Details**:
   - Property location and type
   - Total square footage
   - Year built and recent improvements
   - Property condition

2. **Financial Performance**:
   - Net Operating Income (NOI)
   - Cap rate and market analysis
   - Occupancy rate and tenant mix
   - Revenue and expense breakdown

3. **Tenant Profile**:
   - Major tenants and lease terms
   - Lease expiration schedule
   - Credit quality of tenants
   - Diversification analysis

4. **Market Analysis**:
   - Comparable sales
   - Market trends and outlook
   - Location advantages
   - Growth potential

Format as structured sections with specific financial metrics."""
    
    def _get_general_summary_prompt(self) -> str:
        """Get prompt for general document summarization"""
        return """Summarize this real estate document focusing on:

1. **Key Financial Information**:
   - Revenue, expenses, and net income
   - Property values and market data
   - Lease terms and tenant information

2. **Important Dates and Deadlines**:
   - Lease expirations
   - Payment due dates
   - Renewal options

3. **Risk Factors**:
   - Vacancy risks
   - Market conditions
   - Tenant credit quality

4. **Opportunities**:
   - Value-add potential
   - Market growth prospects
   - Operational improvements

Provide specific financial figures and dates where available."""
    
    def _combine_summaries(self, summaries: List[str], document_type: str) -> str:
        """Combine multiple chunk summaries into final summary"""
        
        if not summaries:
            return "No content to summarize."
        
        if len(summaries) == 1:
            return summaries[0]
        
        # For multiple chunks, create a comprehensive summary
        combined_prompt = f"""Combine the following summaries of a {document_type} document into a single, comprehensive summary:

{chr(10).join([f"Summary {i+1}: {summary}" for i, summary in enumerate(summaries)])}

Provide a unified summary that:
- Eliminates redundancy
- Preserves all important financial details
- Maintains chronological order
- Highlights key risks and opportunities
- Includes specific figures and dates

Format as a structured document with clear sections."""
        
        try:
            if self.is_available:
                response = self.ollama_client.chat(
                    model=self.model_name,
                    messages=[
                        {
                            'role': 'system',
                            'content': 'You are a real estate analyst creating comprehensive document summaries.'
                        },
                        {
                            'role': 'user',
                            'content': combined_prompt
                        }
                    ]
                )
                return response['message']['content']
            else:
                # Fallback: simple concatenation
                return "\n\n".join(summaries)
        except Exception as e:
            logger.error(f"Error combining summaries: {e}")
            return "\n\n".join(summaries)
    
    def _calculate_summary_confidence(self, summaries: List[str]) -> float:
        """Calculate confidence based on consistency across chunks"""
        
        if len(summaries) == 1:
            return 0.75  # Base confidence for single-chunk
        
        if len(summaries) == 0:
            return 0.0
        
        # Simple heuristic: check for consistent key terms
        key_terms = set()
        for summary in summaries:
            # Extract financial terms and numbers
            terms = re.findall(r'\$[\d,]+\.?\d*|\d+%|\d+\.\d+', summary.lower())
            key_terms.update(terms)
        
        # Calculate overlap between summaries
        overlap_scores = []
        for summary in summaries:
            summary_terms = set(re.findall(r'\$[\d,]+\.?\d*|\d+%|\d+\.\d+', summary.lower()))
            if key_terms:
                overlap = len(summary_terms & key_terms) / len(key_terms)
                overlap_scores.append(overlap)
        
        if overlap_scores:
            avg_overlap = sum(overlap_scores) / len(overlap_scores)
            confidence = min(0.70 + (avg_overlap * 0.25), 0.95)
        else:
            confidence = 0.70
        
        return round(confidence, 2)
    
    async def chat_with_ai(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """General AI chat interface for REIMS data"""
        
        if not self.is_available:
            return {
                "error": "LLM service not available",
                "response": "LLM service is not available. Please check Ollama installation.",
                "confidence": 0.0
            }
        
        try:
            # Build context-aware prompt
            system_prompt = """You are a commercial real estate AI assistant for REIMS (Real Estate Intelligence & Management System). 

You can help with:
- Property analysis and valuation
- Market intelligence and trends
- Tenant recommendations
- Financial modeling and analysis
- Risk assessment and alerts
- Document analysis and summarization

Provide accurate, professional advice based on real estate best practices. If you don't know something, say so rather than guessing."""
            
            user_prompt = query
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                user_prompt = f"Context: {context_str}\n\nQuery: {query}"
            
            response = self.ollama_client.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user',
                        'content': user_prompt
                    }
                ]
            )
            
            return {
                'response': response['message']['content'],
                'model': self.model_name,
                'timestamp': datetime.utcnow(),
                'confidence': 0.85  # High confidence for chat responses
            }
            
        except Exception as e:
            logger.error(f"Error in AI chat: {e}")
            return {
                "error": str(e),
                "response": "I'm sorry, I encountered an error processing your request.",
                "confidence": 0.0
            }
    
    async def analyze_market_intelligence(
        self,
        location: str,
        property_type: str = "commercial"
    ) -> Dict[str, Any]:
        """Analyze market intelligence for a location"""
        
        if not self.is_available:
            return {
                "error": "LLM service not available",
                "analysis": "LLM service is not available for market analysis.",
                "confidence": 0.0
            }
        
        try:
            prompt = f"""Analyze the commercial real estate market for {location} focusing on {property_type} properties.

Provide analysis on:

1. **Market Conditions**:
   - Current market trends and outlook
   - Supply and demand dynamics
   - Rental rates and vacancy trends

2. **Economic Factors**:
   - Employment growth and major employers
   - Population demographics and growth
   - Infrastructure developments

3. **Investment Opportunities**:
   - Value-add potential
   - Market gaps and opportunities
   - Risk factors to consider

4. **Tenant Recommendations**:
   - Ideal tenant types for the area
   - Market demand by business type
   - Lease term recommendations

Format as a structured analysis with specific insights and recommendations."""
            
            response = self.ollama_client.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a commercial real estate market analyst with expertise in local market conditions.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )
            
            return {
                'analysis': response['message']['content'],
                'location': location,
                'property_type': property_type,
                'model': self.model_name,
                'generated_at': datetime.utcnow(),
                'confidence': 0.80
            }
            
        except Exception as e:
            logger.error(f"Error in market intelligence analysis: {e}")
            return {
                "error": str(e),
                "analysis": "Error occurred during market analysis",
                "confidence": 0.0
            }

# Text splitter for long documents
class RecursiveCharacterTextSplitter:
    """Simple text splitter for long documents"""
    
    def __init__(self, chunk_size: int = 4000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to break at sentence boundary
            chunk = text[start:end]
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            
            if last_period > last_newline and last_period > start + self.chunk_size // 2:
                end = start + last_period + 1
                chunks.append(text[start:end])
                start = end - self.chunk_overlap
            else:
                chunks.append(chunk)
                start = end - self.chunk_overlap
        
        return chunks

# Global LLM service instance
llm_service = LLMService()
