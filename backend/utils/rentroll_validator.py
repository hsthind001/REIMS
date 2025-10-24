"""
Rent Roll Validator
Specialized validator for rent roll imports
"""

from typing import Dict, List, Set
import re
import PyPDF2
import io
from .import_validator import ImportValidator, ValidationReport, ValidationResult


class RentRollValidator(ImportValidator):
    """
    Specialized validator for rent roll document imports
    Validates unit counts, tenant data, and occupancy calculations
    """
    
    def __init__(self, minio_file_path: str, property_id: int, db_path: str = "reims.db"):
        """
        Initialize rent roll validator
        
        Args:
            minio_file_path: Path to rent roll PDF in MinIO
            property_id: Property ID in database
            db_path: Path to SQLite database
        """
        super().__init__(minio_file_path, property_id, db_path)
        self.pdf_data = None
        self.pdf_text = None
    
    def _download_pdf(self):
        """Download PDF from MinIO"""
        if self.pdf_data is None:
            try:
                # Default to reims-files bucket
                bucket_name = "reims-files"
                object_name = self.minio_file_path
                
                response = self.minio_client.get_object(bucket_name, object_name)
                self.pdf_data = response.read()
                response.close()
                response.release_conn()
            except Exception as e:
                self.report.errors.append(f"Failed to download PDF: {e}")
                raise
    
    def _extract_pdf_text(self):
        """Extract text from PDF"""
        if self.pdf_text is None:
            try:
                self._download_pdf()
                pdf_file = io.BytesIO(self.pdf_data)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                self.pdf_text = ""
                for page in pdf_reader.pages:
                    self.pdf_text += page.extract_text() + "\n"
            except Exception as e:
                self.report.errors.append(f"Failed to extract PDF text: {e}")
                raise
    
    def _get_pdf_units(self) -> Set[str]:
        """Extract unique unit numbers from PDF"""
        self._extract_pdf_text()
        
        # Pattern to match unit numbers in various formats
        # Adjust pattern based on actual rent roll format
        unit_pattern = r'(?:Hammond Aire Plaza|Property)\s+\((?:hmnd|[a-z]+)\)(\d+[A-Z-]*)'
        units = re.findall(unit_pattern, self.pdf_text, re.IGNORECASE)
        
        return set(units)
    
    def _get_db_units(self) -> Set[str]:
        """Get unit numbers from database"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT unit_number FROM stores 
            WHERE property_id = ?
        """, (self.property_id,))
        
        units = set([row['unit_number'] for row in cursor.fetchall()])
        conn.close()
        
        return units
    
    def _get_pdf_tenant_count(self) -> int:
        """Count tenants (occupied units) in PDF"""
        self._extract_pdf_text()
        
        # Count tenant IDs which indicate occupied units
        tenant_ids = re.findall(r'\(t\d{7}\)', self.pdf_text)
        return len(tenant_ids)
    
    def _get_db_tenant_count(self) -> int:
        """Count occupied units in database"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM stores 
            WHERE property_id = ? AND status = 'occupied'
        """, (self.property_id,))
        
        count = cursor.fetchone()['count']
        conn.close()
        
        return count
    
    def validate_unit_count(self) -> ValidationResult:
        """
        Validate total unit count matches between PDF and database
        
        Returns:
            ValidationResult
        """
        try:
            pdf_units = self._get_pdf_units()
            
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count FROM stores WHERE property_id = ?
            """, (self.property_id,))
            db_count = cursor.fetchone()['count']
            conn.close()
            
            return self.validate_count(len(pdf_units), db_count, "total_units")
            
        except Exception as e:
            self.report.errors.append(f"Unit count validation failed: {e}")
            return ValidationResult(
                passed=False,
                entity_type="total_units",
                expected=0,
                actual=0,
                message=f"Error: {e}"
            )
    
    def validate_tenant_names(self) -> ValidationResult:
        """
        Validate occupied unit count matches
        
        Returns:
            ValidationResult
        """
        try:
            pdf_count = self._get_pdf_tenant_count()
            db_count = self._get_db_tenant_count()
            
            return self.validate_count(pdf_count, db_count, "occupied_units")
            
        except Exception as e:
            self.report.errors.append(f"Tenant count validation failed: {e}")
            return ValidationResult(
                passed=False,
                entity_type="occupied_units",
                expected=0,
                actual=0,
                message=f"Error: {e}"
            )
    
    def validate_occupancy_rate(self) -> ValidationResult:
        """
        Validate calculated occupancy rate is correct
        
        Returns:
            ValidationResult
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get property-level occupancy rate
            cursor.execute("""
                SELECT total_units, occupied_units, occupancy_rate 
                FROM properties WHERE id = ?
            """, (self.property_id,))
            
            prop = cursor.fetchone()
            
            if prop:
                total = prop['total_units']
                occupied = prop['occupied_units']
                stored_rate = prop['occupancy_rate']
                
                # Calculate expected rate
                if total > 0:
                    calculated_rate = round((occupied / total) * 100, 1)
                else:
                    calculated_rate = 0
                
                passed = abs(stored_rate - calculated_rate) < 0.5  # Allow 0.5% tolerance
                
                message = f"Occupancy rate: stored {stored_rate}%, calculated {calculated_rate}%"
                if not passed:
                    message += " - MISMATCH"
                    self.report.errors.append(message)
                
                result = ValidationResult(
                    passed=passed,
                    entity_type="occupancy_rate",
                    expected=calculated_rate,
                    actual=stored_rate,
                    message=message
                )
                
                self.report.validations.append(result)
                conn.close()
                return result
            else:
                conn.close()
                raise ValueError(f"Property {self.property_id} not found")
                
        except Exception as e:
            self.report.errors.append(f"Occupancy rate validation failed: {e}")
            return ValidationResult(
                passed=False,
                entity_type="occupancy_rate",
                expected=0,
                actual=0,
                message=f"Error: {e}"
            )
    
    def validate_unit_numbers(self) -> ValidationResult:
        """
        Validate all unit numbers from PDF are present in database
        
        Returns:
            ValidationResult
        """
        try:
            pdf_units = self._get_pdf_units()
            db_units = self._get_db_units()
            
            return self.validate_completeness(pdf_units, db_units, "unit_numbers")
            
        except Exception as e:
            self.report.errors.append(f"Unit number validation failed: {e}")
            return ValidationResult(
                passed=False,
                entity_type="unit_numbers",
                expected=0,
                actual=0,
                message=f"Error: {e}"
            )
    
    def check_missing_units(self) -> List[str]:
        """
        Identify units in PDF but not in database
        
        Returns:
            List of missing unit numbers
        """
        pdf_units = self._get_pdf_units()
        db_units = self._get_db_units()
        
        missing = pdf_units - db_units
        return sorted(list(missing))
    
    def validate_all(self) -> ValidationReport:
        """
        Run all rent roll validations
        
        Returns:
            ValidationReport with all validation results
        """
        print(f"\n{'='*80}")
        print(f"RENT ROLL VALIDATION")
        print(f"Property ID: {self.property_id}")
        print(f"File: {self.minio_file_path}")
        print(f"{'='*80}\n")
        
        # Run all validations
        self.validate_unit_count()
        self.validate_tenant_names()
        self.validate_occupancy_rate()
        self.validate_unit_numbers()
        
        # Check for missing units
        missing = self.check_missing_units()
        if missing:
            self.report.warnings.append(f"Missing units in database: {missing}")
        
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

