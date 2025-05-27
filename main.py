#!/usr/bin/env python3
"""
GP Manager - A dual-pane file manager with APK tools
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
    print(f"Error importing required modules: {e}")
    print("Please install the required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []

    try:
        import PyQt5
        _ = PyQt5  # Suppress unused import warning
    except ImportError:
        missing_deps.append("PyQt5")

    try:
        import pygments
        _ = pygments  # Suppress unused import warning
    except ImportError:
        missing_deps.append("Pygments")

    if missing_deps:
        print("Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nWould you like to run the setup wizard? (y/n): ", end="")

        try:
            response = input().lower().strip()
            if response in ['y', 'yes']:
                print("Starting setup wizard...")
                import subprocess
                result = subprocess.run([sys.executable, 'setup.py', '--gui'],
                                      cwd=Path(__file__).parent)
                if result.returncode == 0:
                    print("Setup completed. Please restart the application.")
                return False
        except (KeyboardInterrupt, EOFError):
            pass

        print("\nAlternatively, install them using:")
        print("python3 setup.py --install")
        print("or manually: sudo apt install python3-pyqt5 python3-pyqt5.qsci python3-pygments")
        return False

    return True


def setup_application():
    """Setup application properties"""
    # Enable high DPI scaling before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("GP Manager")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("GP Manager")
    app.setOrganizationDomain("gpmanager.local")

    return app


def main():
    """Main application entry point"""
    # Check dependencies
    if not check_dependencies():
        return 1

    # Create application
    app = setup_application()

    try:
        # Apply theme
        ThemeManager.apply_dark_theme(app)

        # Create and show main window
        from src.utils.config import config

        # Import MainWindow here to avoid issues
        from src.main_window import MainWindow

        if config.get('use_custom_titlebar', False):
            # Use custom frameless window with title bar
            try:
                from src.ui.title_bar import FramelessWindow

                # Create frameless window
                frameless_window = FramelessWindow()
                frameless_window.set_title("GP Manager")

                # Create main window content
                main_window_content = MainWindow()
                main_window_content.setParent(frameless_window)

                # Set content
                frameless_window.set_content_widget(main_window_content)

                # Connect title updates
                def update_title():
                    title = main_window_content.windowTitle()
                    frameless_window.set_title(title)

                main_window_content.windowTitleChanged.connect(update_title)

                window = frameless_window
            except ImportError:
                # Fallback to regular window
                window = MainWindow()
        else:
            # Use regular window with system title bar
            window = MainWindow()

        window.show()

        # Show welcome message on first run
        if not config.config_file.exists():
            QMessageBox.information(
                window,
                "Welcome to GP Manager",
                "Welcome to GP Manager!\n\n"
                "This is a dual-pane file manager with APK tools integration.\n\n"
                "Features:\n"
                "• Dual-pane file browser\n"
                "• APK decompile/recompile with APKTool\n"
                "• Text editor with syntax highlighting\n"
                "• Archive viewer and extractor\n"
                "• Dark theme support\n\n"
                "You can configure the application in File → Preferences."
            )

        # Run application
        return app.exec_()

    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
