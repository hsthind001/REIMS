#!/usr/bin/env python3
"""
Simple server starter to debug the shutdown issue
"""
import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

try:
    from backend.api.main import app
    print("✓ App imported successfully")
    
    # Test database connection
    from backend.database import engine, Document
    print("✓ Database imported successfully")
    
    # Test a simple database query
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        # Just count documents
        count = db.query(Document).count()
        print(f"✓ Database query successful, {count} documents found")
    except Exception as e:
        print(f"⚠ Database query failed: {e}")
    finally:
        db.close()
    
    # Start uvicorn
    import uvicorn
    print("Starting server...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    
except KeyboardInterrupt:
    print("\nShutting down gracefully...")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()