# Read the file
with open('simple_backend.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the first if __name__ block
first_main_index = None
for i, line in enumerate(lines):
    if line.strip() == 'if __name__ == "__main__":':
        first_main_index = i
        break

if first_main_index is None:
    print("Could not find if __name__ block")
    exit(1)

# Find the routes that need to be moved
routes_start = None
routes_end = None
for i, line in enumerate(lines):
    if line.strip().startswith('# Year-based Financial Data Endpoints'):
        routes_start = i
    elif routes_start is not None and line.strip() == 'if __name__ == "__main__":' and i > routes_start:
        routes_end = i
        break

if routes_start is None or routes_end is None:
    print("Could not find routes section")
    exit(1)

# Extract the routes
routes_section = lines[routes_start:routes_end]

# Remove the routes from their current position
lines_without_routes = lines[:routes_start] + lines[routes_end:]

# Insert routes before the first if __name__ block
final_lines = lines_without_routes[:first_main_index] + routes_section + lines_without_routes[first_main_index:]

# Write the fixed file
with open('simple_backend_fixed.py', 'w', encoding='utf-8') as f:
    f.writelines(final_lines)

print("Fixed file created: simple_backend_fixed.py")
print(f"Original lines: {len(lines)}")
print(f"Fixed lines: {len(final_lines)}")
