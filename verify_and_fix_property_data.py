#!/usr/bin/env python3
"""
Verify and Fix Property KPI Data Quality Issues
Re-extract data from source PDFs and correct database values
"""

import sqlite3
import json
import os
import sys
from minio import Minio
from minio.error import S3Error
import pdfplumber
import tempfile

# Database connection
def get_db_connection():
    return sqlite3.connect('reims.db')

# MinIO connection
def get_minio_client():
    return Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

def analyze_current_data():
    """Analyze current property data and identify issues"""
    print("=== CURRENT PROPERTY DATA ANALYSIS ===")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all property data
    cursor.execute("""
        SELECT id, name, current_market_value, annual_noi, occupancy_rate, monthly_rent
        FROM properties 
        WHERE id IN (1,2,3,6) 
        ORDER BY id
    """)
    properties = cursor.fetchall()
    
    issues = []
    
    for prop in properties:
        prop_id, name, market_value, noi, occupancy, monthly_rent = prop
        cap_rate = (noi / market_value * 100) if market_value and noi else 0
        
        print(f"\nProperty {prop_id}: {name}")
        print(f"  Market Value: ${market_value:,.2f}" if market_value else "  Market Value: None")
        print(f"  Annual NOI: ${noi:,.2f}" if noi else "  Annual NOI: None")
        print(f"  Monthly Rent: ${monthly_rent:,.2f}" if monthly_rent else "  Monthly Rent: None")
        print(f"  Occupancy: {occupancy:.1%}" if occupancy else "  Occupancy: None")
        print(f"  Cap Rate: {cap_rate:.1f}%")
        
        # Identify issues
        if cap_rate > 15 or cap_rate < 3:
            issues.append({
                'property_id': prop_id,
                'property_name': name,
                'issue': f'Unrealistic cap rate: {cap_rate:.1f}%',
                'market_value': market_value,
                'noi': noi,
                'cap_rate': cap_rate
            })
            print(f"  ⚠️  ISSUE: Unrealistic cap rate ({cap_rate:.1f}%)")
    
    conn.close()
    return issues

def get_property_documents():
    """Get document mappings for each property"""
    with open('property_document_mappings.json', 'r') as f:
        mappings = json.load(f)
    
    property_docs = {}
    for mapping in mappings:
        prop_id = mapping['property_id']
        if prop_id not in property_docs:
            property_docs[prop_id] = []
        
        property_docs[prop_id].append({
            'filename': mapping['filename'],
            'minio_path': mapping['minio_path'],
            'document_type': mapping['document_type'],
            'year': mapping['document_year']
        })
    
    return property_docs

def download_pdf_from_minio(minio_path, temp_file):
    """Download PDF from MinIO to temporary file"""
    try:
        minio_client = get_minio_client()
        minio_client.fget_object("reims-files", minio_path, temp_file)
        return True
    except S3Error as e:
        print(f"Error downloading {minio_path}: {e}")
        return False

def extract_financial_data_from_pdf(pdf_path, document_type):
    """Extract financial data from PDF using pdfplumber"""
    extracted_data = {}
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                # Extract based on document type
                if document_type == 'balance_sheet':
                    # Look for total assets, total liabilities, total equity
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if 'total assets' in line.lower() and '$' in line:
                            # Extract number
                            import re
                            numbers = re.findall(r'[\d,]+\.?\d*', line)
                            if numbers:
                                try:
                                    value = float(numbers[-1].replace(',', ''))
                                    extracted_data['total_assets'] = value
                                except:
                                    pass
                        elif 'total liabilities' in line.lower() and '$' in line:
                            import re
                            numbers = re.findall(r'[\d,]+\.?\d*', line)
                            if numbers:
                                try:
                                    value = float(numbers[-1].replace(',', ''))
                                    extracted_data['total_liabilities'] = value
                                except:
                                    pass
                        elif 'total equity' in line.lower() and '$' in line:
                            import re
                            numbers = re.findall(r'[\d,]+\.?\d*', line)
                            if numbers:
                                try:
                                    value = float(numbers[-1].replace(',', ''))
                                    extracted_data['total_equity'] = value
                                except:
                                    pass
                
                elif document_type == 'income_statement':
                    # Look for net income, revenue, expenses
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if 'net income' in line.lower() and '$' in line:
                            import re
                            numbers = re.findall(r'[\d,]+\.?\d*', line)
                            if numbers:
                                try:
                                    value = float(numbers[-1].replace(',', ''))
                                    extracted_data['net_income'] = value
                                except:
                                    pass
                        elif 'total revenue' in line.lower() and '$' in line:
                            import re
                            numbers = re.findall(r'[\d,]+\.?\d*', line)
                            if numbers:
                                try:
                                    value = float(numbers[-1].replace(',', ''))
                                    extracted_data['total_revenue'] = value
                                except:
                                    pass
                
                elif document_type == 'rent_roll':
                    # Look for monthly rent totals
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if 'total monthly' in line.lower() and '$' in line:
                            import re
                            numbers = re.findall(r'[\d,]+\.?\d*', line)
                            if numbers:
                                try:
                                    value = float(numbers[-1].replace(',', ''))
                                    extracted_data['monthly_rent'] = value
                                except:
                                    pass
    
    except Exception as e:
        print(f"Error extracting from PDF {pdf_path}: {e}")
    
    return extracted_data

