#!/usr/bin/env python3
"""
REIMS Frontend Startup Script
This script ensures the frontend always starts from the correct directory
"""

import os
import sys
import subprocess
from pathlib import Path

def start_frontend():
    """Start the REIMS frontend with proper directory handling"""
    
    # Define paths
    reims_root = Path(__file__).parent
    frontend_path = reims_root / "frontend"
    package_json = frontend_path / "package.json"
    node_modules = frontend_path / "node_modules"
    
    print("🚀 Starting REIMS Frontend...")
    
    # Check if frontend directory exists
    if not frontend_path.exists():
        print(f"❌ Error: Frontend directory not found at {frontend_path}")
        return False
    
    # Check if package.json exists
    if not package_json.exists():
        print(f"❌ Error: package.json not found at {package_json}")
        return False
    
    # Change to frontend directory
    os.chdir(frontend_path)
    print(f"📁 Changed to directory: {os.getcwd()}")
    
    # Check if node_modules exists, install if needed
    if not node_modules.exists():
        print("📦 Installing dependencies...")
        try:
            subprocess.run(["npm", "install"], check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: npm install failed with exit code {e.returncode}")
            return False
        except FileNotFoundError:
            print("❌ Error: npm not found. Please install Node.js and npm")
            return False
    
    # Start the development server
    print("🌐 Starting Vite development server...")
    print("🔗 Frontend will be available at: http://localhost:5173")
    
    try:
        # Start npm dev server
        subprocess.run(["npm", "run", "dev"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: npm run dev failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ Error: npm not found. Please install Node.js and npm")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped by user")
        return True

if __name__ == "__main__":
    try:
        success = start_frontend()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)