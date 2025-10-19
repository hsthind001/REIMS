import sqlite3

# Check root reims.db
print("=" * 60)
print("Checking C:\\REIMS\\reims.db (SQLite)")
print("=" * 60)

try:
    conn = sqlite3.connect('reims.db')
    cursor = conn.cursor()
    
    # Check tables
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"\nTotal tables: {len(tables)}")
    doc_tables = [t[0] for t in tables if 'document' in t[0].lower() or 'financial' in t[0].lower()]
    print(f"Document-related tables: {doc_tables}")
    
    # Check financial_documents if exists
    if 'financial_documents' in [t[0] for t in tables]:
        print("\nfinancial_documents table:")
        results = cursor.execute('''
            SELECT id, file_name, document_type, status, upload_date 
            FROM financial_documents 
            ORDER BY upload_date DESC 
            LIMIT 5
        ''').fetchall()
        
        if results:
            print(f"  Found {len(results)} records:")
            for row in results:
                print(f"    ID: {row[0][:36]}")
                print(f"    File: {row[1]}")
                print(f"    Type: {row[2]}")
                print(f"    Status: {row[3]}")
                print(f"    Uploaded: {row[4]}")
                print()
        else:
            print("  No records found")
    else:
        print("\n❌ financial_documents table does not exist!")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)