def re_extract_property_data(property_id, property_name):
    """Re-extract data for a specific property from source PDFs"""
    print(f"\n=== RE-EXTRACTING DATA FOR {property_name} (ID: {property_id}) ===")
    
    property_docs = get_property_documents()
    if property_id not in property_docs:
        print(f"No documents found for property {property_id}")
        return {}
    
    extracted_data = {}
    
    for doc in property_docs[property_id]:
        print(f"\nProcessing: {doc['filename']} ({doc['document_type']})")
        
        # Download PDF from MinIO
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name
        
        if download_pdf_from_minio(doc['minio_path'], temp_path):
            # Extract data from PDF
            doc_data = extract_financial_data_from_pdf(temp_path, doc['document_type'])
            print(f"  Extracted: {doc_data}")
            extracted_data.update(doc_data)
            
            # Clean up temp file
            os.unlink(temp_path)
        else:
            print(f"  Failed to download {doc['filename']}")
    
    return extracted_data

def calculate_corrected_values(property_id, extracted_data):
    """Calculate corrected market value and NOI based on extracted data"""
    print(f"\n=== CALCULATING CORRECTED VALUES FOR PROPERTY {property_id} ===")
    
    corrected_values = {}
    
    # For balance sheet data, use total assets as market value
    if 'total_assets' in extracted_data:
        corrected_values['market_value'] = extracted_data['total_assets']
        print(f"Market Value (from total assets): ${extracted_data['total_assets']:,.2f}")
    
    # For income statement data, use net income as NOI
    if 'net_income' in extracted_data:
        corrected_values['annual_noi'] = extracted_data['net_income']
        print(f"Annual NOI (from net income): ${extracted_data['net_income']:,.2f}")
    
    # For rent roll data, use monthly rent
    if 'monthly_rent' in extracted_data:
        corrected_values['monthly_rent'] = extracted_data['monthly_rent']
        print(f"Monthly Rent (from rent roll): ${extracted_data['monthly_rent']:,.2f}")
    
    return corrected_values

def update_database(property_id, corrected_values):
    """Update database with corrected values"""
    print(f"\n=== UPDATING DATABASE FOR PROPERTY {property_id} ===")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if 'market_value' in corrected_values:
        updates.append("current_market_value = ?")
        params.append(corrected_values['market_value'])
        print(f"Updating market value to: ${corrected_values['market_value']:,.2f}")
    
    if 'annual_noi' in corrected_values:
        updates.append("annual_noi = ?")
        params.append(corrected_values['annual_noi'])
        print(f"Updating annual NOI to: ${corrected_values['annual_noi']:,.2f}")
    
    if 'monthly_rent' in corrected_values:
        updates.append("monthly_rent = ?")
        params.append(corrected_values['monthly_rent'])
        print(f"Updating monthly rent to: ${corrected_values['monthly_rent']:,.2f}")
    
    if updates:
        params.append(property_id)
        query = f"UPDATE properties SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        print("Database updated successfully")
    else:
        print("No updates needed")
    
    conn.close()

def verify_corrected_data():
    """Verify all properties have reasonable cap rates after corrections"""
    print("\n=== VERIFICATION OF CORRECTED DATA ===")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, current_market_value, annual_noi, occupancy_rate
        FROM properties 
        WHERE id IN (1,2,3,6) 
        ORDER BY id
    """)
    properties = cursor.fetchall()
    
    all_good = True
    
    for prop in properties:
        prop_id, name, market_value, noi, occupancy = prop
        cap_rate = (noi / market_value * 100) if market_value and noi else 0
        
        print(f"\nProperty {prop_id}: {name}")
        print(f"  Market Value: ${market_value:,.2f}")
        print(f"  Annual NOI: ${noi:,.2f}")
        print(f"  Cap Rate: {cap_rate:.1f}%")
        
        if 3 <= cap_rate <= 15:
            print("  ✅ Cap rate is in reasonable range (3-15%)")
        else:
            print("  ⚠️  Cap rate is still outside reasonable range")
            all_good = False
    
    conn.close()
    return all_good

def main():
    """Main execution function"""
    print("=== PROPERTY KPI DATA QUALITY INVESTIGATION ===")
    
    # Step 1: Analyze current data
    issues = analyze_current_data()
    
    if not issues:
        print("\n✅ No data quality issues found!")
        return
    
    print(f"\nFound {len(issues)} properties with data quality issues")
    
    # Step 2: Re-extract data for problematic properties
    for issue in issues:
        property_id = issue['property_id']
        property_name = issue['property_name']
        
        print(f"\n{'='*60}")
        print(f"INVESTIGATING: {property_name} (ID: {property_id})")
        print(f"Issue: {issue['issue']}")
        print(f"{'='*60}")
        
        # Re-extract data from PDFs
        extracted_data = re_extract_property_data(property_id, property_name)
        
        if extracted_data:
            # Calculate corrected values
            corrected_values = calculate_corrected_values(property_id, extracted_data)
            
            if corrected_values:
                # Update database
                update_database(property_id, corrected_values)
            else:
                print("No corrected values could be calculated")
        else:
            print("No data could be extracted from PDFs")
    
    # Step 3: Verify all corrections
    print(f"\n{'='*60}")
    print("FINAL VERIFICATION")
    print(f"{'='*60}")
    
    all_good = verify_corrected_data()
    
    if all_good:
        print("\n🎉 All property KPIs are now within reasonable ranges!")
    else:
        print("\n⚠️  Some properties still have data quality issues that need manual review")

if __name__ == "__main__":
    main()
