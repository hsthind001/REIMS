"""
Test script for REIMS health check endpoint

Run this to test all health check endpoints.

Usage:
    python backend/test_health_endpoint.py
"""

import asyncio
import httpx
import sys
from datetime import datetime


BASE_URL = "http://localhost:8000"

ENDPOINTS = [
    ("/health", "Main Health Check"),
    ("/health/database", "Database Health"),
    ("/health/redis", "Redis Health"),
    ("/health/minio", "MinIO Health"),
    ("/health/ollama", "Ollama Health"),
    ("/health/live", "Liveness Probe"),
    ("/health/ready", "Readiness Probe"),
]


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_service_status(name: str, status: str):
    """Print service status with color"""
    icons = {
        "healthy": "✅",
        "degraded": "⚠️",
        "unhealthy": "❌",
        "unavailable": "⚪",
        "alive": "✅",
        "ready": "✅",
        "not_ready": "❌"
    }
    icon = icons.get(status, "❓")
    print(f"  {icon} {name}: {status}")


async def test_endpoint(client: httpx.AsyncClient, path: str, name: str):
    """Test a single endpoint"""
    print(f"\n📍 Testing: {name}")
    print(f"   URL: {BASE_URL}{path}")
    
    try:
        start_time = asyncio.get_event_loop().time()
        response = await client.get(f"{BASE_URL}{path}")
        elapsed = (asyncio.get_event_loop().time() - start_time) * 1000
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Time: {elapsed:.2f}ms")
        
        if response.status_code in [200, 503]:
            data = response.json()
            
            # Print main status
            if "status" in data:
                print_service_status(name, data["status"])
            
            # Print service statuses (for main health check)
            if "services" in data:
                print("\n   Service Statuses:")
                for service, status in data["services"].items():
                    print_service_status(f"    {service.capitalize()}", status)
            
            # Print details summary
            if "details" in data:
                print("\n   Details Summary:")
                for service, details in data["details"].items():
                    if isinstance(details, dict):
                        if "latency_ms" in details:
                            print(f"    • {service.capitalize()}: {details['latency_ms']}ms latency")
                        if "error" in details:
                            print(f"    • {service.capitalize()}: ❌ {details['error']}")
            
            # Print check duration (for main health check)
            if "check_duration_ms" in data:
                print(f"\n   Total Check Duration: {data['check_duration_ms']}ms")
            
            return True
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    
    except httpx.ConnectError:
        print(f"   ❌ Connection failed: Cannot reach {BASE_URL}")
        print(f"   💡 Make sure the backend is running on port 8000")
        return False
    
    except httpx.TimeoutException:
        print(f"   ❌ Request timed out")
        return False
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


async def run_tests():
    """Run all health check tests"""
    print_header("🏥 REIMS Health Check Endpoint Tests")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Backend URL: {BASE_URL}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        results = []
        
        for path, name in ENDPOINTS:
            success = await test_endpoint(client, path, name)
            results.append((name, success))
        
        # Summary
        print_header("📊 Test Summary")
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status}  {name}")
        
        print(f"\n  Total: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n  🎉 All tests passed!")
            return 0
        else:
            print(f"\n  ⚠️  {total - passed} test(s) failed")
            return 1


async def test_main_health_detailed():
    """Detailed test of main health endpoint"""
    print_header("🔍 Detailed Health Check Analysis")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            
            if response.status_code not in [200, 503]:
                print(f"❌ Unexpected status code: {response.status_code}")
                return
            
            data = response.json()
            
            print(f"\n📊 Overall Status: {data.get('status', 'unknown').upper()}")
            print(f"✅ Success: {data.get('success', False)}")
            print(f"⏱️  Check Duration: {data.get('check_duration_ms', 0)}ms")
            print(f"🕐 Timestamp: {data.get('timestamp', 'N/A')}")
            
            print("\n" + "─" * 70)
            print("SERVICE DETAILS")
            print("─" * 70)
            
            services = data.get("services", {})
            details = data.get("details", {})
            
            for service_name, service_status in services.items():
                print(f"\n🔧 {service_name.upper()}")
                print_service_status(f"  Status", service_status)
                
                service_details = details.get(service_name, {})
                if isinstance(service_details, dict):
                    for key, value in service_details.items():
                        if key != "error":
                            print(f"  • {key}: {value}")
                        else:
                            print(f"  ❌ {key}: {value}")
            
            # Recommendations
            print("\n" + "─" * 70)
            print("RECOMMENDATIONS")
            print("─" * 70)
            
            for service_name, service_status in services.items():
                if service_status == "unhealthy":
                    print(f"\n❌ {service_name.upper()} is unhealthy")
                    print(f"   Action: Check {service_name} configuration and logs")
                    
                    service_details = details.get(service_name, {})
                    if "error" in service_details:
                        print(f"   Error: {service_details['error']}")
                
                elif service_status == "unavailable":
                    print(f"\n⚪ {service_name.upper()} is not available")
                    print(f"   This is OK if {service_name} is optional")
            
            if data.get("status") == "healthy":
                print("\n✅ All critical services are healthy!")
                print("   No action needed.")
        
        except Exception as e:
            print(f"❌ Error running detailed health check: {str(e)}")


async def continuous_monitoring(interval: int = 30):
    """Run health check continuously"""
    print_header("🔄 Continuous Health Monitoring")
    print(f"Checking every {interval} seconds...")
    print("Press Ctrl+C to stop\n")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            while True:
                try:
                    response = await client.get(f"{BASE_URL}/health")
                    data = response.json()
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    status = data.get("status", "unknown")
                    duration = data.get("check_duration_ms", 0)
                    
                    # One-line status
                    status_icon = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
                    print(f"[{timestamp}] {status_icon} {status.upper()} ({duration}ms)", end="")
                    
                    # Service summary
                    services = data.get("services", {})
                    unhealthy = [s for s, st in services.items() if st == "unhealthy"]
                    if unhealthy:
                        print(f" - Unhealthy: {', '.join(unhealthy)}")
                    else:
                        print()
                    
                except Exception as e:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] ❌ Check failed: {str(e)}")
                
                await asyncio.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test REIMS health check endpoints")
    parser.add_argument(
        "--mode",
        choices=["test", "detailed", "monitor"],
        default="test",
        help="Test mode: test (all endpoints), detailed (detailed analysis), monitor (continuous)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Monitoring interval in seconds (for monitor mode)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "test":
            exit_code = asyncio.run(run_tests())
            sys.exit(exit_code)
        elif args.mode == "detailed":
            asyncio.run(test_main_health_detailed())
        elif args.mode == "monitor":
            asyncio.run(continuous_monitoring(args.interval))
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted")
        sys.exit(1)


if __name__ == "__main__":
    main()
















