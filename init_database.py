"""
Initialize REIMS Database
Creates all tables in PostgreSQL database
"""

import os
import sys

# Set the DATABASE_URL environment variable before importing database module
os.environ['DATABASE_URL'] = 'postgresql://postgres:dev123@localhost:5432/reims'

# Now import the database module
from backend.database import Base, engine, create_tables

def main():
    print("🔧 Initializing REIMS Database...")
    print(f"📊 Database URL: {os.environ.get('DATABASE_URL')}")
    print()
    
    try:
        # Test connection
        print("⏳ Testing database connection...")
        with engine.connect() as conn:
            print("✅ Database connection successful!")
        
        # Create all tables
        print("\n⏳ Creating database tables...")
        create_tables()
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n✅ Database initialized successfully!")
        print(f"\n📋 Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"   • {table}")
        
        print("\n" + "="*60)
        print("✅ Your database is ready!")
        print("="*60)
        print("\n📖 Next steps:")
        print("  1. Refresh pgAdmin (F5)")
        print("  2. Navigate to: Tables in the left panel")
        print("  3. You should now see all tables!")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("  • Make sure PostgreSQL is running: docker ps | grep postgres")
        print("  • Check connection details in docker-compose.yml")
        print("  • Verify port 5432 is accessible")
        return 1

if __name__ == "__main__":
    sys.exit(main())














