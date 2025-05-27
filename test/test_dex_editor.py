#!/usr/bin/env python3
"""
Test script for DEX editor functionality
"""
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

def test_dex_parser():
    """Test DEX parser functionality"""
    print("Testing DEX parser...")
    
    try:
        from src.parsers.dex_parser import DexParser
        
        # Create a minimal test DEX file (just header)
        test_dex_data = b'dex\n035\x00' + b'\x00' * 106  # Minimal DEX header
        test_file = Path(__file__).parent / 'test.dex'
        
        with open(test_file, 'wb') as f:
            f.write(test_dex_data)
        
        parser = DexParser(str(test_file))
        
        # Test magic validation
        if parser._validate_magic():
            print("✓ DEX magic validation works")
        else:
            print("✗ DEX magic validation failed")
        
        # Clean up
        test_file.unlink()
        
    except ImportError as e:
        print(f"✗ DEX parser import failed: {e}")
    except Exception as e:
        print(f"✗ DEX parser test failed: {e}")

def test_dex_tools():
    """Test DEX tools functionality"""
    print("\nTesting DEX tools...")
    
    try:
        from src.tools.dex_tools import DexTools
        
        # Test tool availability checks
        baksmali_available = DexTools.is_baksmali_available()
        smali_available = DexTools.is_smali_available()
        
        print(f"Baksmali available: {baksmali_available}")
        print(f"Smali available: {smali_available}")
        
        if baksmali_available:
            version = DexTools.get_baksmali_version()
            print(f"Baksmali version: {version}")
        
        if smali_available:
            version = DexTools.get_smali_version()
            print(f"Smali version: {version}")
        
        # Test DEX validation
        test_dex_data = b'dex\n035\x00' + b'\x00' * 106
        test_file = Path(__file__).parent / 'test.dex'
        
        with open(test_file, 'wb') as f:
            f.write(test_dex_data)
        
        is_valid, message = DexTools.validate_dex_file(str(test_file))
        print(f"DEX validation: {is_valid} - {message}")
        
        # Test DEX info
        info = DexTools.get_dex_info(str(test_file))
        print(f"DEX info: {info}")
        
        # Clean up
        test_file.unlink()
        
        print("✓ DEX tools tests completed")
        
    except ImportError as e:
        print(f"✗ DEX tools import failed: {e}")
    except Exception as e:
        print(f"✗ DEX tools test failed: {e}")

def test_file_utils():
    """Test file utility functions for DEX files"""
    print("\nTesting file utilities...")
    
    try:
        from src.utils.file_utils import FileUtils
        
        # Test DEX file detection
        test_files = [
            'test.dex',
            'classes.dex',
            'test.apk',
            'test.txt'
        ]
        
        for filename in test_files:
            is_dex = FileUtils.is_dex_file(filename)
            icon_type = FileUtils.get_file_icon_type(filename)
            print(f"{filename}: is_dex={is_dex}, icon_type={icon_type}")
        
        print("✓ File utilities tests completed")
        
    except ImportError as e:
        print(f"✗ File utilities import failed: {e}")
    except Exception as e:
        print(f"✗ File utilities test failed: {e}")

def test_dex_editor_widget():
    """Test DEX editor widget (requires PyQt5)"""
    print("\nTesting DEX editor widget...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from src.editors.dex_editor import DexEditor
        
        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create DEX editor widget
        editor = DexEditor()
        print("✓ DEX editor widget created successfully")
        
        # Test widget components
        if hasattr(editor, 'structure_viewer'):
            print("✓ Structure viewer component exists")
        if hasattr(editor, 'bytecode_viewer'):
            print("✓ Bytecode viewer component exists")
        if hasattr(editor, 'smali_viewer'):
            print("✓ Smali viewer component exists")
        
        print("✓ DEX editor widget tests completed")
        
    except ImportError as e:
        print(f"✗ DEX editor widget import failed: {e}")
    except Exception as e:
        print(f"✗ DEX editor widget test failed: {e}")

def test_syntax_highlighting():
    """Test syntax highlighting configuration"""
    print("\nTesting syntax highlighting...")
    
    try:
        import json
        
        # Test DEX highlighting config
        dex_highlight_file = Path(__file__).parent.parent / 'src' / 'editors' / 'highlight' / 'dex.json'
        if dex_highlight_file.exists():
            with open(dex_highlight_file, 'r') as f:
                dex_config = json.load(f)
            print("✓ DEX syntax highlighting config loaded")
            print(f"  - Name: {dex_config.get('name')}")
            print(f"  - Extensions: {dex_config.get('extensions')}")
            print(f"  - Rules count: {len(dex_config.get('rules', []))}")
        else:
            print("✗ DEX syntax highlighting config not found")
        
        # Test Smali highlighting config
        smali_highlight_file = Path(__file__).parent.parent / 'src' / 'editors' / 'highlight' / 'smali.json'
        if smali_highlight_file.exists():
            with open(smali_highlight_file, 'r') as f:
                smali_config = json.load(f)
            print("✓ Smali syntax highlighting config loaded")
            print(f"  - Name: {smali_config.get('name')}")
            print(f"  - Extensions: {smali_config.get('extensions')}")
            print(f"  - Rules count: {len(smali_config.get('rules', []))}")
        else:
            print("✗ Smali syntax highlighting config not found")
        
        print("✓ Syntax highlighting tests completed")
        
    except Exception as e:
        print(f"✗ Syntax highlighting test failed: {e}")

def main():
    """Run all tests"""
    print("=== DEX Editor Test Suite ===\n")
    
    test_file_utils()
    test_dex_parser()
    test_dex_tools()
    test_syntax_highlighting()
    test_dex_editor_widget()
    
    print("\n=== Test Suite Complete ===")

if __name__ == '__main__':
    main()
