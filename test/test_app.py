#!/usr/bin/env python3
"""
Test script for MT Manager Linux
"""
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.main_window import MainWindow
        print("✓ MainWindow imported successfully")
    except Exception as e:
        print(f"✗ MainWindow import failed: {e}")
        return False
    
    try:
        from src.file_manager.dual_pane import DualPaneManager
        print("✓ DualPaneManager imported successfully")
    except Exception as e:
        print(f"✗ DualPaneManager import failed: {e}")
        return False
    
    try:
        from src.editors.text_editor import TextEditorWidget
        print("✓ TextEditorWidget imported successfully")
    except Exception as e:
        print(f"✗ TextEditorWidget import failed: {e}")
        return False
    
    try:
        from src.tools.apktool import ApkToolWidget
        print("✓ ApkToolWidget imported successfully")
    except Exception as e:
        print(f"✗ ApkToolWidget import failed: {e}")
        return False
    
    try:
        from src.tools.archive_manager import ArchiveViewer
        print("✓ ArchiveViewer imported successfully")
    except Exception as e:
        print(f"✗ ArchiveViewer import failed: {e}")
        return False
    
    try:
        from src.utils.config import config
        print("✓ Config imported successfully")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    try:
        from src.utils.file_utils import FileUtils
        print("✓ FileUtils imported successfully")
    except Exception as e:
        print(f"✗ FileUtils import failed: {e}")
        return False
    
    return True

def test_file_utils():
    """Test file utility functions"""
    print("\nTesting file utilities...")
    
    try:
        from src.utils.file_utils import FileUtils
        
        # Test file size formatting
        size_str = FileUtils.get_file_size_str(1024)
        assert size_str == "1.0 KB", f"Expected '1.0 KB', got '{size_str}'"
        print("✓ File size formatting works")
        
        # Test file type detection
        icon_type = FileUtils.get_file_icon_type("/test/file.apk")
        assert icon_type == "apk", f"Expected 'apk', got '{icon_type}'"
        print("✓ APK file type detection works")
        
        icon_type = FileUtils.get_file_icon_type("/test/file.txt")
        assert icon_type == "text", f"Expected 'text', got '{icon_type}'"
        print("✓ Text file type detection works")
        
        # Test APK detection
        is_apk = FileUtils.is_apk_file("/test/file.apk")
        assert is_apk == True, "APK detection failed"
        print("✓ APK file detection works")
        
        return True
        
    except Exception as e:
        print(f"✗ File utils test failed: {e}")
        return False

def test_config():
    """Test configuration management"""
    print("\nTesting configuration...")
    
    try:
        from src.utils.config import config
        
        # Test setting and getting values
        config.set('test_key', 'test_value')
        value = config.get('test_key')
        assert value == 'test_value', f"Expected 'test_value', got '{value}'"
        print("✓ Config set/get works")
        
        # Test default values
        default_value = config.get('nonexistent_key', 'default')
        assert default_value == 'default', f"Expected 'default', got '{default_value}'"
        print("✓ Config default values work")
        
        return True
        
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False

def test_syntax_highlighter():
    """Test syntax highlighter"""
    print("\nTesting syntax highlighter...")
    
    try:
        from PyQt5.QtWidgets import QApplication, QTextEdit
        from PyQt5.QtCore import Qt
        from src.editors.syntax_highlighter import SmaliSyntaxHighlighter, JavaSyntaxHighlighter
        
        # Create minimal QApplication for testing
        if not QApplication.instance():
            app = QApplication([])
        
        # Test Smali highlighter
        text_edit = QTextEdit()
        highlighter = SmaliSyntaxHighlighter(text_edit.document())
        print("✓ Smali syntax highlighter created")
        
        # Test Java highlighter
        java_highlighter = JavaSyntaxHighlighter(text_edit.document())
        print("✓ Java syntax highlighter created")
        
        return True
        
    except Exception as e:
        print(f"✗ Syntax highlighter test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("MT Manager Linux - Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_file_utils,
        test_config,
        test_syntax_highlighter
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
