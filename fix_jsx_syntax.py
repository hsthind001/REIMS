#!/usr/bin/env python3
"""
Auto-fix JSX Syntax Issues
Automatically fixes missing semicolons and other common syntax issues
"""

import re
from pathlib import Path

def fix_jsx_files():
    """Fix common JSX syntax issues"""
    print("🔧 AUTO-FIXING JSX SYNTAX ISSUES")
    print("="*50)
    
    frontend_src = Path("frontend/src")
    jsx_files = list(frontend_src.rglob("*.jsx"))
    
    fixes_applied = 0
    files_modified = 0
    
    for file_path in jsx_files:
        print(f"\n📄 Processing: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_fixes = 0
            
            # Fix 1: Add semicolons after variable declarations
            lines = content.split('\n')
            fixed_lines = []
            
            for line in lines:
                stripped = line.strip()
                
                # Add semicolon after const/let/var declarations that end with }
                if re.match(r'^\s*(const|let|var)\s+\w+.*=.*\}$', stripped) and not stripped.endswith(';'):
                    line = line + ';'
                    file_fixes += 1
                
                # Add semicolon after const/let/var declarations that end with ]
                elif re.match(r'^\s*(const|let|var)\s+\w+.*=.*\]$', stripped) and not stripped.endswith(';'):
                    line = line + ';'
                    file_fixes += 1
                
                # Add semicolon after const/let/var declarations that end with )
                elif re.match(r'^\s*(const|let|var)\s+\w+.*=.*\)$', stripped) and not stripped.endswith(';'):
                    line = line + ';'
                    file_fixes += 1
                
                fixed_lines.append(line)
            
            content = '\n'.join(fixed_lines)
            
            # Fix 2: Add missing export statements for components that don't have them
            if file_path.name not in ['index.jsx']:  # Skip index.jsx as it's entry point
                # Check if file has a function component but no export
                has_function_component = re.search(r'function\s+\w+\s*\(', content)
                has_export = re.search(r'export\s+(default\s+)?\w+|export\s*\{.*\}', content)
                
                if has_function_component and not has_export:
                    # Find the main function name
                    func_match = re.search(r'function\s+(\w+)\s*\(', content)
                    if func_match:
                        func_name = func_match.group(1)
                        # Add export at the end
                        content = content + f'\n\nexport default {func_name};\n'
                        file_fixes += 1
            
            # Only write if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"   ✅ Applied {file_fixes} fixes")
                fixes_applied += file_fixes
                files_modified += 1
            else:
                print("   ℹ️ No fixes needed")
                
        except Exception as e:
            print(f"   ❌ Error processing file: {e}")
    
    print("\n" + "="*50)
    print("📋 AUTO-FIX SUMMARY:")
    print(f"✅ Files processed: {len(jsx_files)}")
    print(f"✅ Files modified: {files_modified}")
    print(f"✅ Total fixes applied: {fixes_applied}")
    
    if fixes_applied > 0:
        print("\n💡 FIXES APPLIED:")
        print("   • Added missing semicolons after variable declarations")
        print("   • Added missing export statements for components")
        print("\n🔄 Run the syntax checker again to verify fixes:")
        print("   python check_jsx_syntax.py")
    else:
        print("\n✅ No automatic fixes were needed!")
    
    return fixes_applied > 0

if __name__ == "__main__":
    fix_jsx_files()