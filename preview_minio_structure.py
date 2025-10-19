#!/usr/bin/env python3
"""
Preview how MinIO files would be organized
"""
import sqlite3

def preview_structure():
    """Show how files would be organized"""
    print("\n" + "="*80)
    print("PREVIEW: MinIO Organization - Property/Year/DocumentType")
    print("="*80 + "\n")
    
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    # Get ESP files with metadata
    cursor.execute("""
        SELECT file_name, property_name, document_year, document_type, file_path
        FROM financial_documents
        WHERE file_name LIKE '%ESP%'
        ORDER BY upload_date DESC
        LIMIT 10
    """)
    
    files = cursor.fetchall()
    
    print("📊 Current Structure vs Proposed Structure\n")
    print("-" * 80)
    
    for filename, prop_name, year, doc_type, current_path in files:
        # Proposed structure
        if prop_name and year and doc_type:
            doc_folder = doc_type.replace(" ", "_")
            proposed = f"{prop_name}/{year}/{doc_folder}/{filename}"
        else:
            proposed = "❌ Missing metadata - cannot organize"
        
        print(f"\n📄 {filename}")
        print(f"   Current:  {current_path}")
        print(f"   Proposed: {proposed}")
    
    print("\n" + "="*80)
    print("\n✨ PROPOSED MINIO STRUCTURE:\n")
    print("reims-files/")
    print("  ├── ESP/")
    print("  │   └── 2024/")
    print("  │       ├── Income_Statement/")
    print("  │       │   └── ESP 2024 Income Statement.pdf")
    print("  │       ├── Cash_Flow_Statement/")
    print("  │       │   └── ESP 2024 Cash Flow Statement.pdf")
    print("  │       └── Balance_Sheet/")
    print("  │           └── ESP 2024 Balance Sheet.pdf")
    print()
    print("="*80 + "\n")
    
    # Show what needs to happen
    print("📋 What needs to happen:\n")
    print("1. ✅ Database already has property_name, document_year, document_type columns")
    print("2. ⚠️ Current ESP files have NULL metadata (uploaded before implementation)")
    print("3. 🔄 Options:")
    print("   A. Re-upload ESP files → Automatically organized with new structure")
    print("   B. Run migration script → Parse existing filenames and reorganize")
    print("   C. Manually update metadata → Then reorganize")
    print()
    
    conn.close()

if __name__ == "__main__":
    preview_structure()



