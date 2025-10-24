"""
Property Name Patterns Configuration

Defines regex patterns, abbreviations, and mappings for property name extraction.
This configuration is used by the PropertyNameExtractor to identify and validate property names.
"""

from typing import Dict, List, Tuple, Optional

# Property abbreviation mappings
PROPERTY_ABBREVIATIONS = {
    'ESP': 'Eastern Shore Plaza',
    'TCSH': 'The Crossings of Spring Hill', 
    'HA': 'Hammond Aire',
    'WC': 'Wendover Commons',
    'ES': 'Eastern Shore',
    'TC': 'The Crossings',
    'HAM': 'Hammond',
    'WEN': 'Wendover',
    'WENDO': 'Wendover',
    'CROSS': 'The Crossings',
    'SHORE': 'Eastern Shore',
}

# Reverse mapping: full name to abbreviation
ABBREVIATION_TO_FULL = {v: k for k, v in PROPERTY_ABBREVIATIONS.items()}

# Property name variations and aliases
PROPERTY_ALIASES = {
    'Eastern Shore Plaza': [
        'ESP',
        'Eastern Shore',
        'Shore Plaza',
        'Eastern Shore Plaza (ESP)',
    ],
    'The Crossings of Spring Hill': [
        'TCSH',
        'The Crossings',
        'Crossings of Spring Hill',
        'Spring Hill Crossings',
        'The Crossings of Spring Hill (TCSH)',
    ],
    'Hammond Aire': [
        'HA',
        'Hammond',
        'Hammond Aire (HA)',
    ],
    'Wendover Commons': [
        'WC',
        'Wendover',
        'Wendover Commons (WC)',
    ],
}

# Regex patterns for property name extraction
PROPERTY_NAME_PATTERNS = {
    # High confidence patterns (appear in document headers)
    'property_header': r'(?:Property|Property Name|Property:)\s*:?\s*([A-Za-z\s&,.-]+?)(?:\s*\([A-Z]+\))?',
    'title_case': r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\([A-Z]+\)',
    'all_caps': r'^([A-Z\s]+?)\s*\([A-Z]+\)',
    
    # Document-specific patterns
    'income_statement': r'([A-Za-z\s&,.-]+?)\s*Income\s*Statement',
    'balance_sheet': r'([A-Za-z\s&,.-]+?)\s*Balance\s*Sheet',
    'cash_flow': r'([A-Za-z\s&,.-]+?)\s*Cash\s*Flow',
    'rent_roll': r'([A-Za-z\s&,.-]+?)\s*Rent\s*Roll',
    'financial_statement': r'([A-Za-z\s&,.-]+?)\s*Financial\s*Statement',
    
    # Filename patterns
    'filename_with_abbr': r'^([A-Za-z\s&,.-]+?)\s*\([A-Z]+\)',
    'filename_with_year': r'^([A-Za-z\s&,.-]+?)\s*-\s*\d{4}',
    'filename_simple': r'^([A-Za-z\s&,.-]+?)\s*\d{4}',
    
    # Common variations
    'with_and': r'([A-Za-z\s&,.-]+?)\s*&\s*([A-Za-z\s&,.-]+)',
    'with_comma': r'([A-Za-z\s&,.-]+?),\s*([A-Za-z\s&,.-]+)',
}

# Confidence scores for different patterns
PATTERN_CONFIDENCE_SCORES = {
    'property_header': 0.95,
    'title_case': 0.90,
    'all_caps': 0.85,
    'income_statement': 0.90,
    'balance_sheet': 0.90,
    'cash_flow': 0.90,
    'rent_roll': 0.90,
    'financial_statement': 0.85,
    'filename_with_abbr': 0.80,
    'filename_with_year': 0.75,
    'filename_simple': 0.70,
    'with_and': 0.85,
    'with_comma': 0.80,
}

# Common words to exclude from property names
EXCLUDE_WORDS = {
    'income', 'statement', 'balance', 'sheet', 'cash', 'flow',
    'rent', 'roll', 'financial', 'report', 'summary', 'analysis',
    'year', 'month', 'quarter', 'annual', 'quarterly', 'monthly',
    'statement', 'report', 'summary', 'analysis', 'review',
    'property', 'properties', 'real', 'estate', 'investment',
    'management', 'company', 'corporation', 'llc', 'inc', 'ltd',
    'the', 'and', 'of', 'for', 'in', 'on', 'at', 'by', 'with',
}

# Minimum and maximum length for property names
MIN_PROPERTY_NAME_LENGTH = 3
MAX_PROPERTY_NAME_LENGTH = 100

