#!/usr/bin/env python3
"""
React JSX Syntax Checker for REIMS Frontend
Validates all JSX files for syntax errors and common issues
"""

import os
import re
from pathlib import Path

def check_jsx_syntax():
    """Check all JSX files for syntax issues"""
    print("🔍 CHECKING JSX SYNTAX IN REIMS FRONTEND")
    print("="*50)
    
    frontend_src = Path("frontend/src")
    if not frontend_src.exists():
        print("❌ Frontend src directory not found")
        return False
    
    jsx_files = list(frontend_src.rglob("*.jsx"))
    
    if not jsx_files:
        print("❌ No JSX files found")
        return False
    
    print(f"📁 Found {len(jsx_files)} JSX files to check:")
    
    all_valid = True
    issues_found = []
    
    for file_path in jsx_files:
        print(f"\n📄 Checking: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for common syntax issues
            file_issues = []
            
            # 1. Check for balanced braces
            brace_count = content.count('{') - content.count('}')
            if brace_count != 0:
                file_issues.append(f"Unbalanced braces: {brace_count} extra opening braces")
            
            # 2. Check for balanced parentheses
            paren_count = content.count('(') - content.count(')')
            if paren_count != 0:
                file_issues.append(f"Unbalanced parentheses: {paren_count} extra opening parentheses")
            
            # 3. Check for balanced brackets
            bracket_count = content.count('[') - content.count(']')
            if bracket_count != 0:
                file_issues.append(f"Unbalanced brackets: {bracket_count} extra opening brackets")
            
            # 4. Check for React import
            if 'import React' not in content and 'from "react"' not in content and 'from \'react\'' not in content:
                file_issues.append("Missing React import")
            
            # 5. Check for function export
            export_patterns = [
                r'export default \w+',
                r'export \{ .+ \}',
                r'module\.exports'
            ]
            has_export = any(re.search(pattern, content) for pattern in export_patterns)
            if not has_export:
                file_issues.append("No export statement found")
            
            # 6. Check for common JSX issues
            jsx_issues = []
            
            # Unclosed JSX tags
            jsx_tag_pattern = r'<(\w+)(?:\s[^>]*)?(?<!/)>'
            closing_tag_pattern = r'</(\w+)>'
            
            opening_tags = re.findall(jsx_tag_pattern, content)
            closing_tags = re.findall(closing_tag_pattern, content)
            
            # Self-closing tags don't need closing tags
            self_closing_pattern = r'<\w+(?:\s[^>]*)?/>'
            self_closing_count = len(re.findall(self_closing_pattern, content))
            
            # 7. Check for missing semicolons in important places
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Check for missing semicolons after imports
                if stripped.startswith('import ') and not stripped.endswith(';') and not stripped.endswith('{'):
                    jsx_issues.append(f"Line {i}: Missing semicolon after import")
                
                # Check for missing semicolons after variable declarations
                if re.match(r'^\s*(const|let|var)\s+\w+', stripped) and '=' in stripped and not stripped.endswith(';') and not stripped.endswith('{'):
                    jsx_issues.append(f"Line {i}: Missing semicolon after variable declaration")
            
            # 8. Check for common React hooks issues
            hooks_pattern = r'use\w+\('
            hooks = re.findall(hooks_pattern, content)
            if hooks and 'import React' not in content and 'useState' not in content and 'useEffect' not in content:
                # Check if hooks are properly imported
                if not re.search(r'import.*\{.*use\w+.*\}.*from ["\']react["\']', content):
                    jsx_issues.append("Using hooks but missing proper import")
            
            file_issues.extend(jsx_issues)
            
            if file_issues:
                print(f"   ❌ Issues found ({len(file_issues)}):")
                for issue in file_issues:
                    print(f"      • {issue}")
                issues_found.append((file_path.name, file_issues))
                all_valid = False
            else:
                print("   ✅ Syntax looks good")
                
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
            all_valid = False
    
    print("\n" + "="*50)
    print("📋 SYNTAX CHECK SUMMARY:")
    
    if all_valid:
        print("✅ All JSX files have valid syntax!")
        print("✅ No syntax errors detected")
        print("✅ React imports are proper")
        print("✅ Exports are present")
    else:
        print(f"❌ Found issues in {len(issues_found)} files:")
        for filename, issues in issues_found:
            print(f"\n📄 {filename}:")
            for issue in issues:
                print(f"   • {issue}")
    
    # Check the main entry point
    print("\n🎯 CHECKING MAIN ENTRY POINT:")
    index_jsx = Path("frontend/src/index.jsx")
    if index_jsx.exists():
        with open(index_jsx, 'r', encoding='utf-8') as f:
            index_content = f.read()
        
        print("✅ index.jsx exists")
        
        # Check what component is being rendered
        import_match = re.search(r'import (\w+) from ["\']\.\/([^"\']+)["\']', index_content)
        if import_match:
            component_name = import_match.group(1)
            component_file = import_match.group(2)
            print(f"✅ Main component: {component_name} from {component_file}")
            
            # Check if the imported file exists
            component_path = Path(f"frontend/src/{component_file}")
            if not component_path.exists() and not Path(f"frontend/src/{component_file}.jsx").exists():
                print(f"❌ Main component file not found: {component_file}")
                all_valid = False
            else:
                print(f"✅ Main component file exists")
        else:
            print("❌ Cannot determine main component from index.jsx")
            all_valid = False
    else:
        print("❌ index.jsx not found")
        all_valid = False
    
    print("\n💡 RECOMMENDATIONS:")
    if all_valid:
        print("✅ Your JSX files are syntactically correct!")
        print("✅ If you're seeing issues in the browser:")
        print("   1. Check browser console for runtime errors")
        print("   2. Verify API endpoints are responding")
        print("   3. Check network tab for failed requests")
        print("   4. Try hard refresh (Ctrl+Shift+R)")
    else:
        print("🔧 Fix the syntax issues found above")
        print("🔧 Run this checker again after fixes")
        print("🔧 Use VS Code with ESLint extension for real-time syntax checking")
    
    return all_valid

if __name__ == "__main__":
    check_jsx_syntax()