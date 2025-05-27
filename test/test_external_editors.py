#!/usr/bin/env python3
"""
Test external editor functionality for MT Manager Linux
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

try:
    from src.editors.external_editor import external_editor_manager
    
    def test_external_editors():
        """Test external editor detection and functionality"""
        print("Testing External Editor Functionality")
        print("=" * 50)
        
        # Get available editors
        available_editors = external_editor_manager.get_available_editors()
        print(f"Found {len(available_editors)} editors:")
        
        for editor in available_editors:
            status = "✓ Available" if editor.is_available() else "✗ Not found"
            print(f"  {status}: {editor.name}")
            print(f"    Command: {editor.command}")
            print(f"    Args: {editor.args}")
            print(f"    Extensions: {editor.extensions}")
            print(f"    Description: {editor.description}")
            print()
        
        # Test with a sample file
        test_file = Path(__file__).parent / "README.md"
        if not test_file.exists():
            # Create a test file
            test_file.write_text("# Test File\nThis is a test file for external editor testing.")
        
        print(f"Testing with file: {test_file}")
        print("-" * 30)
        
        # Get suitable editors for the test file
        suitable_editors = external_editor_manager.get_editors_for_file(str(test_file))
        print(f"Suitable editors for {test_file.name}: {len(suitable_editors)}")
        
        for editor in suitable_editors:
            if editor.is_available():
                print(f"  ✓ {editor.name} - Ready to use")
            else:
                print(f"  ✗ {editor.name} - Command not found")
        
        # Test opening with the first available editor (dry run)
        if suitable_editors:
            for editor in suitable_editors:
                if editor.is_available():
                    print(f"\nTesting {editor.name}:")
                    print(f"Would execute: {editor.command} {' '.join(editor.args).replace('{file}', str(test_file))}")
                    
                    # Test the actual opening (commented out to avoid opening editors during test)
                    # success, message = external_editor_manager.open_file(str(test_file), editor.name)
                    # print(f"Result: {message}")
                    break
        else:
            print("No suitable editors found for the test file")
        
        print("\nExternal Editor Test Complete!")
        
        # Test hex editor availability
        print("\nHex Editor Test:")
        print("-" * 20)
        
        # Check for common hex editors
        hex_editors = [
            ("hexedit", "Terminal hex editor"),
            ("ghex", "GNOME hex editor"),
            ("okteta", "KDE hex editor"),
            ("bless", "GTK hex editor"),
            ("xxd", "Command line hex dump")
        ]
        
        import shutil
        for cmd, desc in hex_editors:
            if shutil.which(cmd):
                print(f"  ✓ {cmd} - {desc}")
            else:
                print(f"  ✗ {cmd} - {desc} (not installed)")
        
        print("\nRecommendations:")
        print("- Install VS Code: sudo snap install code")
        print("- Install Vim: sudo apt install vim")
        print("- Install Nano: sudo apt install nano")
        print("- Install Hex editor: sudo apt install hexedit ghex")

    if __name__ == "__main__":
        test_external_editors()

except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure the application is properly set up")
    sys.exit(1)
