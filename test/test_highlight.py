#!/usr/bin/env python3
"""
Test script for syntax highlighting
"""

# Import statements
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

try:
    from PyQt5.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    from src.editors.json_highlighter import highlighter_manager
    
    class HighlightTestWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Syntax Highlighting Test")
            self.setGeometry(100, 100, 800, 600)
            
            layout = QVBoxLayout(self)
            
            # Create text editor
            self.text_edit = QTextEdit()
            self.text_edit.setFont(QFont("monospace", 12))
            layout.addWidget(self.text_edit)
            
            # Apply Python syntax highlighting
            self.highlighter = highlighter_manager.get_highlighter_for_file(
                "test.py", self.text_edit.document()
            )
            
            # Set test Python code
            test_code = '''#!/usr/bin/env python3
"""
MT Manager Linux - A dual-pane file manager with APK tools
Entry point for the application
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtCore import Qt
    from src.ui.themes import ThemeManager
except ImportError as e:
    print(f"Error importing PyQt5: {e}")
    sys.exit(1)

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Test different data types
    numbers = [1, 2.5, 0x1A, 0b1010, 0o777]
    text = "Hello, World!"
    f_string = f"Path: {src_path}"
    
    # Function definition
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    
    # Class definition
    class Calculator:
        def __init__(self):
            self.result = 0
        
        @property
        def value(self):
            return self.result
    
    # Usage
    calc = Calculator()
    result = fibonacci(10)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
'''
            
            self.text_edit.setPlainText(test_code)
            
            print("Syntax highlighting test window created")
            print(f"Highlighter: {self.highlighter}")
            if self.highlighter:
                print("✓ Python syntax highlighter loaded successfully")
            else:
                print("✗ Failed to load Python syntax highlighter")
    
    def main():
        app = QApplication(sys.argv)
        
        print("Testing syntax highlighting system...")
        
        # Test highlighter manager
        print(f"Supported languages: {highlighter_manager.get_supported_languages()}")
        print(f"Supported extensions: {highlighter_manager.get_supported_extensions()}")
        
        # Create test window
        window = HighlightTestWindow()
        window.show()
        
        return app.exec_()

except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure PyQt5 is installed and the application is properly set up")
    sys.exit(1)

if __name__ == "__main__":
    main()
