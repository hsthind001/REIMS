"""
AI-powered document processing agents for REIMS
Provides intelligent data extraction and analysis for real estate documents
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import pandas as pd
from pathlib import Path

# Base agent class
class DocumentProcessingAgent:
    """Base class for all document processing agents"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")
        
    def process(self, content: Any, metadata: Dict) -> Dict[str, Any]:
        """Process document content and return structured data"""
        raise NotImplementedError("Subclasses must implement process method")
    
    def extract_patterns(self, text: str, patterns: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract data using regex patterns"""
        results = {}
        for key, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            results[key] = matches
        return results
    
    def validate_extraction(self, data: Dict) -> Dict[str, Any]:
        """Validate extracted data and add confidence scores"""
        validation_result = {
            "is_valid": True,
            "confidence_score": 0.0,
            "validation_errors": [],
            "validated_data": data
        }
        
        # Basic validation logic - can be overridden by subclasses
        if not data or not isinstance(data, dict):
            validation_result["is_valid"] = False
            validation_result["validation_errors"].append("Invalid data format")
            return validation_result
        
        # Calculate confidence based on data completeness
        total_fields = len(data)
        populated_fields = len([v for v in data.values() if v])
        validation_result["confidence_score"] = populated_fields / total_fields if total_fields > 0 else 0.0
        
        return validation_result

class FinancialStatementAgent(DocumentProcessingAgent):
    """Agent specialized in processing financial statements and reports"""
    
    def __init__(self):
        super().__init__(
            name="financial_statement_agent",
            description="Extracts financial data from income statements, balance sheets, and cash flow statements"
        )
        
        # Financial data patterns
        self.financial_patterns = {
            "revenue": [
                r"(?:total\s+)?revenue[:\s]*\$?([\d,]+\.?\d*)",
                r"(?:gross\s+)?income[:\s]*\$?([\d,]+\.?\d*)",
                r"sales[:\s]*\$?([\d,]+\.?\d*)"
            ],
            "expenses": [
                r"(?:total\s+)?expenses?[:\s]*\$?([\d,]+\.?\d*)",
                r"(?:operating\s+)?costs?[:\s]*\$?([\d,]+\.?\d*)",
                r"expenditures?[:\s]*\$?([\d,]+\.?\d*)"
            ],
            "net_income": [
                r"net\s+income[:\s]*\$?([\d,]+\.?\d*)",
                r"profit[:\s]*\$?([\d,]+\.?\d*)",
                r"earnings[:\s]*\$?([\d,]+\.?\d*)"
            ],
            "assets": [
                r"(?:total\s+)?assets[:\s]*\$?([\d,]+\.?\d*)",
                r"current\s+assets[:\s]*\$?([\d,]+\.?\d*)"
            ],
            "liabilities": [
                r"(?:total\s+)?liabilities[:\s]*\$?([\d,]+\.?\d*)",
                r"current\s+liabilities[:\s]*\$?([\d,]+\.?\d*)"
            ],
            "equity": [
                r"(?:total\s+)?equity[:\s]*\$?([\d,]+\.?\d*)",
                r"(?:shareholders?\s+)?equity[:\s]*\$?([\d,]+\.?\d*)"
            ]
        }
    
    def process(self, content: Any, metadata: Dict) -> Dict[str, Any]:
        """Process financial statement content"""
        try:
            if isinstance(content, str):
                # PDF text content
                return self._process_text_content(content, metadata)
            elif isinstance(content, pd.DataFrame):
                # Excel/CSV content
                return self._process_tabular_content(content, metadata)
            else:
                return self._create_error_result("Unsupported content type")
                
        except Exception as e:
            self.logger.error(f"Error processing financial content: {e}")
            return self._create_error_result(str(e))
    
    def _process_text_content(self, text: str, metadata: Dict) -> Dict[str, Any]:
        """Process text-based financial content"""
        extracted_data = {}
        
        # Extract financial metrics using patterns
        for metric, patterns in self.financial_patterns.items():
            values = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                values.extend(matches)
            
            if values:
                # Clean and parse numeric values
                cleaned_values = []
                for value in values:
                    try:
                        # Remove commas and convert to float
                        numeric_value = float(value.replace(',', ''))
                        cleaned_values.append(numeric_value)
                    except (ValueError, AttributeError):
                        continue
                
                if cleaned_values:
                    extracted_data[metric] = {
                        "values": cleaned_values,
                        "primary_value": cleaned_values[0],  # First found value
                        "currency": "USD"  # Default assumption
                    }
        
        # Extract dates
        date_patterns = [
            r"(?:as of|for the year ending|period ending)\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
            r"(\d{1,2}/\d{1,2}/\d{4})",
            r"(\d{4}-\d{2}-\d{2})"
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        if dates:
            extracted_data["report_dates"] = dates
        
        # Calculate derived metrics
        if "revenue" in extracted_data and "expenses" in extracted_data:
            revenue = extracted_data["revenue"]["primary_value"]
            expenses = extracted_data["expenses"]["primary_value"]
            extracted_data["gross_profit"] = {
                "value": revenue - expenses,
                "calculation": f"Revenue ({revenue}) - Expenses ({expenses})",
                "currency": "USD"
            }
        
        if "assets" in extracted_data and "liabilities" in extracted_data:
            assets = extracted_data["assets"]["primary_value"]
            liabilities = extracted_data["liabilities"]["primary_value"]
            extracted_data["net_worth"] = {
                "value": assets - liabilities,
                "calculation": f"Assets ({assets}) - Liabilities ({liabilities})",
                "currency": "USD"
            }
        
        return {
            "agent": self.name,
            "extraction_type": "financial_statement",
            "extracted_data": extracted_data,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "source_type": "text",
            "validation": self.validate_extraction(extracted_data)
        }
    
    def _process_tabular_content(self, df: pd.DataFrame, metadata: Dict) -> Dict[str, Any]:
        """Process tabular financial data"""
        extracted_data = {}
        
        # Look for financial data in column names and values
        for column in df.columns:
            column_lower = column.lower()
            
            # Check if column contains financial indicators
            for metric in self.financial_patterns.keys():
                if metric.replace('_', ' ') in column_lower or metric in column_lower:
                    # Extract numeric values from this column
                    numeric_values = []
                    for value in df[column]:
                        if pd.notna(value):
                            try:
                                # Try to extract numbers from strings
                                if isinstance(value, str):
                                    numbers = re.findall(r'[\d,]+\.?\d*', str(value))
                                    for num in numbers:
                                        numeric_values.append(float(num.replace(',', '')))
                                elif isinstance(value, (int, float)):
                                    numeric_values.append(float(value))
                            except (ValueError, TypeError):
                                continue
                    
                    if numeric_values:
                        extracted_data[metric] = {
                            "values": numeric_values,
                            "primary_value": numeric_values[0],
                            "column_source": column,
                            "currency": "USD"
                        }
        
        # Look for account names and values in row data
        if len(df.columns) >= 2:
            account_col = df.columns[0]  # Assume first column is account names
            value_col = df.columns[1]    # Assume second column is values
            
            for idx, row in df.iterrows():
                account_name = str(row[account_col]).lower()
                account_value = row[value_col]
                
                # Match account names to financial metrics
                for metric, patterns in self.financial_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern.replace(r'[:\s]*\$?([\d,]+\.?\d*)', ''), account_name, re.IGNORECASE):
                            try:
                                if isinstance(account_value, str):
                                    numeric_value = float(re.sub(r'[^\d.-]', '', account_value))
                                else:
                                    numeric_value = float(account_value)
                                
                                if metric not in extracted_data:
                                    extracted_data[metric] = {
                                        "values": [numeric_value],
                                        "primary_value": numeric_value,
                                        "account_source": account_name,
                                        "currency": "USD"
                                    }
                                break
                            except (ValueError, TypeError):
                                continue
        
        return {
            "agent": self.name,
            "extraction_type": "financial_statement",
            "extracted_data": extracted_data,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "source_type": "tabular",
            "data_shape": {"rows": len(df), "columns": len(df.columns)},
            "validation": self.validate_extraction(extracted_data)
        }
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result structure"""
        return {
            "agent": self.name,
            "extraction_type": "financial_statement",
            "error": error_message,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "extracted_data": {},
            "validation": {"is_valid": False, "confidence_score": 0.0}
        }

class PropertyDataAgent(DocumentProcessingAgent):
    """Agent specialized in extracting property-specific data"""
    
    def __init__(self):
        super().__init__(
            name="property_data_agent",
            description="Extracts property information including addresses, valuations, and characteristics"
        )
        
        self.property_patterns = {
            "addresses": [
                r"(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Circle|Cir),?\s*[A-Za-z\s]*,?\s*[A-Z]{2}\s*\d{5})",
                r"(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Circle|Cir))"
            ],
            "property_values": [
                r"(?:property\s+)?(?:value|worth|valuation)[:\s]*\$?([\d,]+\.?\d*)",
                r"(?:market\s+)?(?:price|value)[:\s]*\$?([\d,]+\.?\d*)",
                r"apprais(?:ed|al)\s+(?:value|at)[:\s]*\$?([\d,]+\.?\d*)"
            ],
            "square_footage": [
                r"([\d,]+\.?\d*)\s*(?:square\s*feet|sq\.?\s*ft\.?|sqft)",
                r"(?:size|area)[:\s]*([\d,]+\.?\d*)\s*(?:square\s*feet|sq\.?\s*ft\.?|sqft)"
            ],
            "bedrooms": [
                r"(\d+)\s*(?:bedroom|bed|br)",
                r"(?:bedroom|bed|br)[:\s]*(\d+)"
            ],
            "bathrooms": [
                r"(\d+(?:\.\d+)?)\s*(?:bathroom|bath|ba)",
                r"(?:bathroom|bath|ba)[:\s]*(\d+(?:\.\d+)?)"
            ],
            "property_type": [
                r"(?:property\s+type|type)[:\s]*([A-Za-z\s]+)",
                r"(residential|commercial|industrial|mixed.use|retail|office|warehouse)"
            ],
            "lot_size": [
                r"lot\s+size[:\s]*([\d,]+\.?\d*)\s*(?:acres?|sq\.?\s*ft\.?|square\s*feet)",
                r"([\d,]+\.?\d*)\s*acres?"
            ]
        }
    
    def process(self, content: Any, metadata: Dict) -> Dict[str, Any]:
        """Process property data content"""
        try:
            if isinstance(content, str):
                return self._process_text_content(content, metadata)
            elif isinstance(content, pd.DataFrame):
                return self._process_tabular_content(content, metadata)
            else:
                return self._create_error_result("Unsupported content type")
                
        except Exception as e:
            self.logger.error(f"Error processing property content: {e}")
            return self._create_error_result(str(e))
    
    def _process_text_content(self, text: str, metadata: Dict) -> Dict[str, Any]:
        """Process text-based property content"""
        extracted_data = {}
        
        # Extract property data using patterns
        for data_type, patterns in self.property_patterns.items():
            values = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                values.extend(matches)
            
            if values:
                if data_type in ["property_values", "square_footage", "lot_size"]:
                    # Numeric data - clean and convert
                    numeric_values = []
                    for value in values:
                        try:
                            numeric_value = float(str(value).replace(',', ''))
                            numeric_values.append(numeric_value)
                        except (ValueError, AttributeError):
                            continue
                    if numeric_values:
                        extracted_data[data_type] = {
                            "values": numeric_values,
                            "primary_value": numeric_values[0]
                        }
                elif data_type in ["bedrooms", "bathrooms"]:
                    # Integer data
                    integer_values = []
                    for value in values:
                        try:
                            integer_value = int(float(value))
                            integer_values.append(integer_value)
                        except (ValueError, AttributeError):
                            continue
                    if integer_values:
                        extracted_data[data_type] = {
                            "values": integer_values,
                            "primary_value": integer_values[0]
                        }
                else:
                    # Text data
                    extracted_data[data_type] = {
                        "values": list(set(values)),  # Remove duplicates
                        "primary_value": values[0]
                    }
        
        # Calculate price per square foot if we have both values
        if "property_values" in extracted_data and "square_footage" in extracted_data:
            property_value = extracted_data["property_values"]["primary_value"]
            sqft = extracted_data["square_footage"]["primary_value"]
            if sqft > 0:
                extracted_data["price_per_sqft"] = {
                    "value": round(property_value / sqft, 2),
                    "calculation": f"${property_value:,.0f} / {sqft:,.0f} sqft",
                    "currency": "USD"
                }
        
        return {
            "agent": self.name,
            "extraction_type": "property_data",
            "extracted_data": extracted_data,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "source_type": "text",
            "validation": self.validate_extraction(extracted_data)
        }
    
    def _process_tabular_content(self, df: pd.DataFrame, metadata: Dict) -> Dict[str, Any]:
        """Process tabular property data"""
        extracted_data = {}
        
        # Map common column names to our data types
        column_mappings = {
            "address": "addresses",
            "location": "addresses",
            "property_address": "addresses",
            "price": "property_values",
            "value": "property_values",
            "cost": "property_values",
            "square_feet": "square_footage",
            "sqft": "square_footage",
            "area": "square_footage",
            "bedrooms": "bedrooms",
            "beds": "bedrooms",
            "bathrooms": "bathrooms",
            "baths": "bathrooms",
            "type": "property_type",
            "property_type": "property_type",
            "lot_size": "lot_size",
            "acreage": "lot_size"
        }
        
        # Process each column
        for column in df.columns:
            column_lower = column.lower().replace(' ', '_')
            
            # Find matching data type
            data_type = None
            for col_key, mapped_type in column_mappings.items():
                if col_key in column_lower:
                    data_type = mapped_type
                    break
            
            if data_type:
                values = []
                for value in df[column]:
                    if pd.notna(value):
                        if data_type in ["property_values", "square_footage", "lot_size"]:
                            # Extract numeric values
                            try:
                                if isinstance(value, str):
                                    # Remove currency symbols and commas
                                    cleaned = re.sub(r'[^\d.-]', '', str(value))
                                    if cleaned:
                                        values.append(float(cleaned))
                                elif isinstance(value, (int, float)):
                                    values.append(float(value))
                            except (ValueError, TypeError):
                                continue
                        elif data_type in ["bedrooms", "bathrooms"]:
                            # Extract integer values
                            try:
                                if isinstance(value, str):
                                    numbers = re.findall(r'\d+', str(value))
                                    if numbers:
                                        values.append(int(numbers[0]))
                                elif isinstance(value, (int, float)):
                                    values.append(int(value))
                            except (ValueError, TypeError):
                                continue
                        else:
                            # Text values
                            values.append(str(value).strip())
                
                if values:
                    extracted_data[data_type] = {
                        "values": values,
                        "primary_value": values[0],
                        "column_source": column
                    }
        
        # Extract individual property records
        property_records = []
        for idx, row in df.iterrows():
            record = {"record_id": idx}
            for column in df.columns:
                column_lower = column.lower().replace(' ', '_')
                for col_key, mapped_type in column_mappings.items():
                    if col_key in column_lower:
                        record[mapped_type] = row[column]
                        break
            if len(record) > 1:  # More than just record_id
                property_records.append(record)
        
        if property_records:
            extracted_data["property_records"] = property_records
        
        return {
            "agent": self.name,
            "extraction_type": "property_data",
            "extracted_data": extracted_data,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "source_type": "tabular",
            "data_shape": {"rows": len(df), "columns": len(df.columns)},
            "record_count": len(property_records),
            "validation": self.validate_extraction(extracted_data)
        }
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result structure"""
        return {
            "agent": self.name,
            "extraction_type": "property_data",
            "error": error_message,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "extracted_data": {},
            "validation": {"is_valid": False, "confidence_score": 0.0}
        }

class DocumentClassificationAgent(DocumentProcessingAgent):
    """Agent specialized in classifying and categorizing documents"""
    
    def __init__(self):
        super().__init__(
            name="document_classification_agent",
            description="Classifies documents by type and identifies key content categories"
        )
        
        self.document_type_indicators = {
            "financial_statement": [
                "income statement", "balance sheet", "cash flow", "profit and loss",
                "revenue", "expenses", "assets", "liabilities", "equity"
            ],
            "property_listing": [
                "for sale", "for rent", "bedrooms", "bathrooms", "square feet",
                "listing price", "mls", "property description"
            ],
            "lease_agreement": [
                "lease", "tenant", "landlord", "rent", "monthly payment",
                "security deposit", "lease term", "rental agreement"
            ],
            "property_deed": [
                "deed", "grantor", "grantee", "conveys", "property description",
                "legal description", "notarized", "recorded"
            ],
            "appraisal_report": [
                "appraisal", "appraised value", "market value", "comparable sales",
                "property valuation", "fair market value"
            ],
            "tax_assessment": [
                "tax assessment", "assessed value", "property tax", "millage rate",
                "exemptions", "tax bill", "assessment notice"
            ],
            "inspection_report": [
                "inspection", "property condition", "defects", "recommendations",
                "safety", "structural", "electrical", "plumbing"
            ]
        }
    
    def process(self, content: Any, metadata: Dict) -> Dict[str, Any]:
        """Classify document content"""
        try:
            if isinstance(content, str):
                return self._classify_text_content(content, metadata)
            elif isinstance(content, pd.DataFrame):
                return self._classify_tabular_content(content, metadata)
            else:
                return self._create_error_result("Unsupported content type")
                
        except Exception as e:
            self.logger.error(f"Error classifying document: {e}")
            return self._create_error_result(str(e))
    
    def _classify_text_content(self, text: str, metadata: Dict) -> Dict[str, Any]:
        """Classify text-based document content"""
        text_lower = text.lower()
        classification_scores = {}
        
        # Calculate scores for each document type
        for doc_type, indicators in self.document_type_indicators.items():
            score = 0
            matched_indicators = []
            
            for indicator in indicators:
                if indicator.lower() in text_lower:
                    score += 1
                    matched_indicators.append(indicator)
            
            # Normalize score by number of indicators
            normalized_score = score / len(indicators)
            
            if score > 0:
                classification_scores[doc_type] = {
                    "score": normalized_score,
                    "matched_indicators": matched_indicators,
                    "match_count": score
                }
        
        # Determine primary classification
        if classification_scores:
            primary_type = max(classification_scores.keys(), 
                             key=lambda k: classification_scores[k]["score"])
            confidence = classification_scores[primary_type]["score"]
        else:
            primary_type = "unknown"
            confidence = 0.0
        
        # Extract additional content characteristics
        characteristics = self._analyze_content_characteristics(text)
        
        return {
            "agent": self.name,
            "extraction_type": "document_classification",
            "primary_classification": primary_type,
            "confidence_score": confidence,
            "all_classifications": classification_scores,
            "content_characteristics": characteristics,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "source_type": "text"
        }
    
    def _classify_tabular_content(self, df: pd.DataFrame, metadata: Dict) -> Dict[str, Any]:
        """Classify tabular document content"""
        # Analyze column names and data to determine document type
        columns_text = " ".join(df.columns).lower()
        
        # Also analyze a sample of the data
        sample_data = ""
        for col in df.columns[:5]:  # Check first 5 columns
            sample_values = df[col].dropna().head(10)  # First 10 non-null values
            sample_data += " " + " ".join(str(v) for v in sample_values)
        
        combined_text = columns_text + " " + sample_data.lower()
        
        classification_scores = {}
        
        # Calculate scores for each document type
        for doc_type, indicators in self.document_type_indicators.items():
            score = 0
            matched_indicators = []
            
            for indicator in indicators:
                if indicator.lower() in combined_text:
                    score += 1
                    matched_indicators.append(indicator)
            
            normalized_score = score / len(indicators)
            
            if score > 0:
                classification_scores[doc_type] = {
                    "score": normalized_score,
                    "matched_indicators": matched_indicators,
                    "match_count": score
                }
        
        # Determine primary classification
        if classification_scores:
            primary_type = max(classification_scores.keys(), 
                             key=lambda k: classification_scores[k]["score"])
            confidence = classification_scores[primary_type]["score"]
        else:
            # Default classification for tabular data
            if any(col.lower() in ["property", "address", "price", "bedrooms"] for col in df.columns):
                primary_type = "property_data"
                confidence = 0.5
            elif any(col.lower() in ["revenue", "income", "assets", "expenses"] for col in df.columns):
                primary_type = "financial_data"
                confidence = 0.5
            else:
                primary_type = "data_table"
                confidence = 0.3
        
        # Analyze data structure
        data_characteristics = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "has_numeric_data": any(df.dtypes == 'float64') or any(df.dtypes == 'int64'),
            "has_date_columns": any('date' in col.lower() for col in df.columns),
            "completeness": {col: (df[col].notna().sum() / len(df)) for col in df.columns}
        }
        
        return {
            "agent": self.name,
            "extraction_type": "document_classification",
            "primary_classification": primary_type,
            "confidence_score": confidence,
            "all_classifications": classification_scores,
            "data_characteristics": data_characteristics,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "source_type": "tabular"
        }
    
    def _analyze_content_characteristics(self, text: str) -> Dict[str, Any]:
        """Analyze general characteristics of text content"""
        words = text.split()
        
        return {
            "word_count": len(words),
            "character_count": len(text),
            "average_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "has_monetary_values": bool(re.search(r'\$[\d,]+', text)),
            "has_dates": bool(re.search(r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}', text)),
            "has_addresses": bool(re.search(r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd)', text, re.IGNORECASE)),
            "has_phone_numbers": bool(re.search(r'\(\d{3}\)\s*\d{3}-\d{4}|\d{3}-\d{3}-\d{4}', text)),
            "language": "en",  # Default assumption
            "formality_score": self._calculate_formality_score(text)
        }
    
    def _calculate_formality_score(self, text: str) -> float:
        """Calculate a simple formality score based on content"""
        formal_indicators = [
            "hereby", "whereas", "therefore", "pursuant", "notwithstanding",
            "heretofore", "aforementioned", "undersigned", "witnesseth"
        ]
        
        text_lower = text.lower()
        formal_count = sum(1 for indicator in formal_indicators if indicator in text_lower)
        
        # Normalize by text length (per 1000 words)
        words = len(text.split())
        if words > 0:
            return min(formal_count / (words / 1000), 1.0)
        return 0.0
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result structure"""
        return {
            "agent": self.name,
            "extraction_type": "document_classification",
            "error": error_message,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "primary_classification": "error",
            "confidence_score": 0.0
        }

# Agent registry and factory
class AgentRegistry:
    """Registry for managing document processing agents"""
    
    def __init__(self):
        self.agents = {}
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register the default set of agents"""
        self.register_agent(FinancialStatementAgent())
        self.register_agent(PropertyDataAgent())
        self.register_agent(DocumentClassificationAgent())
    
    def register_agent(self, agent: DocumentProcessingAgent):
        """Register a new agent"""
        self.agents[agent.name] = agent
    
    def get_agent(self, name: str) -> Optional[DocumentProcessingAgent]:
        """Get an agent by name"""
        return self.agents.get(name)
    
    def get_all_agents(self) -> Dict[str, DocumentProcessingAgent]:
        """Get all registered agents"""
        return self.agents.copy()
    
    def process_with_all_agents(self, content: Any, metadata: Dict) -> Dict[str, Any]:
        """Process content with all registered agents"""
        results = {}
        
        for agent_name, agent in self.agents.items():
            try:
                result = agent.process(content, metadata)
                results[agent_name] = result
            except Exception as e:
                results[agent_name] = {
                    "agent": agent_name,
                    "error": str(e),
                    "processing_timestamp": datetime.utcnow().isoformat()
                }
        
        return {
            "processing_summary": {
                "agents_used": list(self.agents.keys()),
                "successful_agents": len([r for r in results.values() if "error" not in r]),
                "failed_agents": len([r for r in results.values() if "error" in r]),
                "total_processing_time": datetime.utcnow().isoformat()
            },
            "agent_results": results
        }

# Global agent registry instance
agent_registry = AgentRegistry()