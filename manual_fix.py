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

# Find where the routes start (after the uvicorn.run line)
routes_start = None
for i, line in enumerate(lines):
    if 'uvicorn.run(app, host="0.0.0.0", port=8001)' in line:
        routes_start = i + 1
        break

if routes_start is None:
    print("Could not find uvicorn.run line")
    exit(1)

# Find where the routes end (before the second if __name__ block)
routes_end = None
for i in range(routes_start, len(lines)):
    if lines[i].strip() == 'if __name__ == "__main__":' and i > routes_start:
        routes_end = i
        break

if routes_end is None:
    print("Could not find end of routes")
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
with open('simple_backend_manual_fix.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(final_lines))

print("Manual fix file created: simple_backend_manual_fix.py")
print(f"Original lines: {len(lines)}")
print(f"Final lines: {len(final_lines)}")
print(f"Routes section: {len(routes_section)} lines")
print(f"Main index: {main_index}")
print(f"Routes start: {routes_start}")
print(f"Routes end: {routes_end}")
