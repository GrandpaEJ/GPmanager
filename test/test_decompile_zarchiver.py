#!/usr/bin/env python3
"""
Test script for decompiling ZArchiver APK
Tests the APK decompile functionality with a real APK file
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox, QPushButton, QLabel, QTextEdit
    from PyQt5.QtCore import QTimer
    from src.tools.apktool import ApkToolWidget
    from src.ui.themes import ThemeManager
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install the required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)


class ZArchiverTestWindow(QMainWindow):
    """Test window for ZArchiver APK decompilation"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZArchiver APK Decompile Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # APK file path
        self.apk_path = "/home/grandpa/Downloads/ZArchiver_1.0.10_APKPure.apk"
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Info section
        info_label = QLabel(f"Testing APK Decompilation")
        info_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(info_label)
        
        # APK path info
        apk_info = QLabel(f"APK File: {self.apk_path}")
        apk_info.setStyleSheet("margin: 5px;")
        layout.addWidget(apk_info)
        
        # Check if APK exists
        if not Path(self.apk_path).exists():
            error_label = QLabel("❌ APK file not found!")
            error_label.setStyleSheet("color: red; font-weight: bold; margin: 10px;")
            layout.addWidget(error_label)
            
            # Show alternative path suggestion
            alt_label = QLabel("Please ensure the ZArchiver APK is at the specified path, or update the path in this script.")
            alt_label.setStyleSheet("margin: 10px;")
            layout.addWidget(alt_label)
        else:
            success_label = QLabel("✅ APK file found!")
            success_label.setStyleSheet("color: green; font-weight: bold; margin: 10px;")
            layout.addWidget(success_label)
        
        # Test buttons
        button_layout = QVBoxLayout()
        
        # Auto test button
        self.auto_test_btn = QPushButton("🚀 Start Automatic Decompile Test")
        self.auto_test_btn.setStyleSheet("padding: 10px; font-size: 14px; font-weight: bold;")
        self.auto_test_btn.clicked.connect(self.start_auto_test)
        button_layout.addWidget(self.auto_test_btn)
        
        # Manual test button
        self.manual_test_btn = QPushButton("🔧 Open APKTool Widget for Manual Testing")
        self.manual_test_btn.setStyleSheet("padding: 10px; font-size: 14px;")
        self.manual_test_btn.clicked.connect(self.start_manual_test)
        button_layout.addWidget(self.manual_test_btn)
        
        layout.addLayout(button_layout)
        
        # Results area
        self.results_text = QTextEdit()
        self.results_text.setPlaceholderText("Test results will appear here...")
        layout.addWidget(self.results_text)
        
        # APKTool widget (initially hidden)
        self.apktool_widget = None
        
    def log_message(self, message):
        """Add message to results"""
        self.results_text.append(f"[{self.get_timestamp()}] {message}")
        
    def get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
        
    def start_auto_test(self):
        """Start automatic decompile test"""
        if not Path(self.apk_path).exists():
            QMessageBox.warning(self, "APK Not Found", 
                              f"APK file not found at:\n{self.apk_path}\n\n"
                              "Please check the path and try again.")
            return
            
        self.log_message("🚀 Starting automatic decompile test...")
        self.log_message(f"📁 APK Path: {self.apk_path}")
        
        # Disable button during test
        self.auto_test_btn.setEnabled(False)
        self.auto_test_btn.setText("⏳ Testing in progress...")
        
        # Create APKTool widget if not exists
        if not self.apktool_widget:
            self.apktool_widget = ApkToolWidget()
            
        # Set the APK file
        try:
            self.log_message("📱 Loading APK in APKTool widget...")
            self.apktool_widget.set_apk_file(self.apk_path)
            self.log_message("✅ APK loaded successfully!")
            
            # Check dependencies
            self.log_message("🔍 Checking dependencies...")
            if hasattr(self.apktool_widget, 'dependencies_ok'):
                if self.apktool_widget.dependencies_ok:
                    self.log_message("✅ Dependencies are OK!")
                    self.start_decompile_process()
                else:
                    self.log_message("❌ Dependencies missing!")
                    self.log_message("💡 Please install dependencies using the Setup tab")
            else:
                self.log_message("⚠️ Cannot check dependencies status")
                
        except Exception as e:
            self.log_message(f"❌ Error loading APK: {str(e)}")
            
        # Re-enable button
        self.auto_test_btn.setEnabled(True)
        self.auto_test_btn.setText("🚀 Start Automatic Decompile Test")
        
    def start_decompile_process(self):
        """Start the actual decompile process"""
        try:
            self.log_message("🔨 Starting decompile process...")
            
            # Connect to APKTool signals for monitoring
            if hasattr(self.apktool_widget, 'current_worker'):
                worker = self.apktool_widget.current_worker
                if worker:
                    worker.operation_status.connect(self.on_operation_status)
                    worker.progress_percentage.connect(self.on_progress_update)
                    worker.output_received.connect(self.on_output_received)
                    worker.operation_finished.connect(self.on_operation_finished)
                    worker.operation_error.connect(self.on_operation_error)
            
            # Trigger decompile (this would normally be done through the UI)
            # For testing, we'll simulate the button click
            if hasattr(self.apktool_widget, 'decompile_btn'):
                self.log_message("🎯 Triggering decompile operation...")
                self.apktool_widget.decompile_btn.click()
            else:
                self.log_message("⚠️ Cannot find decompile button")
                
        except Exception as e:
            self.log_message(f"❌ Error starting decompile: {str(e)}")
    
    def on_operation_status(self, status):
        """Handle operation status updates"""
        self.log_message(f"📊 Status: {status}")
        
    def on_progress_update(self, percentage):
        """Handle progress updates"""
        self.log_message(f"📈 Progress: {percentage}%")
        
    def on_output_received(self, output):
        """Handle output from APKTool"""
        self.log_message(f"🔧 APKTool: {output}")
        
    def on_operation_finished(self, success, message):
        """Handle operation completion"""
        if success:
            self.log_message(f"✅ Decompile completed successfully!")
            self.log_message(f"📝 Result: {message}")
        else:
            self.log_message(f"❌ Decompile failed!")
            self.log_message(f"📝 Error: {message}")
            
    def on_operation_error(self, error):
        """Handle operation errors"""
        self.log_message(f"💥 Error: {error}")
        
    def start_manual_test(self):
        """Start manual test with APKTool widget"""
        if not Path(self.apk_path).exists():
            QMessageBox.warning(self, "APK Not Found", 
                              f"APK file not found at:\n{self.apk_path}\n\n"
                              "Please check the path and try again.")
            return
            
        self.log_message("🔧 Opening APKTool widget for manual testing...")
        
        # Create and show APKTool widget
        if not self.apktool_widget:
            self.apktool_widget = ApkToolWidget()
            
        # Set the APK file
        self.apktool_widget.set_apk_file(self.apk_path)
        
        # Show the widget
        self.apktool_widget.show()
        self.apktool_widget.raise_()
        self.apktool_widget.activateWindow()
        
        self.log_message("✅ APKTool widget opened!")
        self.log_message("💡 You can now manually test the decompile functionality")


def main():
    """Main test function"""
    app = QApplication(sys.argv)
    
    # Apply dark theme
    ThemeManager.apply_dark_theme(app)
    
    # Create test window
    window = ZArchiverTestWindow()
    window.show()
    
    print("ZArchiver APK Decompile Test Started")
    print("=" * 50)
    print("APK File: /home/grandpa/Downloads/ZArchiver_1.0.10_APKPure.apk")
    print("=" * 50)
    print("Instructions:")
    print("1. Click 'Start Automatic Decompile Test' for automated testing")
    print("2. Click 'Open APKTool Widget' for manual testing")
    print("3. Watch the results area for progress and status updates")
    print("=" * 50)
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
