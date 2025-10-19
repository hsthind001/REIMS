#!/usr/bin/env python3
"""
Rent Roll Parser Module
Parses rent roll documents in various formats (PDF, Excel, CSV)
and extracts structured unit/tenant data
"""

import re
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RentRollParser:
    """
    Universal rent roll parser supporting multiple formats
    """
    
    def __init__(self):
        # Common rent roll field patterns
        self.field_patterns = {
            'unit_number': r'(?:unit|suite|space|store)[\s#:]*([A-Z0-9/-]+)',
            'tenant_name': r'tenant[\s:]*(.+)',
            'sqft': r'(?:sq\.?\s*ft\.?|area|size)[\s:]*([0-9,]+\.?\d*)',
            'monthly_rent': r'(?:monthly|month)[\s]+(?:rent|payment)[\s:]*\$?\s*([0-9,]+\.?\d*)',
            'annual_rent': r'(?:annual|yearly)[\s]+rent[\s:]*\$?\s*([0-9,]+\.?\d*)',
            'lease_start': r'(?:lease[\s]+start|from)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'lease_end': r'(?:lease[\s]+end|to|expires)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        }
        
        # Rent roll detection keywords
        self.rent_roll_indicators = [
            'rent roll', 'tenancy schedule', 'tenant roster', 'lease status',
            'occupancy schedule', 'tenant list', 'rental schedule'
        ]
        
        # Exclusion patterns (not actual leases)
        self.exclusion_patterns = [
            r'\[NAP\]', r'NAP-Exp', r'Expense Only', r'Common Area',
            r'Vacant.*0\.00.*0\.00', r'Total.*\d+\.\d+.*\d+\.\d+'
        ]
    
    def is_rent_roll(self, text: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Detect if document is a rent roll
        """
        text_lower = text.lower()
        
        # Check for rent roll indicators
        indicator_count = sum(1 for indicator in self.rent_roll_indicators 
                             if indicator in text_lower)
        
        # Check for typical rent roll structure
        has_unit_numbers = bool(re.search(r'unit\s*(?:#|number)?[\s:]+\d+', text_lower))
        has_tenant_list = text_lower.count('tenant') > 3
        has_rent_amounts = text_lower.count('rent') > 5 or text_lower.count('$') > 10
        
        # Check metadata if provided
        doc_type_match = False
        if metadata:
            filename = metadata.get('original_filename', '').lower()
            doc_type = metadata.get('document_type', '').lower()
            doc_type_match = 'rent' in filename or 'tenancy' in filename or 'rent' in doc_type
        
        return (indicator_count >= 1 or 
                (has_unit_numbers and has_tenant_list and has_rent_amounts) or 
                doc_type_match)
    
    def parse(self, data: Any, format_type: str = 'pdf', metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Parse rent roll data from various formats
        
        Args:
            data: Text string (PDF), DataFrame (Excel), or file path (CSV)
            format_type: 'pdf', 'excel', or 'csv'
            metadata: Optional metadata about the document
        
        Returns:
            Dictionary with parsed units and summary information
        """
        try:
            if format_type == 'pdf':
                return self._parse_pdf(data, metadata)
            elif format_type == 'excel':
                return self._parse_excel(data, metadata)
            elif format_type == 'csv':
                return self._parse_csv(data, metadata)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
        
        except Exception as e:
            logger.error(f"Error parsing rent roll ({format_type}): {e}")
            return {
                'status': 'error',
                'error': str(e),
                'units': [],
                'summary': {}
            }
    
    def _parse_pdf(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Parse rent roll from PDF text
        Uses pattern matching and text analysis
        """
        units = []
        
        # Split into lines for processing
        lines = text.split('\n')
        
        # Try to detect rent roll format
        if 'Tenancy Schedule' in text or 'Property:' in text:
            # Format like TCSH rent roll
            units = self._parse_tabular_rent_roll(text)
        else:
            # Generic format - try pattern matching
            units = self._parse_generic_format(lines)
        
        # Extract summary information
        summary = self._extract_summary(text)
        
        # Validate units
        valid_units = [u for u in units if self._is_valid_unit(u)]
        
        return {
            'status': 'success',
            'format': 'pdf_tabular',
            'units': valid_units,
            'summary': summary,
            'total_units': len(valid_units),
            'metadata': metadata or {}
        }
    
    def _parse_tabular_rent_roll(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse tabular rent roll format (like TCSH)
        Detects repeated property headers and extracts unit data
        """
        units = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for property header pattern
            if 'The Crossings of Spring' in line or line.startswith('The ') or 'Property' in line:
                # Check if next line has unit number
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    
                    # Check if it looks like a unit number
                    if next_line and (next_line[0].isdigit() or 'Target' in next_line or len(next_line) < 20):
                        # Potential unit found
                        unit = self._extract_unit_from_context(lines, i)
                        
                        if unit and not self._should_exclude(unit):
                            units.append(unit)
            
            i += 1
        
        return units
    
    def _extract_unit_from_context(self, lines: List[str], start_index: int) -> Optional[Dict[str, Any]]:
        """
        Extract unit data from surrounding context (next 10-15 lines)
        """
        unit = {}
        
        # Get context window
        context_lines = lines[start_index:min(start_index + 15, len(lines))]
        context_text = '\n'.join(context_lines)
        
        # Extract unit number
        if start_index + 1 < len(lines):
            potential_unit = lines[start_index + 1].strip()
            if potential_unit:
                unit['unit_number'] = potential_unit[:50]
        
        # Extract tenant name
        if start_index + 2 < len(lines):
            potential_tenant = lines[start_index + 2].strip()
            if potential_tenant and not potential_tenant[0].isdigit():
                unit['tenant_name'] = potential_tenant[:255]
        
        # Look for numbers in context (sqft, rent)
        numbers = re.findall(r'([\d,]+\.?\d*)', context_text)
        
        # Try to identify sqft (usually 3-5 digits)
        for num_str in numbers:
            try:
                num = float(num_str.replace(',', ''))
                if 100 < num < 50000 and 'sqft' not in unit:
                    unit['sqft'] = num
                elif 100 < num < 100000 and 'monthly_rent' not in unit:
                    unit['monthly_rent'] = num
            except:
                pass
        
        # Extract dates
        dates = re.findall(r'(\d{1,2}/\d{1,2}/\d{4})', context_text)
        if len(dates) >= 1:
            unit['lease_start_date'] = dates[0]
        if len(dates) >= 2:
            unit['lease_end_date'] = dates[1]
        
        # Default status
        unit['status'] = 'occupied'
        
        return unit if 'unit_number' in unit else None
    
    def _parse_generic_format(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Parse generic rent roll format using pattern matching
        """
        units = []
        current_unit = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_unit and 'unit_number' in current_unit:
                    units.append(current_unit)
                    current_unit = {}
                continue
            
            # Try to extract fields using patterns
            for field, pattern in self.field_patterns.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if field in ['sqft', 'monthly_rent', 'annual_rent']:
                        try:
                            value = float(value.replace(',', ''))
                        except:
                            pass
                    current_unit[field] = value
        
        # Add last unit if exists
        if current_unit and 'unit_number' in current_unit:
            units.append(current_unit)
        
        return units
    
    def _parse_excel(self, df: pd.DataFrame, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Parse rent roll from Excel DataFrame
        """
        units = []
        
        # Try to identify column mappings
        column_map = self._map_columns(df.columns)
        
        # Extract units row by row
        for _, row in df.iterrows():
            unit = {}
            
            for standard_field, excel_column in column_map.items():
                if excel_column:
                    value = row[excel_column]
                    if pd.notna(value):
                        unit[standard_field] = value
            
            if unit and 'unit_number' in unit:
                if not self._should_exclude(unit):
                    units.append(unit)
        
        summary = self._calculate_summary(units)
        
        return {
            'status': 'success',
            'format': 'excel',
            'units': units,
            'summary': summary,
            'total_units': len(units),
            'metadata': metadata or {}
        }
    
    def _parse_csv(self, file_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Parse rent roll from CSV file
        """
        try:
            df = pd.read_csv(file_path)
            return self._parse_excel(df, metadata)  # CSV can use same logic as Excel
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'units': [],
                'summary': {}
            }
    
    def _map_columns(self, columns: List[str]) -> Dict[str, Optional[str]]:
        """
        Map Excel/CSV columns to standard field names
        """
        column_map = {
            'unit_number': None,
            'tenant_name': None,
            'sqft': None,
            'monthly_rent': None,
            'annual_rent': None,
            'lease_start_date': None,
            'lease_end_date': None,
            'status': None
        }
        
        # Column name variations
        patterns = {
            'unit_number': ['unit', 'suite', 'space', 'unit #', 'unit number'],
            'tenant_name': ['tenant', 'tenant name', 'occupant', 'lessee'],
            'sqft': ['sqft', 'sq ft', 'square feet', 'area', 'size'],
            'monthly_rent': ['monthly rent', 'rent', 'monthly payment'],
            'annual_rent': ['annual rent', 'yearly rent'],
            'lease_start_date': ['lease start', 'start date', 'from'],
            'lease_end_date': ['lease end', 'end date', 'to', 'expiration'],
            'status': ['status', 'occupancy', 'occupied']
        }
        
        for col in columns:
            col_lower = col.lower().strip()
            for field, variations in patterns.items():
                if any(var in col_lower for var in variations):
                    column_map[field] = col
                    break
        
        return column_map
    
    def _extract_summary(self, text: str) -> Dict[str, Any]:
        """
        Extract summary information from rent roll text
        """
        summary = {}
        
        # Try to find occupancy summary section
        occupancy_match = re.search(r'Occupancy Summary.*?Occupied Area\s+([\d,]+\.?\d*)\s+([\d.]+)', 
                                   text, re.DOTALL)
        if occupancy_match:
            summary['total_sqft'] = float(occupancy_match.group(1).replace(',', ''))
            summary['occupancy_rate'] = float(occupancy_match.group(2))
        
        # Try to find lease count
        lease_count_match = re.search(r'#\s*of\s*Leases\s*.*?\s+(\d+)', text, re.IGNORECASE)
        if lease_count_match:
            summary['lease_count'] = int(lease_count_match.group(1))
        
        # Find total area
        total_area_match = re.search(r'Total.*?(?:Area|Sqft).*?([\d,]+)', text, re.IGNORECASE)
        if total_area_match:
            summary['total_area'] = float(total_area_match.group(1).replace(',', ''))
        
        return summary
    
    def _calculate_summary(self, units: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate summary statistics from units
        """
        total_units = len(units)
        occupied = sum(1 for u in units if u.get('status', '').lower() == 'occupied')
        
        total_sqft = sum(float(u.get('sqft', 0)) for u in units if u.get('sqft'))
        total_rent = sum(float(u.get('monthly_rent', 0)) for u in units if u.get('monthly_rent'))
        
        occupancy_rate = (occupied / total_units * 100) if total_units > 0 else 0
        
        return {
            'total_units': total_units,
            'occupied_units': occupied,
            'vacant_units': total_units - occupied,
            'occupancy_rate': occupancy_rate,
            'total_sqft': total_sqft,
            'total_monthly_rent': total_rent,
            'average_rent_per_sqft': (total_rent / total_sqft) if total_sqft > 0 else 0
        }
    
    def _should_exclude(self, unit: Dict[str, Any]) -> bool:
        """
        Check if unit should be excluded (NAP, expense only, etc.)
        """
        # Check unit number and tenant name for exclusion patterns
        unit_str = f"{unit.get('unit_number', '')} {unit.get('tenant_name', '')}"
        
        for pattern in self.exclusion_patterns:
            if re.search(pattern, unit_str, re.IGNORECASE):
                return True
        
        # Exclude if unit has 0 sqft and 0 rent (likely not a real lease)
        if (unit.get('sqft', 0) == 0 and 
            unit.get('monthly_rent', 0) == 0 and 
            unit.get('annual_rent', 0) == 0):
            return True
        
        return False
    
    def _is_valid_unit(self, unit: Dict[str, Any]) -> bool:
        """
        Validate if unit has minimum required fields
        """
        return ('unit_number' in unit and 
                unit['unit_number'] and 
                len(unit) > 2)  # Has at least 3 fields


# Global parser instance
rent_roll_parser = RentRollParser()

