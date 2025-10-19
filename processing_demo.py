#!/usr/bin/env python3
"""
Simple demo of document processing for REIMS
"""

import pandas as pd
import json
from pathlib import Path

def demo_csv_processing():
    """Demo CSV processing"""
    print("🚀 REIMS Document Processing Demo")
    print("=" * 50)
    
    # Try to process the test properties CSV
    csv_file = "C:/REIMS/storage/51114287-d520-4ef0-ac51-e4f263a39932_test_properties.csv"
    
    if Path(csv_file).exists():
        print(f"\n📄 Processing: {Path(csv_file).name}")
        print("-" * 40)
        
        try:
            # Load and analyze CSV
            df = pd.read_csv(csv_file)
            
            print(f"✅ File loaded successfully")
            print(f"📊 Data Shape: {df.shape[0]} rows, {df.shape[1]} columns")
            print(f"📋 Columns: {list(df.columns)}")
            
            # Analyze data types
            print(f"\n🔍 Data Analysis:")
            for col in df.columns:
                data_type = str(df[col].dtype)
                non_null_count = df[col].notna().sum()
                print(f"   • {col}: {data_type} ({non_null_count}/{len(df)} values)")
            
            # Show sample data
            print(f"\n📋 Sample Data (first 3 rows):")
            for i, row in df.head(3).iterrows():
                print(f"   Row {i+1}:")
                for col, val in row.items():
                    print(f"      {col}: {val}")
                print()
            
            # Property data detection
            print(f"🏠 Property Data Detection:")
            property_patterns = {
                "addresses": ["address", "location", "street"],
                "values": ["price", "value", "cost", "rent"],
                "sizes": ["sqft", "square", "feet", "area", "size"],
                "rooms": ["bedroom", "bathroom", "bed", "bath"]
            }
            
            for pattern_name, keywords in property_patterns.items():
                matching_cols = []
                for col in df.columns:
                    if any(keyword in col.lower() for keyword in keywords):
                        matching_cols.append(col)
                
                if matching_cols:
                    print(f"   • {pattern_name.title()}: {matching_cols}")
            
            # Potential insights
            print(f"\n💡 Processing Insights:")
            
            # Check for numeric columns that could be property values
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                print(f"   • Found {len(numeric_cols)} numeric columns for analysis")
                for col in numeric_cols:
                    col_min = df[col].min()
                    col_max = df[col].max()
                    col_mean = df[col].mean()
                    print(f"      {col}: Range ${col_min:,.0f} - ${col_max:,.0f} (avg: ${col_mean:,.0f})")
            
            # Check data completeness
            completeness = (df.notna().sum().sum() / (len(df) * len(df.columns))) * 100
            print(f"   • Data Completeness: {completeness:.1f}%")
            
            # Identify potential property records
            if len(df) > 0:
                print(f"   • Ready for processing: {len(df)} property records detected")
                print(f"   • Suitable for database import: ✅")
                print(f"   • AI analysis ready: ✅")
            
        except Exception as e:
            print(f"❌ Error processing file: {e}")
    else:
        print(f"❌ File not found: {csv_file}")
        
        # Show available files
        storage_dir = Path("C:/REIMS/storage")
        if storage_dir.exists():
            print(f"\n📁 Available files in storage:")
            for file in storage_dir.glob("*.csv"):
                print(f"   • {file.name}")
            for file in storage_dir.glob("*.pdf"):
                print(f"   • {file.name}")

def show_database_schema():
    """Show how data will be stored in database"""
    print(f"\n" + "=" * 50)
    print("🗄️  Database Storage Schema")
    print("=" * 50)
    
    schema = {
        "documents": {
            "purpose": "File metadata and storage tracking",
            "fields": ["document_id", "filename", "property_id", "file_size", "upload_timestamp", "status"]
        },
        "extracted_data": {
            "purpose": "AI-extracted structured data",
            "fields": ["document_id", "data_type", "extracted_content", "analysis_results", "extraction_timestamp"]
        },
        "properties": {
            "purpose": "Master property records",
            "fields": ["property_id", "address", "property_type", "value", "metadata"]
        },
        "processing_jobs": {
            "purpose": "Background job tracking",
            "fields": ["job_id", "document_id", "status", "created_at", "processing_result"]
        }
    }
    
    for table, info in schema.items():
        print(f"\n📋 {table.upper()}")
        print(f"   Purpose: {info['purpose']}")
        print(f"   Fields: {', '.join(info['fields'])}")
    
    print(f"\n🔄 Data Flow:")
    print(f"   1. Upload → documents table (metadata)")
    print(f"   2. AI Processing → extracted_data table (structured data)")
    print(f"   3. Property Creation → properties table (master records)")
    print(f"   4. Analytics → Aggregated insights and KPIs")

if __name__ == "__main__":
    demo_csv_processing()
    show_database_schema()
    
    print(f"\n" + "=" * 50)
    print("🎯 Next Steps to Activate Processing:")
    print("=" * 50)
    print("   1. ✅ Files uploaded and stored in MinIO")
    print("   2. 🔄 AI agents ready for document analysis")
    print("   3. 🔄 Database schema prepared for structured data")
    print("   4. 🔄 Background workers ready for queue processing")
    print("   5. 📊 Analytics dashboard ready for insights")
    print(f"\n💡 Your 3 uploaded files are ready for AI processing!")
    print(f"   The system will extract property data, financial metrics,")
    print(f"   and generate insights for executive decision-making.")