# Read the current file
with open('simple_backend.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Read the complete endpoints
with open('new_endpoints.py', 'r', encoding='utf-8') as f:
    endpoints_content = f.read()

# Find where to insert the endpoints (before the first if __name__ block)
lines = content.split('\n')
main_index = None
for i, line in enumerate(lines):
    if line.strip() == 'if __name__ == "__main__":':
        main_index = i
        break

if main_index is None:
    print("Could not find if __name__ block")
    exit(1)

# Create the new content
before_main = lines[:main_index]
after_main = lines[main_index:]

# Split the endpoints content into lines
endpoints_lines = endpoints_content.split('\n')

# Combine everything
final_lines = before_main + [''] + endpoints_lines + [''] + after_main

# Write the complete file
with open('simple_backend_complete.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(final_lines))

print("Complete file created: simple_backend_complete.py")
print(f"Original lines: {len(lines)}")
print(f"Final lines: {len(final_lines)}")
print(f"Endpoints lines: {len(endpoints_lines)}")