# Confidence thresholds
CONFIDENCE_THRESHOLDS = {
    'exact_match': 0.95,      # Names match exactly
    'fuzzy_match': 0.80,      # Minor differences
    'partial_match': 0.50,    # Significant differences, needs review
    'no_match': 0.50,         # Clear mismatch, block processing
}

# Validation status levels
VALIDATION_STATUS = {
    'exact': 'exact_match',
    'fuzzy': 'fuzzy_match', 
    'mismatch': 'no_match',
    'pending': 'partial_match',
}

# Property name cleaning rules
CLEANING_RULES = [
    # Remove common prefixes
    (r'^(Property|Property Name|Property:)\s*', ''),
    # Remove trailing abbreviations in parentheses
    (r'\s*\([A-Z]+\)$', ''),
    # Remove trailing punctuation
    (r'\s*[,;.]$', ''),
    # Remove leading/trailing dashes
    (r'^\s*-\s*', ''),
    (r'\s*-\s*$', ''),
    # Normalize whitespace
    (r'\s+', ' '),
    # Remove extra spaces
    (r'^\s+|\s+$', ''),
]

# Property name validation rules
VALIDATION_RULES = [
    # Must contain letters
    (r'[A-Za-z]', 'Must contain letters'),
    # Should not be too short
    (lambda name: len(name) >= MIN_PROPERTY_NAME_LENGTH, f'Must be at least {MIN_PROPERTY_NAME_LENGTH} characters'),
    # Should not be too long
    (lambda name: len(name) <= MAX_PROPERTY_NAME_LENGTH, f'Must be no more than {MAX_PROPERTY_NAME_LENGTH} characters'),
    # Should not be common document words
    (lambda name: name.lower() not in EXCLUDE_WORDS, 'Cannot be a common document word'),
    # Should not be all numbers
    (lambda name: not name.isdigit(), 'Cannot be all numbers'),
    # Should not be all special characters
    (lambda name: any(c.isalnum() for c in name), 'Must contain alphanumeric characters'),
]

def get_property_aliases(property_name: str) -> List[str]:
    """Get all aliases for a property name"""
    aliases = []
    
    # Direct lookup
    if property_name in PROPERTY_ALIASES:
        aliases.extend(PROPERTY_ALIASES[property_name])
    
    # Check if it's an abbreviation
    if property_name in PROPERTY_ABBREVIATIONS:
        full_name = PROPERTY_ABBREVIATIONS[property_name]
        if full_name in PROPERTY_ALIASES:
            aliases.extend(PROPERTY_ALIASES[full_name])
    
    # Check if it's a full name
    for full_name, name_aliases in PROPERTY_ALIASES.items():
        if property_name.lower() == full_name.lower():
            aliases.extend(name_aliases)
    
    return list(set(aliases))  # Remove duplicates

def get_property_abbreviation(property_name: str) -> Optional[str]:
    """Get abbreviation for a property name"""
    # Direct lookup
    if property_name in ABBREVIATION_TO_FULL:
        return ABBREVIATION_TO_FULL[property_name]
    
    # Check aliases
    for full_name, aliases in PROPERTY_ALIASES.items():
        if property_name.lower() == full_name.lower():
            return ABBREVIATION_TO_FULL.get(full_name)
    
    return None

def clean_property_name(name: str) -> str:
    """Clean and normalize property name using cleaning rules"""
    cleaned = name
    
    for pattern, replacement in CLEANING_RULES:
        if callable(pattern):
            # Custom function
            cleaned = pattern(cleaned, replacement)
        else:
            # Regex pattern
            import re
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip()

def validate_property_name(name: str) -> Tuple[bool, List[str]]:
    """Validate property name and return (is_valid, error_messages)"""
    errors = []
    
    for rule in VALIDATION_RULES:
        if callable(rule):
            # Custom function
            try:
                if not rule(name):
                    errors.append("Invalid property name format")
            except Exception as e:
                errors.append(f"Validation error: {e}")
        else:
            # Regex pattern
            import re
            if not re.search(rule[0], name):
                errors.append(rule[1])
    
    return len(errors) == 0, errors

def get_confidence_threshold(status: str) -> float:
    """Get confidence threshold for validation status"""
    return CONFIDENCE_THRESHOLDS.get(status, 0.50)

def get_validation_status(confidence: float) -> str:
    """Get validation status based on confidence score"""
    if confidence >= CONFIDENCE_THRESHOLDS['exact_match']:
        return 'exact'
    elif confidence >= CONFIDENCE_THRESHOLDS['fuzzy_match']:
        return 'fuzzy'
    elif confidence >= CONFIDENCE_THRESHOLDS['partial_match']:
        return 'pending'
    else:
        return 'mismatch'
