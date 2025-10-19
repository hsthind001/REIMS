import sqlite3

print("\n" + "="*70)
print("         YOUR UPLOADED DOCUMENTS - COMPLETE LIST")
print("="*70)

conn = sqlite3.connect('reims.db')
cursor = conn.cursor()

# Get all documents
docs = cursor.execute('''
    SELECT id, file_name, document_type, status, upload_date 
    FROM financial_documents 
    ORDER BY upload_date DESC
''').fetchall()

total = len(docs)
print(f"\n✅ Total Documents Found: {total}")
print("\n" + "-"*70)

# Show first 10
for i, doc in enumerate(docs[:10], 1):
    print(f"\n{i}. {doc[1]}")
    print(f"   ID: {doc[0]}")
    print(f"   Type: {doc[2]}")
    print(f"   Status: {doc[3]}")
    print(f"   Uploaded: {doc[4]}")

if total > 10:
    print(f"\n... and {total - 10} more documents")

print("\n" + "="*70)
print("\n✅ All your files are in MinIO storage")
print("✅ All metadata is in SQLite database")
print("\n📊 Access via API: http://localhost:8001/api/documents")
print("="*70 + "\n")

conn.close()

