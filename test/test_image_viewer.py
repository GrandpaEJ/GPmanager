#!/usr/bin/env python3
"""
Test script for the Image Viewer component
"""
import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from viewers.image_viewer import ImageViewer


class TestWindow(QMainWindow):
    """Test window for image viewer"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Viewer Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Open button
        open_btn = QPushButton("Open Image")
        open_btn.clicked.connect(self.open_image)
        layout.addWidget(open_btn)
        
        # Image viewer
        self.image_viewer = ImageViewer()
        layout.addWidget(self.image_viewer)
    
    def open_image(self):
        """Open image file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp *.tiff *.ico);;All Files (*)"
        )
        if file_path:
            self.image_viewer.load_image(file_path)


def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Apply dark theme
    app.setStyleSheet("""
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QPushButton {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
        }
        QPushButton:pressed {
            background-color: #2a2a2a;
        }
    """)
    
    window = TestWindow()
    window.show()
    
    # Try to load a test image if available
    test_images = [
        "/usr/share/pixmaps/python3.png",
        "/usr/share/icons/hicolor/48x48/apps/firefox.png",
        "/usr/share/pixmaps/debian-logo.png"
    ]
    
    for test_image in test_images:
        if Path(test_image).exists():
            print(f"Loading test image: {test_image}")
            window.image_viewer.load_image(test_image)
            break
    else:
        print("No test images found. Use the 'Open Image' button to load an image.")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
