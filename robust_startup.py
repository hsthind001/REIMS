#!/usr/bin/env python3
"""
Robust REIMS System Startup with Dependency Management
Handles service dependencies, retries, and graceful error recovery
"""

import subprocess
import time
import requests
import sys
import os
from pathlib import Path
import json
import signal
import threading
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reims_startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ServiceManager:
    """Manages REIMS services with dependency checking and restart capabilities"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.service_status: Dict[str, bool] = {}
        self.restart_counts: Dict[str, int] = {}
        self.max_restarts = 3
        self.shutdown_requested = False
        
        # Service configuration with dependencies
        self.services = {
            'minio': {
                'port': 9000,
                'console_port': 9001,
                'dependencies': [],
                'startup_timeout': 30,
                'health_check': self._check_minio_health,
                'start_function': self._start_minio,
                'critical': True
            },
            'database': {
                'dependencies': [],
                'startup_timeout': 10,
                'health_check': self._check_database_health,
                'start_function': self._prepare_database,
                'critical': True
            },
            'backend': {
                'port': 8001,
                'dependencies': ['minio', 'database'],
                'startup_timeout': 30,
                'health_check': self._check_backend_health,
                'start_function': self._start_backend,
                'critical': True
            },
            'frontend': {
                'port': 5173,
                'dependencies': ['backend'],
                'startup_timeout': 40,
                'health_check': self._check_frontend_health,
                'start_function': self._start_frontend,
                'critical': False
            }
        }
        
        # Initialize status
        for service in self.services:
            self.service_status[service] = False
            self.restart_counts[service] = 0

    def _check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0

    def _wait_for_port(self, port: int, timeout: int = 30) -> bool:
        """Wait for a port to become available"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self._check_port_available(port):
                return True
            time.sleep(0.5)
        return False

    def _check_minio_health(self) -> bool:
        """Check MinIO health"""
        try:
            if self._check_port_available(9000):
                return False
            
            # Try to connect to MinIO client
            from minio import Minio
            client = Minio(
                endpoint="localhost:9000",
                access_key="minioadmin",
                secret_key="minioadmin",
                secure=False
            )
            
            # Test bucket listing
            list(client.list_buckets())
            return True
        except Exception as e:
            logger.debug(f"MinIO health check failed: {e}")
            return False

    def _check_database_health(self) -> bool:
        """Check database health"""
        try:
            import sqlite3
            conn = sqlite3.connect("reims.db", timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='documents'")
            result = cursor.fetchone()
            conn.close()
            return result and result[0] > 0
        except Exception as e:
            logger.debug(f"Database health check failed: {e}")
            return False

    def _check_backend_health(self) -> bool:
        """Check backend health"""
        try:
            if self._check_port_available(8001):
                return False
            
            response = requests.get('http://localhost:8001/health', timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Backend health check failed: {e}")
            return False

    def _check_frontend_health(self) -> bool:
        """Check frontend health"""
        try:
            if self._check_port_available(5173):
                return False
            
            response = requests.get('http://localhost:5173', timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Frontend health check failed: {e}")
            return False

    def _start_minio(self) -> bool:
        """Start MinIO server"""
        logger.info("Starting MinIO Server...")
        
        try:
            # Check if already running
            if self._check_minio_health():
                logger.info("MinIO already running")
                return True
            
            # Kill any existing MinIO processes
            self._kill_process_on_port(9000)
            self._kill_process_on_port(9001)
            time.sleep(2)
            
            # Check if minio.exe exists
            minio_path = Path("minio.exe")
            if not minio_path.exists():
                logger.error("minio.exe not found in current directory")
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
            if self._wait_for_port(9000, timeout=30):
                # Additional wait for full initialization
                time.sleep(3)
                
                # Setup buckets
                self._setup_minio_buckets()
                
                logger.info("MinIO Server started successfully")
                return True
            else:
                logger.error("MinIO failed to start within timeout")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start MinIO: {e}")
            return False

    def _setup_minio_buckets(self):
        """Setup MinIO buckets with retry logic"""
        max_retries = 5
        for attempt in range(max_retries):
            try:
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
                        logger.info(f"Created bucket: {bucket_name}")
                
                return True
                
            except Exception as e:
                logger.warning(f"MinIO bucket setup attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    logger.error("MinIO bucket setup failed after all retries")
                    return False

    def _prepare_database(self) -> bool:
        """Prepare database with proper schema"""
        logger.info("Preparing database...")
        
        try:
            # Ensure we're using the right Python environment
            python_exe = self._get_python_executable()
            
            # Run database migration
            result = subprocess.run([
                python_exe, "backend/database.py"
            ], capture_output=True, text=True, timeout=30, cwd=os.getcwd())
            
            if result.returncode == 0:
                logger.info("Database schema ready")
                return True
            else:
                logger.error(f"Database preparation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Database preparation error: {e}")
            return False

    def _start_backend(self) -> bool:
        """Start the backend server with retry logic"""
        logger.info("Starting Backend Server...")
        
        try:
            # Check if already running
            if self._check_backend_health():
                logger.info("Backend already running")
                return True
            
            # Kill any existing backend processes
            self._kill_process_on_port(8001)
            time.sleep(2)
            
            # Get the right Python executable
            python_exe = self._get_python_executable()
            
            # Start backend
            self.processes['backend'] = subprocess.Popen(
                [python_exe, "simple_backend.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0,
                cwd=os.getcwd()
            )
            
            # Wait for backend to start
            if self._wait_for_port(8001, timeout=30):
                # Additional health check
                time.sleep(2)
                if self._check_backend_health():
                    logger.info("Backend Server started successfully")
                    return True
            
            logger.error("Backend failed to start properly")
            return False
                
        except Exception as e:
            logger.error(f"Failed to start backend: {e}")
            return False

    def _start_frontend(self) -> bool:
        """Start the frontend development server with backend dependency check"""
        logger.info("Starting Frontend Server...")
        
        try:
            # CRITICAL: Verify backend is running first
            if not self._check_backend_health():
                logger.error("Backend must be running before starting frontend")
                logger.info("Frontend depends on backend API at http://localhost:8001")
                return False
            
            # Check if already running
            if self._check_frontend_health():
                logger.info("Frontend already running")
                return True
            
            # Kill any existing frontend processes
            self._kill_process_on_port(5173)
            time.sleep(2)
            
            # FIXED: Use absolute path and ensure we're in the right directory
            frontend_dir = Path(os.getcwd()) / "frontend"
            if not frontend_dir.exists():
                logger.error(f"Frontend directory not found at: {frontend_dir}")
                return False
            
            logger.info(f"Frontend directory: {frontend_dir}")
            
            # Check if npm is available
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("npm not found - please install Node.js")
                return False
            
            # Install dependencies if needed
            node_modules_dir = frontend_dir / "node_modules"
            if not node_modules_dir.exists():
                logger.info("Installing frontend dependencies...")
                result = subprocess.run(
                    ["npm", "install"], 
                    cwd=str(frontend_dir), 
                    capture_output=True, 
                    text=True,
                    timeout=300  # 5 minutes timeout for npm install
                )
                if result.returncode != 0:
                    logger.error(f"npm install failed: {result.stderr}")
                    return False
                logger.info("Frontend dependencies installed successfully")
            
            # Verify package.json exists
            package_json = frontend_dir / "package.json"
            if not package_json.exists():
                logger.error(f"package.json not found at: {package_json}")
                return False
            
            # FIXED: Start frontend with proper working directory
            logger.info(f"Starting npm run dev in directory: {frontend_dir}")
            
            self.processes['frontend'] = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(frontend_dir),  # CRITICAL: Ensure we're in frontend directory
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            # Wait for frontend to start with extended timeout
            logger.info("Waiting for frontend to start on port 5173...")
            if self._wait_for_port(5173, timeout=60):  # Increased timeout
                # Additional wait for Vite to fully initialize
                time.sleep(5)
                
                # Verify frontend is responding
                if self._check_frontend_health():
                    logger.info("✅ Frontend Server started successfully")
                    logger.info("   🌐 Frontend URL: http://localhost:5173")
                    logger.info("   📡 Backend API: http://localhost:8001")
                    return True
                else:
                    logger.warning("Frontend port is open but health check failed")
                    # Give it more time for React to load
                    time.sleep(5)
                    if self._check_frontend_health():
                        logger.info("✅ Frontend Server started successfully (after additional wait)")
                        return True
            
            logger.error("Frontend failed to start within timeout")
            
            # Log process output for debugging
            if 'frontend' in self.processes:
                process = self.processes['frontend']
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    logger.error(f"Frontend process stdout: {stdout.decode() if stdout else 'None'}")
                    logger.error(f"Frontend process stderr: {stderr.decode() if stderr else 'None'}")
            
            return False
                
        except Exception as e:
            logger.error(f"Failed to start frontend: {e}")
            return False

    def _get_python_executable(self) -> str:
        """Get the correct Python executable"""
        # Try virtual environment first
        venv_python = Path("queue_service/venv/Scripts/python.exe")
        if venv_python.exists():
            return str(venv_python)
        
        # Fallback to system Python
        return sys.executable

    def _kill_process_on_port(self, port: int):
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

    def _wait_for_dependencies(self, service_name: str) -> bool:
        """Wait for service dependencies to be ready"""
        dependencies = self.services[service_name]['dependencies']
        
        for dep in dependencies:
            max_wait = 60  # Maximum wait time for dependencies
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                if self.service_status.get(dep, False):
                    break
                time.sleep(1)
            else:
                logger.error(f"Dependency {dep} not ready for {service_name}")
                return False
        
        return True

    def start_service(self, service_name: str) -> bool:
        """Start a single service with dependency management"""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
        
        service_config = self.services[service_name]
        
        # Check if already running
        if self.service_status.get(service_name, False):
            logger.info(f"{service_name} already running")
            return True
        
        # Wait for dependencies
        if not self._wait_for_dependencies(service_name):
            logger.error(f"Dependencies not satisfied for {service_name}")
            return False
        
        # Start the service
        logger.info(f"Starting {service_name}...")
        
        try:
            success = service_config['start_function']()
            
            if success:
                # Wait for service to be fully ready
                timeout = service_config['startup_timeout']
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    if service_config['health_check']():
                        self.service_status[service_name] = True
                        logger.info(f"✅ {service_name} is ready")
                        return True
                    time.sleep(1)
                
                logger.error(f"{service_name} failed health check within timeout")
                return False
            else:
                logger.error(f"Failed to start {service_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting {service_name}: {e}")
            return False

    def restart_service(self, service_name: str) -> bool:
        """Restart a service with backoff"""
        if self.restart_counts[service_name] >= self.max_restarts:
            logger.error(f"Max restarts exceeded for {service_name}")
            return False
        
        logger.info(f"Restarting {service_name} (attempt {self.restart_counts[service_name] + 1})")
        
        # Stop the service
        self.stop_service(service_name)
        time.sleep(2)
        
        # Increment restart counter
        self.restart_counts[service_name] += 1
        
        # Start the service
        return self.start_service(service_name)

    def stop_service(self, service_name: str):
        """Stop a service"""
        if service_name in self.processes:
            process = self.processes[service_name]
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=10)
                except:
                    try:
                        process.kill()
                    except:
                        pass
                finally:
                    del self.processes[service_name]
        
        self.service_status[service_name] = False
        logger.info(f"Stopped {service_name}")

    def monitor_services(self):
        """Monitor services and restart if needed"""
        while not self.shutdown_requested:
            for service_name, config in self.services.items():
                if not self.service_status.get(service_name, False):
                    continue
                
                # Check health
                if not config['health_check']():
                    logger.warning(f"{service_name} health check failed")
                    if config['critical']:
                        if self.restart_service(service_name):
                            logger.info(f"Successfully restarted {service_name}")
                        else:
                            logger.error(f"Failed to restart {service_name}")
                    else:
                        logger.info(f"Non-critical service {service_name} failed")
            
            time.sleep(10)  # Check every 10 seconds

    def start_all_services(self) -> bool:
        """Start all services in dependency order"""
        logger.info("🚀 STARTING REIMS ROBUST SYSTEM")
        logger.info("="*50)
        
        # Start services in dependency order
        service_order = ['minio', 'database', 'backend', 'frontend']
        
        for service_name in service_order:
            if not self.start_service(service_name):
                logger.error(f"Failed to start {service_name}")
                if self.services[service_name]['critical']:
                    logger.error("Critical service failed - stopping startup")
                    return False
                else:
                    logger.warning(f"Non-critical service {service_name} failed - continuing")
        
        return True

    def show_system_status(self):
        """Show comprehensive system status"""
        logger.info("\n" + "="*60)
        logger.info("🎉 REIMS SYSTEM STATUS")
        logger.info("="*60)
        
        for service_name, status in self.service_status.items():
            icon = "✅" if status else "❌"
            logger.info(f"   {icon} {service_name.upper()}: {'RUNNING' if status else 'STOPPED'}")
        
        if all(self.service_status.values()):
            logger.info("\n🌐 Service URLs:")
            logger.info("   • Frontend UI:      http://localhost:5173")
            logger.info("   • Backend API:      http://localhost:8001")
            logger.info("   • MinIO Console:    http://localhost:9001")
            
            logger.info("\n💡 System is ready for testing!")
        else:
            logger.info("\n⚠️ Some services are not running")

    def cleanup(self):
        """Clean up all processes"""
        logger.info("🛑 Stopping all services...")
        self.shutdown_requested = True
        
        for service_name in self.services:
            self.stop_service(service_name)
        
        logger.info("✅ All services stopped")

    def run(self):
        """Main run method"""
        try:
            # Start all services
            if not self.start_all_services():
                logger.error("Failed to start all services")
                return False
            
            # Show status
            self.show_system_status()
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
            monitor_thread.start()
            
            # Keep running
            logger.info("\n🔄 Services are running. Press Ctrl+C to stop all services.")
            
            try:
                while not self.shutdown_requested:
                    time.sleep(5)
                    
                    # Quick overall health check
                    healthy_services = sum(1 for status in self.service_status.values() if status)
                    total_services = len(self.service_status)
                    
                    if healthy_services < total_services:
                        logger.warning(f"Only {healthy_services}/{total_services} services healthy")
                    
            except KeyboardInterrupt:
                logger.info("\n🛑 Shutdown requested...")
            
            return True
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Main function"""
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info("\n🛑 Received shutdown signal")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the service manager
    service_manager = ServiceManager()
    
    try:
        success = service_manager.run()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())