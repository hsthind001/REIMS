import pandas as pd
import fitz  # PyMuPDF
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Document processing engine for different file types"""
    
    def __init__(self):
        self.supported_types = {
            '.csv': self.process_csv,
            '.xlsx': self.process_excel,
            '.xls': self.process_excel,
            '.pdf': self.process_pdf
        }
    
    def process(self, file_path: str, metadata: dict) -> dict:
        """Main processing entry point"""
        try:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension not in self.supported_types:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            processor = self.supported_types[file_extension]
            result = processor(file_path, metadata)
            
            # Add processing metadata
            result.update({
                "processing_timestamp": datetime.utcnow().isoformat(),
                "file_extension": file_extension,
                "processor_version": "1.0.0"
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            raise
    
    def process_csv(self, file_path: str, metadata: dict) -> dict:
        """Process CSV files and extract structured data"""
        try:
            # Read CSV with various encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            df = None
            used_encoding = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    used_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("Could not read CSV file with any supported encoding")
            
            # Basic data analysis
            analysis = {
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns),
                "data_types": df.dtypes.astype(str).to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "encoding_used": used_encoding
            }
            
            # Sample data (first 5 rows)
            sample_data = df.head().to_dict('records')
            
            # Detect potential property data patterns
            property_indicators = self._detect_property_patterns(df)
            
            # Convert DataFrame to JSON-serializable format
            full_data = df.to_dict('records')
            
            return {
                "type": "csv",
                "status": "processed",
                "analysis": analysis,
                "sample_data": sample_data,
                "property_indicators": property_indicators,
                "extracted_data": {
                    "records": full_data,
                    "summary": {
                        "total_records": len(full_data),
                        "columns": list(df.columns)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"CSV processing error: {str(e)}")
            return {
                "type": "csv",
                "status": "error",
                "error": str(e)
            }
    
    def process_excel(self, file_path: str, metadata: dict) -> dict:
        """Process Excel files (.xlsx, .xls)"""
        try:
            # Read Excel file and get all sheet names
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            sheets_data = {}
            total_rows = 0
            
            for sheet_name in sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    sheet_analysis = {
                        "row_count": len(df),
                        "column_count": len(df.columns),
                        "columns": list(df.columns),
                        "data_types": df.dtypes.astype(str).to_dict(),
                        "missing_values": df.isnull().sum().to_dict()
                    }
                    
                    # Sample data (first 3 rows for each sheet)
                    sample_data = df.head(3).to_dict('records')
                    
                    # Convert full data
                    full_data = df.to_dict('records')
                    total_rows += len(df)
                    
                    sheets_data[sheet_name] = {
                        "analysis": sheet_analysis,
                        "sample_data": sample_data,
                        "data": full_data,
                        "property_indicators": self._detect_property_patterns(df)
                    }
                    
                except Exception as e:
                    logger.warning(f"Error processing sheet {sheet_name}: {str(e)}")
                    sheets_data[sheet_name] = {
                        "error": str(e),
                        "status": "failed"
                    }
            
            return {
                "type": "excel",
                "status": "processed",
                "sheet_count": len(sheet_names),
                "sheet_names": sheet_names,
                "total_rows": total_rows,
                "extracted_data": {
                    "sheets": sheets_data,
                    "summary": {
                        "total_sheets": len(sheet_names),
                        "total_records": total_rows
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Excel processing error: {str(e)}")
            return {
                "type": "excel",
                "status": "error",
                "error": str(e)
            }
    
    def process_pdf(self, file_path: str, metadata: dict) -> dict:
        """Process PDF files and extract text content"""
        try:
            doc = fitz.open(file_path)
            
            pages_content = []
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                pages_content.append({
                    "page_number": page_num + 1,
                    "text": text,
                    "char_count": len(text),
                    "word_count": len(text.split()) if text else 0
                })
                
                full_text += text + "\n"
            
            # Store page count before closing
            page_count = len(doc)
            
            # Text analysis
            analysis = {
                "page_count": page_count,
                "total_characters": len(full_text),
                "total_words": len(full_text.split()),
                "average_words_per_page": len(full_text.split()) / page_count if page_count > 0 else 0
            }
            
            # Simple keyword extraction for real estate
            keywords = self._extract_keywords(full_text)
            
            # Close the document after all processing is done
            doc.close()
            
            return {
                "type": "pdf",
                "status": "processed",
                "analysis": analysis,
                "keywords": keywords,
                "extracted_data": {
                    "full_text": full_text,
                    "pages": pages_content,
                    "summary": analysis
                }
            }
            
        except Exception as e:
            logger.error(f"PDF processing error: {str(e)}")
            return {
                "type": "pdf",
                "status": "error",
                "error": str(e)
            }
    
    def _detect_property_patterns(self, df: pd.DataFrame) -> dict:
        """Detect real estate related patterns in data"""
        patterns = {
            "potential_property_columns": [],
            "potential_address_columns": [],
            "potential_value_columns": [],
            "potential_date_columns": []
        }
        
        for column in df.columns:
            column_lower = column.lower()
            
            # Property ID patterns
            if any(keyword in column_lower for keyword in ['property', 'prop', 'id', 'parcel']):
                patterns["potential_property_columns"].append(column)
            
            # Address patterns
            if any(keyword in column_lower for keyword in ['address', 'street', 'location', 'addr']):
                patterns["potential_address_columns"].append(column)
            
            # Value patterns
            if any(keyword in column_lower for keyword in ['value', 'price', 'amount', 'cost', 'rent']):
                patterns["potential_value_columns"].append(column)
            
            # Date patterns
            if any(keyword in column_lower for keyword in ['date', 'time', 'created', 'modified']):
                patterns["potential_date_columns"].append(column)
        
        return patterns
    
    def _extract_keywords(self, text: str) -> dict:
        """Extract real estate related keywords from text"""
        real_estate_keywords = [
            'property', 'real estate', 'house', 'apartment', 'condo', 'commercial',
            'residential', 'lease', 'rent', 'mortgage', 'deed', 'title',
            'appraisal', 'assessment', 'zoning', 'square feet', 'bedroom', 'bathroom'
        ]
        
        text_lower = text.lower()
        found_keywords = {}
        
        for keyword in real_estate_keywords:
            count = text_lower.count(keyword)
            if count > 0:
                found_keywords[keyword] = count
        
        return {
            "real_estate_keywords": found_keywords,
            "total_keyword_matches": sum(found_keywords.values())
        }

# Global processor instance
document_processor = DocumentProcessor()