"""
Comprehensive Dependency Checker for REIMS
Checks backend Python packages, frontend Node packages, and Docker services
"""

import sys
import subprocess
import importlib
import json
import os
import io
from pathlib import Path

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_python_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name.split('[')[0].replace('-', '_')
    
    try:
        importlib.import_module(import_name)
        return True, "Installed"
    except ImportError:
        return False, "NOT INSTALLED"

def check_backend_dependencies():
    """Check all backend Python dependencies"""
    print("=" * 70)
    print("BACKEND PYTHON DEPENDENCIES")
    print("=" * 70)
    
    # Critical packages to check
    packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("sqlalchemy", "sqlalchemy"),
        ("psycopg2-binary", "psycopg2"),
        ("redis", "redis"),
        ("minio", "minio"),
        ("passlib", "passlib"),
        ("python-jose", "jose"),
        ("pydantic", "pydantic"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("scikit-learn", "sklearn"),
        ("matplotlib", "matplotlib"),
        ("prometheus-client", "prometheus_client"),
        ("celery", "celery"),
        ("apscheduler", "apscheduler"),
        ("httpx", "httpx"),
        ("python-multipart", "multipart"),
        ("python-dotenv", "dotenv"),
        ("cryptography", "cryptography"),
    ]
    
    results = []
    all_installed = True
    
    for package_name, import_name in packages:
        installed, status = check_python_package(package_name, import_name)
        results.append((package_name, status, installed))
        if not installed:
            all_installed = False
        
        status_icon = "✅" if installed else "❌"
        print(f"  {status_icon} {package_name:<30} {status}")
    
    print("\n" + "=" * 70)
    if all_installed:
        print("✅ All critical backend dependencies are installed!")
    else:
        print("❌ Some backend dependencies are missing!")
        print("\nTo install missing packages:")
        print("  cd backend && pip install -r requirements.txt")
    
    return all_installed

def check_frontend_dependencies():
    """Check frontend Node.js dependencies"""
    print("\n" + "=" * 70)
    print("FRONTEND NODE.JS DEPENDENCIES")
    print("=" * 70)
    
    frontend_path = Path("frontend")
    package_json = frontend_path / "package.json"
    node_modules = frontend_path / "node_modules"
    
    if not package_json.exists():
        print("❌ package.json not found!")
        return False
    
    if not node_modules.exists():
        print("❌ node_modules not found!")
        print("\nTo install:")
        print("  cd frontend && npm install")
        return False
    
    # Check if key packages exist
    key_packages = [
        "react",
        "vite",
        "tailwindcss",
        "@tanstack/react-query",
        "recharts",
        "framer-motion",
    ]
    
    all_present = True
    for package in key_packages:
        package_path = node_modules / package.replace("@", "").replace("/", os.sep)
        if "@" in package:
            package_path = node_modules / "@tanstack" / "react-query"
        
        exists = package_path.exists() or (node_modules / package).exists()
        status_icon = "✅" if exists else "❌"
        status = "Installed" if exists else "NOT INSTALLED"
        print(f"  {status_icon} {package:<30} {status}")
        if not exists:
            all_present = False
    
    # Count total packages
    try:
        package_count = sum(1 for p in node_modules.iterdir() if p.is_dir() and not p.name.startswith('.'))
        print(f"\n  📦 Total packages installed: {package_count}")
    except Exception as e:
        print(f"\n  ⚠️  Could not count packages: {e}")
    
    print("\n" + "=" * 70)
    if all_present:
        print("✅ All critical frontend dependencies are installed!")
    else:
        print("❌ Some frontend dependencies are missing!")
    
    return all_present

