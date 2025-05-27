#!/usr/bin/env python3
"""
Debug script to test image file detection
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.file_utils import FileUtils

def test_image_detection():
    """Test image file detection"""
    
    # Test cases
    test_files = [
        "test.jpg",
        "test.jpeg", 
        "test.png",
        "test.gif",
        "test.bmp",
        "test.svg",
        "test.webp",
        "test.tiff",
        "test.ico",
        "1000_F_945209778_QNLukvfcQL0kkcCIajN1FYCHb12pKUfv.jpg",  # The file from the screenshot
        "test.txt",
        "test.apk",
        "test.zip"
    ]
    
    print("Testing image file detection:")
    print("=" * 50)
    
    for test_file in test_files:
        is_image = FileUtils.is_image_file(test_file)
        is_apk = FileUtils.is_apk_file(test_file)
        is_archive = FileUtils.is_archive_file(test_file)
        is_text = FileUtils.is_text_file(test_file)
        
        print(f"{test_file:<50} | Image: {is_image:<5} | APK: {is_apk:<5} | Archive: {is_archive:<5} | Text: {is_text}")
    
    print("\n" + "=" * 50)
    
    # Test the specific file from the screenshot
    specific_file = "1000_F_945209778_QNLukvfcQL0kkcCIajN1FYCHb12pKUfv.jpg"
    print(f"\nSpecific test for: {specific_file}")
    print(f"Extension: {Path(specific_file).suffix}")
    print(f"Extension lower: {Path(specific_file).suffix.lower()}")
    print(f"Is image: {FileUtils.is_image_file(specific_file)}")
    
    # Test extension detection
    ext = Path(specific_file).suffix.lower()
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff', '.ico']
    print(f"Extension '{ext}' in image_extensions: {ext in image_extensions}")

if __name__ == "__main__":
    test_image_detection()
