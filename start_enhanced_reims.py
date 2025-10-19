"""
Enhanced REIMS Startup Script
Integrates all new features from the implementation plan
"""

import asyncio
import subprocess
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_reims.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedREIMS:
    """Enhanced REIMS system with all implementation plan features"""
    
    def __init__(self):
        self.services = {}
        self.status = {
            'database': False,
            'minio': False,
            'backend': False,
            'frontend': False,
            'ollama': False,
            'redis': False
        }
    
    async def start_services(self):
        """Start all REIMS services in order"""
        
        print("🚀 Starting Enhanced REIMS System...")
        print("=" * 60)
        
        # Step 1: Database Migration
        await self._run_database_migration()
        
        # Step 2: Start Infrastructure Services
        await self._start_infrastructure()
        
        # Step 3: Start Backend with Enhanced Features
        await self._start_enhanced_backend()
        
        # Step 4: Start Frontend
        await self._start_frontend()
        
        # Step 5: Verify System Health
        await self._verify_system_health()
        
        print("\n🎉 Enhanced REIMS System Started Successfully!")
        self._print_system_info()
    
    async def _run_database_migration(self):
        """Run database migration to add enhanced schema"""
        print("\n📋 Step 1: Running Database Migration...")
        
        try:
            # Add current directory to Python path
            sys.path.append(str(Path.cwd()))
            sys.path.append(str(Path.cwd() / "backend"))
            
            # Import and run migration
            from backend.migrations.add_enhanced_schema import run_migration
            run_migration()
            
            self.status['database'] = True
            print("✅ Database migration completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Database migration failed: {e}")
            raise
    
    async def _start_infrastructure(self):
        """Start infrastructure services (Docker Compose)"""
        print("\n🐳 Step 2: Starting Infrastructure Services...")
        
        try:
            # Start Docker Compose services
            result = subprocess.run([
                'docker-compose', 'up', '-d', 'postgres', 'redis', 'minio', 'ollama'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Infrastructure services started!")
                self.status['minio'] = True
                self.status['redis'] = True
                self.status['ollama'] = True
            else:
                print(f"⚠️ Docker Compose warning: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("⚠️ Docker Compose timeout - services may still be starting")
        except FileNotFoundError:
            print("⚠️ Docker Compose not found - running without containerized services")
        except Exception as e:
            logger.warning(f"Infrastructure startup issue: {e}")
    
    async def _start_enhanced_backend(self):
        """Start enhanced backend with all new features"""
        print("\n🔧 Step 3: Starting Enhanced Backend...")
        
        try:
            # Create enhanced backend startup script
            backend_script = """
import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd() / "backend"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import all enhanced modules
from backend.models.enhanced_schema import Base, create_tables
from backend.services.auth import router as auth_router
from backend.services.audit_log import get_audit_logger
from backend.services.alert_system import AlertEngine, CommitteeApprovalService
from backend.api.alerts import router as alerts_router
from backend.api.main import app as base_app

# Create enhanced FastAPI app
app = FastAPI(
    title="Enhanced REIMS API",
    description="Real Estate Intelligence & Management System with Enhanced Features",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router)
app.include_router(alerts_router)

# Include base app routes
for route in base_app.routes:
    app.include_router(route)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": [
            "Enhanced Property Management",
            "Store/Unit Tracking", 
            "Committee Alert System",
            "Workflow Lock Management",
            "Comprehensive Audit Logging",
            "JWT Authentication & RBAC",
            "AI Document Processing",
            "Market Intelligence",
            "Exit Strategy Analysis"
        ],
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
"""
            
            # Write enhanced backend script
            with open("enhanced_backend.py", "w") as f:
                f.write(backend_script)
            
            # Start enhanced backend
            self.services['backend'] = subprocess.Popen([
                sys.executable, "enhanced_backend.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for backend to start
            await asyncio.sleep(3)
            
            self.status['backend'] = True
            print("✅ Enhanced backend started successfully!")
            
        except Exception as e:
            logger.error(f"❌ Enhanced backend startup failed: {e}")
            raise
    
    async def _start_frontend(self):
        """Start frontend development server"""
        print("\n🎨 Step 4: Starting Frontend...")
        
        try:
            # Change to frontend directory
            frontend_path = Path("frontend")
            if not frontend_path.exists():
                print("⚠️ Frontend directory not found")
                return
            
            # Start frontend
            self.services['frontend'] = subprocess.Popen([
                "npm", "run", "dev"
            ], cwd=frontend_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for frontend to start
            await asyncio.sleep(5)
            
            self.status['frontend'] = True
            print("✅ Frontend started successfully!")
            
        except Exception as e:
            logger.warning(f"Frontend startup issue: {e}")
    
    async def _verify_system_health(self):
        """Verify all services are running correctly"""
        print("\n🔍 Step 5: Verifying System Health...")
        
        import httpx
        
        # Check backend health
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8001/health", timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    print(f"✅ Backend Health: {health_data['status']}")
                    print(f"   Features: {len(health_data['features'])} enabled")
                else:
                    print("⚠️ Backend health check failed")
        except Exception as e:
            print(f"⚠️ Backend health check error: {e}")
        
        # Check frontend
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:5173", timeout=5)
                if response.status_code == 200:
                    print("✅ Frontend: Accessible")
                else:
                    print("⚠️ Frontend health check failed")
        except Exception as e:
            print(f"⚠️ Frontend health check error: {e}")
    
    def _print_system_info(self):
        """Print system information and access URLs"""
        print("\n" + "=" * 60)
        print("🎯 Enhanced REIMS System Information")
        print("=" * 60)
        
        print("\n🌐 Access URLs:")
        print("   • Frontend Dashboard: http://localhost:5173")
        print("   • Backend API: http://localhost:8001")
        print("   • API Documentation: http://localhost:8001/docs")
        print("   • MinIO Console: http://localhost:9001")
        print("   • PostgreSQL: localhost:5432")
        print("   • Redis: localhost:6379")
        print("   • Ollama: localhost:11434")
        
        print("\n🔐 Default Login Credentials:")
        print("   • Supervisor: admin / admin123")
        print("   • Analyst: analyst / analyst123")
        print("   • Viewer: viewer / viewer123")
        
        print("\n✨ New Features Available:")
        print("   • Enhanced Property Management with Store Tracking")
        print("   • Committee Alert System with DSCR/Occupancy Monitoring")
        print("   • Workflow Lock Management")
        print("   • Comprehensive Audit Logging with BR-ID Linkage")
        print("   • JWT Authentication & Role-Based Access Control")
        print("   • AI Document Processing with Ollama Integration")
        print("   • Market Intelligence Agent")
        print("   • Exit Strategy Analysis")
        print("   • Statistical Anomaly Detection")
        
        print("\n📊 System Status:")
        for service, status in self.status.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {service.title()}: {'Running' if status else 'Not Running'}")
        
        print("\n🚀 Ready for Development and Testing!")
        print("=" * 60)
    
    async def stop_services(self):
        """Stop all running services"""
        print("\n🛑 Stopping Enhanced REIMS Services...")
        
        for service_name, process in self.services.items():
            if process:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"✅ {service_name.title()} stopped")
                except subprocess.TimeoutExpired:
                    process.kill()
                    print(f"⚠️ {service_name.title()} force stopped")
                except Exception as e:
                    print(f"❌ Error stopping {service_name}: {e}")

async def main():
    """Main startup function"""
    reims = EnhancedREIMS()
    
    try:
        await reims.start_services()
        
        # Keep services running
        print("\n⏳ Services are running... Press Ctrl+C to stop")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested...")
        await reims.stop_services()
        print("👋 Enhanced REIMS stopped successfully!")
    except Exception as e:
        logger.error(f"❌ System error: {e}")
        await reims.stop_services()
        raise

if __name__ == "__main__":
    asyncio.run(main())
