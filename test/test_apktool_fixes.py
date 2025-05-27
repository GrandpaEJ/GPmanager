#!/usr/bin/env python3
"""
Test script for APKTool fixes
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    from src.tools.apktool import ApkToolWidget
    from src.ui.themes import ThemeManager
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install the required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)


class TestWindow(QMainWindow):
    """Test window for APKTool widget"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("APKTool Test - Decompile & Progress Fixes")
        self.setGeometry(100, 100, 1000, 700)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)

        # Create APKTool widget
        self.apktool_widget = ApkToolWidget()
        layout.addWidget(self.apktool_widget)


def main():
    """Main test function"""
    app = QApplication(sys.argv)

    # Apply dark theme
    ThemeManager.apply_dark_theme(app)

    # Create test window
    window = TestWindow()
    window.show()

    print("APKTool Test Window Started")
    print("=" * 50)
    print("Test Instructions:")
    print("1. Go to the Setup tab and check dependencies")
    print("2. Install missing dependencies if needed")
    print("3. Go to Operations tab and test decompile")
    print("4. Check progress bar and log window functionality")
    print("5. Test the detailed logs window")
    print("=" * 50)

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
