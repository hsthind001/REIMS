import sys
import traceback

try:
    print("Importing simple_backend...")
    from simple_backend import app
    
    print("\nChecking if routes are registered...")
    financial_routes = [r for r in app.routes if hasattr(r, 'path') and 'financials' in r.path]
    
    if financial_routes:
        print(f"Found {len(financial_routes)} financial routes:")
        for route in financial_routes:
            print(f"  - {route.path}")
    else:
        print("No financial routes found!")
        
    print("\nAll routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  {route.path}")
            
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()

