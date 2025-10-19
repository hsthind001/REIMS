"""
Delete Test Data from SQLite Database
Removes test properties and documents, keeping only legitimate properties
"""

import sqlite3
from datetime import datetime

DB_PATH = "reims.db"

print("=" * 80)
print("REIMS Database Test Data Cleanup")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

def main():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("Step 1: Identifying Current Properties")
        print("-" * 40)
        
        # Get all properties
        cursor.execute("SELECT id, name FROM properties ORDER BY id")
        properties = cursor.fetchall()
        
        print("Current properties in database:")
        for prop in properties:
            print(f"  ID {prop[0]}: {prop[1]}")
        
        # Identify test properties (ID > 3 or names containing test keywords)
        test_property_ids = []
        test_keywords = ["Test", "Riverside", "Sunset"]
        
        for prop in properties:
            prop_id, prop_name = prop
            is_test = prop_id > 3 or any(keyword in prop_name for keyword in test_keywords)
            if is_test:
                test_property_ids.append(prop_id)
                print(f"  🗑️  Marked for deletion: ID {prop_id} - {prop_name}")
        
        if not test_property_ids:
            print("✅ No test properties found")
            conn.close()
            return True
        
        print(f"\nFound {len(test_property_ids)} test properties to delete: {test_property_ids}")
        
        print("\nStep 2: Deleting Test Documents")
        print("-" * 40)
        
        total_deleted_docs = 0
        for prop_id in test_property_ids:
            # Count documents first
            cursor.execute("SELECT COUNT(*) FROM financial_documents WHERE property_id = ?", (prop_id,))
            doc_count = cursor.fetchone()[0]
            
            if doc_count > 0:
                print(f"  Property ID {prop_id}: {doc_count} documents")
                
                # Delete documents
                cursor.execute("DELETE FROM financial_documents WHERE property_id = ?", (prop_id,))
                deleted_count = cursor.rowcount
                total_deleted_docs += deleted_count
                print(f"    ✅ Deleted {deleted_count} documents")
            else:
                print(f"  Property ID {prop_id}: No documents found")
        
        print(f"\nTotal documents deleted: {total_deleted_docs}")
        
        print("\nStep 3: Deleting Test Properties")
        print("-" * 40)
        
        for prop_id in test_property_ids:
            cursor.execute("DELETE FROM properties WHERE id = ?", (prop_id,))
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                print(f"  ✅ Deleted property ID {prop_id}")
            else:
                print(f"  ❌ Failed to delete property ID {prop_id}")
        
        # Commit all changes
        conn.commit()
        
        print("\nStep 4: Verification")
        print("-" * 40)
        
        # Verify remaining properties
        cursor.execute("SELECT id, name FROM properties ORDER BY id")
        remaining_props = cursor.fetchall()
        
        print("Remaining properties in database:")
        for prop in remaining_props:
            print(f"  ID {prop[0]}: {prop[1]}")
        print(f"Total: {len(remaining_props)} properties")
        
        # Verify remaining documents
        cursor.execute("SELECT COUNT(*) FROM financial_documents")
        remaining_docs = cursor.fetchone()[0]
        print(f"Total documents remaining: {remaining_docs}")
        
        # Show document breakdown by property
        cursor.execute("""
            SELECT p.id, p.name, COUNT(fd.id) as doc_count
            FROM properties p
            LEFT JOIN financial_documents fd ON p.id = fd.property_id
            GROUP BY p.id, p.name
            ORDER BY p.id
        """)
        doc_breakdown = cursor.fetchall()
        
        print("\nDocument breakdown by property:")
        for row in doc_breakdown:
            prop_id, prop_name, doc_count = row
            print(f"  Property {prop_id} ({prop_name}): {doc_count} documents")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("DATABASE CLEANUP COMPLETE")
        print("=" * 80)
        print("✅ Test properties deleted from database")
        print("✅ Test documents deleted from database")
        print("✅ Only legitimate properties remain")
        print(f"✅ {len(remaining_props)} properties, {remaining_docs} documents")
        print("\nPlease refresh your browser to see the updated frontend.")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
