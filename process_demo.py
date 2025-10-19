#!/usr/bin/env python3
"""
Demo script to show REIMS AI document processing in action
"""

import sys
import asyncio
import json
from pathlib import Path

# Add paths to import modules
sys.path.append(str(Path(__file__).parent / "backend" / "agents"))
sys.path.append(str(Path(__file__).parent / "queue_service"))

from ai_orchestrator import ai_orchestrator
from document_processor import document_processor

async def demo_processing():
    """Demonstrate the full AI processing pipeline"""
    
    print("🚀 REIMS AI Document Processing Demo")
    print("=" * 50)
    
    # Demo files from storage
    demo_files = [
        {
            "file": "C:/REIMS/storage/fd9ce1bf-7481-4b63-b536-d50e27676f3e_ESP 2024 Income Statement.pdf",
            "metadata": {"document_id": "fd9ce1bf-7481-4b63-b536-d50e27676f3e", "property_id": "ESP_2024", "type": "financial"}
        },
        {
            "file": "C:/REIMS/storage/51114287-d520-4ef0-ac51-e4f263a39932_test_properties.csv", 
            "metadata": {"document_id": "51114287-d520-4ef0-ac51-e4f263a39932", "property_id": "PROP_TEST", "type": "property"}
        }
    ]
    
    for i, demo in enumerate(demo_files, 1):
        file_path = demo["file"]
        metadata = demo["metadata"]
        
        print(f"\n📄 Processing File {i}: {Path(file_path).name}")
        print("-" * 40)
        
        if not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            continue
        
        try:
            # Process with AI Orchestrator
            print("🤖 Running AI Orchestrator...")
            result = await ai_orchestrator.process_document(file_path, metadata)
            
            print(f"✅ Processing Status: {result['processing_status']}")
            print(f"⏱️  Processing Time: {result.get('processing_time_seconds', 0):.2f} seconds")
            print(f"📋 Document Type: {result.get('classification', {}).get('primary_classification', 'unknown')}")
            print(f"🎯 Confidence: {result.get('classification', {}).get('confidence_score', 0):.1%}")
            
            # Show extracted data summary
            specialized = result.get('specialized_analysis', {})
            synthesis = result.get('synthesis', {})
            
            if 'financial_statement_agent' in specialized:
                financial_data = specialized['financial_statement_agent'].get('extracted_data', {})
                print(f"💰 Financial Data Found: {len(financial_data)} metrics")
                for metric, data in financial_data.items():
                    if isinstance(data, dict) and 'primary_value' in data:
                        print(f"   • {metric}: ${data['primary_value']:,.0f}")
            
            if 'property_data_agent' in specialized:
                property_data = specialized['property_data_agent'].get('extracted_data', {})
                print(f"🏠 Property Data Found: {len(property_data)} attributes")
                for attr, data in property_data.items():
                    if isinstance(data, dict) and 'primary_value' in data:
                        print(f"   • {attr}: {data['primary_value']}")
            
            # Show insights
            insights = result.get('insights', {})
            key_findings = insights.get('key_findings', [])
            if key_findings:
                print(f"💡 Key Insights:")
                for finding in key_findings:
                    print(f"   • {finding}")
            
            # Show recommendations
            recommendations = insights.get('recommendations', [])
            if recommendations:
                print(f"📋 Recommendations:")
                for rec in recommendations:
                    print(f"   • {rec}")
            
            print(f"🎯 Data Completeness: {synthesis.get('completeness_score', 0):.1%}")
            
        except Exception as e:
            print(f"❌ Error processing {Path(file_path).name}: {e}")
        
        print("\n" + "=" * 50)
    
    # Show processing statistics
    stats = ai_orchestrator.get_processing_stats()
    print("\n📊 Processing Statistics:")
    print(f"   • Total Documents: {stats['total_documents_processed']}")
    print(f"   • Success Rate: {stats['success_rate']:.1%}")
    print(f"   • Average Time: {stats['average_processing_time']:.2f}s")

if __name__ == "__main__":
    asyncio.run(demo_processing())