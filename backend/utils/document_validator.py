"""
Document Validator
Generic validator for document metadata and storage
"""

from typing import Dict, Optional
import re
from .import_validator import ImportValidator, ValidationReport, ValidationResult


class DocumentValidator(ImportValidator):
    """
    Generic validator for document imports
    Validates metadata extraction, storage paths, and database records
    """
    
    def __init__(self, minio_file_path: str, property_id: int, 
                 document_id: Optional[str] = None, db_path: str = "reims.db"):
        """
        Initialize document validator
        
        Args:
            minio_file_path: Path to document in MinIO
            property_id: Property ID in database
            document_id: Optional document ID to validate
            db_path: Path to SQLite database
        """
        super().__init__(minio_file_path, property_id, db_path)
        self.document_id = document_id
    
    def validate_metadata_extraction(self, expected_metadata: Dict) -> ValidationResult:
        """
        Validate metadata was extracted correctly
        
        Args:
            expected_metadata: Dictionary of expected metadata fields
        
        Returns:
            ValidationResult
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Check financial_documents table
            cursor.execute("""
                SELECT property_id, document_year, document_type, property_name
                FROM financial_documents
                WHERE property_id = ? AND file_path = ?
                LIMIT 1
            """, (self.property_id, self.minio_file_path))
            
            record = cursor.fetchone()
            conn.close()
            
            if not record:
                self.report.errors.append("Document record not found in database")
                return ValidationResult(
                    passed=False,
                    entity_type="metadata",
                    expected="record_exists",
                    actual="not_found",
                    message="Document record not found in database"
                )
            
            # Validate each metadata field
            mismatches = []
            for field, expected_value in expected_metadata.items():
                if field in record.keys():
                    actual_value = record[field]
                    if str(expected_value) != str(actual_value):
                        mismatches.append({
                            "field": field,
                            "expected": expected_value,
                            "actual": actual_value
                        })
            
            passed = len(mismatches) == 0
            message = f"Metadata validation: {len(expected_metadata) - len(mismatches)}/{len(expected_metadata)} fields match"
            
            if mismatches:
                message += f" - Mismatches: {mismatches}"
                self.report.errors.append(f"Metadata mismatches: {mismatches}")
            
            result = ValidationResult(
                passed=passed,
                entity_type="metadata",
                expected=len(expected_metadata),
                actual=len(expected_metadata) - len(mismatches),
                message=message
            )
            
            self.report.validations.append(result)
            return result
            
        except Exception as e:
            self.report.errors.append(f"Metadata validation failed: {e}")
            return ValidationResult(
                passed=False,
                entity_type="metadata",
                expected=0,
                actual=0,
                message=f"Error: {e}"
            )
    
    def validate_storage_path(self) -> ValidationResult:
        """
        Validate file is stored in correct MinIO location
        
        Returns:
            ValidationResult
        """
        try:
            # Check if file exists in MinIO
            bucket_name = "reims-files"
            object_name = self.minio_file_path
            
            # Try to get object metadata
            try:
                stat = self.minio_client.stat_object(bucket_name, object_name)
                file_exists = True
                file_size = stat.size
            except:
                file_exists = False
                file_size = 0
            
            passed = file_exists and file_size > 0
            message = f"File storage: {'exists' if file_exists else 'NOT FOUND'}"
            
            if file_exists:
                message += f" ({file_size} bytes)"
            else:
                self.report.errors.append(f"File not found in MinIO: {self.minio_file_path}")
            
            # Validate path follows standard structure
            if file_exists:
                # Expected pattern: Financial Statements/{year}/{type}/{filename}
                path_pattern = r'Financial Statements/\d{4}/[^/]+/.+\.(pdf|xlsx|csv|xls)$'
                if re.match(path_pattern, self.minio_file_path, re.IGNORECASE):
                    message += " - Path follows standard structure"
                else:
                    self.report.warnings.append(f"Path doesn't follow standard structure: {self.minio_file_path}")
            
            result = ValidationResult(
                passed=passed,
                entity_type="storage_path",
                expected="file_exists",
                actual="exists" if file_exists else "not_found",
                message=message
            )
            
            self.report.validations.append(result)
            return result
            
        except Exception as e:
            self.report.errors.append(f"Storage path validation failed: {e}")
            return ValidationResult(
                passed=False,
                entity_type="storage_path",
                expected=0,
                actual=0,
                message=f"Error: {e}"
            )
    
    def validate_database_record(self) -> ValidationResult:
        """
        Validate database record exists and is complete
        
        Returns:
            ValidationResult
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Check financial_documents table
            cursor.execute("""
                SELECT COUNT(*) as count FROM financial_documents
                WHERE property_id = ? AND file_path = ?
            """, (self.property_id, self.minio_file_path))
            
            fd_count = cursor.fetchone()['count']
            
            # Check documents table
            cursor.execute("""
                SELECT COUNT(*) as count FROM documents
                WHERE property_id = ? AND minio_object_name = ?
            """, (str(self.property_id), self.minio_file_path))
            
            doc_count = cursor.fetchone()['count']
            
            conn.close()
            
            # At least one table should have the record
            passed = fd_count > 0 or doc_count > 0
            message = f"Database records: financial_documents={fd_count}, documents={doc_count}"
            
            if not passed:
                self.report.errors.append("No database record found for this document")
            
            if fd_count == 0 and doc_count > 0:
                self.report.warnings.append("Document only in 'documents' table, not in 'financial_documents'")
            elif fd_count > 0 and doc_count == 0:
                self.report.warnings.append("Document only in 'financial_documents' table, not in 'documents'")
            elif fd_count > 0 and doc_count > 0:
                message += " - Synced across both tables ✓"
            
            result = ValidationResult(
                passed=passed,
                entity_type="database_record",
                expected="record_exists",
                actual=f"fd={fd_count},doc={doc_count}",
                message=message
            )
            
            self.report.validations.append(result)
            return result
            
        except Exception as e:
            self.report.errors.append(f"Database record validation failed: {e}")
            return ValidationResult(
                passed=False,
                entity_type="database_record",
                expected=0,
                actual=0,
                message=f"Error: {e}"
            )
    
    def validate_all(self, expected_metadata: Optional[Dict] = None) -> ValidationReport:
        """
        Run all document validations
        
        Args:
            expected_metadata: Optional metadata to validate against
        
        Returns:
            ValidationReport with all validation results
        """
        print(f"\n{'='*80}")
        print(f"DOCUMENT VALIDATION")
        print(f"Property ID: {self.property_id}")
        print(f"File: {self.minio_file_path}")
        print(f"{'='*80}\n")
        
        # Run validations
        self.validate_storage_path()
        self.validate_database_record()
        
        if expected_metadata:
            self.validate_metadata_extraction(expected_metadata)
        
        # Log results
        self.log_discrepancies()
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"VALIDATION SUMMARY")
        print(f"{'='*80}")
        print(f"Status: {'✅ PASS' if self.report.passed else '❌ FAIL'}")
        print(f"Validations run: {len(self.report.validations)}")
        print(f"Passed: {sum(1 for v in self.report.validations if v.passed)}")
        print(f"Failed: {sum(1 for v in self.report.validations if not v.passed)}")
        print(f"Errors: {len(self.report.errors)}")
        print(f"Warnings: {len(self.report.warnings)}")
        print(f"{'='*80}\n")
        
        return self.report




