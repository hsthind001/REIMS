#!/usr/bin/env python3
"""
Investigate Property KPI Data Quality Issues
Query database to understand current values and their sources
"""

import sqlite3
import json
import os

def investigate_database():
    """Query database to understand current property values and their sources"""
    
    # Connect to database
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    print("=== DATABASE SCHEMA ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"Table: {table[0]}")
    
    print("\n=== CURRENT PROPERTY VALUES ===")
    cursor.execute("""
        SELECT id, name, current_market_value, annual_noi, occupancy_rate, monthly_rent
        FROM properties 
        WHERE id IN (1,2,3,6) 
        ORDER BY id
    """)
    properties = cursor.fetchall()
    
    for prop in properties:
        prop_id, name, market_value, noi, occupancy, monthly_rent = prop
        cap_rate = (noi / market_value * 100) if market_value and noi else 0
        print(f"Property {prop_id}: {name}")
        print(f"  Market Value: ${market_value:,.2f}" if market_value else "  Market Value: None")
        print(f"  Annual NOI: ${noi:,.2f}" if noi else "  Annual NOI: None")
        print(f"  Monthly Rent: ${monthly_rent:,.2f}" if monthly_rent else "  Monthly Rent: None")
        print(f"  Occupancy: {occupancy:.1%}" if occupancy else "  Occupancy: None")
        print(f"  Cap Rate: {cap_rate:.1f}%")
        print()
    
    print("=== EXTRACTED_METRICS COLUMNS ===")
    cursor.execute("PRAGMA table_info(extracted_metrics)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"{col[1]} ({col[2]})")
    
    print("\n=== EXTRACTED METRICS DATA ===")
    try:
        cursor.execute("SELECT * FROM extracted_metrics LIMIT 10")
        metrics = cursor.fetchall()
        print(f"Found {len(metrics)} extracted metrics records")
        for metric in metrics[:5]:  # Show first 5
            print(f"  {metric}")
    except Exception as e:
        print(f"Error querying extracted_metrics: {e}")
    
    print("\n=== FINANCIAL_DOCUMENTS COLUMNS ===")
    cursor.execute("PRAGMA table_info(financial_documents)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"{col[1]} ({col[2]})")
    
    print("\n=== FINANCIAL DOCUMENTS DATA ===")
    try:
        cursor.execute("SELECT * FROM financial_documents LIMIT 10")
        docs = cursor.fetchall()
        print(f"Found {len(docs)} financial document records")
        for doc in docs[:5]:  # Show first 5
            print(f"  {doc}")
    except Exception as e:
        print(f"Error querying financial_documents: {e}")
    
    print("\n=== DOCUMENTS TABLE ===")
    try:
        cursor.execute("SELECT id, property_id, document_type, filename FROM documents WHERE property_id IN (1,2,3,6) ORDER BY property_id")
        docs = cursor.fetchall()
        print(f"Found {len(docs)} document records")
        for doc in docs:
            doc_id, prop_id, doc_type, filename = doc
            print(f"  Property {prop_id}: {doc_type} - {filename}")
    except Exception as e:
        print(f"Error querying documents: {e}")
    
    conn.close()

def check_property_mappings():
    """Check property document mappings file"""
    print("\n=== PROPERTY DOCUMENT MAPPINGS ===")
    if os.path.exists('property_document_mappings.json'):
        with open('property_document_mappings.json', 'r') as f:
            mappings = json.load(f)
        print(f"Found {len(mappings)} property mappings")
        for prop_id, mapping in mappings.items():
            print(f"Property {prop_id}: {mapping}")
    else:
        print("property_document_mappings.json not found")

if __name__ == "__main__":
    investigate_database()
    check_property_mappings()
