"""
Filename Parser Utility
Extracts property name, year, document type, and period from filenames
"""
import re
from typing import Dict, Optional

class FilenameParser:
    """Parse financial document filenames for metadata extraction"""
    
    # Document type patterns (order matters - more specific first)
    DOCUMENT_TYPES = [
        "Income Statement",
        "Cash Flow Statement", 
        "Balance Sheet",
        "Offering Memorandum",
        "Rent Roll",
        "Operating Statement",
        "P&L",
        "Profit and Loss",
        "Financial Statement",
        "Annual Report",
        "Quarterly Report"
    ]
    
    # Period patterns
    PERIOD_PATTERNS = {
        r'\bQ1\b': 'Q1',
        r'\bQ2\b': 'Q2',
        r'\bQ3\b': 'Q3',
        r'\bQ4\b': 'Q4',
        r'\bJanuary\b': 'January',
        r'\bFebruary\b': 'February',
        r'\bMarch\b': 'March',
        r'\bApril\b': 'April',
        r'\bMay\b': 'May',
        r'\bJune\b': 'June',
        r'\bJuly\b': 'July',
        r'\bAugust\b': 'August',
        r'\bSeptember\b': 'September',
        r'\bOctober\b': 'October',
        r'\bNovember\b': 'November',
        r'\bDecember\b': 'December',
        r'\bAnnual\b': 'Annual',
        r'\bYearly\b': 'Annual',
        r'\bYTD\b': 'YTD',
    }
    
    @staticmethod
    def parse(filename: str) -> Dict[str, Optional[str]]:
        """
        Parse filename to extract metadata
        
        Args:
            filename: Original filename (e.g., "ESP 2024 Income Statement.pdf")
            
        Returns:
            Dict with keys: property_name, document_year, document_type, document_period
            
        Examples:
            >>> FilenameParser.parse("ESP 2024 Income Statement.pdf")
            {
                'property_name': 'ESP',
                'document_year': 2024,
                'document_type': 'Income Statement',
                'document_period': 'Annual'
            }
            
            >>> FilenameParser.parse("Empire State 2023 Q1 Balance Sheet.xlsx")
            {
                'property_name': 'Empire State',
                'document_year': 2023,
                'document_type': 'Balance Sheet',
                'document_period': 'Q1'
            }
        """
        result = {
            "property_name": None,
            "document_year": None,
            "document_type": None,
            "document_period": "Annual"  # Default
        }
        
        if not filename:
            return result
        
        # Remove file extension
        name_without_ext = re.sub(r'\.(pdf|xlsx?|csv|txt|docx?)$', '', filename, flags=re.IGNORECASE)
        
        # Extract year (4-digit number starting with 20)
        year_match = re.search(r'\b(20\d{2})\b', name_without_ext)
        if year_match:
            result["document_year"] = int(year_match.group(1))
            year_position = year_match.start()
        else:
            year_position = len(name_without_ext)
        
        # Extract period (quarterly, monthly, etc.)
        for pattern, period_name in FilenameParser.PERIOD_PATTERNS.items():
            if re.search(pattern, name_without_ext, re.IGNORECASE):
                result["document_period"] = period_name
                break
        
        # Extract document type
        for doc_type in FilenameParser.DOCUMENT_TYPES:
            if doc_type.lower() in name_without_ext.lower():
                result["document_type"] = doc_type
                # Remove document type from name for property extraction
                name_without_ext = name_without_ext.replace(doc_type, '')
                name_without_ext = name_without_ext.replace(doc_type.lower(), '')
                name_without_ext = name_without_ext.replace(doc_type.upper(), '')
                break
        
        # Extract property name (everything before the year, after removing type and period)
        if year_match:
            property_part = name_without_ext[:year_position]
        else:
            property_part = name_without_ext
        
        # Clean up property name
        # Remove period indicators
        for pattern in FilenameParser.PERIOD_PATTERNS.keys():
            property_part = re.sub(pattern, '', property_part, flags=re.IGNORECASE)
        
        # Remove extra whitespace and special characters
        property_part = re.sub(r'[_-]+', ' ', property_part)
        property_part = property_part.strip()
        property_part = re.sub(r'\s+', ' ', property_part)
        
        if property_part:
            result["property_name"] = property_part
        
        return result
    
    @staticmethod
    def suggest_property_id(property_name: str) -> str:
        """
        Generate a property ID from property name
        
        Args:
            property_name: Property name (e.g., "Empire State Plaza")
            
        Returns:
            Property ID (e.g., "ESP" or "EMPIRE-STATE-PLAZA")
        """
        if not property_name:
            return ""
        
        # Try to create acronym from capital letters
        capitals = ''.join([c for c in property_name if c.isupper()])
        if len(capitals) >= 2:
            return capitals
        
        # Otherwise, use kebab-case
        prop_id = property_name.upper()
        prop_id = re.sub(r'[^A-Z0-9]+', '-', prop_id)
        prop_id = prop_id.strip('-')
        return prop_id


# Convenience function
def parse_filename(filename: str) -> Dict[str, Optional[str]]:
    """Parse filename to extract metadata"""
    return FilenameParser.parse(filename)


# Test cases (if run directly)
if __name__ == "__main__":
    test_cases = [
        "ESP 2024 Income Statement.pdf",
        "ESP 2024 Cash Flow Statement.pdf",
        "ESP 2024 Balance Sheet.pdf",
        "Empire State Plaza 2023 Q1 Rent Roll.xlsx",
        "Downtown Tower 2022 Annual Report.pdf",
        "ABC Property 2024 Operating Statement.csv",
        "Property_123_2023_Balance_Sheet.xlsx",
    ]
    
    print("\nFilename Parser Test Cases")
    print("=" * 80)
    
    for filename in test_cases:
        result = parse_filename(filename)
        print(f"\nFilename: {filename}")
        print(f"  Property: {result['property_name']}")
        print(f"  Year: {result['document_year']}")
        print(f"  Type: {result['document_type']}")
        print(f"  Period: {result['document_period']}")
        
        if result['property_name']:
            prop_id = FilenameParser.suggest_property_id(result['property_name'])
            print(f"  Suggested ID: {prop_id}")
    
    print("\n" + "=" * 80)



