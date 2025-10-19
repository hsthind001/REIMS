"""
Database Migration: Add Enhanced Schema
Adds all missing tables from the implementation plan
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reims.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_enhanced_tables():
    """Create all enhanced schema tables"""
    
    # Import the enhanced schema
    from ..models.enhanced_schema import Base
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Enhanced schema tables created successfully!")
        
        # Create indexes for performance
        with engine.connect() as conn:
            # Indexes for alerts
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_committee_alerts_property_id 
                ON committee_alerts(property_id);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_committee_alerts_status 
                ON committee_alerts(status);
            """))
            
            # Indexes for stores
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_stores_property_id 
                ON stores(property_id);
            """))
            
            # Indexes for audit log
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp 
                ON audit_log(timestamp);
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_audit_log_property_id 
                ON audit_log(property_id);
            """))
            
            conn.commit()
        
        print("✅ Performance indexes created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating enhanced schema: {e}")
        raise

def create_default_users():
    """Create default users for testing"""
    
    from ..services.auth import auth_service
    from ..models.enhanced_schema import User, UserRole
    
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("✅ Users already exist, skipping default user creation")
            return
        
        # Create default users
        users = [
            {
                "username": "admin",
                "email": "admin@reims.com",
                "password": "admin123",
                "role": UserRole.SUPERVISOR
            },
            {
                "username": "analyst",
                "email": "analyst@reims.com", 
                "password": "analyst123",
                "role": UserRole.ANALYST
            },
            {
                "username": "viewer",
                "email": "viewer@reims.com",
                "password": "viewer123", 
                "role": UserRole.VIEWER
            }
        ]
        
        for user_data in users:
            user = auth_service.create_user(
                db=db,
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"],
                role=user_data["role"]
            )
            print(f"✅ Created user: {user.username} ({user.role.value})")
        
        print("✅ Default users created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating default users: {e}")
        raise
    finally:
        db.close()

def run_migration():
    """Run the complete migration"""
    print("🚀 Starting REIMS Enhanced Schema Migration...")
    print(f"📅 Migration started at: {datetime.utcnow()}")
    
    try:
        # Step 1: Create enhanced tables
        print("\n📋 Step 1: Creating enhanced schema tables...")
        create_enhanced_tables()
        
        # Step 2: Create default users
        print("\n👥 Step 2: Creating default users...")
        create_default_users()
        
        print("\n🎉 Migration completed successfully!")
        print("📊 Enhanced schema includes:")
        print("   • Enhanced Property Management")
        print("   • Store/Unit Tracking")
        print("   • Committee Alert System")
        print("   • Workflow Lock Management")
        print("   • Comprehensive Audit Logging")
        print("   • User Authentication & RBAC")
        print("   • Anomaly Detection Tables")
        print("   • Market Intelligence Tables")
        print("   • Exit Strategy Analysis Tables")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()
