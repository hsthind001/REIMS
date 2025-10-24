#!/usr/bin/env python3
"""
Financial data extraction from PDF documents
"""
import fitz  # PyMuPDF
import re
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialExtractor:
    """Base class for financial document extraction"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.text = self._extract_full_text()
    
    def _extract_full_text(self) -> str:
        """Extract all text from PDF"""
        text = ""
        for page in self.doc:
            text += page.get_text()
        return text
    
    def _parse_currency(self, text: str) -> Optional[Decimal]:
        """Parse currency value from text"""
        # Remove commas, dollar signs, and spaces
        cleaned = re.sub(r'[$,\s]', '', text)
        # Handle parentheses as negative
        if '(' in cleaned:
            cleaned = '-' + cleaned.replace('(', '').replace(')', '')
        try:
            return Decimal(cleaned)
        except:
            return None
    
    def _search_for_value(self, label_pattern: str, context_lines: int = 2) -> Optional[Decimal]:
        """Search for a financial value near a label"""
        lines = self.text.split('\n')
        for i, line in enumerate(lines):
            if re.search(label_pattern, line, re.IGNORECASE):
                # Search in current line and next few lines
                search_area = '\n'.join(lines[i:i+context_lines+1])
                # Find numbers in the search area
                numbers = re.findall(r'\$?[\d,]+\.?\d*', search_area)
                for num in numbers:
                    value = self._parse_currency(num)
                    if value and abs(value) > 0:
                        return value
        return None
    
    def close(self):
        """Close the PDF document"""
        if self.doc:
            self.doc.close()

class BalanceSheetExtractor(FinancialExtractor):
    """Extract data from Balance Sheet"""
    
    def extract(self) -> Dict:
        """Extract balance sheet data"""
        logger.info(f"Extracting Balance Sheet from {self.pdf_path}")
        
        data = {
            'total_assets': self._search_for_value(r'total\s+assets'),
            'property_and_equipment': self._search_for_value(r'total\s+property\s+(&|and)\s+equipment'),
            'current_assets': self._search_for_value(r'current\s+assets'),
            'fixed_assets': self._search_for_value(r'(fixed|property|plant|equipment)\s+assets'),
            'total_liabilities': self._search_for_value(r'total\s+liabilities'),
            'current_liabilities': self._search_for_value(r'current\s+liabilities'),
            'long_term_debt': self._search_for_value(r'long[- ]term\s+(debt|liabilities)'),
            'total_equity': self._search_for_value(r'(total\s+)?(stockholders?|shareholders?)?\'?\s*equity'),
        }
        
        # If property_and_equipment not found directly, try to calculate it
        if not data.get('property_and_equipment'):
            # Look for property-related assets and depreciation
            property_items = self._search_for_value(r'(land|buildings?|improvements?|roof|hvac|parking)')
            depreciation = self._search_for_value(r'accum.*depr')
            if property_items and depreciation:
                data['property_and_equipment'] = property_items + depreciation  # depreciation is negative
        
        # Calculate derived metrics
        if data['total_assets'] and data['total_liabilities']:
            # Debt-to-Equity Ratio
            if data['total_equity'] and data['total_equity'] != 0:
                data['debt_to_equity_ratio'] = float(data['total_liabilities'] / data['total_equity'])
        
        if data['current_assets'] and data['current_liabilities']:
            # Current Ratio
            if data['current_liabilities'] != 0:
                data['current_ratio'] = float(data['current_assets'] / data['current_liabilities'])
        
        # Convert Decimals to float for JSON serialization
        return {k: float(v) if isinstance(v, Decimal) else v for k, v in data.items() if v is not None}

class IncomeStatementExtractor(FinancialExtractor):
    """Extract data from Income Statement"""
    
    def extract(self) -> Dict:
        """Extract income statement data"""
        logger.info(f"Extracting Income Statement from {self.pdf_path}")
        
        data = {
            'total_revenue': self._search_for_value(r'total\s+(revenue|income)'),
            'rental_revenue': self._search_for_value(r'rental\s+(revenue|income)'),
            'gross_profit': self._search_for_value(r'gross\s+profit'),
            'operating_expenses': self._search_for_value(r'(total\s+)?operating\s+expenses'),
            'net_operating_income': self._search_for_value(r'net\s+operating\s+income|NOI'),
            'net_income': self._search_for_value(r'net\s+income'),
            'ebitda': self._search_for_value(r'EBITDA'),
        }
        
        # Calculate NOI if not directly found
        if not data['net_operating_income'] and data['total_revenue'] and data['operating_expenses']:
            data['net_operating_income'] = data['total_revenue'] - data['operating_expenses']
        
        # Calculate profit margins
        if data['net_income'] and data['total_revenue'] and data['total_revenue'] != 0:
            data['profit_margin'] = float((data['net_income'] / data['total_revenue']) * 100)
        
        if data['net_operating_income'] and data['total_revenue'] and data['total_revenue'] != 0:
            data['operating_margin'] = float((data['net_operating_income'] / data['total_revenue']) * 100)
        
        # Convert Decimals to float
        return {k: float(v) if isinstance(v, Decimal) else v for k, v in data.items() if v is not None}

class CashFlowExtractor(FinancialExtractor):
    """Extract data from Cash Flow Statement"""
    
    def extract(self) -> Dict:
        """Extract cash flow data"""
        logger.info(f"Extracting Cash Flow from {self.pdf_path}")
        
        data = {
            'operating_cash_flow': self._search_for_value(r'(net\s+)?cash\s+(from|provided\s+by)\s+operating'),
            'investing_cash_flow': self._search_for_value(r'cash\s+(from|used\s+in)\s+investing'),
            'financing_cash_flow': self._search_for_value(r'cash\s+(from|used\s+in)\s+financing'),
            'net_cash_flow': self._search_for_value(r'net\s+(increase|decrease|change)\s+in\s+cash'),
            'beginning_cash': self._search_for_value(r'(cash|beginning)\s+(at\s+)?beginning'),
            'ending_cash': self._search_for_value(r'(cash|ending)\s+(at\s+)?end'),
        }
        
        # Convert Decimals to float
        return {k: float(v) if isinstance(v, Decimal) else v for k, v in data.items() if v is not None}

class RentRollExtractor(FinancialExtractor):
    """Extract data from Rent Roll"""
    
    def extract(self) -> Dict:
        """Extract rent roll data"""
        logger.info(f"Extracting Rent Roll from {self.pdf_path}")
        
        tenants = []
        lines = self.text.split('\n')
        
        # Try to extract tenant data (simplified approach)
        # Real implementation would need more sophisticated parsing
        for line in lines:
            # Look for lines with unit numbers and dollar amounts
            unit_match = re.search(r'(\d+[A-Z]?)\s+', line)
            rent_match = re.search(r'\$\s*[\d,]+\.?\d*', line)
            sqft_match = re.search(r'(\d{2,5})\s*(?:sf|sq\.?\s*ft)', line, re.IGNORECASE)
            
            if unit_match and rent_match:
                tenant = {
                    'unit_number': unit_match.group(1),
                    'monthly_rent': float(self._parse_currency(rent_match.group()) or 0),
                }
                if sqft_match:
                    tenant['sqft'] = int(sqft_match.group(1))
                tenants.append(tenant)
        
        # Calculate summary metrics
        total_units = len(tenants)
        occupied_units = sum(1 for t in tenants if t.get('monthly_rent', 0) > 0)
        total_rent = sum(t.get('monthly_rent', 0) for t in tenants)
        
        return {
            'tenants': tenants,
            'total_units': total_units,
            'occupied_units': occupied_units,
            'vacancy_count': total_units - occupied_units,
            'occupancy_rate': (occupied_units / total_units * 100) if total_units > 0 else 0,
            'total_monthly_rent': total_rent,
            'annual_rental_income': total_rent * 12,
        }

def extract_financial_document(pdf_path: str, document_type: str) -> Dict:
    """
    Main extraction function - routes to appropriate extractor
    
    Args:
        pdf_path: Path to PDF file
        document_type: Type of document (balance_sheet, income_statement, etc.)
    
    Returns:
        Dict with extracted data
    """
    try:
        if document_type == 'balance_sheet':
            extractor = BalanceSheetExtractor(pdf_path)
        elif document_type == 'income_statement':
            extractor = IncomeStatementExtractor(pdf_path)
        elif document_type == 'cash_flow_statement':
            extractor = CashFlowExtractor(pdf_path)
        elif document_type == 'rent_roll':
            extractor = RentRollExtractor(pdf_path)
        else:
            logger.warning(f"Unknown document type: {document_type}")
            return {}
        
        data = extractor.extract()
        extractor.close()
        return data
    
    except Exception as e:
        logger.error(f"Error extracting {pdf_path}: {e}")
        return {}

if __name__ == "__main__":
    # Test extraction
    import sys
    if len(sys.argv) > 2:
        pdf_path = sys.argv[1]
        doc_type = sys.argv[2]
        result = extract_financial_document(pdf_path, doc_type)
        import json
        print(json.dumps(result, indent=2))

