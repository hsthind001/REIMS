#!/usr/bin/env python3
"""
Complete REIMS System Startup Script
Starts all services and verifies they're working correctly
"""

import subprocess
import time
import requests
import sys
import os
from pathlib import Path
import json

class REIMSStartup:
    def __init__(self):
        self.processes = {}
        self.services = {
            'minio': {'port': 9000, 'console_port': 9001, 'process': None},
            'backend': {'port': 8001, 'process': None},
            'frontend': {'port': 5173, 'process': None}
        }
        
    def check_port_available(self, port):
        """Check if a port is available"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    def wait_for_service(self, port, timeout=30, service_name="service"):
        """Wait for a service to become available on a port"""
        print(f"⏳ Waiting for {service_name} on port {port}...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if port == 8001:
                    # For backend, check health endpoint
                    response = requests.get(f'http://localhost:{port}/health', timeout=2)
                    if response.status_code == 200:
                        print(f"✅ {service_name} is ready on port {port}")
                        return True
                else:
                    # For other services, just check port connectivity
                    import socket
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        if s.connect_ex(('localhost', port)) == 0:
                            print(f"✅ {service_name} is ready on port {port}")
                            return True
            except:
                pass
            time.sleep(1)
        
        print(f"❌ {service_name} failed to start on port {port} within {timeout}s")
        return False
    
    def start_minio(self):
        """Start MinIO server"""
        print("\n🗂️ Starting MinIO Server...")
        
        if not self.check_port_available(9000) or not self.check_port_available(9001):
            print("ℹ️ MinIO appears to already be running")
            if self.wait_for_service(9000, timeout=5, service_name="MinIO"):
                return True
        
        try:
            # Check if minio.exe exists
            minio_path = Path("minio.exe")
            if not minio_path.exists():
                print("❌ minio.exe not found in current directory")
                return False
            
            # Create data directory
            data_dir = Path("minio-data")
            data_dir.mkdir(exist_ok=True)
            
            # Start MinIO
            cmd = [
                str(minio_path),
                "server",
                str(data_dir),
                "--console-address", ":9001"
            ]
            
            self.processes['minio'] = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            # Wait for MinIO to start
            if self.wait_for_service(9000, service_name="MinIO"):
                print("✅ MinIO Server started successfully")
                print("   📊 Console: http://localhost:9001 (admin/admin123)")
                print("   🗂️ API: http://localhost:9000")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Failed to start MinIO: {e}")
            return False
    
    def setup_minio_buckets(self):
        """Setup MinIO buckets"""
        print("\n🪣 Setting up MinIO buckets...")
        
        try:
            # Wait a moment for MinIO to be fully ready
            time.sleep(2)
            
            from minio import Minio
            client = Minio(
                endpoint="localhost:9000",
                access_key="minioadmin",
                secret_key="minioadmin",
                secure=False
            )
            
            buckets = ["reims-documents", "reims-documents-backup", "reims-documents-archive"]
            
            for bucket_name in buckets:
                if not client.bucket_exists(bucket_name):
                    client.make_bucket(bucket_name)
                    print(f"✅ Created bucket: {bucket_name}")
                else:
                    print(f"ℹ️ Bucket already exists: {bucket_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup MinIO buckets: {e}")
            return False
    
    def prepare_database(self):
        """Prepare database with proper schema"""
        print("\n🗄️ Preparing database...")
        
        try:
            # Run database migration
            result = subprocess.run([
                sys.executable, "backend/database.py"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Database schema ready")
                return True
            else:
                print(f"❌ Database preparation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Database preparation error: {e}")
            return False
    
    def start_backend(self):
        """Start the backend server"""
        print("\n⚙️ Starting Backend Server...")
        
        if not self.check_port_available(8001):
            print("ℹ️ Backend appears to already be running")
            if self.wait_for_service(8001, timeout=5, service_name="Backend"):
                return True
        
        try:
            self.processes['backend'] = subprocess.Popen(
                [sys.executable, "simple_backend.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            if self.wait_for_service(8001, service_name="Backend"):
                print("✅ Backend Server started successfully")
                print("   🔗 API: http://localhost:8001")
                print("   📋 Health: http://localhost:8001/health")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the frontend development server"""
        print("\n🌐 Starting Frontend Server...")
        
        if not self.check_port_available(5173):
            print("ℹ️ Frontend appears to already be running")
            if self.wait_for_service(5173, timeout=5, service_name="Frontend"):
                return True
        
        try:
            # FIXED: Use absolute path for frontend directory
            current_dir = Path(__file__).parent
            frontend_dir = current_dir / "frontend"
            
            if not frontend_dir.exists():
                print(f"❌ Frontend directory not found at: {frontend_dir}")
                return False
            
            print(f"📁 Frontend directory: {frontend_dir}")
            
            # Start frontend with proper working directory
            self.processes['frontend'] = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(frontend_dir),  # CRITICAL: Use absolute path
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            if self.wait_for_service(5173, timeout=20, service_name="Frontend"):
                print("✅ Frontend Server started successfully")
                print("   🌐 UI: http://localhost:5173")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def verify_system(self):
        """Verify all systems are working correctly"""
        print("\n🔍 Verifying System Integration...")
        
        checks = {
            'MinIO': False,
            'Backend': False,
            'Frontend': False,
            'Database': False,
            'Integration': False
        }
        
        # Check MinIO
        try:
            from minio import Minio
            client = Minio("localhost:9000", "minioadmin", "minioadmin", secure=False)
            buckets = client.list_buckets()
            checks['MinIO'] = len(buckets) >= 1
        except:
            pass
        
        # Check Backend
        try:
            response = requests.get('http://localhost:8001/health', timeout=5)
            checks['Backend'] = response.status_code == 200
        except:
            pass
        
        # Check Frontend
        try:
            response = requests.get('http://localhost:5173', timeout=5)
            checks['Frontend'] = response.status_code == 200
        except:
            pass
        
        # Check Database
        try:
            import sqlite3
            conn = sqlite3.connect("reims.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            cursor.fetchone()
            conn.close()
            checks['Database'] = True
        except:
            pass
        
        # Check Integration
        try:
            response = requests.get('http://localhost:8001/api/documents', timeout=5)
            checks['Integration'] = response.status_code == 200
        except:
            pass
        
        # Display results
        print("\n📊 System Status:")
        for service, status in checks.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {service}")
        
        return all(checks.values())
    
    def show_system_info(self):
        """Show system information and URLs"""
        print("\n" + "="*60)
        print("🎉 REIMS SYSTEM IS READY!")
        print("="*60)
        
        print("\n🌐 Service URLs:")
        print("   • Frontend UI:      http://localhost:5173")
        print("   • Backend API:      http://localhost:8001")
        print("   • MinIO Console:    http://localhost:9001")
        print("   • API Health:       http://localhost:8001/health")
        print("   • API Docs:         http://localhost:8001/docs")
        
        print("\n🔐 Default Credentials:")
        print("   • MinIO: minioadmin / minioadmin")
        
        print("\n📁 Key Features Available:")
        print("   • Document Upload with Property ID")
        print("   • MinIO Object Storage")
        print("   • Database Integration")
        print("   • Real-time Analytics")
        print("   • Property Management")
        
        print("\n🧪 Testing Commands:")
        print("   • Test Data Flow:    python test_data_flow.py")
        print("   • Monitor System:    python monitor_data_flow.py")
        print("   • Verify Database:   python verify_database.py")
        
        print("\n💡 Getting Started:")
        print("   1. Open http://localhost:5173 in your browser")
        print("   2. Navigate to Document Management")
        print("   3. Upload files with Property IDs")
        print("   4. Files will be stored in MinIO and tracked in database")
        
        print("\n⚠️ To stop services:")
        print("   • Close the console windows that opened")
        print("   • Or press Ctrl+C in this terminal")
    
    def cleanup(self):
        """Clean up processes"""
        print("\n🛑 Stopping services...")
        for name, process in self.processes.items():
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"✅ Stopped {name}")
                except:
                    try:
                        process.kill()
                        print(f"🔥 Force stopped {name}")
                    except:
                        pass
    
    def start_all(self):
        """Start all REIMS services"""
        print("🚀 STARTING REIMS COMPLETE SOLUTION")
        print("="*50)
        
        try:
            # Step 1: Prepare database
            if not self.prepare_database():
                print("❌ Cannot proceed - database preparation failed")
                return False
            
            # Step 2: Start MinIO
            if not self.start_minio():
                print("❌ Cannot proceed - MinIO failed to start")
                return False
            
            # Step 3: Setup MinIO buckets
            if not self.setup_minio_buckets():
                print("❌ Warning - MinIO buckets setup failed")
            
            # Step 4: Start Backend
            if not self.start_backend():
                print("❌ Cannot proceed - Backend failed to start")
                return False
            
            # Step 5: Start Frontend
            if not self.start_frontend():
                print("❌ Cannot proceed - Frontend failed to start")
                return False
            
            # Step 6: Verify everything
            if self.verify_system():
                self.show_system_info()
                
                # Keep running
                print("\n🔄 Services are running. Press Ctrl+C to stop all services.")
                try:
                    while True:
                        time.sleep(60)
                        # Quick health check
                        try:
                            requests.get('http://localhost:8001/health', timeout=2)
                        except:
                            print("⚠️ Backend health check failed")
                            break
                except KeyboardInterrupt:
                    print("\n🛑 Shutdown requested...")
                
                return True
            else:
                print("❌ System verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Startup failed: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Main function"""
    startup = REIMSStartup()
    
    try:
        success = startup.start_all()
        if not success:
            print("\n❌ REIMS startup failed")
            return 1
    except KeyboardInterrupt:
        print("\n🛑 Startup cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    finally:
        startup.cleanup()
    
    return 0

if __name__ == "__main__":
    exit(main())