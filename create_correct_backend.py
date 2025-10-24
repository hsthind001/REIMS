# Read the original file
with open('simple_backend.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Split into lines
lines = content.split('\n')

# Find the first if __name__ block
main_index = None
for i, line in enumerate(lines):
    if line.strip() == 'if __name__ == "__main__":':
        main_index = i
        break

if main_index is None:
    print("Could not find if __name__ block")
    exit(1)

# Find the routes (they start with the comment and end with the extract_year_from_filename function)
routes_start = None
routes_end = None

for i, line in enumerate(lines):
    if 'Year-based Financial Data Endpoints' in line:
        routes_start = i
    elif routes_start is not None and 'def extract_year_from_filename' in line:
        # Find the end of this function
        for j in range(i, len(lines)):
            if j > i + 10 and (lines[j].strip() == '' or lines[j].strip().startswith('if __name__')):
                routes_end = j
                break
        break

if routes_start is None or routes_end is None:
    print("Could not find routes section")
    print("Routes start:", routes_start)
    print("Routes end:", routes_end)
    exit(1)

# Extract the routes
routes_section = lines[routes_start:routes_end]

# Create the new file structure
# Everything before the main block
before_main = lines[:main_index]

# Everything after the routes (from the end of routes to the end)
after_routes = lines[routes_end:]

# Combine: before_main + routes + after_routes
final_lines = before_main + routes_section + after_routes

# Write the fixed file
with open('simple_backend_correct.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(final_lines))

print("Correct file created: simple_backend_correct.py")
print(f"Original lines: {len(lines)}")
print(f"Final lines: {len(final_lines)}")
print(f"Routes section: {len(routes_section)} lines")
