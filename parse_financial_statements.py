#!/usr/bin/env python3
"""
Parse Financial Statements from Extracted PDF Data
Extracts structured financial metrics from ESP 2024 financial documents
"""

import sqlite3
import json
import uuid
import re
from datetime import datetime

DB_PATH = "reims.db"

def extract_financial_metrics(text, document_type):
    """Extract financial metrics from document text"""
    metrics = {}
    
    # Common patterns for financial data
    currency_pattern = r'[\$]?\s*([\d,]+\.?\d*)'
    
    if "Balance Sheet" in document_type:
        # Extract balance sheet items
        patterns = {
            'total_assets': r'Total Assets[:\s]+([\d,]+\.?\d*)',
            'total_liabilities': r'Total Liabilities[:\s]+([\d,]+\.?\d*)',
            'equity': r'(?:Total Equity|Net Worth)[:\s]+([\d,]+\.?\d*)',
            'cash': r'Cash[:\s]+(?:Operating|on Hand)[:\s]+([\d,]+\.?\d*)',
        }
        
    elif "Income Statement" in document_type:
        # Extract income statement items
        patterns = {
            'total_revenue': r'(?:Total Revenue|Base Rentals)[:\s]+([\d,]+\.?\d*)',
            'total_expenses': r'Total (?:Expenses|Operating Expenses)[:\s]+([\d,]+\.?\d*)',
            'net_income': r'(?:Net Income|Net Operating Income|NOI)[:\s]+([\d,]+\.?\d*)',
            'occupancy_rate': r'Occupancy[:\s]+([\d\.]+)%?',
        }
        
    elif "Cash Flow" in document_type:
        # Extract cash flow items
        patterns = {
            'operating_cash_flow': r'(?:Operating Activities|Cash from Operations)[:\s]+([\d,]+\.?\d*)',
            'investing_cash_flow': r'(?:Investing Activities|Cash from Investing)[:\s]+([\d,]+\.?\d*)',
            'financing_cash_flow': r'(?:Financing Activities|Cash from Financing)[:\s]+([\d,]+\.?\d*)',
        }
    else:
        patterns = {}
    
    # Extract metrics using patterns
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value_str = match.group(1).replace(',', '').replace('$', '')
            try:
                metrics[key] = float(value_str)
            except ValueError:
                metrics[key] = None
    
    return metrics

