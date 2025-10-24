#!/usr/bin/env python3
"""
Audit current database state and identify data gaps
"""
import sqlite3
import json
from datetime import datetime

def audit_database():
    """Audit the current database state"""
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("DATABASE AUDIT REPORT")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Check properties table
    print("1. PROPERTIES TABLE")
    print("-" * 80)
    cursor.execute("SELECT id, name, annual_noi, total_units, occupied_units, occupancy_rate FROM properties")
    properties = cursor.fetchall()
    print(f"Total Properties: {len(properties)}\n")
    for prop in properties:
        print(f"  ID: {prop[0]}")
        print(f"  Name: {prop[1]}")
        print(f"  Annual NOI: ${prop[2]:,.2f}" if prop[2] else "  Annual NOI: NULL")
        print(f"  Total Units: {prop[3]}" if prop[3] else "  Total Units: NULL")
        print(f"  Occupied Units: {prop[4]}" if prop[4] else "  Occupied Units: NULL")
        print(f"  Occupancy Rate: {prop[5]:.2%}" if prop[5] else "  Occupancy Rate: NULL")
        print()
    
    # 2. Check documents table
    print("\n2. DOCUMENTS TABLE")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*), status FROM documents GROUP BY status")
    doc_status = cursor.fetchall()
    print("Document Status Summary:")
    for status in doc_status:
        print(f"  {status[1]}: {status[0]} documents")
    
    cursor.execute("SELECT COUNT(*) FROM documents WHERE property_name IS NULL")
    null_property = cursor.fetchone()[0]
    if null_property > 0:
        print(f"\n  WARNING: {null_property} documents have NULL property_name")
    
    # 3. Check stores table
    print("\n3. STORES TABLE")
    print("-" * 80)
    cursor.execute("SELECT property_id, COUNT(*) FROM stores GROUP BY property_id")
    stores_by_property = cursor.fetchall()
    print("Stores/Units by Property:")
    for prop_id, count in stores_by_property:
        cursor.execute("SELECT name FROM properties WHERE id = ?", (prop_id,))
        prop_name = cursor.fetchone()
        if prop_name:
            print(f"  {prop_name[0]}: {count} units")
        else:
            print(f"  Property ID {prop_id}: {count} units (ORPHANED)")
    
    # 4. Check extracted_data table
    print("\n4. EXTRACTED_DATA TABLE")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) FROM extracted_data")
    extracted_count = cursor.fetchone()[0]
    print(f"Total Extracted Data Records: {extracted_count}")
    
    cursor.execute("""
        SELECT document_id, data_type, extraction_timestamp 
        FROM extracted_data 
        ORDER BY extraction_timestamp DESC 
        LIMIT 5
    """)
    recent_extractions = cursor.fetchall()
    if recent_extractions:
        print("\nRecent Extractions:")
        for doc_id, data_type, timestamp in recent_extractions:
            print(f"  {doc_id[:8]}... - {data_type} - {timestamp}")
    
    # 5. Check extracted_metrics table
    print("\n5. EXTRACTED_METRICS TABLE")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) FROM extracted_metrics")
    metrics_count = cursor.fetchone()[0]
    print(f"Total Metrics: {metrics_count}")
    
    # 6. Check financial_documents table
    print("\n6. FINANCIAL_DOCUMENTS TABLE")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*), status FROM financial_documents GROUP BY status")
    fin_doc_status = cursor.fetchall()
    print("Financial Document Status:")
    for status in fin_doc_status:
        print(f"  {status[1]}: {status[0]} documents")
    
    # 7. Data gaps analysis
    print("\n7. DATA GAPS ANALYSIS")
    print("-" * 80)
    gaps = []
    
    # Check for properties without NOI
    cursor.execute("SELECT COUNT(*) FROM properties WHERE annual_noi IS NULL OR annual_noi = 0")
    no_noi = cursor.fetchone()[0]
    if no_noi > 0:
        gaps.append(f"Properties without NOI: {no_noi}")
    
    # Check for properties without occupancy data
    cursor.execute("SELECT COUNT(*) FROM properties WHERE occupancy_rate IS NULL OR occupancy_rate = 0")
    no_occupancy = cursor.fetchone()[0]
    if no_occupancy > 0:
        gaps.append(f"Properties without occupancy data: {no_occupancy}")
    
    # Check for documents without extracted data
    cursor.execute("""
        SELECT COUNT(*) FROM documents d
        LEFT JOIN extracted_data ed ON d.document_id = ed.document_id
        WHERE ed.id IS NULL AND d.status = 'completed'
    """)
    no_extraction = cursor.fetchone()[0]
    if no_extraction > 0:
        gaps.append(f"Completed documents without extracted data: {no_extraction}")
    
    if gaps:
        print("GAPS FOUND:")
        for gap in gaps:
            print(f"  ⚠️  {gap}")
    else:
        print("✅ No critical data gaps found")
    
    # 8. Property-Document Mapping
    print("\n8. PROPERTY-DOCUMENT MAPPING")
    print("-" * 80)
    cursor.execute("""
        SELECT property_name, document_type, document_year, COUNT(*)
        FROM documents
        WHERE property_name IS NOT NULL
        GROUP BY property_name, document_type, document_year
        ORDER BY property_name, document_year, document_type
    """)
    doc_mapping = cursor.fetchall()
    current_property = None
    for prop_name, doc_type, doc_year, count in doc_mapping:
        if prop_name != current_property:
            print(f"\n{prop_name}:")
            current_property = prop_name
        print(f"  {doc_year} {doc_type}: {count} file(s)")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("END OF AUDIT REPORT")
    print("=" * 80)

if __name__ == "__main__":
    audit_database()

