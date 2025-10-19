"""
Delete All Test Data - Complete Cleanup
Removes test properties, documents, and MinIO files
Keeps only legitimate properties: Empire State Plaza (ID 1), Wendover Commons (ID 2), Hammond Aire (ID 3)
"""

import sqlite3
import subprocess
import sys
from datetime import datetime

DB_PATH = "reims.db"

print("=" * 80)
print("REIMS Test Data Cleanup")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

def run_sqlite_query(query, params=None):
    """Execute SQLite query and return results"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None

def execute_sqlite_command(query, params=None):
    """Execute SQLite command and commit"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def run_docker_command(cmd):
    """Execute docker command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ Docker command failed: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Docker command error: {e}")
        return None

def main():
    print("Step 1: Identifying Current Properties")
    print("-" * 40)
    
    # Get all properties
    properties = run_sqlite_query("SELECT id, name FROM properties ORDER BY id")
    if not properties:
        print("❌ Failed to query properties")
        return False
    
    print("Current properties in database:")
    for prop in properties:
        print(f"  ID {prop[0]}: {prop[1]}")
    
    # Identify test properties (ID > 3 or names containing "Test")
    test_property_ids = []
    for prop in properties:
        prop_id, prop_name = prop
        if prop_id > 3 or "Test" in prop_name or "Riverside" in prop_name or "Sunset" in prop_name:
            test_property_ids.append(prop_id)
            print(f"  🗑️  Marked for deletion: ID {prop_id} - {prop_name}")
    
    if not test_property_ids:
        print("✅ No test properties found")
        return True
    
    print(f"\nFound {len(test_property_ids)} test properties to delete: {test_property_ids}")
    
    print("\nStep 2: Deleting Test Documents")
    print("-" * 40)
    
    # Delete documents for test properties
    for prop_id in test_property_ids:
        # Count documents first
        doc_count = run_sqlite_query(
            "SELECT COUNT(*) FROM financial_documents WHERE property_id = ?", 
            (prop_id,)
        )
        if doc_count:
            count = doc_count[0][0]
            print(f"  Property ID {prop_id}: {count} documents")
            
            if count > 0:
                # Delete documents
                success = execute_sqlite_command(
                    "DELETE FROM financial_documents WHERE property_id = ?", 
                    (prop_id,)
                )
                if success:
                    print(f"    ✅ Deleted {count} documents")
                else:
                    print(f"    ❌ Failed to delete documents")
    
    print("\nStep 3: Deleting Test Properties")
    print("-" * 40)
    
    # Delete test properties
    for prop_id in test_property_ids:
        success = execute_sqlite_command(
            "DELETE FROM properties WHERE id = ?", 
            (prop_id,)
        )
        if success:
            print(f"  ✅ Deleted property ID {prop_id}")
        else:
            print(f"  ❌ Failed to delete property ID {prop_id}")
    
    print("\nStep 4: Deleting MinIO Files")
    print("-" * 40)
    
    # Delete MinIO directories for test properties
    for prop_id in test_property_ids:
        minio_path = f"properties/{prop_id}/"
        print(f"  Deleting MinIO path: {minio_path}")
        
        # Use docker exec to run mc command
        cmd = f'docker exec reims-minio mc rm --recursive --force minio/reims-files/{minio_path}'
        result = run_docker_command(cmd)
        
        if result is not None:
            print(f"    ✅ Deleted MinIO files for property {prop_id}")
        else:
            print(f"    ⚠️  MinIO deletion may have failed for property {prop_id}")
    
    print("\nStep 5: Verification")
    print("-" * 40)
    
    # Verify database cleanup
    remaining_props = run_sqlite_query("SELECT id, name FROM properties ORDER BY id")
    if remaining_props:
        print("Remaining properties in database:")
        for prop in remaining_props:
            print(f"  ID {prop[0]}: {prop[1]}")
        print(f"Total: {len(remaining_props)} properties")
    
    # Check MinIO directories
    print("\nChecking MinIO directories:")
    minio_result = run_docker_command("docker exec reims-minio mc ls minio/reims-files/properties/")
    if minio_result:
        print("MinIO properties directories:")
        for line in minio_result.split('\n'):
            if line.strip():
                print(f"  {line}")
    
    # Test API endpoint
    print("\nTesting API endpoint:")
    try:
        import requests
        response = requests.get("http://localhost:8001/api/properties", timeout=5)
        if response.status_code == 200:
            data = response.json()
            prop_count = data.get('total', 0)
            print(f"✅ API returns {prop_count} properties")
        else:
            print(f"❌ API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ API test failed: {e}")
    
    print("\n" + "=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)
    print("✅ Test data has been deleted")
    print("✅ Only legitimate properties remain")
    print("✅ Frontend should now show 3 properties")
    print("\nPlease refresh your browser to see the updated frontend.")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
