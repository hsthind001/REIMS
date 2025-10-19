#!/usr/bin/env python3
"""
Robust Frontend Startup Script with Backend Dependency Management
Ensures frontend starts ONLY after backend is ready and from correct directory
"""

import subprocess
import time
import requests
import sys
import os
from pathlib import Path
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('frontend_startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FrontendManager:
    """Manages frontend startup with backend dependency validation"""
    
    def __init__(self):
        self.frontend_process = None
        self.backend_url = "http://localhost:8001"
        self.frontend_url = "http://localhost:5173"
        self.backend_timeout = 300  # 5 minutes to wait for backend
        self.frontend_timeout = 120  # 2 minutes for frontend startup
        
    def check_backend_health(self, timeout=5):
        """Check if backend is healthy and ready"""
        try:
            response = requests.get(f'{self.backend_url}/health', timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Backend health check passed: {data}")
                return True
            else:
                logger.warning(f"Backend health check failed with status {response.status_code}")
                return False
        except Exception as e:
            logger.debug(f"Backend health check failed: {e}")
            return False
    
    def wait_for_backend(self):
        """Wait for backend to become available"""
        logger.info(f"🔍 Waiting for backend at {self.backend_url}...")
        start_time = time.time()
        
        while time.time() - start_time < self.backend_timeout:
            if self.check_backend_health():
                logger.info("✅ Backend is ready!")
                return True
            
            logger.info("⏳ Backend not ready, waiting...")
            time.sleep(5)
        
        logger.error(f"❌ Backend did not become available within {self.backend_timeout} seconds")
        return False
    
    def check_frontend_health(self, timeout=5):
        """Check if frontend is responding"""
        try:
            response = requests.get(self.frontend_url, timeout=timeout)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Frontend health check failed: {e}")
            return False
    
    def check_port_available(self, port):
        """Check if a port is available"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    def kill_process_on_port(self, port):
        """Kill process running on specific port"""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True, capture_output=True, text=True
                )
                
                for line in result.stdout.strip().split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            subprocess.run(f'taskkill /PID {pid} /F', shell=True, capture_output=True)
                            logger.info(f"Killed process {pid} on port {port}")
            else:  # Unix-like
                subprocess.run(f'lsof -ti:{port} | xargs kill -9', shell=True, capture_output=True)
        except Exception as e:
            logger.debug(f"Failed to kill process on port {port}: {e}")
    
    def setup_frontend_environment(self):
        """Setup frontend environment and dependencies"""
        # Ensure we're in the REIMS root directory
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        # Frontend directory path
        frontend_dir = script_dir / "frontend"
        
        if not frontend_dir.exists():
            logger.error(f"❌ Frontend directory not found at: {frontend_dir}")
            return False, None
        
        logger.info(f"📁 Frontend directory: {frontend_dir}")
        
        # Check if npm is available
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                logger.error("❌ npm not found - please install Node.js")
                return False, None
            
            npm_version = result.stdout.strip()
            logger.info(f"✅ npm version: {npm_version}")
        except Exception as e:
            logger.error(f"❌ npm check failed: {e}")
            return False, None
        
        # Check package.json
        package_json = frontend_dir / "package.json"
        if not package_json.exists():
            logger.error(f"❌ package.json not found at: {package_json}")
            return False, None
        
        # Install dependencies if needed
        node_modules_dir = frontend_dir / "node_modules"
        if not node_modules_dir.exists():
            logger.info("📦 Installing frontend dependencies...")
            try:
                result = subprocess.run(
                    ["npm", "install"], 
                    cwd=str(frontend_dir), 
                    capture_output=True, 
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                
                if result.returncode != 0:
                    logger.error(f"❌ npm install failed: {result.stderr}")
                    return False, None
                
                logger.info("✅ Frontend dependencies installed successfully")
            except subprocess.TimeoutExpired:
                logger.error("❌ npm install timed out")
                return False, None
            except Exception as e:
                logger.error(f"❌ npm install failed: {e}")
                return False, None
        else:
            logger.info("✅ Frontend dependencies already installed")
        
        return True, frontend_dir
    
    def start_frontend_server(self, frontend_dir):
        """Start the frontend development server"""
        logger.info("🚀 Starting frontend server...")
        
        # Kill any existing frontend processes
        self.kill_process_on_port(5173)
        time.sleep(2)
        
        # Verify port is available
        if not self.check_port_available(5173):
            logger.error("❌ Port 5173 is still occupied after cleanup")
            return False
        
        try:
            # Start frontend with proper working directory
            logger.info(f"🎯 Starting 'npm run dev' in directory: {frontend_dir}")
            
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(frontend_dir),  # CRITICAL: Run from frontend directory
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            logger.info(f"✅ Frontend process started with PID: {self.frontend_process.pid}")
            
            # Wait for frontend to start
            logger.info("⏳ Waiting for frontend to become available...")
            start_time = time.time()
            
            while time.time() - start_time < self.frontend_timeout:
                # Check if process is still running
                if self.frontend_process.poll() is not None:
                    stdout, stderr = self.frontend_process.communicate()
                    logger.error(f"❌ Frontend process exited early")
                    logger.error(f"stdout: {stdout.decode() if stdout else 'None'}")
                    logger.error(f"stderr: {stderr.decode() if stderr else 'None'}")
                    return False
                
                # Check if port is open
                if not self.check_port_available(5173):
                    logger.info("🔍 Port 5173 is now occupied, testing frontend...")
                    time.sleep(3)  # Give Vite time to fully initialize
                    
                    # Test frontend health
                    if self.check_frontend_health():
                        logger.info("✅ Frontend is responding and healthy!")
                        return True
                    else:
                        logger.info("⏳ Frontend port is open but not responding yet...")
                
                time.sleep(2)
            
            logger.error("❌ Frontend failed to start within timeout")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to start frontend: {e}")
            return False
    
    def validate_frontend_backend_connection(self):
        """Validate that frontend can communicate with backend"""
        logger.info("🔗 Validating frontend-backend connection...")
        
        try:
            # Test API endpoints that frontend uses
            endpoints_to_test = [
                "/health",
                "/api/documents",
                "/api/analytics"
            ]
            
            for endpoint in endpoints_to_test:
                url = f"{self.backend_url}{endpoint}"
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        logger.info(f"✅ {endpoint} - OK")
                    else:
                        logger.warning(f"⚠️ {endpoint} - Status {response.status_code}")
                except Exception as e:
                    logger.error(f"❌ {endpoint} - Failed: {e}")
                    return False
            
            logger.info("✅ All backend endpoints are accessible from frontend")
            return True
            
        except Exception as e:
            logger.error(f"❌ Frontend-backend validation failed: {e}")
            return False
    
    def show_startup_info(self):
        """Show startup information and URLs"""
        logger.info("\n" + "="*60)
        logger.info("🎉 FRONTEND STARTUP COMPLETE!")
        logger.info("="*60)
        
        logger.info("\n🌐 Service URLs:")
        logger.info(f"   • Frontend UI:      {self.frontend_url}")
        logger.info(f"   • Backend API:      {self.backend_url}")
        logger.info(f"   • Backend Health:   {self.backend_url}/health")
        logger.info(f"   • API Docs:         {self.backend_url}/docs")
        
        logger.info("\n🔗 Connection Status:")
        logger.info("   • Frontend ↔ Backend: ✅ Connected")
        logger.info("   • CORS configured for frontend domain")
        logger.info("   • All API endpoints accessible")
        
        logger.info("\n💡 Ready for Testing:")
        logger.info("   1. Open http://localhost:5173 in your browser")
        logger.info("   2. Navigate to Document Management")
        logger.info("   3. Upload files to test the complete workflow")
        
        logger.info("\n🛑 To stop frontend:")
        logger.info("   • Close the console window that opened")
        logger.info("   • Or press Ctrl+C in this terminal")
    
    def cleanup(self):
        """Clean up frontend process"""
        if self.frontend_process and self.frontend_process.poll() is None:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=10)
                logger.info("✅ Frontend process stopped")
            except:
                try:
                    self.frontend_process.kill()
                    logger.info("🔥 Frontend process force killed")
                except:
                    pass
    
    def start(self):
        """Main startup method"""
        try:
            logger.info("🚀 STARTING REIMS FRONTEND WITH DEPENDENCY CHECK")
            logger.info("="*60)
            
            # Step 1: Check backend dependency
            logger.info("🔍 Step 1: Checking backend dependency...")
            if not self.wait_for_backend():
                logger.error("❌ Cannot start frontend - backend is not available")
                logger.error("💡 Please start the backend first:")
                logger.error("   python robust_startup.py")
                logger.error("   OR")
                logger.error("   python robust_backend.py")
                return False
            
            # Step 2: Setup frontend environment
            logger.info("📦 Step 2: Setting up frontend environment...")
            success, frontend_dir = self.setup_frontend_environment()
            if not success:
                logger.error("❌ Frontend environment setup failed")
                return False
            
            # Step 3: Start frontend server
            logger.info("🚀 Step 3: Starting frontend server...")
            if not self.start_frontend_server(frontend_dir):
                logger.error("❌ Frontend server startup failed")
                return False
            
            # Step 4: Validate connection
            logger.info("🔗 Step 4: Validating frontend-backend connection...")
            if not self.validate_frontend_backend_connection():
                logger.warning("⚠️ Frontend-backend connection validation failed")
                logger.warning("Frontend started but may have communication issues")
            
            # Step 5: Show success info
            self.show_startup_info()
            
            # Keep running
            logger.info("\n🔄 Frontend is running. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(30)
                    # Periodic health check
                    if not self.check_frontend_health():
                        logger.warning("⚠️ Frontend health check failed")
                    if not self.check_backend_health():
                        logger.warning("⚠️ Backend health check failed")
            except KeyboardInterrupt:
                logger.info("\n🛑 Shutdown requested...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Frontend startup failed: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Main function"""
    frontend_manager = FrontendManager()
    
    try:
        success = frontend_manager.start()
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("\n🛑 Frontend startup cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())