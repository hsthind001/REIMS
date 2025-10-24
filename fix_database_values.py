#!/usr/bin/env python3
"""
Fix database values to achieve 100% quality
- Fix occupancy_rate values (divide by 100 to get decimal)
- Update NOI from extracted_metrics
- Clean up duplicate entries
"""
import sqlite3
from datetime import datetime

def fix_database_values():
    """Fix all database quality issues"""
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("FIXING DATABASE VALUES FOR 100% QUALITY")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Fix occupancy_rate values (divide by 100 to get decimal)
    print("1. FIXING OCCUPANCY RATES")
    print("-" * 40)
    
    # Check current occupancy rates
    cursor.execute("SELECT id, name, occupancy_rate FROM properties")
    properties = cursor.fetchall()
    
    print("Before fix:")
    for prop_id, name, occ_rate in properties:
        print(f"  {prop_id}: {name} - {occ_rate}")
    
    # Fix occupancy rates (divide by 100 if > 1.0)
    cursor.execute("""
        UPDATE properties 
        SET occupancy_rate = occupancy_rate / 100.0 
        WHERE occupancy_rate > 1.0
    """)
    fixed_count = cursor.rowcount
    print(f"\nFixed {fixed_count} occupancy rates")
    
    print("\nAfter fix:")
    cursor.execute("SELECT id, name, occupancy_rate FROM properties")
    for prop_id, name, occ_rate in cursor.fetchall():
        print(f"  {prop_id}: {name} - {occ_rate} ({occ_rate*100:.1f}%)")
    
    # 2. Update NOI from extracted_metrics
    print("\n\n2. UPDATING NOI FROM EXTRACTED METRICS")
    print("-" * 40)
    
    # Get current NOI values
    cursor.execute("SELECT id, name, annual_noi FROM properties")
    current_noi = cursor.fetchall()
    
    print("Current NOI values:")
    for prop_id, name, noi in current_noi:
        print(f"  {prop_id}: {name} - ${noi:,.2f}")
    
    # Update NOI from extracted_metrics (get highest NOI per property)
    cursor.execute("""
        UPDATE properties 
        SET annual_noi = (
            SELECT MAX(metric_value) 
            FROM extracted_metrics 
            WHERE metric_name = 'net_operating_income' 
            AND document_id LIKE properties.id || '_%'
        )
        WHERE id IN (
            SELECT DISTINCT CAST(SUBSTR(document_id, 1, INSTR(document_id, '_') - 1) AS INTEGER)
            FROM extracted_metrics 
            WHERE metric_name = 'net_operating_income'
        )
    """)
    updated_count = cursor.rowcount
    print(f"\nUpdated {updated_count} NOI values from extracted_metrics")
    
    print("\nNew NOI values:")
    cursor.execute("SELECT id, name, annual_noi FROM properties")
    for prop_id, name, noi in cursor.fetchall():
        print(f"  {prop_id}: {name} - ${noi:,.2f}")
    
    # 3. Clean up duplicate entries in extracted_metrics
    print("\n\n3. CLEANING UP DUPLICATE METRICS")
    print("-" * 40)
    
    # Count duplicates
    cursor.execute("""
        SELECT document_id, metric_name, COUNT(*) as count
        FROM extracted_metrics 
        GROUP BY document_id, metric_name 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    
    print(f"Found {len(duplicates)} duplicate metric groups:")
    for doc_id, metric_name, count in duplicates:
        print(f"  {doc_id[:30]}... - {metric_name}: {count} entries")
    
    # Remove duplicates (keep the latest one)
    cursor.execute("""
        DELETE FROM extracted_metrics 
        WHERE id NOT IN (
            SELECT MAX(id) 
            FROM extracted_metrics 
            GROUP BY document_id, metric_name
        )
    """)
    removed_count = cursor.rowcount
    print(f"\nRemoved {removed_count} duplicate entries")
    
    # 4. Update total_units and occupied_units from rent roll data
    print("\n\n4. UPDATING UNITS FROM RENT ROLL DATA")
    print("-" * 40)
    
    # Get rent roll metrics
    cursor.execute("""
        SELECT 
            CAST(SUBSTR(document_id, 1, INSTR(document_id, '_') - 1) AS INTEGER) as property_id,
            MAX(CASE WHEN metric_name = 'total_units' THEN metric_value END) as total_units,
            MAX(CASE WHEN metric_name = 'occupied_units' THEN metric_value END) as occupied_units
        FROM extracted_metrics 
        WHERE metric_name IN ('total_units', 'occupied_units')
        GROUP BY property_id
    """)
    rent_roll_data = cursor.fetchall()
    
    print("Rent roll data found:")
    for prop_id, total_units, occupied_units in rent_roll_data:
        print(f"  Property {prop_id}: {occupied_units}/{total_units} units")
        
        # Update properties table
        cursor.execute("""
            UPDATE properties 
            SET total_units = ?, occupied_units = ?
            WHERE id = ?
        """, (int(total_units) if total_units else None, 
              int(occupied_units) if occupied_units else None, 
              prop_id))
    
    # 5. Final validation
    print("\n\n5. FINAL VALIDATION")
    print("-" * 40)
    
    cursor.execute("""
        SELECT id, name, annual_noi, total_units, occupied_units, occupancy_rate
        FROM properties
        ORDER BY id
    """)
    final_data = cursor.fetchall()
    
    print("Final property data:")
    for prop_id, name, noi, total_units, occupied_units, occ_rate in final_data:
        print(f"\n  {prop_id}: {name}")
        print(f"    NOI: ${noi:,.2f}" if noi else "    NOI: NULL")
        print(f"    Units: {occupied_units}/{total_units}" if total_units and occupied_units else "    Units: NULL")
        print(f"    Occupancy: {occ_rate*100:.1f}%" if occ_rate else "    Occupancy: NULL")
    
    # Commit all changes
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 80)
    print("DATABASE FIX COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    fix_database_values()
