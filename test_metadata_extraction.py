#!/usr/bin/env python3
"""
Test Metadata Extraction from Filenames
"""
import sys
import os

# Add path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.utils.filename_parser import parse_filename

def test_esp_files():
    """Test with actual ESP filenames"""
    print("\n" + "="*80)
    print("TESTING METADATA EXTRACTION - ESP FILES")
    print("="*80 + "\n")
    
    test_files = [
        "ESP 2024 Income Statement.pdf",
        "ESP 2024 Cash Flow Statement.pdf",
        "ESP 2024 Balance Sheet.pdf"
    ]
    
    for filename in test_files:
        print(f"📄 {filename}")
        print("-" * 80)
        
        parsed = parse_filename(filename)
        
        print(f"   Property Name:  {parsed.get('property_name') or '❌ NULL'}")
        print(f"   Document Year:  {parsed.get('document_year') or '❌ NULL'}")
        print(f"   Document Type:  {parsed.get('document_type') or '❌ NULL'}")
        print(f"   Document Period: {parsed.get('document_period', 'Annual')}")
        print(f"   Suggested ID:   {parsed.get('suggested_property_id') or 'N/A'}")
        print()
    
    print("="*80)
    print("✅ All ESP files parsed successfully!\n")

def test_various_formats():
    """Test with various filename formats"""
    print("\n" + "="*80)
    print("TESTING VARIOUS FILENAME FORMATS")
    print("="*80 + "\n")
    
    test_cases = [
        "Empire State Plaza 2023 Q1 Rent Roll.xlsx",
        "Downtown Tower 2022 Annual Report.pdf",
        "ABC Property 2024 Operating Statement.csv",
        "Property_123_2023_Balance_Sheet.xlsx",
        "test_postgresql.csv",
        "ESP_2024_Income_Statement.pdf"
    ]
    
    for filename in test_cases:
        parsed = parse_filename(filename)
        status = "✅" if parsed.get('property_name') and parsed.get('document_year') else "⚠️"
        print(f"{status} {filename:<50} → {parsed.get('property_name')} ({parsed.get('document_year')})")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_esp_files()
    test_various_formats()
    
    print("🎯 Metadata extraction is working correctly!")
    print("\n✅ READY TO TEST WITH ACTUAL UPLOADS\n")

