#!/usr/bin/env python3
"""
Populate property_financials_history with data from existing properties and documents
"""

import sqlite3
import re
import json
from datetime import datetime
from typing import Optional, List, Dict

def extract_year_from_filename(filename: str) -> Optional[int]:
    """Extract 4-digit year from filename"""
    match = re.search(r'\b(20\d{2})\b', filename)
    return int(match.group(1)) if match else None

def determine_document_type(filename: str) -> str:
    """Determine document type from filename"""
    filename_lower = filename.lower()
    
    if 'balance' in filename_lower:
        return 'Balance Sheet'
    elif 'income' in filename_lower or 'p&l' in filename_lower or 'profit' in filename_lower:
        return 'Income Statement'
    elif 'cash' in filename_lower or 'flow' in filename_lower:
        return 'Cash Flow Statement'
    elif 'rent' in filename_lower:
        return 'Rent Roll'
    else:
        return 'Other'

def populate_historical_data():
    """Populate property_financials_history with existing data"""
    
    conn = sqlite3.connect("reims.db")
    cursor = conn.cursor()
    
    try:
        print("🔍 Analyzing existing data...")
        
        # Get all properties with their current financial data
        cursor.execute("""
            SELECT id, name, current_market_value, monthly_rent, annual_noi, 
                   occupancy_rate, total_units, occupied_units
            FROM properties
            WHERE current_market_value IS NOT NULL
        """)
        properties = cursor.fetchall()
        
        print(f"Found {len(properties)} properties with financial data")
        
        # Get all documents with years
        cursor.execute("""
            SELECT id, property_id, original_filename, upload_timestamp, document_type
            FROM documents
            WHERE original_filename IS NOT NULL
        """)
        documents = cursor.fetchall()
        
        print(f"Found {len(documents)} documents")
        
        # Group documents by property and year
        property_years = {}
        for doc in documents:
            doc_id, property_id, filename, upload_date, doc_type = doc
            year = extract_year_from_filename(filename)
            
            if year:
                if property_id not in property_years:
                    property_years[property_id] = {}
                if year not in property_years[property_id]:
                    property_years[property_id][year] = {
                        'documents': [],
                        'document_types': set(),
                        'latest_date': None
                    }
                
                property_years[property_id][year]['documents'].append(doc_id)
                property_years[property_id][year]['document_types'].add(determine_document_type(filename))
                
                # Track latest document date for this year
                if upload_date:
                    if not property_years[property_id][year]['latest_date'] or upload_date > property_years[property_id][year]['latest_date']:
                        property_years[property_id][year]['latest_date'] = upload_date
        
        print(f"Found year data for {len(property_years)} properties")
        
        # Create historical records
        records_created = 0
        
        for property_id, years_data in property_years.items():
            # Get current property data
            property_data = next((p for p in properties if p[0] == property_id), None)
            if not property_data:
                continue
                
            _, name, current_market_value, monthly_rent, annual_noi, occupancy_rate, total_units, occupied_units = property_data
            
            for year, year_info in years_data.items():
                # Determine if this is a partial year (current year)
                current_year = datetime.now().year
                is_partial_year = year == current_year
                
                # Determine completeness based on document types
                doc_types = year_info['document_types']
                has_balance = 'Balance Sheet' in doc_types
                has_income = 'Income Statement' in doc_types
                has_cash_flow = 'Cash Flow Statement' in doc_types
                
                # Calculate confidence score based on document completeness
                confidence_score = 0.0
                if has_balance: confidence_score += 0.3
                if has_income: confidence_score += 0.4
                if has_cash_flow: confidence_score += 0.3
                
                # Create historical record
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO property_financials_history (
                            property_id, fiscal_year, is_partial_year, data_through_date,
                            current_market_value, monthly_rent, annual_noi, occupancy_rate,
                            total_units, occupied_units, data_source, document_ids, confidence_score
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        property_id,
                        year,
                        is_partial_year,
                        year_info['latest_date'],
                        current_market_value,
                        monthly_rent,
                        annual_noi,
                        occupancy_rate,
                        total_units,
                        occupied_units,
                        ', '.join(sorted(doc_types)),
                        json.dumps(year_info['documents']),
                        confidence_score
                    ))
                    records_created += 1
                    print(f"  ✅ Created record for {name} - {year} (confidence: {confidence_score:.1f})")
                    
                except Exception as e:
                    print(f"  ❌ Error creating record for property {property_id}, year {year}: {e}")
        
        # Update documents with year information
        print("\n📝 Updating documents with year information...")
        documents_updated = 0
        
        for doc in documents:
            doc_id, property_id, filename, upload_date, doc_type = doc
            year = extract_year_from_filename(filename)
            
            if year:
                # Determine if partial year
                current_year = datetime.now().year
                is_partial_year = year == current_year
                
                # Determine document period
                if 'rent' in filename.lower():
                    document_period = 'Monthly'
                elif any(quarter in filename.lower() for quarter in ['q1', 'q2', 'q3', 'q4']):
                    document_period = 'Quarterly'
                else:
                    document_period = 'Annual'
                
                try:
                    cursor.execute("""
                        UPDATE documents 
                        SET fiscal_year = ?, is_partial_year = ?, document_period = ?
                        WHERE id = ?
                    """, (year, is_partial_year, document_period, doc_id))
                    documents_updated += 1
                    
                except Exception as e:
                    print(f"  ❌ Error updating document {doc_id}: {e}")
        
        conn.commit()
        
        print(f"\n✅ Successfully created {records_created} historical records")
        print(f"✅ Updated {documents_updated} documents with year information")
        
        # Show summary
        cursor.execute("""
            SELECT fiscal_year, COUNT(*) as count, 
                   AVG(confidence_score) as avg_confidence
            FROM property_financials_history 
            GROUP BY fiscal_year 
            ORDER BY fiscal_year DESC
        """)
        
        print("\n📊 Historical Data Summary:")
        for row in cursor.fetchall():
            year, count, avg_conf = row
            print(f"  {year}: {count} properties (avg confidence: {avg_conf:.2f})")
            
    except Exception as e:
        print(f"❌ Error populating historical data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    populate_historical_data()
