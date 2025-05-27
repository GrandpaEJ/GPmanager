"""
System dependency installer for GP Manager
Supports multiple package managers and installation methods
"""
import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
from urllib.request import urlretrieve
import tempfile


class SystemInstaller:
    """Handles automatic installation of system dependencies"""

    def __init__(self):
        self.system = platform.system().lower()
        self.distro = self._detect_distro()
        self.package_manager = self._detect_package_manager()
        self.dependencies = {
            'python3-pyqt5': {
                'description': 'PyQt5 GUI framework',
                'check_command': ['python3', '-c', 'import PyQt5'],
                'install_methods': {
                    'apt': ['python3-pyqt5', 'python3-pyqt5.qtwidgets'],
                    'dnf': ['python3-qt5'],
                    'pacman': ['python-pyqt5'],
                    'zypper': ['python3-qt5'],
                    'pip': ['PyQt5>=5.15.0']
                }
            },
            'python3-pyqt5.qsci': {
                'description': 'QScintilla for PyQt5 (text editor component)',
                'check_command': ['python3', '-c', 'import PyQt5.Qsci'],
                'install_methods': {
                    'apt': ['python3-pyqt5.qsci'],
                    'dnf': ['qscintilla-python3'],
                    'pacman': ['qscintilla-python'],
                    'zypper': ['python3-QScintilla'],
                    'pip': ['QScintilla>=2.13.0']
                }
            },
            'python3-pygments': {
                'description': 'Syntax highlighting library',
                'check_command': ['python3', '-c', 'import pygments'],
                'install_methods': {
                    'apt': ['python3-pygments'],
                    'dnf': ['python3-pygments'],
                    'pacman': ['python-pygments'],
                    'zypper': ['python3-Pygments'],
                    'pip': ['Pygments>=2.10.0']
                }
            },
            'python3-magic': {
                'description': 'File type detection library',
                'check_command': ['python3', '-c', 'import magic'],
                'install_methods': {
                    'apt': ['python3-magic'],
                    'dnf': ['python3-magic'],
                    'pacman': ['python-magic'],
                    'zypper': ['python3-python-magic'],
                    'pip': ['python-magic>=0.4.24']
                }
            },
            'apktool': {
                'description': 'APK decompilation tool',
                'check_command': ['apktool', '--version'],
                'install_methods': {
                    'apt': ['apktool'],
                    'dnf': ['apktool'],
                    'pacman': ['apktool'],
                    'zypper': ['apktool'],
                    'manual': self._install_apktool_manual
                }
            },
            'java': {
                'description': 'Java Runtime Environment',
                'check_command': ['java', '-version'],
                'install_methods': {
                    'apt': ['default-jdk'],
                    'dnf': ['java-11-openjdk-devel'],
                    'pacman': ['jdk-openjdk'],
                    'zypper': ['java-11-openjdk-devel'],
                    'snap': ['openjdk']
                }
            },
            'git': {
                'description': 'Version control system',
                'check_command': ['git', '--version'],
                'install_methods': {
                    'apt': ['git'],
                    'dnf': ['git'],
                    'pacman': ['git'],
                    'zypper': ['git'],
                    'snap': ['git']
                }
            }
        }

    def _detect_distro(self):
        """Detect Linux distribution"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if 'ubuntu' in content or 'debian' in content:
                    return 'debian'
                elif 'fedora' in content or 'rhel' in content or 'centos' in content:
                    return 'fedora'
                elif 'arch' in content or 'manjaro' in content:
                    return 'arch'
                elif 'opensuse' in content or 'suse' in content:
                    return 'opensuse'
        except:
            pass
        return 'unknown'

    def _detect_package_manager(self):
        """Detect available package manager"""
        managers = ['apt', 'dnf', 'yum', 'pacman', 'zypper', 'snap', 'flatpak']
        for manager in managers:
            if shutil.which(manager):
                return manager
        return None

    def check_dependency(self, dep_name):
        """Check if a dependency is installed"""
        if dep_name not in self.dependencies:
            return False

        check_cmd = self.dependencies[dep_name]['check_command']
        try:
            result = subprocess.run(
                check_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False

    def install_dependency(self, dep_name, method=None, interactive=True):
        """Install a dependency using specified method or auto-detect"""
        if dep_name not in self.dependencies:
            return False, f"Unknown dependency: {dep_name}"

        dep_info = self.dependencies[dep_name]
        install_methods = dep_info['install_methods']

        # If method not specified, try to auto-detect best method
        if method is None:
            if self.package_manager in install_methods:
                method = self.package_manager
            elif 'manual' in install_methods:
                method = 'manual'
            elif 'pip' in install_methods:
                method = 'pip'
            else:
                return False, f"No installation method available for {dep_name}"

        if method not in install_methods:
            return False, f"Installation method '{method}' not available for {dep_name}"

        # Get installation command/function
        install_target = install_methods[method]

        if method == 'manual':
            # Call manual installation function
            return install_target()
        elif method == 'pip':
            return self._install_with_pip(install_target)
        else:
            # Use system package manager
            return self._install_with_package_manager(method, install_target, interactive)

    def _install_with_package_manager(self, manager, packages, interactive=True):
        """Install packages using system package manager"""
        if isinstance(packages, str):
            packages = [packages]

        # Build installation command
        if manager == 'apt':
            cmd = ['sudo', 'apt', 'update', '&&', 'sudo', 'apt', 'install', '-y'] + packages
        elif manager == 'dnf':
            cmd = ['sudo', 'dnf', 'install', '-y'] + packages
        elif manager == 'yum':
            cmd = ['sudo', 'yum', 'install', '-y'] + packages
        elif manager == 'pacman':
            cmd = ['sudo', 'pacman', '-S', '--noconfirm'] + packages
        elif manager == 'zypper':
            cmd = ['sudo', 'zypper', 'install', '-y'] + packages
        elif manager == 'snap':
            cmd = ['sudo', 'snap', 'install'] + packages
        else:
            return False, f"Unsupported package manager: {manager}"

        try:
            if interactive:
                print(f"Installing {packages} using {manager}...")
                print(f"Command: {' '.join(cmd)}")

            # For apt, we need to run update and install separately
            if manager == 'apt':
                subprocess.run(['sudo', 'apt', 'update'], check=True)
                result = subprocess.run(['sudo', 'apt', 'install', '-y'] + packages, check=True)
            else:
                result = subprocess.run(cmd, check=True)

            return True, f"Successfully installed {packages}"

        except subprocess.CalledProcessError as e:
            return False, f"Installation failed: {e}"
        except Exception as e:
            return False, f"Installation error: {e}"

    def _install_with_pip(self, packages):
        """Install packages using pip"""
        if isinstance(packages, str):
            packages = [packages]

        try:
            # Try pip3 first, then pip
            pip_cmd = 'pip3' if shutil.which('pip3') else 'pip'

            # Check if we can install without --break-system-packages
            try:
                cmd = [pip_cmd, 'install'] + packages
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                return True, f"Successfully installed {packages} with pip"
            except subprocess.CalledProcessError:
                # Try with --break-system-packages flag
                cmd = [pip_cmd, 'install', '--break-system-packages'] + packages
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                return True, f"Successfully installed {packages} with pip (--break-system-packages)"

        except subprocess.CalledProcessError as e:
            return False, f"Pip installation failed: {e}"
        except Exception as e:
            return False, f"Pip installation error: {e}"

    def _install_apktool_manual(self):
        """Manually install APKTool"""
        try:
            # Create local bin directory
            local_bin = Path.home() / '.local' / 'bin'
            local_bin.mkdir(parents=True, exist_ok=True)

            # Download APKTool
            apktool_url = "https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool"
            apktool_jar_url = "https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.8.1.jar"

            print("Downloading APKTool...")

            # Download wrapper script
            apktool_script = local_bin / 'apktool'
            urlretrieve(apktool_url, str(apktool_script))
            apktool_script.chmod(0o755)

            # Download JAR file
            apktool_jar = local_bin / 'apktool.jar'
            urlretrieve(apktool_jar_url, str(apktool_jar))

            # Add to PATH if not already there
            bashrc = Path.home() / '.bashrc'
            path_line = f'export PATH="$HOME/.local/bin:$PATH"'

            if bashrc.exists():
                with open(bashrc, 'r') as f:
                    content = f.read()
                if path_line not in content:
                    with open(bashrc, 'a') as f:
                        f.write(f'\n# Added by MT Manager Linux\n{path_line}\n')

            return True, "APKTool installed manually to ~/.local/bin"

        except Exception as e:
            return False, f"Manual APKTool installation failed: {e}"

    def check_all_dependencies(self):
        """Check status of all dependencies"""
        status = {}
        for dep_name in self.dependencies:
            status[dep_name] = {
                'installed': self.check_dependency(dep_name),
                'description': self.dependencies[dep_name]['description']
            }
        return status

    def install_missing_dependencies(self, interactive=True, skip_optional=False):
        """Install all missing dependencies"""
        optional_deps = ['apktool', 'java', 'git']
        status = self.check_all_dependencies()
        results = {}

        for dep_name, dep_status in status.items():
            if dep_status['installed']:
                results[dep_name] = (True, "Already installed")
                continue

            if skip_optional and dep_name in optional_deps:
                results[dep_name] = (False, "Skipped (optional)")
                continue

            if interactive:
                print(f"\nInstalling {dep_name}: {dep_status['description']}")

            success, message = self.install_dependency(dep_name, interactive=interactive)
            results[dep_name] = (success, message)

            if interactive:
                if success:
                    print(f"✓ {message}")
                else:
                    print(f"✗ {message}")

        return results

    def get_installation_script(self):
        """Generate installation script for manual execution"""
        script_lines = [
            "#!/bin/bash",
            "# MT Manager Linux - Dependency Installation Script",
            "# Generated automatically",
            "",
            "set -e",
            "",
            "echo 'Installing MT Manager Linux dependencies...'",
            ""
        ]

        if self.package_manager == 'apt':
            script_lines.extend([
                "# Update package list",
                "sudo apt update",
                "",
                "# Install Python dependencies",
                "sudo apt install -y python3-pyqt5 python3-pyqt5.qsci python3-pygments python3-magic",
                "",
                "# Install optional tools",
                "sudo apt install -y apktool default-jdk git",
                ""
            ])
        elif self.package_manager == 'dnf':
            script_lines.extend([
                "# Install Python dependencies",
                "sudo dnf install -y python3-qt5 qscintilla-python3 python3-pygments python3-magic",
                "",
                "# Install optional tools",
                "sudo dnf install -y apktool java-11-openjdk-devel git",
                ""
            ])
        elif self.package_manager == 'pacman':
            script_lines.extend([
                "# Install Python dependencies",
                "sudo pacman -S --noconfirm python-pyqt5 qscintilla-python python-pygments python-magic",
                "",
                "# Install optional tools",
                "sudo pacman -S --noconfirm apktool jdk-openjdk git",
                ""
            ])

        script_lines.extend([
            "echo 'Installation completed!'",
            "echo 'You can now run GP Manager with: python3 main.py'"
        ])

        return '\n'.join(script_lines)
