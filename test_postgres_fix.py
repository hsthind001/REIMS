import psycopg2
import sys

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host='127.0.0.1',
        port=5432,
        database='reims',
        user='postgres',
        password='dev123'
    )
    
    cursor = conn.cursor()
    
    # Get version
    cursor.execute('SELECT version()')
    version = cursor.fetchone()[0]
    postgres_version = version.split()[1]
    
    # Get database name
    cursor.execute('SELECT current_database()')
    database = cursor.fetchone()[0]
    
    # Count tables
    cursor.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname='public'")
    table_count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    print("="*70)
    print("PostgreSQL CONNECTION SUCCESS!")
    print("="*70)
    print(f"PostgreSQL Version: {postgres_version}")
    print(f"Database: {database}")
    print(f"Tables in public schema: {table_count}")
    print(f"Host: 127.0.0.1:5432")
    print("="*70)
    print("STATUS: FULLY OPERATIONAL")
    print("="*70)
    
    sys.exit(0)
    
except Exception as e:
    print("="*70)
    print("PostgreSQL CONNECTION FAILED!")
    print("="*70)
    print(f"Error: {e}")
    print("="*70)
    sys.exit(1)


