def create_property_from_documents():
    """Create ESP property record from financial documents"""
    print("\n╔══════════════════════════════════════════════════════════════════════╗")
    print("║          📊 PARSING FINANCIAL STATEMENTS 📊                          ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all documents for property 1 (ESP)
    cursor.execute("""
        SELECT d.document_id, d.original_filename, d.property_id, e.extracted_content
        FROM documents d
        JOIN extracted_data e ON d.document_id = e.document_id
        WHERE d.property_id = '1'
    """)
    
    documents = cursor.fetchall()
    
    if not documents:
        print("❌ No documents found for ESP (Property ID: 1)")
        conn.close()
        return
    
    print(f"📄 Found {len(documents)} ESP financial documents\n")
    
    # Initialize property data
    property_data = {
        'property_code': 'ESP001',
        'name': 'Empire State Plaza',
        'address': '1 Empire State Plaza',
        'city': 'Albany',
        'state': 'NY',
        'zip_code': '12210',
        'country': 'USA',
        'property_type': 'commercial',
        'status': 'active',
        'year': 2024,
        'documents_count': len(documents),
        'financial_metrics': {}
    }
    
    # Parse each document
    for doc_id, filename, prop_id, extracted_json in documents:
        print(f"📋 Processing: {filename}")
        
        try:
            extracted_data = json.loads(extracted_json)
            full_text = extracted_data.get('full_text', '')
            
            # Determine document type from filename
            if 'Balance Sheet' in filename:
                doc_type = 'Balance Sheet'
            elif 'Income Statement' in filename:
                doc_type = 'Income Statement'
            elif 'Cash Flow' in filename:
                doc_type = 'Cash Flow Statement'
            else:
                doc_type = 'Other'
            
            # Extract metrics
            metrics = extract_financial_metrics(full_text, doc_type)
            property_data['financial_metrics'][doc_type] = metrics
            
            print(f"   ✓ Extracted {len(metrics)} metrics from {doc_type}")
            for key, value in metrics.items():
                if value is not None:
                    print(f"     • {key}: {value:,.2f}" if isinstance(value, float) else f"     • {key}: {value}")
            print()
            
        except Exception as e:
            print(f"   ⚠️  Error parsing {filename}: {e}\n")
    
    # Calculate derived metrics
    financials = property_data['financial_metrics']
    
    # Aggregate key metrics
    aggregated = {
        'total_value': 0,
        'monthly_revenue': 0,
        'annual_expenses': 0,
        'noi': 0,
        'occupancy_rate': 95.0,  # Default if not found
    }
    
    # Get values from statements
    if 'Balance Sheet' in financials:
        bs = financials['Balance Sheet']
        aggregated['total_value'] = bs.get('property_and_equipment', bs.get('total_assets', 0))
    
    if 'Income Statement' in financials:
        inc = financials['Income Statement']
        aggregated['monthly_revenue'] = inc.get('total_revenue', 0) / 12 if inc.get('total_revenue') else 0
        aggregated['annual_expenses'] = inc.get('total_expenses', 0)
        aggregated['noi'] = inc.get('net_income', 0)
        if inc.get('occupancy_rate'):
            aggregated['occupancy_rate'] = inc['occupancy_rate']
    
    property_data['aggregated_metrics'] = aggregated
    
    # Check if property already exists
    cursor.execute("SELECT COUNT(*) FROM properties WHERE property_code = ?", ('ESP001',))
    exists = cursor.fetchone()[0] > 0
    
    if exists:
        print("📝 Updating existing ESP property record...")
        cursor.execute("""
            UPDATE properties
            SET name = ?, address = ?, city = ?, state = ?, zip_code = ?, country = ?,
                property_type = ?, status = ?, current_market_value = ?,
                monthly_rent = ?, updated_at = ?
            WHERE property_code = ?
        """, (
            property_data['name'],
            property_data['address'],
            property_data['city'],
            property_data['state'],
            property_data['zip_code'],
            property_data['country'],
            property_data['property_type'],
            property_data['status'],
            aggregated['total_value'],
            aggregated['monthly_revenue'],
            datetime.utcnow(),
            'ESP001'
        ))
    else:
        print("📝 Creating new ESP property record...")
        cursor.execute("""
            INSERT INTO properties (
                property_code, name, address, city, state, zip_code, country,
                property_type, status, current_market_value, monthly_rent, 
                year_built, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'ESP001',
            property_data['name'],
            property_data['address'],
            property_data['city'],
            property_data['state'],
            property_data['zip_code'],
            property_data['country'],
            property_data['property_type'],
            property_data['status'],
            aggregated['total_value'],
            aggregated['monthly_revenue'],
            2024,
            datetime.utcnow()
        ))
    
    conn.commit()
    
    # Display summary
    print("\n" + "="*70)
    print("📊 PROPERTY RECORD CREATED/UPDATED")
    print("="*70)
    print(f"\n  Property: {property_data['name']}")
    print(f"  Property Code: {property_data['property_code']}")
    print(f"  Location: {property_data['city']}, {property_data['state']}")
    print(f"  Type: {property_data['property_type']}")
    print(f"  Status: {property_data['status']}")
    print(f"  Year: {property_data['year']}")
    print(f"  Documents: {property_data['documents_count']}")
    print(f"\n  Financial Metrics:")
    print(f"    Total Value: ${aggregated['total_value']:,.2f}")
    print(f"    Monthly Revenue: ${aggregated['monthly_revenue']:,.2f}")
    print(f"    Annual Expenses: ${aggregated['annual_expenses']:,.2f}")
    print(f"    NOI: ${aggregated['noi']:,.2f}")
    print(f"    Occupancy Rate: {aggregated['occupancy_rate']:.1f}%")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM properties WHERE property_code = 'ESP001'")
    count = cursor.fetchone()[0]
    
    print(f"\n✅ Property record {'updated' if exists else 'created'} successfully!")
    print(f"   ESP property in database: {count}")
    
    # Get total properties
    cursor.execute("SELECT COUNT(*) FROM properties")
    total = cursor.fetchone()[0]
    print(f"   Total properties in database: {total}")
    print("\n" + "="*70)
    
    conn.close()
    
    return property_data

if __name__ == "__main__":
    create_property_from_documents()

