#!/usr/bin/env python3
"""
Rent Roll Importer Service
Imports parsed rent roll data into the database with validation
"""

import sqlite3
import uuid
from typing import List, Dict, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RentRollImporter:
    """
    Service for importing rent roll data into stores table
    """
    
    def __init__(self, db_path: str = "reims.db"):
        self.db_path = db_path
    
    def import_rent_roll(
        self,
        property_id: int,
        units: List[Dict[str, Any]],
        source_metadata: Dict[str, Any] = None,
        replace_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Import rent roll units into database
        
        Args:
            property_id: Property ID to import units for
            units: List of unit dictionaries
            source_metadata: Metadata about source document
            replace_existing: If True, delete existing units before import
        
        Returns:
            Dictionary with import results
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Validate data before import
            validation = self.validate_rent_roll_data(units, source_metadata)
            
            if not validation['valid']:
                return {
                    'status': 'validation_failed',
                    'validation': validation,
                    'imported_count': 0
                }
            
            # Clear existing data if requested
            if replace_existing:
                self.clear_existing_units(conn, property_id)
            
            # Import units
            imported_count = self.import_units(conn, property_id, units)
            
            # Update property metrics
            self.update_property_metrics(conn, property_id)
            
            conn.close()
            
            return {
                'status': 'success',
                'imported_count': imported_count,
                'validation': validation,
                'property_id': property_id
            }
        
        except Exception as e:
            logger.error(f"Error importing rent roll: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'imported_count': 0
            }
    
    def validate_rent_roll_data(
        self,
        units: List[Dict[str, Any]],
        source_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Validate rent roll data before import
        
        Checks:
        - Unit count matches source document (if provided)
        - All units have required fields
        - No duplicate unit numbers
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'unit_count': len(units)
        }
        
        # Check if we have any units
        if len(units) == 0:
            validation['valid'] = False
            validation['errors'].append("No units to import")
            return validation
        
        # Check for required fields
        required_fields = ['unit_number']
        for i, unit in enumerate(units):
            for field in required_fields:
                if field not in unit or not unit[field]:
                    validation['errors'].append(
                        f"Unit {i+1}: Missing required field '{field}'"
                    )
                    validation['valid'] = False
        
        # Check for duplicate unit numbers
        unit_numbers = [u.get('unit_number') for u in units if u.get('unit_number')]
        duplicates = [num for num in set(unit_numbers) if unit_numbers.count(num) > 1]
        if duplicates:
            validation['warnings'].append(
                f"Duplicate unit numbers found: {', '.join(duplicates)}"
            )
        
        # Validate against source metadata if provided
        if source_metadata:
            expected_count = source_metadata.get('lease_count') or source_metadata.get('total_units')
            if expected_count and len(units) != expected_count:
                validation['warnings'].append(
                    f"Unit count mismatch: {len(units)} units parsed, "
                    f"but source document indicates {expected_count} leases"
                )
        
        return validation
    
    def clear_existing_units(self, conn: sqlite3.Connection, property_id: int) -> int:
        """
        Delete existing units for property
        
        Returns:
            Number of units deleted
        """
        cursor = conn.cursor()
        
        # Count existing units
        cursor.execute(
            "SELECT COUNT(*) FROM stores WHERE property_id = ?",
            (property_id,)
        )
        count = cursor.fetchone()[0]
        
        # Delete all units for this property
        cursor.execute(
            "DELETE FROM stores WHERE property_id = ?",
            (property_id,)
        )
        conn.commit()
        
        logger.info(f"Deleted {count} existing units for property {property_id}")
        return count
    
    def import_units(
        self,
        conn: sqlite3.Connection,
        property_id: int,
        units: List[Dict[str, Any]]
    ) -> int:
        """
        Import units into stores table
        
        Returns:
            Number of units successfully imported
        """
        cursor = conn.cursor()
        imported_count = 0
        
        for unit in units:
            try:
                # Prepare data
                unit_id = str(uuid.uuid4())
                unit_number = unit.get('unit_number', 'Unknown')[:50]
                tenant_name = unit.get('tenant_name', '')[:255]
                status = unit.get('status', 'occupied')[:11]
                sqft = self._to_decimal(unit.get('sqft', 0))
                monthly_rent = self._to_decimal(unit.get('monthly_rent', 0))
                
                # Parse dates if present
                lease_start = self._parse_date(unit.get('lease_start_date'))
                lease_end = self._parse_date(unit.get('lease_end_date'))
                
                # Insert into database
                cursor.execute("""
                    INSERT INTO stores (
                        id, property_id, unit_number, tenant_name, status, sqft,
                        monthly_rent, lease_start, lease_end, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    unit_id,
                    property_id,
                    unit_number,
                    tenant_name,
                    status,
                    sqft,
                    monthly_rent,
                    lease_start,
                    lease_end,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
                imported_count += 1
                logger.debug(f"Imported unit: {unit_number} - {tenant_name}")
            
            except Exception as e:
                logger.error(f"Error importing unit {unit.get('unit_number', 'unknown')}: {e}")
                continue
        
        conn.commit()
        logger.info(f"Successfully imported {imported_count} units")
        
        return imported_count
    
    def update_property_metrics(self, conn: sqlite3.Connection, property_id: int) -> None:
        """
        Update property occupancy metrics based on imported units
        """
        cursor = conn.cursor()
        
        # Calculate metrics
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'occupied' THEN 1 ELSE 0 END) as occupied,
                SUM(sqft) as total_sqft
            FROM stores
            WHERE property_id = ?
        """, (property_id,))
        
        result = cursor.fetchone()
        total_units = result[0]
        occupied_units = result[1] or 0
        total_sqft = result[2] or 0
        
        occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
        
        # Update properties table
        cursor.execute("""
            UPDATE properties
            SET total_units = ?,
                occupied_units = ?,
                occupancy_rate = ?,
                square_footage = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            total_units,
            occupied_units,
            occupancy_rate,
            total_sqft,
            datetime.now().isoformat(),
            property_id
        ))
        
        conn.commit()
        
        logger.info(
            f"Updated property {property_id} metrics: "
            f"{occupied_units}/{total_units} units ({occupancy_rate:.2f}% occupancy)"
        )
    
    @staticmethod
    def _to_decimal(value: Any) -> float:
        """Convert value to decimal, handling strings with commas"""
        if value is None or value == '':
            return 0.0
        
        if isinstance(value, str):
            value = value.replace(',', '').replace('$', '').strip()
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def _parse_date(date_str: Any) -> str:
        """Parse date string to ISO format, returns None if can't parse"""
        if not date_str:
            return None
        
        if isinstance(date_str, datetime):
            return date_str.isoformat()
        
        # Try common date formats
        formats = [
            '%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d/%m/%Y',
            '%m-%d-%Y', '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(str(date_str), fmt)
                return dt.isoformat()
            except ValueError:
                continue
        
        return None


# Global importer instance
rent_roll_importer = RentRollImporter()

