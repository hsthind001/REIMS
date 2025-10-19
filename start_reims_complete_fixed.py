#!/usr/bin/env python3
"""
REIMS Complete System Startup Script
This script starts both backend and frontend services with proper directory management
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path
from threading import Thread

class REIMSStartup:
    def __init__(self):
        self.reims_root = Path(__file__).parent
        self.frontend_path = self.reims_root / "frontend"
        self.backend_script = self.reims_root / "simple_backend.py"
        self.venv_python = self.reims_root / "queue_service" / "venv" / "Scripts" / "python.exe"
        
        self.backend_process = None
        self.frontend_process = None
        
    def check_dependencies(self):
        """Check if all required dependencies are available"""
        print("🔍 Checking system dependencies...")
        
        # Check if backend script exists
        if not self.backend_script.exists():
            print(f"❌ Backend script not found: {self.backend_script}")
            return False
            
        # Check if frontend directory exists
        if not self.frontend_path.exists():
            print(f"❌ Frontend directory not found: {self.frontend_path}")
            return False
            
        # Check if package.json exists
        if not (self.frontend_path / "package.json").exists():
            print(f"❌ Frontend package.json not found")
            return False
            
        # Check if virtual environment Python exists
        if not self.venv_python.exists():
            print(f"❌ Virtual environment Python not found: {self.venv_python}")
            return False
            
        print("✅ All dependencies found")
        return True
        
    def start_backend(self):
        """Start the backend service"""
        print("🚀 Starting REIMS Backend...")
        
        try:
            # Start backend using virtual environment Python
            self.backend_process = subprocess.Popen(
                [str(self.venv_python), str(self.backend_script)],
                cwd=str(self.reims_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait a moment for startup
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print("✅ Backend started successfully on http://localhost:8001")
                return True
            else:
                print("❌ Backend failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            return False
            
    def start_frontend(self):
        """Start the frontend service"""
        print("🌐 Starting REIMS Frontend...")
        
        try:
            # Change to frontend directory first
            original_cwd = os.getcwd()
            os.chdir(self.frontend_path)
            
            print(f"📁 Changed to directory: {os.getcwd()}")
            
            # Start frontend development server
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(self.frontend_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait a moment for startup
            time.sleep(5)
            
            # Restore original directory
            os.chdir(original_cwd)
            
            if self.frontend_process.poll() is None:
                print("✅ Frontend started successfully on http://localhost:5173")
                return True
            else:
                print("❌ Frontend failed to start")
                return False
                
        except FileNotFoundError:
            print("❌ npm not found. Please ensure Node.js is installed and in PATH")
            return False
        except Exception as e:
            print(f"❌ Error starting frontend: {e}")
            return False
            
    def stop_services(self):
        """Stop both services"""
        print("\n🛑 Stopping REIMS services...")
        
        if self.backend_process and self.backend_process.poll() is None:
            self.backend_process.terminate()
            print("✅ Backend stopped")
            
        if self.frontend_process and self.frontend_process.poll() is None:
            self.frontend_process.terminate()
            print("✅ Frontend stopped")
            
    def signal_handler(self, signum, frame):
        """Handle termination signals"""
        self.stop_services()
        sys.exit(0)
        
    def run(self):
        """Main startup routine"""
        print("🎯 REIMS Complete System Startup")
        print("=" * 50)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Check dependencies
        if not self.check_dependencies():
            print("❌ Dependency check failed. Please fix the issues above.")
            return False
            
        # Start backend
        if not self.start_backend():
            print("❌ Failed to start backend")
            return False
            
        # Start frontend
        if not self.start_frontend():
            print("❌ Failed to start frontend")
            self.stop_services()
            return False
            
        print("\n" + "=" * 50)
        print("🎉 REIMS System Started Successfully!")
        print("🔗 Backend API: http://localhost:8001")
        print("🌐 Frontend UI: http://localhost:5173")
        print("⏹️  Press Ctrl+C to stop all services")
        print("=" * 50)
        
        try:
            # Keep the script running
            while True:
                # Check if processes are still running
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend process died unexpectedly")
                    break
                    
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ Frontend process died unexpectedly")
                    break
                    
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_services()
            
        return True

if __name__ == "__main__":
    startup = REIMSStartup()
    success = startup.run()
    sys.exit(0 if success else 1)