#!/usr/bin/env python3
"""
Simple script to populate property_financials_history with current data
"""

import sqlite3
import re
import json
from datetime import datetime

def extract_year_from_filename(filename: str):
    """Extract 4-digit year from filename"""
    match = re.search(r'\b(20\d{2})\b', filename)
    return int(match.group(1)) if match else None

def main():
    conn = sqlite3.connect("reims.db")
    cursor = conn.cursor()
    
    try:
        # Get all properties
        cursor.execute("""
            SELECT id, name, current_market_value, monthly_rent, annual_noi, 
                   occupancy_rate, total_units, occupied_units
            FROM properties
        """)
        properties = cursor.fetchall()
        
        print(f"Found {len(properties)} properties")
        
        # Get documents with years
        cursor.execute("""
            SELECT property_id, original_filename, upload_timestamp
            FROM documents
            WHERE original_filename IS NOT NULL
        """)
        documents = cursor.fetchall()
        
        print(f"Found {len(documents)} documents")
        
        # Create historical records for each property
        for prop in properties:
            prop_id, name, market_value, monthly_rent, annual_noi, occupancy_rate, total_units, occupied_units = prop
            
            # Find documents for this property
            prop_docs = [doc for doc in documents if doc[0] == str(prop_id)]
            
            # Extract years from documents
            years = set()
            for doc in prop_docs:
                year = extract_year_from_filename(doc[1])
                if year:
                    years.add(year)
            
            # If no years found, use current year
            if not years:
                years = {datetime.now().year}
            
            print(f"Processing {name} (ID: {prop_id}) - Years: {sorted(years)}")
            
            # Create records for each year
            for year in sorted(years):
                is_partial_year = year == datetime.now().year
                
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO property_financials_history (
                            property_id, fiscal_year, is_partial_year,
                            current_market_value, monthly_rent, annual_noi, 
                            occupancy_rate, total_units, occupied_units,
                            data_source, confidence_score
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        prop_id, year, is_partial_year,
                        market_value, monthly_rent, annual_noi,
                        occupancy_rate, total_units, occupied_units,
                        'Current Data', 0.8
                    ))
                    print(f"  ✅ Created record for {year}")
                    
                except Exception as e:
                    print(f"  ❌ Error: {e}")
        
        conn.commit()
        print(f"\n✅ Successfully populated historical data!")
        
        # Show summary
        cursor.execute("""
            SELECT fiscal_year, COUNT(*) as count
            FROM property_financials_history 
            GROUP BY fiscal_year 
            ORDER BY fiscal_year DESC
        """)
        
        print("\n📊 Summary:")
        for row in cursor.fetchall():
            year, count = row
            print(f"  {year}: {count} properties")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
