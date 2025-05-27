#!/usr/bin/env python3
"""
GP Manager Setup Script
Handles dependency installation and system setup
"""
import sys
import os
import argparse
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True


def run_gui_installer():
    """Run GUI installation wizard"""
    try:
        from PyQt5.QtWidgets import QApplication
        from src.ui.install_wizard import InstallWizard

        app = QApplication(sys.argv)
        wizard = InstallWizard()
        wizard.show()
        return app.exec_()

    except ImportError:
        print("PyQt5 not available. Please install it first:")
        print("sudo apt install python3-pyqt5")
        return 1


def run_cli_installer(args):
    """Run command-line installation"""
    try:
        from src.utils.system_installer import SystemInstaller

        installer = SystemInstaller()

        if args.check:
            print("Checking dependencies...")
            status = installer.check_all_dependencies()

            print("\nDependency Status:")
            print("=" * 50)

            for dep_name, dep_status in status.items():
                status_symbol = "✓" if dep_status['installed'] else "✗"
                print(f"{status_symbol} {dep_name}: {dep_status['description']}")

            missing = [name for name, status in status.items() if not status['installed']]
            if missing:
                print(f"\nMissing dependencies: {len(missing)}")
                return 1
            else:
                print("\nAll dependencies are installed!")
                return 0

        elif args.install:
            print("Installing missing dependencies...")
            results = installer.install_missing_dependencies(
                interactive=True,
                skip_optional=args.skip_optional
            )

            print("\nInstallation Results:")
            print("=" * 50)

            for dep_name, (success, message) in results.items():
                status_symbol = "✓" if success else "✗"
                print(f"{status_symbol} {dep_name}: {message}")

            failed = sum(1 for success, _ in results.values() if not success)
            if failed > 0:
                print(f"\n{failed} installations failed.")
                return 1
            else:
                print("\nAll installations successful!")
                return 0

        elif args.script:
            print("Generating installation script...")
            script = installer.get_installation_script()

            if args.output:
                with open(args.output, 'w') as f:
                    f.write(script)
                print(f"Installation script saved to: {args.output}")
            else:
                print("\nInstallation Script:")
                print("=" * 50)
                print(script)

            return 0

        else:
            print("No action specified. Use --help for options.")
            return 1

    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Some dependencies may be missing.")
        return 1


def create_desktop_entry():
    """Create desktop entry for the application"""
    desktop_dir = Path.home() / '.local' / 'share' / 'applications'
    desktop_dir.mkdir(parents=True, exist_ok=True)

    app_dir = Path(__file__).parent.absolute()
    desktop_file = desktop_dir / 'gpmanager.desktop'

    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=GP Manager
Comment=Dual-pane file manager with APK tools
Exec={app_dir}/run.sh
Icon=folder-manager
Terminal=false
Categories=System;FileManager;
Keywords=file;manager;apk;android;decompile;
StartupNotify=true
MimeType=application/vnd.android.package-archive;
"""

    with open(desktop_file, 'w') as f:
        f.write(desktop_content)

    desktop_file.chmod(0o755)
    print(f"Desktop entry created: {desktop_file}")


def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(
        description="GP Manager Setup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 setup.py --gui                    # Run GUI installer
  python3 setup.py --check                  # Check dependency status
  python3 setup.py --install                # Install missing dependencies
  python3 setup.py --install --skip-optional # Install only required dependencies
  python3 setup.py --script                 # Generate installation script
  python3 setup.py --script -o install.sh   # Save script to file
  python3 setup.py --desktop                # Create desktop entry
        """
    )

    parser.add_argument('--gui', action='store_true',
                       help='Run GUI installation wizard')
    parser.add_argument('--check', action='store_true',
                       help='Check dependency status')
    parser.add_argument('--install', action='store_true',
                       help='Install missing dependencies')
    parser.add_argument('--script', action='store_true',
                       help='Generate installation script')
    parser.add_argument('--desktop', action='store_true',
                       help='Create desktop entry')
    parser.add_argument('--skip-optional', action='store_true',
                       help='Skip optional dependencies (APKTool, Java, Git)')
    parser.add_argument('-o', '--output', type=str,
                       help='Output file for generated script')

    args = parser.parse_args()

    # Check Python version
    if not check_python_version():
        return 1

    # If no arguments, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    # Handle desktop entry creation
    if args.desktop:
        try:
            create_desktop_entry()
            return 0
        except Exception as e:
            print(f"Error creating desktop entry: {e}")
            return 1

    # Handle GUI installer
    if args.gui:
        return run_gui_installer()

    # Handle CLI operations
    return run_cli_installer(args)


if __name__ == "__main__":
    sys.exit(main())
