"""
Integration script to add health check endpoint to existing REIMS backend

This script shows how to integrate the health check endpoint into your
existing FastAPI backend.

Instructions:
1. Read this file to understand the integration
2. Apply changes to your main backend file (start_optimized_server.py)
3. Test the endpoints

Author: REIMS Development Team
Date: October 12, 2025
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn


# ============================================================================
# STEP 1: Import Health Router
# ============================================================================

# Add this import at the top of your file
from backend.api.health import router as health_router, startup_health_check


# ============================================================================
# STEP 2: Update Lifespan Manager (if you have one)
# ============================================================================

# If you already have a lifespan manager, add the startup health check
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle with health checks"""
    print("🚀 Starting REIMS application...")
    
    # Initialize database (if you're using the db module)
    try:
        from backend.db import init_db, close_db
        await init_db()
        print("✅ Database connection pool initialized")
    except ImportError:
        print("⚠️  Database module not available")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
    
    # Run startup health checks (OPTIONAL but recommended)
    print("\n" + "="*60)
    print("Running startup health checks...")
    print("="*60)
    health_status = await startup_health_check()
    
    # Check if critical services are healthy
    if health_status.get("database") == "unhealthy":
        print("\n⚠️  WARNING: Database is unhealthy!")
        print("Application may not function correctly.")
    
    yield  # Application runs here
    
    # Shutdown
    print("\n🛑 Shutting down REIMS application...")
    try:
        from backend.db import close_db
        await close_db()
        print("✅ Database connections closed")
    except:
        pass


# ============================================================================
# STEP 3: Create FastAPI App with Lifespan
# ============================================================================

app = FastAPI(
    title="REIMS API",
    version="2.0",
    description="Real Estate Intelligence Management System",
    lifespan=lifespan  # Add this!
)


# ============================================================================
# STEP 4: Register Health Check Router
# ============================================================================

# Add this BEFORE your other routers
app.include_router(health_router)

# Then include your other routers
# app.include_router(upload_router)
# app.include_router(analytics_router)
# app.include_router(property_router)
# etc.


# ============================================================================
# STEP 5: Add Root Endpoint (Optional)
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with links to important endpoints"""
    return {
        "message": "REIMS API v2.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "health_database": "/health/database",
            "health_redis": "/health/redis",
            "health_minio": "/health/minio",
            "health_ollama": "/health/ollama",
            "liveness": "/health/live",
            "readiness": "/health/ready",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


# ============================================================================
# STEP 6: Run the Application
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("REIMS API Server with Health Checks")
    print("=" * 70)
    print("\n📚 Available endpoints:")
    print("  • Main API: http://localhost:8000")
    print("  • Health Check: http://localhost:8000/health")
    print("  • API Docs: http://localhost:8000/docs")
    print("\n🧪 Test health endpoint:")
    print("  curl http://localhost:8000/health | jq")
    print("\n" + "=" * 70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )


# ============================================================================
# COMPLETE EXAMPLE: Minimal Integration
# ============================================================================

"""
# Minimal integration example (copy to your backend file):

from fastapi import FastAPI
from backend.api.health import router as health_router

app = FastAPI(title="REIMS API", version="2.0")

# Register health router
app.include_router(health_router)

# Your existing routers...
# app.include_router(upload_router)
# app.include_router(analytics_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""


# ============================================================================
# TESTING INSTRUCTIONS
# ============================================================================

"""
After integration, test with:

1. Start the backend:
   python start_optimized_server.py

2. Test health endpoint:
   curl http://localhost:8000/health

3. Test individual services:
   curl http://localhost:8000/health/database
   curl http://localhost:8000/health/redis
   curl http://localhost:8000/health/minio
   curl http://localhost:8000/health/ollama

4. Run automated tests:
   python backend/test_health_endpoint.py

5. Run detailed analysis:
   python backend/test_health_endpoint.py --mode detailed

6. Run continuous monitoring:
   python backend/test_health_endpoint.py --mode monitor --interval 30

Expected output (healthy):
{
  "success": true,
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "minio": "healthy",
    "ollama": "healthy"
  },
  "details": {...},
  "timestamp": "2025-10-12T19:32:53Z",
  "check_duration_ms": 234.56
}
"""
















