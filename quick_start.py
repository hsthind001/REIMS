#!/usr/bin/env python3
"""
Quick Start Script for REIMS with Robust Backend
Uses the new robust components with proper dependency management
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def main():
    print("🚀 REIMS QUICK START WITH ROBUST BACKEND")
    print("="*50)
    
    # Change to REIMS directory
    reims_dir = Path(__file__).parent
    os.chdir(reims_dir)
    
    print("📁 Working directory:", os.getcwd())
    
    # Option 1: Use the robust startup system
    print("\n🔧 Starting REIMS with robust dependency management...")
    
    try:
        result = subprocess.run([
            sys.executable, "robust_startup.py"
        ], check=False)
        
        if result.returncode == 0:
            print("✅ REIMS started successfully with robust system")
        else:
            print("⚠️ Robust startup had issues, trying fallback...")
            
            # Fallback: Start services manually
            print("\n🔄 Starting services manually...")
            
            # Start MinIO
            print("1. Starting MinIO...")
            minio_process = subprocess.Popen([
                "minio.exe", "server", "minio-data", "--console-address", ":9001"
            ], creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            
            time.sleep(5)  # Wait for MinIO
            
            # Start robust backend
            print("2. Starting robust backend...")
            backend_process = subprocess.Popen([
                sys.executable, "robust_backend.py"
            ], creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            
            time.sleep(5)  # Wait for backend
            
            # Start frontend with FIXED directory handling
            print("3. Starting frontend...")
            frontend_dir = reims_dir / "frontend"
            if not frontend_dir.exists():
                print(f"❌ Frontend directory not found at: {frontend_dir}")
                return 1
            
            print(f"   📁 Frontend directory: {frontend_dir}")
            frontend_process = subprocess.Popen([
                "npm", "run", "dev"
            ], cwd=str(frontend_dir), creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            
            print("\n🎉 Services started manually!")
            print("🌐 Frontend: http://localhost:5173")
            print("⚙️ Backend: http://localhost:8001")
            print("🗂️ MinIO: http://localhost:9001")
            
            print("\n💡 Check the console windows for service status")
            print("🛑 Close console windows to stop services")
            
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())