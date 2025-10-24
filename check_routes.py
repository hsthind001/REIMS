from simple_backend import app

print('App routes:')
for route in app.routes:
    if hasattr(route, 'path'):
        methods = getattr(route, 'methods', 'N/A')
        print(f'  {route.path} - {methods}')

print(f'\nTotal routes: {len(app.routes)}')
print('Routes with financials:')
for route in app.routes:
    if hasattr(route, 'path') and 'financials' in route.path:
        print(f'  {route.path}')
