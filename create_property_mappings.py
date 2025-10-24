#!/usr/bin/env python3
"""
Create mappings between MinIO filenames and property IDs
"""
import sqlite3
from minio import Minio
import re

# Property name mappings from filenames
PROPERTY_NAME_PATTERNS = {
    r'(?i)esp': 'Empire State Plaza',
    r'(?i)hammond': 'Hammond Aire',
    r'(?i)tcsh|crossings': 'The Crossings of Spring Hill',
    r'(?i)wendover': 'Wendover Commons'
}

def extract_property_from_filename(filename):
    """Extract property name from filename"""
    for pattern, property_name in PROPERTY_NAME_PATTERNS.items():
        if re.search(pattern, filename):
            return property_name
    return None

def extract_year_from_filename(filename):
    """Extract year from filename"""
    match = re.search(r'\b(20\d{2})\b', filename)
    return int(match.group(1)) if match else None

def extract_document_type(path):
    """Extract document type from MinIO path"""
    if 'Balance Sheets' in path or 'Balance Sheet' in path.lower():
        return 'balance_sheet'
    elif 'Income Statements' in path or 'Income Statement' in path.lower():
        return 'income_statement'
    elif 'Cash Flow' in path:
        return 'cash_flow_statement'
    elif 'Rent Roll' in path:
        return 'rent_roll'
    return 'other'

def create_mappings():
    """Create property-document mappings"""
    # Connect to MinIO
    minio_client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    
    # Connect to database
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    # Get property IDs
    cursor.execute("SELECT id, name FROM properties")
    properties = {name: prop_id for prop_id, name in cursor.fetchall()}
    
    print("=" * 80)
    print("PROPERTY-DOCUMENT MAPPING")
    print("=" * 80)
    print(f"\nFound {len(properties)} properties in database:")
    for name, prop_id in properties.items():
        print(f"  {prop_id}: {name}")
    
    # List all files in MinIO
    print("\n" + "=" * 80)
    print("MinIO Files Analysis")
    print("=" * 80)
    
    bucket_name = "reims-files"
    prefix = "Financial Statements/"
    
    mappings = []
    objects = minio_client.list_objects(bucket_name, prefix=prefix, recursive=True)
    
    for obj in objects:
        filename = obj.object_name.split('/')[-1]
        property_name = extract_property_from_filename(filename)
        year = extract_year_from_filename(filename)
        doc_type = extract_document_type(obj.object_name)
        
        if property_name and property_name in properties:
            property_id = properties[property_name]
            mappings.append({
                'minio_path': obj.object_name,
                'filename': filename,
                'property_id': property_id,
                'property_name': property_name,
                'document_year': year,
                'document_type': doc_type,
                'file_size': obj.size
            })
            print(f"\n✅ {filename}")
            print(f"   Property: {property_name} (ID: {property_id})")
            print(f"   Type: {doc_type}")
            print(f"   Year: {year}")
            print(f"   Path: {obj.object_name}")
        else:
            print(f"\n⚠️  {filename}")
            print(f"   Property: NOT FOUND")
            print(f"   Detected name: {property_name}")
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: {len(mappings)} files successfully mapped")
    print("=" * 80)
    
    conn.close()
    
    return mappings

if __name__ == "__main__":
    mappings = create_mappings()
    
    # Save mappings to JSON for reference
    import json
    with open('property_document_mappings.json', 'w') as f:
        json.dump(mappings, f, indent=2)
    
    print(f"\n✅ Mappings saved to property_document_mappings.json")

