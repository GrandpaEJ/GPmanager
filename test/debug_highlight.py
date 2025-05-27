#!/usr/bin/env python3
"""
Debug script for syntax highlighting - shows what rules are being applied
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

try:
    from src.editors.json_highlighter import highlighter_manager
    
    def test_python_rules():
        """Test Python syntax highlighting rules"""
        print("=== Testing Python Syntax Highlighting ===")
        
        # Get Python language info
        py_info = highlighter_manager.get_language_info('py')
        if not py_info:
            print("❌ Could not load Python language info")
            return
        
        print(f"✓ Loaded Python config: {py_info['name']}")
        print(f"✓ Extensions: {py_info['extensions']}")
        print(f"✓ Colors: {list(py_info['colors'].keys())}")
        print(f"✓ Rules: {len(py_info['rules'])}")
        print(f"✓ Multiline rules: {len(py_info.get('multiline_rules', []))}")
        
        # Test specific patterns
        test_cases = [
            ("import sys", "keywords"),
            ("from pathlib import Path", "keywords"),
            ("def main():", "keywords"),
            ("class MyClass:", "keywords"),
            ("try:", "keywords"),
            ("except Exception:", "keywords"),
            ("'hello world'", "strings"),
            ('"hello world"', "strings"),
            ("f'Hello {name}'", "strings"),
            ('"""docstring"""', "strings"),
            ("# This is a comment", "comments"),
            ("123", "numbers"),
            ("0x1A", "numbers"),
            ("str(value)", "builtin functions"),
            ("len(items)", "builtin functions"),
        ]
        
        print("\n--- Testing Pattern Matches ---")
        for test_text, expected_type in test_cases:
            print(f"Testing: {test_text:<25} -> Expected: {expected_type}")
            
            # Test against rules
            rules = py_info['rules']
            matched = False
            
            for rule in rules:
                pattern = rule.get('pattern', '')
                if not pattern:
                    continue
                
                import re
                try:
                    if re.search(pattern, test_text):
                        print(f"  ✓ Matched rule: {rule['name']} (color: {rule.get('color', 'unknown')})")
                        matched = True
                        break
                except re.error as e:
                    print(f"  ❌ Regex error in rule {rule['name']}: {e}")
            
            if not matched:
                print(f"  ❌ No rule matched")
        
        print("\n--- Rule Details ---")
        for i, rule in enumerate(py_info['rules']):
            print(f"{i+1:2d}. {rule['name']:<25} -> {rule.get('color', 'unknown'):<10} | {rule.get('pattern', '')[:50]}")
    
    def test_all_languages():
        """Test all supported languages"""
        print("\n=== Testing All Languages ===")
        
        languages = highlighter_manager.get_supported_languages()
        print(f"Total languages: {len(languages)}")
        
        for lang in sorted(languages):
            info = highlighter_manager.get_language_info(lang)
            if info:
                rules_count = len(info.get('rules', []))
                multiline_count = len(info.get('multiline_rules', []))
                extensions = ', '.join(info.get('extensions', []))
                print(f"  {lang:<12} | {rules_count:2d} rules, {multiline_count:2d} multiline | {extensions}")
            else:
                print(f"  {lang:<12} | ❌ Failed to load")
    
    def test_highlighter_creation():
        """Test creating highlighters for different file types"""
        print("\n=== Testing Highlighter Creation ===")
        
        test_files = [
            'test.py', 'test.java', 'test.cpp', 'test.js', 'test.html',
            'test.css', 'test.json', 'test.xml', 'test.smali', 'test.sql'
        ]
        
        for file_path in test_files:
            highlighter = highlighter_manager.get_highlighter_for_file(file_path)
            if highlighter:
                print(f"  ✓ {file_path:<12} -> {type(highlighter).__name__}")
            else:
                print(f"  ❌ {file_path:<12} -> No highlighter")
    
    def main():
        print("Syntax Highlighting Debug Tool")
        print("=" * 50)
        
        test_python_rules()
        test_all_languages()
        test_highlighter_creation()
        
        print("\n" + "=" * 50)
        print("Debug complete!")

except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

if __name__ == "__main__":
    main()
