"""
Property Name Validation Integration

Integrates property name validation into the document upload workflow.
Validates extracted property names against database and handles mismatches.
"""

import logging
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime
import sqlite3

from backend.utils.property_name_extractor import PropertyNameExtractor, extract_property_name
from backend.utils.property_validator import PropertyValidator, ValidationResult
from backend.utils.alias_resolver import AliasResolver, resolve_property_name

logger = logging.getLogger(__name__)

class ValidationIntegration:
    """Integrates property name validation into document upload workflow"""
    
    def __init__(self, db_path: str = "reims.db"):
        self.db_path = db_path
        self.extractor = PropertyNameExtractor()
        self.validator = PropertyValidator(db_path)
        self.alias_resolver = AliasResolver(db_path)
    
    def validate_uploaded_document(
        self, 
        document_path: str, 
        document_id: str,
        property_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate property name from uploaded document
        
        Args:
            document_path: Path to uploaded document
            document_id: Document identifier
            property_id: Optional property ID to validate against
            
        Returns:
            Validation result with recommendations
        """
        try:
            # Extract property name from document
            extraction_results = self.extractor.extract_from_pdf(document_path)
            extraction_result = extraction_results[0] if extraction_results else None
            
            if not extraction_result:
                return {
                    'valid': False,
                    'status': 'no_extraction',
                    'message': 'Could not extract property name from document',
                    'recommendation': 'manual_review',
                    'extracted_name': None,
                    'confidence': 0.0,
                    'property_id': property_id,
                    'needs_review': True
                }
            
            # Convert property_id to int if provided
            property_id_int = None
            if property_id:
                try:
                    property_id_int = int(property_id)
                except ValueError:
                    logger.warning(f"Invalid property_id format: {property_id}")
            
            # Validate extracted name
            validation_result = self.validator.validate_property_name(
                extraction_result.name,
                document_id,
                property_id_int
            )
            
            # Store validation result in database
            self._store_validation_result(
                document_id,
                property_id_int,
                extraction_result,
                validation_result
            )
            
            # Determine recommendation
            recommendation = self._get_recommendation(validation_result)
            
            return {
                'valid': validation_result.is_valid,
                'status': validation_result.status,
                'message': self._get_validation_message(validation_result),
                'recommendation': recommendation,
                'extracted_name': extraction_result.name,
                'confidence': validation_result.confidence,
                'property_id': validation_result.property_id,
                'database_name': validation_result.database_name,
                'needs_review': validation_result.needs_review,
                'suggestions': validation_result.suggestions
            }
            
        except Exception as e:
            logger.error(f"Error validating document {document_path}: {e}")
            return {
                'valid': False,
                'status': 'error',
                'message': f'Validation error: {str(e)}',
                'recommendation': 'manual_review',
                'extracted_name': None,
                'confidence': 0.0,
                'property_id': property_id,
                'needs_review': True
            }
    
    def _store_validation_result(
        self,
        document_id: str,
        property_id: Optional[int],
        extraction_result,
        validation_result: ValidationResult
    ):
        """Store validation result in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO property_name_validations (
                    document_id, property_id, extracted_name, database_name,
                    extraction_method, match_score, validation_status,
                    resolution_action, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document_id,
                property_id,
                extraction_result.name,
                validation_result.database_name,
                extraction_result.method,
                validation_result.confidence,
                validation_result.status,
                'pending',
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Stored validation result for document {document_id}")
            
        except Exception as e:
            logger.error(f"Error storing validation result: {e}")
    
    def _get_recommendation(self, validation_result: ValidationResult) -> str:
        """Get recommendation based on validation result"""
        if validation_result.status == 'exact':
            return 'auto_approve'
        elif validation_result.status == 'fuzzy':
            return 'auto_approve'
        elif validation_result.status == 'pending':
            return 'manual_review'
        else:  # mismatch
            return 'manual_review'
    
    def _get_validation_message(self, validation_result: ValidationResult) -> str:
        """Get human-readable validation message"""
        if validation_result.status == 'exact':
            return f"Property name matches exactly: {validation_result.database_name}"
        elif validation_result.status == 'fuzzy':
            return f"Property name matches closely: {validation_result.database_name} (confidence: {validation_result.confidence:.2f})"
        elif validation_result.status == 'pending':
            return f"Property name needs review: {validation_result.extracted_name} vs {validation_result.database_name}"
        else:  # mismatch
            return f"Property name mismatch: {validation_result.extracted_name} does not match any known property"
    
    def get_validation_queue(self) -> List[Dict[str, Any]]:
        """Get documents that need manual review"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    document_id, property_id, extracted_name, database_name,
                    match_score, validation_status, created_at
                FROM property_name_validations
                WHERE validation_status IN ('pending', 'mismatch')
                ORDER BY created_at DESC
            """)
            
            queue = []
            for row in cursor.fetchall():
                queue.append({
                    'document_id': row[0],
                    'property_id': row[1],
                    'extracted_name': row[2],
                    'database_name': row[3],
                    'confidence': row[4],
                    'status': row[5],
                    'created_at': row[6]
                })
            
            conn.close()
            return queue
            
        except Exception as e:
            logger.error(f"Error getting validation queue: {e}")
            return []
    
    def approve_validation(
        self, 
        document_id: str, 
        approved_property_id: int,
        reviewer: str = "admin"
    ) -> bool:
        """Approve a validation result"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE property_name_validations
                SET resolution_action = 'approved',
                    reviewed_by = ?,
                    reviewed_at = ?
                WHERE document_id = ?
            """, (reviewer, datetime.now(), document_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Approved validation for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error approving validation: {e}")
            return False
    
    def correct_validation(
        self, 
        document_id: str, 
        corrected_property_id: int,
        corrected_name: str,
        reviewer: str = "admin"
    ) -> bool:
        """Correct a validation result"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE property_name_validations
                SET resolution_action = 'corrected',
                    corrected_name = ?,
                    reviewed_by = ?,
                    reviewed_at = ?
                WHERE document_id = ?
            """, (corrected_name, reviewer, datetime.now(), document_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Corrected validation for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error correcting validation: {e}")
            return False
    
    def add_alias_for_validation(
        self, 
        document_id: str, 
        property_id: int,
        alias_name: str,
        reviewer: str = "admin"
    ) -> bool:
        """Add alias based on validation result"""
        try:
            # Add alias to database
            success = self.alias_resolver.add_alias(property_id, alias_name, 'common_name')
            
            if success:
                # Update validation record
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE property_name_validations
                    SET resolution_action = 'alias_added',
                        reviewed_by = ?,
                        reviewed_at = ?
                    WHERE document_id = ?
                """, (reviewer, datetime.now(), document_id))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Added alias '{alias_name}' for property {property_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding alias: {e}")
            return False
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation system statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if validation table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='property_name_validations'
            """)
            
            if not cursor.fetchone():
                return {
                    'total_validations': 0,
                    'exact_matches': 0,
                    'fuzzy_matches': 0,
                    'mismatches': 0,
                    'pending_reviews': 0,
                    'success_rate': 0.0
                }
            
            # Get statistics
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
            logger.error(f"Error getting validation statistics: {e}")
            return {
                'total_validations': 0,
                'exact_matches': 0,
                'fuzzy_matches': 0,
                'mismatches': 0,
                'pending_reviews': 0,
                'success_rate': 0.0
            }

# Convenience functions for easy integration
def validate_uploaded_document(document_path: str, document_id: str, property_id: Optional[str] = None) -> Dict[str, Any]:
    """Validate uploaded document - convenience function"""
    integration = ValidationIntegration()
    return integration.validate_uploaded_document(document_path, document_id, property_id)

def get_validation_queue() -> List[Dict[str, Any]]:
    """Get validation queue - convenience function"""
    integration = ValidationIntegration()
    return integration.get_validation_queue()

def get_validation_statistics() -> Dict[str, Any]:
    """Get validation statistics - convenience function"""
    integration = ValidationIntegration()
    return integration.get_validation_statistics()
