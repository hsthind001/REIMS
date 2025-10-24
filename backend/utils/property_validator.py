"""
Property Name Validation Module

Validates property names extracted from documents against database property names.
Uses fuzzy matching, confidence scoring, and alias resolution to ensure accuracy.
"""

import logging
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import sqlite3
from difflib import SequenceMatcher

from backend.utils.property_name_extractor import PropertyNameExtractor, PropertyNameResult
from backend.config.property_name_patterns import (
    PROPERTY_ABBREVIATIONS, PROPERTY_ALIASES, CONFIDENCE_THRESHOLDS,
    get_validation_status, clean_property_name, validate_property_name
)

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of property name validation"""
    is_valid: bool
    confidence: float
    status: str  # 'exact', 'fuzzy', 'mismatch', 'pending'
    extracted_name: str
    database_name: str
    property_id: Optional[int]
    match_type: str  # 'exact', 'fuzzy', 'alias', 'abbreviation', 'none'
    suggestions: List[str]
    needs_review: bool
    error_message: Optional[str] = None

class PropertyValidator:
    """Validates property names against database using multiple strategies"""
    
    def __init__(self, db_path: str = "reims.db"):
        self.db_path = db_path
        self.extractor = PropertyNameExtractor()
        
    def validate_property_name(
        self, 
        extracted_name: str, 
        document_id: str,
        property_id: Optional[int] = None
    ) -> ValidationResult:
        """
        Validate extracted property name against database
        
        Args:
            extracted_name: Name extracted from document
            document_id: Document identifier
            property_id: Optional specific property ID to validate against
            
        Returns:
            ValidationResult with validation details
        """
        try:
            # Clean the extracted name
            cleaned_name = clean_property_name(extracted_name)
            
            # Validate name format
            is_valid_format, format_errors = validate_property_name(cleaned_name)
            if not is_valid_format:
                return ValidationResult(
                    is_valid=False,
                    confidence=0.0,
                    status='mismatch',
                    extracted_name=extracted_name,
                    database_name='',
                    property_id=None,
                    match_type='none',
                    suggestions=[],
                    needs_review=True,
                    error_message=f"Invalid name format: {', '.join(format_errors)}"
                )
            
            # Get all properties from database
            properties = self._get_all_properties()
            
            if not properties:
                return ValidationResult(
                    is_valid=False,
                    confidence=0.0,
                    status='mismatch',
                    extracted_name=extracted_name,
                    database_name='',
                    property_id=None,
                    match_type='none',
                    suggestions=[],
                    needs_review=True,
                    error_message="No properties found in database"
                )
            
            # If specific property ID provided, validate against that property
            if property_id:
                return self._validate_against_property(cleaned_name, property_id, properties)
            
            # Find best match across all properties
            return self._find_best_match(cleaned_name, properties)
            
        except Exception as e:
            logger.error(f"Error validating property name '{extracted_name}': {e}")
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                status='mismatch',
                extracted_name=extracted_name,
                database_name='',
                property_id=None,
                match_type='none',
                suggestions=[],
                needs_review=True,
                error_message=f"Validation error: {str(e)}"
            )
    
    def _get_all_properties(self) -> List[Dict[str, Any]]:
        """Get all properties from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, address, city, state
                FROM properties
                ORDER BY id
            """)
            
            properties = []
            for row in cursor.fetchall():
                properties.append({
                    'id': row[0],
                    'name': row[1],
                    'address': row[2],
                    'city': row[3],
                    'state': row[4]
                })
            
            conn.close()
            return properties
            
        except Exception as e:
            logger.error(f"Error getting properties from database: {e}")
            return []
    
    def _validate_against_property(
        self, 
        extracted_name: str, 
        property_id: int, 
        properties: List[Dict[str, Any]]
    ) -> ValidationResult:
        """Validate extracted name against specific property"""
        # Find the property
        target_property = None
        for prop in properties:
            if prop['id'] == property_id:
                target_property = prop
                break
        
        if not target_property:
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                status='mismatch',
                extracted_name=extracted_name,
                database_name='',
                property_id=property_id,
                match_type='none',
                suggestions=[],
                needs_review=True,
                error_message=f"Property ID {property_id} not found"
            )
        
        # Check for exact match
        if extracted_name.lower() == target_property['name'].lower():
            return ValidationResult(
                is_valid=True,
                confidence=1.0,
                status='exact',
                extracted_name=extracted_name,
                database_name=target_property['name'],
                property_id=property_id,
                match_type='exact',
                suggestions=[],
                needs_review=False
            )
        
        # Check for fuzzy match
        similarity = self._calculate_similarity(extracted_name, target_property['name'])
        
        if similarity >= CONFIDENCE_THRESHOLDS['fuzzy_match']:
            return ValidationResult(
                is_valid=True,
                confidence=similarity,
                status='fuzzy',
                extracted_name=extracted_name,
                database_name=target_property['name'],
                property_id=property_id,
                match_type='fuzzy',
                suggestions=[],
                needs_review=False
            )
        
        # Check for alias match
        alias_match = self._check_alias_match(extracted_name, target_property['name'])
        if alias_match:
            return ValidationResult(
                is_valid=True,
                confidence=0.9,
                status='fuzzy',
                extracted_name=extracted_name,
                database_name=target_property['name'],
                property_id=property_id,
                match_type='alias',
                suggestions=[],
                needs_review=False
            )
        
        # No match found
        return ValidationResult(
            is_valid=False,
            confidence=similarity,
            status=get_validation_status(similarity),
            extracted_name=extracted_name,
            database_name=target_property['name'],
            property_id=property_id,
            match_type='none',
            suggestions=[target_property['name']],
            needs_review=True
        )
    
    def _find_best_match(
        self, 
        extracted_name: str, 
        properties: List[Dict[str, Any]]
    ) -> ValidationResult:
        """Find best matching property across all properties"""
        best_match = None
        best_confidence = 0.0
        best_property = None
        
        for property_data in properties:
            # Check exact match
            if extracted_name.lower() == property_data['name'].lower():
                return ValidationResult(
                    is_valid=True,
                    confidence=1.0,
                    status='exact',
                    extracted_name=extracted_name,
                    database_name=property_data['name'],
                    property_id=property_data['id'],
                    match_type='exact',
                    suggestions=[],
                    needs_review=False
                )
            
            # Check fuzzy match
            similarity = self._calculate_similarity(extracted_name, property_data['name'])
            
            # Check alias match
            alias_match = self._check_alias_match(extracted_name, property_data['name'])
            if alias_match:
                similarity = max(similarity, 0.9)
            
            if similarity > best_confidence:
                best_confidence = similarity
                best_property = property_data
                best_match = ValidationResult(
                    is_valid=similarity >= CONFIDENCE_THRESHOLDS['fuzzy_match'],
                    confidence=similarity,
                    status=get_validation_status(similarity),
                    extracted_name=extracted_name,
                    database_name=property_data['name'],
                    property_id=property_data['id'],
                    match_type='fuzzy' if similarity >= CONFIDENCE_THRESHOLDS['fuzzy_match'] else 'none',
                    suggestions=[],
                    needs_review=similarity < CONFIDENCE_THRESHOLDS['fuzzy_match']
                )
        
        if best_match:
            return best_match
        
        # No good match found
        suggestions = [prop['name'] for prop in properties[:5]]  # Top 5 suggestions
        return ValidationResult(
            is_valid=False,
            confidence=0.0,
            status='mismatch',
            extracted_name=extracted_name,
            database_name='',
            property_id=None,
            match_type='none',
            suggestions=suggestions,
            needs_review=True
        )
    
    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two property names using multiple methods"""
        # Normalize names
        norm1 = name1.lower().strip()
        norm2 = name2.lower().strip()
        
        # Sequence matcher similarity
        seq_similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Check for substring matches
        substring_bonus = 0.0
        if norm1 in norm2 or norm2 in norm1:
            substring_bonus = 0.2
        
        # Check for word overlap
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        if words1 and words2:
            word_overlap = len(words1.intersection(words2)) / len(words1.union(words2))
        else:
            word_overlap = 0.0
        
        # Combine similarities
        final_similarity = max(seq_similarity, word_overlap) + substring_bonus
        
        return min(1.0, final_similarity)
    
    def _check_alias_match(self, extracted_name: str, database_name: str) -> bool:
        """Check if extracted name matches any alias of the database name"""
        # Check direct aliases
        if database_name in PROPERTY_ALIASES:
            aliases = PROPERTY_ALIASES[database_name]
            for alias in aliases:
                if extracted_name.lower() == alias.lower():
                    return True
        
        # Check abbreviation mappings
        for abbr, full_name in PROPERTY_ABBREVIATIONS.items():
            if (abbr.lower() in extracted_name.lower() and 
                full_name.lower() == database_name.lower()):
                return True
        
        # Check reverse abbreviation
        if database_name in PROPERTY_ABBREVIATIONS:
            abbr = PROPERTY_ABBREVIATIONS[database_name]
            if abbr.lower() == extracted_name.lower():
                return True
        
        return False
    
    def validate_document_property(
        self, 
        document_path: str, 
        document_id: str,
        property_id: Optional[int] = None
    ) -> ValidationResult:
        """
        Validate property name from document file
        
        Args:
            document_path: Path to document file
            document_id: Document identifier
            property_id: Optional specific property ID to validate against
            
        Returns:
            ValidationResult with validation details
        """
        try:
            # Extract property name from document
            extraction_result = self.extractor.extract_property_name(document_path)
            
            if not extraction_result:
                return ValidationResult(
                    is_valid=False,
                    confidence=0.0,
                    status='mismatch',
                    extracted_name='',
                    database_name='',
                    property_id=property_id,
                    match_type='none',
                    suggestions=[],
                    needs_review=True,
                    error_message="Could not extract property name from document"
                )
            
            # Validate the extracted name
            return self.validate_property_name(
                extraction_result.name,
                document_id,
                property_id
            )
            
        except Exception as e:
            logger.error(f"Error validating document {document_path}: {e}")
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                status='mismatch',
                extracted_name='',
                database_name='',
                property_id=property_id,
                match_type='none',
                suggestions=[],
                needs_review=True,
                error_message=f"Document validation error: {str(e)}"
            )
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if validation table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='property_name_validations'
            """)
            
            if not cursor.fetchone():
                conn.close()
                return {
                    'total_validations': 0,
                    'exact_matches': 0,
                    'fuzzy_matches': 0,
                    'mismatches': 0,
                    'pending_reviews': 0,
                    'success_rate': 0.0
                }
            
            # Get validation statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN validation_status = 'exact' THEN 1 ELSE 0 END) as exact,
                    SUM(CASE WHEN validation_status = 'fuzzy' THEN 1 ELSE 0 END) as fuzzy,
                    SUM(CASE WHEN validation_status = 'mismatch' THEN 1 ELSE 0 END) as mismatch,
                    SUM(CASE WHEN validation_status = 'pending' THEN 1 ELSE 0 END) as pending
                FROM property_name_validations
            """)
            
            row = cursor.fetchone()
            total = row[0] or 0
            exact = row[1] or 0
            fuzzy = row[2] or 0
            mismatch = row[3] or 0
            pending = row[4] or 0
            
            success_rate = (exact + fuzzy) / total if total > 0 else 0.0
            
            conn.close()
            
            return {
                'total_validations': total,
                'exact_matches': exact,
                'fuzzy_matches': fuzzy,
                'mismatches': mismatch,
                'pending_reviews': pending,
                'success_rate': round(success_rate, 3)
            }
            
        except Exception as e:
            logger.error(f"Error getting validation summary: {e}")
            return {
                'total_validations': 0,
                'exact_matches': 0,
                'fuzzy_matches': 0,
                'mismatches': 0,
                'pending_reviews': 0,
                'success_rate': 0.0
            }

# Convenience functions
def validate_property_name_simple(extracted_name: str, property_id: Optional[int] = None) -> ValidationResult:
    """Simple property name validation - convenience function"""
    validator = PropertyValidator()
    return validator.validate_property_name(extracted_name, "manual", property_id)

def validate_document_simple(document_path: str, property_id: Optional[int] = None) -> ValidationResult:
    """Simple document validation - convenience function"""
    validator = PropertyValidator()
    return validator.validate_document_property(document_path, "manual", property_id)