def check_docker_services():
    """Check Docker services status"""
    print("\n" + "=" * 70)
    print("DOCKER SERVICES STATUS")
    print("=" * 70)
    
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            services = []
            for line in result.stdout.strip().split('\n'):
                try:
                    service = json.loads(line)
                    services.append(service)
                except:
                    pass
            
            if services:
                for service in services:
                    name = service.get('Service', 'Unknown')
                    state = service.get('State', 'Unknown')
                    health = service.get('Health', 'N/A')
                    
                    if state == 'running':
                        status_icon = "✅"
                    else:
                        status_icon = "❌"
                    
                    health_str = f"({health})" if health != 'N/A' else ""
                    print(f"  {status_icon} {name:<20} {state:<15} {health_str}")
                
                running = sum(1 for s in services if s.get('State') == 'running')
                print(f"\n  📊 {running}/{len(services)} services running")
                print("\n" + "=" * 70)
                
                if running == len(services):
                    print("✅ All Docker services are running!")
                else:
                    print("⚠️  Some Docker services are not running!")
                    print("\nTo start services:")
                    print("  docker-compose up -d")
                
                return running == len(services)
            else:
                print("  ℹ️  No services found")
                print("\nTo start services:")
                print("  docker-compose up -d")
                return False
        else:
            print("  ⚠️  Docker Compose not running or no services defined")
            print("\nTo start services:")
            print("  docker-compose up -d")
            return False
            
    except FileNotFoundError:
        print("  ❌ Docker or Docker Compose not found!")
        print("\nPlease install Docker Desktop:")
        print("  https://www.docker.com/products/docker-desktop")
        return False
    except Exception as e:
        print(f"  ❌ Error checking Docker: {e}")
        return False

def check_service_ports():
    """Check if required services are listening on expected ports"""
    print("\n" + "=" * 70)
    print("SERVICE PORT STATUS")
    print("=" * 70)
    
    ports_to_check = {
        "8001": "Backend API",
        "5173": "Frontend Dev Server",
        "5432": "PostgreSQL",
        "6379": "Redis",
        "9000": "MinIO API",
        "9001": "MinIO Console",
        "11434": "Ollama",
        "3000": "Grafana",
    }
    
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        listening_ports = set()
        for line in result.stdout.split('\n'):
            if 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 2:
                    addr = parts[1]
                    if ':' in addr:
                        port = addr.split(':')[-1]
                        listening_ports.add(port)
        
        services_up = 0
        for port, service_name in ports_to_check.items():
            if port in listening_ports:
                print(f"  ✅ Port {port:<6} {service_name}")
                services_up += 1
            else:
                print(f"  ❌ Port {port:<6} {service_name} (not listening)")
        
        print(f"\n  📊 {services_up}/{len(ports_to_check)} services listening")
        print("\n" + "=" * 70)
        
        if services_up >= len(ports_to_check) * 0.75:  # At least 75%
            print("✅ Most critical services are running!")
        else:
            print("⚠️  Many services are not running!")
        
        return services_up >= len(ports_to_check) * 0.75
        
    except Exception as e:
        print(f"  ❌ Error checking ports: {e}")
        return False

def main():
    """Main dependency check function"""
    import os
    
    print("\n" + "=" * 70)
    print("REIMS COMPREHENSIVE DEPENDENCY CHECK")
    print("=" * 70)
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Platform: {sys.platform}")
    print("=" * 70)
    
    # Run all checks
    backend_ok = check_backend_dependencies()
    frontend_ok = check_frontend_dependencies()
    docker_ok = check_docker_services()
    ports_ok = check_service_ports()
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    
    checks = [
        ("Backend Dependencies", backend_ok),
        ("Frontend Dependencies", frontend_ok),
        ("Docker Services", docker_ok),
        ("Service Ports", ports_ok),
    ]
    
    for check_name, status in checks:
        icon = "✅" if status else "❌"
        status_text = "PASS" if status else "FAIL"
        print(f"  {icon} {check_name:<25} {status_text}")
    
    passed = sum(1 for _, status in checks if status)
    total = len(checks)
    
    print(f"\n  📊 Overall: {passed}/{total} checks passed ({passed/total*100:.0f}%)")
    print("\n" + "=" * 70)
    
    if passed == total:
        print("🎉 ALL DEPENDENCIES ARE INSTALLED AND WORKING!")
        print("\n✅ REIMS is ready to run!")
        return 0
    else:
        print("⚠️  SOME DEPENDENCIES NEED ATTENTION")
        print("\nPlease review the output above and install missing components.")
        return 1

if __name__ == "__main__":
    import os
    sys.exit(main())

