"""
Property Name Extraction Module

Extracts property names from PDF documents using various methods:
1. PDF header text extraction
2. Filename pattern matching
3. Document content analysis

Provides confidence scoring and multiple extraction strategies.
"""

import re
import logging
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PyPDF2 not available. PDF text extraction disabled.")

try:
    import fitz  # PyMuPDF
    MUPDF_AVAILABLE = True
except ImportError:
    MUPDF_AVAILABLE = False
    logging.warning("PyMuPDF not available. Advanced PDF extraction disabled.")

logger = logging.getLogger(__name__)

@dataclass
class PropertyNameResult:
    """Result of property name extraction"""
    name: str
    confidence: float  # 0.0 to 1.0
    method: str  # 'pdf_header', 'filename', 'content', 'manual'
    context: str  # Additional context about the extraction
    page_number: Optional[int] = None
    line_number: Optional[int] = None

class PropertyNameExtractor:
    """Extracts property names from documents using multiple strategies"""
    
    def __init__(self):
        self.patterns = self._load_name_patterns()
        self.abbreviations = self._load_abbreviations()
        
    def _load_name_patterns(self) -> Dict[str, str]:
        """Load regex patterns for property name extraction"""
        return {
            # Common property name patterns
            'property_header': r'(?:Property|Property Name|Property:)\s*:?\s*([A-Za-z\s&,.-]+?)(?:\s*\([A-Z]+\))?',
            'title_case': r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\([A-Z]+\)',
            'all_caps': r'^([A-Z\s]+?)\s*\([A-Z]+\)',
            'income_statement': r'([A-Za-z\s&,.-]+?)\s*Income\s*Statement',
            'balance_sheet': r'([A-Za-z\s&,.-]+?)\s*Balance\s*Sheet',
            'cash_flow': r'([A-Za-z\s&,.-]+?)\s*Cash\s*Flow',
            'rent_roll': r'([A-Za-z\s&,.-]+?)\s*Rent\s*Roll',
        }
    
    def _load_abbreviations(self) -> Dict[str, str]:
        """Load property abbreviation mappings"""
        return {
            'ESP': 'Eastern Shore Plaza',
            'TCSH': 'The Crossings of Spring Hill',
            'HA': 'Hammond Aire',
            'WC': 'Wendover Commons',
            'ES': 'Eastern Shore',
            'TC': 'The Crossings',
            'HAM': 'Hammond',
            'WEN': 'Wendover',
        }
    
    def extract_from_pdf(self, pdf_path: str, max_pages: int = 2) -> List[PropertyNameResult]:
        """Extract property names from PDF document"""
        results = []
        
        if not PDF_AVAILABLE and not MUPDF_AVAILABLE:
            logger.warning("No PDF libraries available")
            return results
            
        try:
            # Try PyMuPDF first (better text extraction)
            if MUPDF_AVAILABLE:
                results.extend(self._extract_with_pymupdf(pdf_path, max_pages))
            
            # Fallback to PyPDF2
            if not results and PDF_AVAILABLE:
                results.extend(self._extract_with_pypdf2(pdf_path, max_pages))
                
        except Exception as e:
            logger.error(f"Error extracting from PDF {pdf_path}: {e}")
            
        return results
    
    def _extract_with_pymupdf(self, pdf_path: str, max_pages: int) -> List[PropertyNameResult]:
        """Extract using PyMuPDF (better text extraction)"""
        results = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(min(max_pages, len(doc))):
                page = doc[page_num]
                text = page.get_text()
                
                # Extract property names from page text
                page_results = self._extract_from_text(text, f"page_{page_num + 1}")
                for result in page_results:
                    result.page_number = page_num + 1
                    results.append(result)
            
            doc.close()
            
        except Exception as e:
            logger.error(f"PyMuPDF extraction error: {e}")
            
        return results
    
    def _extract_with_pypdf2(self, pdf_path: str, max_pages: int) -> List[PropertyNameResult]:
        """Extract using PyPDF2 (fallback)"""
        results = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(min(max_pages, len(pdf_reader.pages))):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # Extract property names from page text
                    page_results = self._extract_from_text(text, f"page_{page_num + 1}")
                    for result in page_results:
                        result.page_number = page_num + 1
                        results.append(result)
                        
        except Exception as e:
            logger.error(f"PyPDF2 extraction error: {e}")
            
        return results
    
    def _extract_from_text(self, text: str, context: str) -> List[PropertyNameResult]:
        """Extract property names from text using regex patterns"""
        results = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Try each pattern
            for pattern_name, pattern in self.patterns.items():
                matches = re.finditer(pattern, line, re.IGNORECASE)
                
                for match in matches:
                    name = match.group(1).strip()
                    
                    # Clean up the name
                    name = self._clean_property_name(name)
                    
                    if self._is_valid_property_name(name):
                        confidence = self._calculate_confidence(name, pattern_name, line)
                        
                        result = PropertyNameResult(
                            name=name,
                            confidence=confidence,
                            method='pdf_header',
                            context=f"{context}, line {line_num + 1}",
                            line_number=line_num + 1
                        )
                        results.append(result)
        
        # Remove duplicates and sort by confidence
        unique_results = self._deduplicate_results(results)
        return sorted(unique_results, key=lambda x: x.confidence, reverse=True)
    
    def extract_from_filename(self, filename: str) -> List[PropertyNameResult]:
        """Extract property name from filename"""
        results = []
        
        # Remove file extension
        name_part = Path(filename).stem
        
        # Try to extract property name from filename patterns
        patterns = [
            r'^([A-Za-z\s&,.-]+?)\s*\([A-Z]+\)',  # "Property Name (ESP)"
            r'^([A-Za-z\s&,.-]+?)\s*-\s*\d{4}',   # "Property Name - 2024"
            r'^([A-Za-z\s&,.-]+?)\s*\d{4}',       # "Property Name 2024"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name_part, re.IGNORECASE)
            if match:
                name = self._clean_property_name(match.group(1))
                
                if self._is_valid_property_name(name):
                    confidence = 0.7  # Filename extraction is moderately reliable
                    
                    result = PropertyNameResult(
                        name=name,
                        confidence=confidence,
                        method='filename',
                        context=f"filename: {filename}"
                    )
                    results.append(result)
        
        # Check for abbreviations in filename
        for abbr, full_name in self.abbreviations.items():
            if abbr.upper() in name_part.upper():
                confidence = 0.8  # Abbreviation match is quite reliable
                
                result = PropertyNameResult(
                    name=full_name,
                    confidence=confidence,
                    method='filename',
                    context=f"abbreviation '{abbr}' in filename: {filename}"
                )
                results.append(result)
        
        return results
    
    def _clean_property_name(self, name: str) -> str:
        """Clean and normalize property name"""
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name.strip())
        
        # Remove common prefixes/suffixes
        name = re.sub(r'^(Property|Property Name|Property:)\s*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*\([A-Z]+\)$', '', name)  # Remove trailing (ESP)
        
        # Fix common issues
        name = re.sub(r'\s*,\s*$', '', name)  # Remove trailing comma
        name = re.sub(r'^\s*-\s*', '', name)  # Remove leading dash
        
        return name.strip()
    
    def _is_valid_property_name(self, name: str) -> bool:
        """Check if extracted name is a valid property name"""
        if not name or len(name) < 3:
            return False
            
        # Must contain letters
        if not re.search(r'[A-Za-z]', name):
            return False
            
        # Should not be common document words
        common_words = {
            'income', 'statement', 'balance', 'sheet', 'cash', 'flow',
            'rent', 'roll', 'financial', 'report', 'summary', 'analysis'
        }
        
        if name.lower() in common_words:
            return False
            
        return True
    
    def _calculate_confidence(self, name: str, pattern_name: str, context: str) -> float:
        """Calculate confidence score for extracted name"""
        confidence = 0.5  # Base confidence
        
        # Pattern-specific confidence
        pattern_scores = {
            'property_header': 0.9,
            'title_case': 0.8,
            'all_caps': 0.7,
            'income_statement': 0.8,
            'balance_sheet': 0.8,
            'cash_flow': 0.8,
            'rent_roll': 0.8,
        }
        
        confidence = pattern_scores.get(pattern_name, 0.5)
        
        # Boost confidence for known abbreviations
        for abbr, full_name in self.abbreviations.items():
            if abbr.upper() in name.upper() or full_name.lower() in name.lower():
                confidence = min(1.0, confidence + 0.2)
                break
        
        # Boost confidence for longer, more specific names
        if len(name) > 10:
            confidence = min(1.0, confidence + 0.1)
        
        # Reduce confidence for very short names
        if len(name) < 5:
            confidence = max(0.1, confidence - 0.2)
        
        return round(confidence, 2)
    
    def _deduplicate_results(self, results: List[PropertyNameResult]) -> List[PropertyNameResult]:
        """Remove duplicate results, keeping the highest confidence"""
        seen = {}
        
        for result in results:
            key = result.name.lower()
            
            if key not in seen or result.confidence > seen[key].confidence:
                seen[key] = result
        
        return list(seen.values())
    
    def get_best_match(self, results: List[PropertyNameResult]) -> Optional[PropertyNameResult]:
        """Get the best property name match from results"""
        if not results:
            return None
            
        # Sort by confidence and return the best
        sorted_results = sorted(results, key=lambda x: x.confidence, reverse=True)
        return sorted_results[0]
    
    def expand_abbreviation(self, name: str) -> str:
        """Expand known abbreviations in property name"""
        expanded = name
        
        for abbr, full_name in self.abbreviations.items():
            # Replace abbreviation with full name
            expanded = re.sub(
                rf'\b{re.escape(abbr)}\b',
                full_name,
                expanded,
                flags=re.IGNORECASE
            )
        
        return expanded

# Convenience functions for easy use
def extract_property_name_from_pdf(pdf_path: str) -> Optional[PropertyNameResult]:
    """Extract property name from PDF - convenience function"""
    extractor = PropertyNameExtractor()
    results = extractor.extract_from_pdf(pdf_path)
    return extractor.get_best_match(results)

def extract_property_name_from_filename(filename: str) -> Optional[PropertyNameResult]:
    """Extract property name from filename - convenience function"""
    extractor = PropertyNameExtractor()
    results = extractor.extract_from_filename(filename)
    return extractor.get_best_match(results)

def extract_property_name(file_path: str) -> Optional[PropertyNameResult]:
    """Extract property name from file (PDF or filename) - main function"""
    path = Path(file_path)
    
    if path.suffix.lower() == '.pdf':
        return extract_property_name_from_pdf(str(path))
    else:
        return extract_property_name_from_filename(path.name)
