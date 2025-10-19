#!/usr/bin/env python3
"""
Data Validator Service
Validates extracted data against source documents
Logs discrepancies and generates validation reports
"""

import sqlite3
import json
import uuid
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Service for validating extracted document data
    """
    
    def __init__(self, db_path: str = "reims.db"):
        self.db_path = db_path
    
    def validate_rent_roll(
        self,
        document_id: str,
        property_id: int,
        parsed_data: Dict[str, Any],
        source_summary: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Validate rent roll extraction against source document
        
        Args:
            document_id: Document being validated
            property_id: Property the data belongs to
            parsed_data: Parsed unit data
            source_summary: Summary from source document (lease count, area, etc.)
        
        Returns:
            Validation report dictionary
        """
        validation_report = {
            'document_id': document_id,
            'property_id': property_id,
            'validation_type': 'rent_roll',
            'timestamp': datetime.now().isoformat(),
            'status': 'pass',
            'discrepancies': [],
            'metrics': {}
        }
        
        # Extract data
        units = parsed_data.get('units', [])
        parsed_summary = parsed_data.get('summary', {})
        
        # Metric 1: Unit count
        extracted_count = len(units)
        expected_count = (source_summary or {}).get('lease_count') or parsed_summary.get('lease_count')
        
        validation_report['metrics']['unit_count'] = {
            'extracted': extracted_count,
            'expected': expected_count,
            'match': extracted_count == expected_count if expected_count else None
        }
        
        if expected_count and extracted_count != expected_count:
            validation_report['status'] = 'warning'
            validation_report['discrepancies'].append({
                'type': 'unit_count_mismatch',
                'severity': 'warning',
                'message': f"Unit count mismatch: extracted {extracted_count}, expected {expected_count}",
                'extracted_value': extracted_count,
                'expected_value': expected_count
            })
        
        # Metric 2: Occupancy rate
        if parsed_summary.get('occupancy_rate'):
            validation_report['metrics']['occupancy_rate'] = {
                'value': parsed_summary['occupancy_rate'],
                'source': 'parsed_summary'
            }
        
        # Metric 3: Total area
        extracted_sqft = sum(float(u.get('sqft', 0)) for u in units)
        expected_sqft = parsed_summary.get('total_sqft') or parsed_summary.get('total_area')
        
        validation_report['metrics']['total_sqft'] = {
            'extracted': extracted_sqft,
            'expected': expected_sqft,
            'match': None
        }
        
        if expected_sqft:
            # Allow 1% variance
            variance = abs(extracted_sqft - expected_sqft) / expected_sqft
            match = variance < 0.01
            validation_report['metrics']['total_sqft']['match'] = match
            validation_report['metrics']['total_sqft']['variance'] = variance * 100
            
            if not match:
                validation_report['status'] = 'warning'
                validation_report['discrepancies'].append({
                    'type': 'sqft_mismatch',
                    'severity': 'warning',
                    'message': f"Total sqft mismatch: extracted {extracted_sqft:,.0f}, expected {expected_sqft:,.0f}",
                    'extracted_value': extracted_sqft,
                    'expected_value': expected_sqft,
                    'variance_pct': variance * 100
                })
        
        # Metric 4: Data completeness
        fields_check = self._check_data_completeness(units)
        validation_report['metrics']['data_completeness'] = fields_check
        
        if fields_check['completeness_pct'] < 80:
            validation_report['status'] = 'warning'
            validation_report['discrepancies'].append({
                'type': 'incomplete_data',
                'severity': 'info',
                'message': f"Data completeness: {fields_check['completeness_pct']:.1f}%",
                'details': fields_check
            })
        
        # Log validation result
        self._log_validation(validation_report)
        
        return validation_report
    
    def _check_data_completeness(self, units: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check how complete the extracted data is
        """
        if not units:
            return {
                'total_units': 0,
                'completeness_pct': 0,
                'fields': {}
            }
        
        # Check key fields
        key_fields = ['unit_number', 'tenant_name', 'sqft', 'monthly_rent', 
                      'lease_start_date', 'lease_end_date']
        
        field_stats = {}
        for field in key_fields:
            present_count = sum(1 for u in units if u.get(field))
            field_stats[field] = {
                'present': present_count,
                'missing': len(units) - present_count,
                'percentage': (present_count / len(units) * 100) if units else 0
            }
        
        # Calculate overall completeness
        total_fields = len(key_fields) * len(units)
        filled_fields = sum(sum(1 for u in units if u.get(field)) for field in key_fields)
        completeness_pct = (filled_fields / total_fields * 100) if total_fields > 0 else 0
        
        return {
            'total_units': len(units),
            'completeness_pct': completeness_pct,
            'fields': field_stats
        }
    
    def _log_validation(self, validation_report: Dict[str, Any]) -> None:
        """
        Log validation result to database
        Note: Requires validation_log table (migration 015)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if validation_log table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='data_validation_log'
            """)
            
            if not cursor.fetchone():
                logger.warning("validation_log table does not exist, skipping log")
                conn.close()
                return
            
            # Insert validation log
            cursor.execute("""
                INSERT INTO data_validation_log (
                    id, document_id, property_id, validation_type,
                    expected_count, actual_count, match_status,
                    discrepancies, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                validation_report['document_id'],
                validation_report['property_id'],
                validation_report['validation_type'],
                validation_report['metrics'].get('unit_count', {}).get('expected'),
                validation_report['metrics'].get('unit_count', {}).get('extracted'),
                validation_report['status'],
                json.dumps(validation_report['discrepancies']),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Logged validation for document {validation_report['document_id']}")
        
        except Exception as e:
            logger.error(f"Error logging validation: {e}")
    
    def get_validation_report(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve validation report for a document
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM data_validation_log
                WHERE document_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (document_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'document_id': row['document_id'],
                    'property_id': row['property_id'],
                    'validation_type': row['validation_type'],
                    'expected_count': row['expected_count'],
                    'actual_count': row['actual_count'],
                    'match_status': row['match_status'],
                    'discrepancies': json.loads(row['discrepancies']) if row['discrepancies'] else [],
                    'created_at': row['created_at']
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error retrieving validation report: {e}")
            return None


# Global validator instance
data_validator = DataValidator()

