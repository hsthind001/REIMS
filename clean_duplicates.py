# Read the file
with open('simple_backend.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track what we've seen to avoid duplicates
seen_routes = set()
seen_functions = set()
cleaned_lines = []
skip_until_next_route = False

for i, line in enumerate(lines):
    # Check for duplicate route definitions
    if line.strip().startswith('@app.get("/api/properties/{property_id}/financials'):
        route_key = line.strip()
        if route_key in seen_routes:
            # Skip this duplicate route
            skip_until_next_route = True
            continue
        else:
            seen_routes.add(route_key)
            skip_until_next_route = False
    
    # Check for duplicate function definitions
    elif line.strip().startswith('def extract_year_from_filename'):
        if 'extract_year_from_filename' in seen_functions:
            # Skip this duplicate function
            skip_until_next_route = True
            continue
        else:
            seen_functions.add('extract_year_from_filename')
            skip_until_next_route = False
    
    if skip_until_next_route:
        # Skip lines until we hit the next route, function, or class definition
        if (line.strip().startswith('@app.') or 
            line.strip().startswith('def ') or 
            line.strip().startswith('class ') or 
            line.strip().startswith('if __name__')):
            skip_until_next_route = False
        else:
            continue
    
    cleaned_lines.append(line)

# Write the cleaned file
with open('simple_backend_final.py', 'w', encoding='utf-8') as f:
    f.writelines(cleaned_lines)

print("Cleaned file created: simple_backend_final.py")
print(f"Original lines: {len(lines)}")
print(f"Cleaned lines: {len(cleaned_lines)}")
print(f"Removed {len(lines) - len(cleaned_lines)} duplicate lines")
