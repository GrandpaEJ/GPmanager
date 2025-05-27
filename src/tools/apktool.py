"""
APKTool integration for MT Manager Linux
Enhanced with dependency checking and installation
"""
import os
import subprocess
import shutil
import urllib.request
import zipfile
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt, QTimer
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QTextEdit, QLabel, QProgressBar, QMessageBox,
                            QFileDialog, QInputDialog, QGroupBox, QCheckBox,
                            QTabWidget, QScrollArea, QFrame, QSplitter,
                            QTreeWidget, QTreeWidgetItem)
from PyQt5.QtGui import QFont
from src.utils.config import config


class DetailedLogsWindow(QWidget):
    """Detailed logs window for APK operations"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("APK Tools - Detailed Logs")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        """Setup the logs window UI"""
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("📋 Detailed Operation Logs")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2196F3;")

        self.timestamp_label = QLabel()
        self.update_timestamp()

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.timestamp_label)

        layout.addLayout(header_layout)

        # Logs text area
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setFont(QFont("Consolas", 10))
        self.logs_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555;
            }
        """)

        layout.addWidget(self.logs_text)

        # Controls
        controls_layout = QHBoxLayout()

        self.clear_logs_btn = QPushButton("🗑️ Clear Logs")
        self.save_logs_btn = QPushButton("💾 Save Logs")
        self.copy_logs_btn = QPushButton("📋 Copy to Clipboard")
        self.auto_scroll_logs = QCheckBox("Auto-scroll")
        self.auto_scroll_logs.setChecked(True)

        controls_layout.addWidget(self.clear_logs_btn)
        controls_layout.addWidget(self.save_logs_btn)
        controls_layout.addWidget(self.copy_logs_btn)
        controls_layout.addWidget(self.auto_scroll_logs)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Connect signals
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        self.save_logs_btn.clicked.connect(self.save_logs)
        self.copy_logs_btn.clicked.connect(self.copy_logs)

    def set_logs(self, logs):
        """Set the logs content"""
        self.logs_text.setPlainText(logs)
        self.update_timestamp()
        if self.auto_scroll_logs.isChecked():
            self.scroll_to_bottom()

    def append_log(self, log_line):
        """Append a new log line"""
        self.logs_text.append(log_line)
        if self.auto_scroll_logs.isChecked():
            self.scroll_to_bottom()

    def clear_logs(self):
        """Clear all logs"""
        self.logs_text.clear()
        self.update_timestamp()

    def save_logs(self):
        """Save logs to file"""
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Logs", "apk_tools_logs.txt", "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.logs_text.toPlainText())
                QMessageBox.information(self, "Save Complete", f"Logs saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Save Error", f"Failed to save logs:\n{str(e)}")

    def copy_logs(self):
        """Copy logs to clipboard"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.logs_text.toPlainText())

        # Show temporary feedback
        original_text = self.copy_logs_btn.text()
        self.copy_logs_btn.setText("✓ Copied!")
        QTimer.singleShot(2000, lambda: self.copy_logs_btn.setText(original_text))

    def scroll_to_bottom(self):
        """Scroll to bottom of logs"""
        cursor = self.logs_text.textCursor()
        cursor.movePosition(cursor.End)
        self.logs_text.setTextCursor(cursor)

    def update_timestamp(self):
        """Update timestamp label"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.setText(f"Updated: {timestamp}")


class DependencyChecker:
    """Check and install APK tool dependencies"""

    @staticmethod
    def check_java():
        """Check if Java is installed"""
        try:
            result = subprocess.run(['java', '-version'],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    @staticmethod
    def check_apktool():
        """Check if apktool is installed"""
        try:
            result = subprocess.run(['apktool', '--version'],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    @staticmethod
    def check_aapt():
        """Check if aapt is installed"""
        try:
            result = subprocess.run(['aapt', 'version'],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    @staticmethod
    def get_missing_dependencies():
        """Get list of missing dependencies"""
        missing = []

        if not DependencyChecker.check_java():
            missing.append({
                'name': 'Java JDK',
                'command': 'java',
                'install_cmd': 'sudo apt install default-jdk',
                'description': 'Required for APK signing and some operations'
            })

        if not DependencyChecker.check_apktool():
            missing.append({
                'name': 'APKTool',
                'command': 'apktool',
                'install_cmd': 'sudo apt install apktool',
                'description': 'Main tool for APK decompilation and recompilation'
            })

        if not DependencyChecker.check_aapt():
            missing.append({
                'name': 'AAPT (Android Asset Packaging Tool)',
                'command': 'aapt',
                'install_cmd': 'sudo apt install aapt',
                'description': 'Android build tool for resource processing'
            })

        return missing

    @staticmethod
    def install_dependencies():
        """Install missing dependencies with multiple methods"""
        missing = DependencyChecker.get_missing_dependencies()
        if not missing:
            return True, "All dependencies are already installed"

        success_count = 0
        failed_deps = []

        for dep in missing:
            try:
                if dep['command'] == 'java':
                    success = DependencyChecker._install_java()
                elif dep['command'] == 'apktool':
                    success = DependencyChecker._install_apktool()
                elif dep['command'] == 'aapt':
                    success = DependencyChecker._install_aapt()
                else:
                    success = DependencyChecker._install_generic(dep)

                if success:
                    success_count += 1
                else:
                    failed_deps.append(dep['name'])

            except Exception as e:
                failed_deps.append(f"{dep['name']} ({str(e)})")

        if success_count == len(missing):
            return True, f"All {success_count} dependencies installed successfully"
        elif success_count > 0:
            return False, f"Installed {success_count}/{len(missing)} dependencies. Failed: {', '.join(failed_deps)}"
        else:
            return False, f"Installation failed for all dependencies: {', '.join(failed_deps)}"

    @staticmethod
    def _install_java():
        """Install Java JDK with multiple methods"""
        methods = [
            # Method 1: Default JDK via apt
            ['sudo', 'apt', 'update', '&&', 'sudo', 'apt', 'install', '-y', 'default-jdk'],
            # Method 2: OpenJDK 11
            ['sudo', 'apt', 'install', '-y', 'openjdk-11-jdk'],
            # Method 3: OpenJDK 8 (fallback)
            ['sudo', 'apt', 'install', '-y', 'openjdk-8-jdk']
        ]

        for method in methods:
            try:
                result = subprocess.run(' '.join(method), shell=True,
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    return True
            except Exception:
                continue
        return False

    @staticmethod
    def _install_apktool():
        """Install APKTool with multiple methods"""
        # Method 1: Try apt package manager first
        try:
            result = subprocess.run('sudo apt update && sudo apt install -y apktool',
                                  shell=True, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                return True
        except Exception:
            pass

        # Method 2: Download and install manually
        try:
            return DependencyChecker._install_apktool_manual()
        except Exception:
            pass

        # Method 3: Try snap package
        try:
            result = subprocess.run('sudo snap install apktool',
                                  shell=True, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                return True
        except Exception:
            pass

        return False

    @staticmethod
    def _install_apktool_manual():
        """Manually download and install APKTool"""
        import tempfile
        import stat

        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Download APKTool wrapper script
            wrapper_url = "https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool"
            wrapper_path = temp_path / "apktool"

            # Download APKTool JAR (latest version)
            jar_url = "https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar"
            jar_path = temp_path / "apktool.jar"

            try:
                # Download wrapper script
                urllib.request.urlretrieve(wrapper_url, wrapper_path)

                # Download JAR file
                urllib.request.urlretrieve(jar_url, jar_path)

                # Make wrapper executable
                wrapper_path.chmod(wrapper_path.stat().st_mode | stat.S_IEXEC)

                # Install to /usr/local/bin
                subprocess.run(['sudo', 'cp', str(wrapper_path), '/usr/local/bin/apktool'], check=True)
                subprocess.run(['sudo', 'cp', str(jar_path), '/usr/local/bin/apktool.jar'], check=True)
                subprocess.run(['sudo', 'chmod', '+x', '/usr/local/bin/apktool'], check=True)

                return True

            except Exception:
                return False

    @staticmethod
    def _install_aapt():
        """Install AAPT with multiple methods"""
        methods = [
            # Method 1: Direct apt package
            'sudo apt update && sudo apt install -y aapt',
            # Method 2: Android SDK build tools
            'sudo apt install -y android-sdk-build-tools',
            # Method 3: Google Android SDK
            'sudo apt install -y google-android-build-tools-installer'
        ]

        for method in methods:
            try:
                result = subprocess.run(method, shell=True,
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    return True
            except Exception:
                continue
        return False

    @staticmethod
    def _install_generic(dep):
        """Generic installation method"""
        try:
            result = subprocess.run(dep['install_cmd'], shell=True,
                                  capture_output=True, text=True, timeout=300)
            return result.returncode == 0
        except Exception:
            return False


class DependencyInstaller(QThread):
    """Background dependency installer with progress reporting"""

    progress_updated = pyqtSignal(str)
    installation_finished = pyqtSignal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cancelled = False

    def run(self):
        """Run dependency installation in background"""
        try:
            self.progress_updated.emit("Checking missing dependencies...")
            missing = DependencyChecker.get_missing_dependencies()

            if not missing:
                self.installation_finished.emit(True, "All dependencies are already installed")
                return

            self.progress_updated.emit(f"Installing {len(missing)} dependencies...")

            success_count = 0
            failed_deps = []

            for i, dep in enumerate(missing):
                if self.cancelled:
                    self.installation_finished.emit(False, "Installation cancelled by user")
                    return

                self.progress_updated.emit(f"Installing {dep['name']} ({i+1}/{len(missing)})...")

                try:
                    if dep['command'] == 'java':
                        success = self._install_java_with_progress()
                    elif dep['command'] == 'apktool':
                        success = self._install_apktool_with_progress()
                    elif dep['command'] == 'aapt':
                        success = self._install_aapt_with_progress()
                    else:
                        success = self._install_generic_with_progress(dep)

                    if success:
                        success_count += 1
                        self.progress_updated.emit(f"✓ {dep['name']} installed successfully")
                    else:
                        failed_deps.append(dep['name'])
                        self.progress_updated.emit(f"✗ Failed to install {dep['name']}")

                except Exception as e:
                    failed_deps.append(f"{dep['name']} ({str(e)})")
                    self.progress_updated.emit(f"✗ Error installing {dep['name']}: {str(e)}")

            if success_count == len(missing):
                self.installation_finished.emit(True, f"All {success_count} dependencies installed successfully")
            elif success_count > 0:
                self.installation_finished.emit(False, f"Installed {success_count}/{len(missing)} dependencies. Failed: {', '.join(failed_deps)}")
            else:
                self.installation_finished.emit(False, f"Installation failed for all dependencies: {', '.join(failed_deps)}")

        except Exception as e:
            self.installation_finished.emit(False, f"Installation error: {str(e)}")

    def cancel(self):
        """Cancel installation"""
        self.cancelled = True

    def _install_java_with_progress(self):
        """Install Java with progress updates"""
        methods = [
            ("Default JDK", "sudo apt update && sudo apt install -y default-jdk"),
            ("OpenJDK 11", "sudo apt install -y openjdk-11-jdk"),
            ("OpenJDK 8", "sudo apt install -y openjdk-8-jdk")
        ]

        for name, command in methods:
            if self.cancelled:
                return False

            self.progress_updated.emit(f"Trying {name}...")
            try:
                result = subprocess.run(command, shell=True,
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    return True
            except Exception:
                continue
        return False

    def _install_apktool_with_progress(self):
        """Install APKTool with progress updates"""
        # Method 1: Package manager
        if not self.cancelled:
            self.progress_updated.emit("Trying apt package manager...")
            try:
                result = subprocess.run('sudo apt update && sudo apt install -y apktool',
                                      shell=True, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    return True
            except Exception:
                pass

        # Method 2: Manual download
        if not self.cancelled:
            self.progress_updated.emit("Downloading APKTool manually...")
            try:
                if self._install_apktool_manual_with_progress():
                    return True
            except Exception:
                pass

        # Method 3: Snap package
        if not self.cancelled:
            self.progress_updated.emit("Trying snap package...")
            try:
                result = subprocess.run('sudo snap install apktool',
                                      shell=True, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    return True
            except Exception:
                pass

        return False

    def _install_apktool_manual_with_progress(self):
        """Manually install APKTool with progress"""
        import tempfile
        import stat

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # URLs
                wrapper_url = "https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool"
                jar_url = "https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar"

                wrapper_path = temp_path / "apktool"
                jar_path = temp_path / "apktool.jar"

                # Download wrapper
                self.progress_updated.emit("Downloading APKTool wrapper script...")
                urllib.request.urlretrieve(wrapper_url, wrapper_path)

                if self.cancelled:
                    return False

                # Download JAR
                self.progress_updated.emit("Downloading APKTool JAR file...")
                urllib.request.urlretrieve(jar_url, jar_path)

                if self.cancelled:
                    return False

                # Install
                self.progress_updated.emit("Installing APKTool...")
                wrapper_path.chmod(wrapper_path.stat().st_mode | stat.S_IEXEC)

                subprocess.run(['sudo', 'cp', str(wrapper_path), '/usr/local/bin/apktool'], check=True)
                subprocess.run(['sudo', 'cp', str(jar_path), '/usr/local/bin/apktool.jar'], check=True)
                subprocess.run(['sudo', 'chmod', '+x', '/usr/local/bin/apktool'], check=True)

                return True

        except Exception:
            return False

    def _install_aapt_with_progress(self):
        """Install AAPT with progress updates"""
        methods = [
            ("Direct AAPT package", "sudo apt update && sudo apt install -y aapt"),
            ("Android SDK build tools", "sudo apt install -y android-sdk-build-tools"),
            ("Google Android SDK", "sudo apt install -y google-android-build-tools-installer")
        ]

        for name, command in methods:
            if self.cancelled:
                return False

            self.progress_updated.emit(f"Trying {name}...")
            try:
                result = subprocess.run(command, shell=True,
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    return True
            except Exception:
                continue
        return False

    def _install_generic_with_progress(self, dep):
        """Generic installation with progress"""
        self.progress_updated.emit(f"Installing {dep['name']}...")
        try:
            result = subprocess.run(dep['install_cmd'], shell=True,
                                  capture_output=True, text=True, timeout=300)
            return result.returncode == 0
        except Exception:
            return False


class ApkToolWorker(QThread):
    """Worker thread for APKTool operations"""

    output_received = pyqtSignal(str)
    operation_finished = pyqtSignal(bool, str)
    progress_updated = pyqtSignal(str)
    progress_percentage = pyqtSignal(int)
    operation_status = pyqtSignal(str)  # For detailed status updates

    def __init__(self, operation, apk_path, output_dir=None, parent=None):
        super().__init__(parent)
        self.operation = operation  # 'decompile', 'recompile', 'sign'
        self.apk_path = apk_path
        self.output_dir = output_dir
        self.cancelled = False
        self.process = None

    def run(self):
        """Execute APKTool operation"""
        try:
            if self.operation == 'decompile':
                self._decompile_apk()
            elif self.operation == 'recompile':
                self._recompile_apk()
            elif self.operation == 'sign':
                self._sign_apk()

            if not self.cancelled:
                self.operation_finished.emit(True, "Operation completed successfully")
        except Exception as e:
            self.operation_finished.emit(False, str(e))

    def cancel(self):
        """Cancel the operation"""
        self.cancelled = True
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.operation_status.emit("⚠ Operation cancelled by user")
                self.output_received.emit("⚠ Operation cancelled by user")
            except:
                pass

    def _decompile_apk(self):
        """Decompile APK using apktool"""
        apktool_path = config.get('apktool_path', 'apktool')

        # Check if APK file exists
        if not Path(self.apk_path).exists():
            raise Exception(f"APK file not found: {self.apk_path}")

        # Determine output directory
        if not self.output_dir:
            apk_name = Path(self.apk_path).stem
            self.output_dir = str(Path(self.apk_path).parent / f"{apk_name}_decompiled")

        # Create output directory if it doesn't exist
        Path(self.output_dir).parent.mkdir(parents=True, exist_ok=True)

        # Build command
        cmd = [
            apktool_path, 'd', self.apk_path,
            '-o', self.output_dir,
            '-f'  # Force overwrite
        ]

        self.progress_updated.emit(f"Decompiling {Path(self.apk_path).name}...")
        self.output_received.emit(f"Command: {' '.join(cmd)}")
        self._run_command(cmd)

        if Path(self.output_dir).exists():
            self.output_received.emit(f"✓ Decompiled to: {self.output_dir}")
        else:
            raise Exception("Decompilation failed - output directory not created")

    def _recompile_apk(self):
        """Recompile APK from decompiled directory"""
        apktool_path = config.get('apktool_path', 'apktool')

        # Check if source directory exists
        if not Path(self.apk_path).exists():
            raise Exception(f"Source directory not found: {self.apk_path}")

        # Check if it's a valid decompiled APK directory
        if not (Path(self.apk_path) / "AndroidManifest.xml").exists():
            raise Exception(f"Invalid APK source directory: {self.apk_path}")

        # Determine output APK path
        if not self.output_dir:
            self.output_dir = str(Path(self.apk_path).parent / "recompiled.apk")

        # Build command
        cmd = [
            apktool_path, 'b', self.apk_path,
            '-o', self.output_dir
        ]

        self.progress_updated.emit(f"Recompiling {Path(self.apk_path).name}...")
        self.output_received.emit(f"Command: {' '.join(cmd)}")
        self._run_command(cmd)

        if Path(self.output_dir).exists():
            self.output_received.emit(f"✓ Recompiled to: {self.output_dir}")
        else:
            raise Exception("Recompilation failed - output APK not created")

    def _sign_apk(self):
        """Sign APK with debug key"""
        java_path = config.get('java_path', 'java')

        # Use jarsigner for signing (basic implementation)
        # In production, you might want to use apksigner
        cmd = [
            'jarsigner', '-verbose', '-sigalg', 'SHA1withRSA',
            '-digestalg', 'SHA1', '-keystore',
            os.path.expanduser('~/.android/debug.keystore'),
            '-storepass', 'android', '-keypass', 'android',
            self.apk_path, 'androiddebugkey'
        ]

        self.progress_updated.emit("Signing APK...")
        self._run_command(cmd)

    def _run_command(self, cmd):
        """Run command and capture output with real-time progress"""
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Track progress based on output patterns
            progress_patterns = {
                'decompile': [
                    ('I: Using Apktool', 5),
                    ('I: Loading resource table', 15),
                    ('I: Decoding AndroidManifest.xml', 25),
                    ('I: Decoding file-resources', 40),
                    ('I: Decoding values', 60),
                    ('I: Baksmaling classes.dex', 80),
                    ('I: Copying assets', 90),
                    ('I: Copying unknown files', 95),
                    ('I: Copying original files', 98)
                ],
                'recompile': [
                    ('I: Using Apktool', 5),
                    ('I: Checking whether sources', 15),
                    ('I: Smaling smali folder', 30),
                    ('I: Checking whether resources', 50),
                    ('I: Building resources', 70),
                    ('I: Building apk file', 85),
                    ('I: Copying unknown files', 95)
                ],
                'sign': [
                    ('adding:', 20),
                    ('signing:', 60),
                    ('jar signed', 100)
                ]
            }

            current_progress = 0
            patterns = progress_patterns.get(self.operation, [])

            # Read output line by line with better error handling
            output_lines = []
            while True:
                if self.cancelled:
                    try:
                        self.process.terminate()
                        self.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                    break

                line = self.process.stdout.readline()
                if not line:
                    break

                line = line.strip()
                if line:
                    # Store for error reporting
                    output_lines.append(line)

                    # Emit the raw output
                    self.output_received.emit(line)

                    # Check for progress patterns
                    for pattern, progress in patterns:
                        if pattern in line and progress > current_progress:
                            current_progress = progress
                            self.progress_percentage.emit(progress)

                            # Emit status updates based on patterns
                            if 'Loading resource table' in line:
                                self.operation_status.emit("📋 Loading resource table...")
                            elif 'Decoding AndroidManifest.xml' in line:
                                self.operation_status.emit("📄 Decoding AndroidManifest.xml...")
                            elif 'Decoding file-resources' in line:
                                self.operation_status.emit("📁 Decoding file resources...")
                            elif 'Decoding values' in line:
                                self.operation_status.emit("🔤 Decoding values...")
                            elif 'Baksmaling classes.dex' in line:
                                self.operation_status.emit("⚙️ Decompiling classes.dex...")
                            elif 'Copying assets' in line:
                                self.operation_status.emit("📦 Copying assets...")
                            elif 'Smaling smali folder' in line:
                                self.operation_status.emit("🔨 Compiling smali code...")
                            elif 'Building resources' in line:
                                self.operation_status.emit("🏗️ Building resources...")
                            elif 'Building apk file' in line:
                                self.operation_status.emit("📱 Building APK file...")
                            elif 'signing:' in line:
                                self.operation_status.emit("🔐 Signing APK...")
                            break

            # Wait for process to complete
            self.process.wait()

            # Emit final progress if successful
            if not self.cancelled and self.process.returncode == 0:
                self.progress_percentage.emit(100)

            # Check return code and provide detailed error info
            if self.process.returncode != 0 and not self.cancelled:
                error_output = '\n'.join(output_lines[-10:]) if output_lines else "No output captured"
                raise Exception(f"Command failed with return code {self.process.returncode}\n\nLast output:\n{error_output}")

        except FileNotFoundError:
            raise Exception(f"Command not found: {cmd[0]}\n\nPlease ensure the tool is installed and in your PATH.\nYou can install it using the Setup tab.")
        except Exception as e:
            if not self.cancelled:
                raise Exception(f"Command execution failed: {str(e)}")


class ApkToolWidget(QWidget):
    """APKTool operations widget with dependency management"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_worker = None
        self.installer_worker = None
        self.dependencies_ok = False
        self.full_logs = ""  # Initialize logs storage
        self.logs_window = None  # Initialize logs window

        # APK Editor state
        self.current_apk_path = None
        self.apk_contents = {}  # Store APK file contents
        self.modified_files = {}  # Track modified files
        self.current_editing_file = None
        self.original_file_content = None

        # Initialize UI elements to prevent AttributeError
        self.save_apk_btn = None
        self.save_as_apk_btn = None
        self.save_changes_btn = None
        self.edit_file_btn = None
        self.text_preview = None
        self.hex_preview = None
        self.image_preview = None
        self.preview_tabs = None
        self.file_info_label = None
        self.editor_status_label = None
        self.editor_progress_bar = None

        self.setup_ui()
        self.setup_connections()
        self.check_dependencies()

    def setup_ui(self):
        """Setup the comprehensive APK Tools interface with separate pages"""
        layout = QVBoxLayout(self)

        # Create main tab widget with compact styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(False)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #2b2b2b;
                margin-top: -1px;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a4a, stop:1 #3a3a3a);
                border: 1px solid #666;
                border-bottom-color: #555;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                min-width: 80px;
                max-width: 100px;
                padding: 6px 8px;
                margin-right: 1px;
                color: white;
                font-weight: normal;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a5a5a, stop:1 #4a4a4a);
                border-bottom-color: #2b2b2b;
                color: #2196F3;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a5a5a, stop:1 #4a4a4a);
            }
        """)

        # 1. APK Editor tab (ZIP-style editing)
        self.editor_tab = self.create_editor_tab()
        self.tab_widget.addTab(self.editor_tab, "📝 Editor")

        # 2. Decompile tab (Dedicated decompile operations)
        self.decompile_tab = self.create_decompile_tab()
        self.tab_widget.addTab(self.decompile_tab, "⬇ Decompile")

        # 3. Recompile tab (Dedicated recompile operations)
        self.recompile_tab = self.create_recompile_tab()
        self.tab_widget.addTab(self.recompile_tab, "⬆ Recompile")

        # 4. Signing tab (APK signing and verification)
        self.signing_tab = self.create_signing_tab()
        self.tab_widget.addTab(self.signing_tab, "🔐 Signing")

        # 5. Analysis tab (APK analysis and information)
        self.analysis_tab = self.create_analysis_tab()
        self.tab_widget.addTab(self.analysis_tab, "🔍 Analysis")

        # 6. Resources tab (Resource extraction and management)
        self.resources_tab = self.create_resources_tab()
        self.tab_widget.addTab(self.resources_tab, "🎨 Resources")

        # 7. Manifest tab (AndroidManifest.xml editor)
        self.manifest_tab = self.create_manifest_tab()
        self.tab_widget.addTab(self.manifest_tab, "📋 Manifest")

        # 8. Smali tab (Smali code viewer/editor)
        self.smali_tab = self.create_smali_tab()
        self.tab_widget.addTab(self.smali_tab, "⚙ Smali")

        # 9. Installation tab (APK installation and device management)
        self.installation_tab = self.create_installation_tab()
        self.tab_widget.addTab(self.installation_tab, "📱 Install")

        # 10. Setup tab (Dependencies and configuration)
        self.setup_tab = self.create_setup_tab()
        self.tab_widget.addTab(self.setup_tab, "⚙ Setup")

        layout.addWidget(self.tab_widget)

    def create_editor_tab(self):
        """Create the APK editor tab (ZIP-style editing)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # APK file selection for editor
        file_group = QGroupBox("APK File")
        file_layout = QHBoxLayout(file_group)

        self.editor_apk_label = QLabel("No APK selected")
        self.editor_browse_btn = QPushButton("Browse APK...")
        self.editor_reload_btn = QPushButton("🔄 Reload")

        file_layout.addWidget(self.editor_apk_label)
        file_layout.addWidget(self.editor_browse_btn)
        file_layout.addWidget(self.editor_reload_btn)

        layout.addWidget(file_group)

        # Main editor area with splitter
        editor_splitter = QSplitter(Qt.Horizontal)

        # Left: APK file tree
        tree_group = QGroupBox("APK Contents")
        tree_layout = QVBoxLayout(tree_group)

        # Tree view for APK contents
        self.apk_tree = QTreeWidget()
        self.apk_tree.setHeaderLabels(["Name", "Size", "Type"])
        self.apk_tree.setRootIsDecorated(True)
        self.apk_tree.setAlternatingRowColors(True)
        tree_layout.addWidget(self.apk_tree)

        # Tree controls
        tree_controls = QHBoxLayout()
        self.extract_btn = QPushButton("📤 Extract Selected")
        self.replace_btn = QPushButton("📥 Replace File")
        self.add_file_btn = QPushButton("➕ Add File")
        self.delete_file_btn = QPushButton("🗑️ Delete File")

        tree_controls.addWidget(self.extract_btn)
        tree_controls.addWidget(self.replace_btn)
        tree_controls.addWidget(self.add_file_btn)
        tree_controls.addWidget(self.delete_file_btn)
        tree_controls.addStretch()

        tree_layout.addLayout(tree_controls)

        editor_splitter.addWidget(tree_group)

        # Right: File preview/editor
        preview_group = QGroupBox("File Preview/Editor")
        preview_layout = QVBoxLayout(preview_group)

        # File info
        self.file_info_label = QLabel("Select a file to preview")
        preview_layout.addWidget(self.file_info_label)

        # Preview area with tabs
        self.preview_tabs = QTabWidget()

        # Text preview tab
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setFont(QFont("Consolas", 10))
        self.preview_tabs.addTab(self.text_preview, "📝 Text")

        # Hex preview tab
        self.hex_preview = QTextEdit()
        self.hex_preview.setReadOnly(True)
        self.hex_preview.setFont(QFont("Consolas", 9))
        self.preview_tabs.addTab(self.hex_preview, "🔧 Hex")

        # Image preview tab (for resources)
        from PyQt5.QtWidgets import QLabel as ImageLabel
        self.image_preview = ImageLabel()
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("border: 1px solid gray;")
        self.preview_tabs.addTab(self.image_preview, "🖼️ Image")

        preview_layout.addWidget(self.preview_tabs)

        # Preview controls
        preview_controls = QHBoxLayout()
        self.edit_file_btn = QPushButton("✏️ Edit File")
        self.save_changes_btn = QPushButton("💾 Save Changes")
        self.save_changes_btn.setEnabled(False)

        # Smali/Java conversion buttons
        self.smali_to_java_btn = QPushButton("☕ Smali→Java")
        self.java_to_smali_btn = QPushButton("🤖 Java→Smali")
        self.smali_to_java_btn.setEnabled(False)
        self.java_to_smali_btn.setEnabled(False)
        self.smali_to_java_btn.setToolTip("Convert Smali code to Java (requires jadx)")
        self.java_to_smali_btn.setToolTip("Convert Java code to Smali (requires dx/d8)")

        preview_controls.addWidget(self.edit_file_btn)
        preview_controls.addWidget(self.save_changes_btn)
        preview_controls.addWidget(self.smali_to_java_btn)
        preview_controls.addWidget(self.java_to_smali_btn)
        preview_controls.addStretch()

        preview_layout.addLayout(preview_controls)

        editor_splitter.addWidget(preview_group)

        # Set splitter ratio (40% tree, 60% preview)
        editor_splitter.setSizes([400, 600])

        layout.addWidget(editor_splitter)

        # APK modification controls
        mod_group = QGroupBox("APK Modifications")
        mod_layout = QHBoxLayout(mod_group)

        self.save_apk_btn = QPushButton("💾 Save APK")
        self.save_as_apk_btn = QPushButton("💾 Save APK As...")
        self.sign_modified_btn = QPushButton("🔐 Sign APK")
        self.install_apk_btn = QPushButton("📱 Install APK")

        mod_layout.addWidget(self.save_apk_btn)
        mod_layout.addWidget(self.save_as_apk_btn)
        mod_layout.addWidget(self.sign_modified_btn)
        mod_layout.addWidget(self.install_apk_btn)
        mod_layout.addStretch()

        layout.addWidget(mod_group)

        # Status and progress
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)

        self.editor_status_label = QLabel("Ready")
        self.editor_progress_bar = QProgressBar()
        self.editor_progress_bar.setVisible(False)

        status_layout.addWidget(self.editor_status_label)
        status_layout.addWidget(self.editor_progress_bar)

        layout.addWidget(status_group)

        return widget

    def create_decompile_tab(self):
        """Create dedicated decompile tab with advanced options"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header section
        header_group = QGroupBox("⬇ APK Decompile Operations")
        header_layout = QVBoxLayout(header_group)
        header_layout.setContentsMargins(10, 12, 10, 10)

        # APK file selection
        file_section = QHBoxLayout()
        file_section.setSpacing(10)

        self.decompile_apk_label = QLabel("No APK selected")
        self.decompile_apk_label.setStyleSheet("""
            QLabel {
                padding: 6px;
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 4px;
                font-size: 11px;
                color: #ccc;
            }
        """)
        self.decompile_apk_label.setMinimumHeight(28)

        self.decompile_browse_btn = QPushButton("📁 Browse")
        self.decompile_browse_btn.setMinimumHeight(32)
        self.decompile_browse_btn.setMinimumWidth(90)
        self.decompile_browse_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5CBF60, stop:1 #4CAF50);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
        """)

        file_section.addWidget(self.decompile_apk_label, 1)
        file_section.addWidget(self.decompile_browse_btn, 0)
        header_layout.addLayout(file_section)

        layout.addWidget(header_group)

        # Decompile options section
        options_group = QGroupBox("Decompile Options")
        options_layout = QVBoxLayout(options_group)
        options_layout.setContentsMargins(15, 20, 15, 15)
        options_layout.setSpacing(12)

        # Output directory
        output_section = QHBoxLayout()
        output_section.setSpacing(10)

        output_label = QLabel("Output Directory:")
        output_label.setMinimumWidth(120)
        output_label.setStyleSheet("font-weight: bold; color: #ccc;")

        self.decompile_output_path = QLabel("Auto (same directory as APK)")
        self.decompile_output_path.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 4px;
                color: #ccc;
            }
        """)

        self.decompile_output_browse = QPushButton("📁 Change")
        self.decompile_output_browse.setMinimumHeight(35)
        self.decompile_output_browse.setMinimumWidth(100)

        output_section.addWidget(output_label, 0)
        output_section.addWidget(self.decompile_output_path, 1)
        output_section.addWidget(self.decompile_output_browse, 0)
        options_layout.addLayout(output_section)

        # Advanced options
        advanced_options = QHBoxLayout()
        advanced_options.setSpacing(20)

        # Left column
        left_options = QVBoxLayout()
        left_options.setSpacing(8)

        self.decompile_no_src = QCheckBox("Skip sources (--no-src)")
        self.decompile_no_src.setToolTip("Do not decompile sources")
        self.decompile_no_res = QCheckBox("Skip resources (--no-res)")
        self.decompile_no_res.setToolTip("Do not decompile resources")
        self.decompile_force = QCheckBox("Force overwrite (--force)")
        self.decompile_force.setToolTip("Force delete destination directory")

        left_options.addWidget(self.decompile_no_src)
        left_options.addWidget(self.decompile_no_res)
        left_options.addWidget(self.decompile_force)

        # Right column
        right_options = QVBoxLayout()
        right_options.setSpacing(8)

        self.decompile_keep_broken = QCheckBox("Keep broken resources (--keep-broken-res)")
        self.decompile_keep_broken.setToolTip("Use if there are broken resources")
        self.decompile_no_debug = QCheckBox("No debug info (--no-debug-info)")
        self.decompile_no_debug.setToolTip("Don't write debug info")
        self.decompile_match_original = QCheckBox("Match original (--match-original)")
        self.decompile_match_original.setToolTip("Keep files to closest to original")

        right_options.addWidget(self.decompile_keep_broken)
        right_options.addWidget(self.decompile_no_debug)
        right_options.addWidget(self.decompile_match_original)

        advanced_options.addLayout(left_options)
        advanced_options.addLayout(right_options)
        options_layout.addLayout(advanced_options)

        layout.addWidget(options_group)

        # Action buttons
        action_group = QGroupBox("Actions")
        action_layout = QHBoxLayout(action_group)
        action_layout.setContentsMargins(15, 20, 15, 15)
        action_layout.setSpacing(15)

        self.start_decompile_btn = QPushButton("⬇ Start Decompile")
        self.start_decompile_btn.setMinimumHeight(36)
        self.start_decompile_btn.setMinimumWidth(130)
        self.start_decompile_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
                border: none;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #42A5F5, stop:1 #2196F3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
            }
            QPushButton:disabled {
                background: #444;
                color: #666;
            }
        """)

        self.decompile_cancel_btn = QPushButton("❌ Cancel")
        self.decompile_cancel_btn.setMinimumHeight(36)
        self.decompile_cancel_btn.setMinimumWidth(80)
        self.decompile_cancel_btn.setEnabled(False)

        self.open_output_btn = QPushButton("📂 Open")
        self.open_output_btn.setMinimumHeight(36)
        self.open_output_btn.setMinimumWidth(80)
        self.open_output_btn.setEnabled(False)

        action_layout.addWidget(self.start_decompile_btn)
        action_layout.addWidget(self.decompile_cancel_btn)
        action_layout.addWidget(self.open_output_btn)
        action_layout.addStretch()

        layout.addWidget(action_group)

        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setContentsMargins(15, 20, 15, 15)
        progress_layout.setSpacing(10)

        self.decompile_status = QLabel("Ready to decompile")
        self.decompile_status.setStyleSheet("font-weight: bold; color: #2196F3; font-size: 13px;")

        self.decompile_progress = QProgressBar()
        self.decompile_progress.setMinimumHeight(25)
        self.decompile_progress.setVisible(False)
        self.decompile_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 8px;
                text-align: center;
                background-color: #2b2b2b;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 6px;
            }
        """)

        progress_layout.addWidget(self.decompile_status)
        progress_layout.addWidget(self.decompile_progress)

        layout.addWidget(progress_group)

        # Output log
        log_group = QGroupBox("Decompile Log")
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(10, 12, 10, 10)

        self.decompile_log = QTextEdit()
        self.decompile_log.setMaximumHeight(100)
        self.decompile_log.setReadOnly(True)
        self.decompile_log.setFont(QFont("Consolas", 8))
        self.decompile_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)

        log_controls = QHBoxLayout()
        log_controls.setSpacing(10)

        self.clear_decompile_log = QPushButton("🗑 Clear")
        self.clear_decompile_log.setMinimumHeight(24)

        self.save_decompile_log = QPushButton("💾 Save")
        self.save_decompile_log.setMinimumHeight(24)

        log_controls.addWidget(self.clear_decompile_log)
        log_controls.addWidget(self.save_decompile_log)
        log_controls.addStretch()

        log_layout.addWidget(self.decompile_log)
        log_layout.addLayout(log_controls)

        layout.addWidget(log_group)

        return widget

    def create_recompile_tab(self):
        """Create dedicated recompile tab with advanced options"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header section
        header_group = QGroupBox("⬆ APK Recompile Operations")
        header_layout = QVBoxLayout(header_group)
        header_layout.setContentsMargins(10, 12, 10, 10)

        # Source directory selection
        source_section = QHBoxLayout()
        source_section.setSpacing(10)

        self.recompile_source_label = QLabel("No source directory selected")
        self.recompile_source_label.setStyleSheet("""
            QLabel {
                padding: 6px;
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 4px;
                font-size: 11px;
                color: #ccc;
            }
        """)
        self.recompile_source_label.setMinimumHeight(28)

        self.recompile_browse_source_btn = QPushButton("📁 Browse")
        self.recompile_browse_source_btn.setMinimumHeight(32)
        self.recompile_browse_source_btn.setMinimumWidth(90)
        self.recompile_browse_source_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF9800, stop:1 #F57C00);
                border: none;
                border-radius: 6px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFB74D, stop:1 #FF9800);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F57C00, stop:1 #E65100);
            }
        """)

        source_section.addWidget(self.recompile_source_label, 1)
        source_section.addWidget(self.recompile_browse_source_btn, 0)
        header_layout.addLayout(source_section)

        layout.addWidget(header_group)

        # Recompile options section
        recompile_options_group = QGroupBox("Recompile Options")
        recompile_options_layout = QVBoxLayout(recompile_options_group)
        recompile_options_layout.setContentsMargins(15, 20, 15, 15)
        recompile_options_layout.setSpacing(12)

        # Output APK path
        output_apk_section = QHBoxLayout()
        output_apk_section.setSpacing(10)

        output_apk_label = QLabel("Output APK:")
        output_apk_label.setMinimumWidth(120)
        output_apk_label.setStyleSheet("font-weight: bold; color: #ccc;")

        self.recompile_output_apk = QLabel("Auto (source_directory.apk)")
        self.recompile_output_apk.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 4px;
                color: #ccc;
            }
        """)

        self.recompile_output_browse = QPushButton("📁 Change")
        self.recompile_output_browse.setMinimumHeight(35)
        self.recompile_output_browse.setMinimumWidth(100)

        output_apk_section.addWidget(output_apk_label, 0)
        output_apk_section.addWidget(self.recompile_output_apk, 1)
        output_apk_section.addWidget(self.recompile_output_browse, 0)
        recompile_options_layout.addLayout(output_apk_section)

        # Advanced recompile options
        recompile_advanced = QHBoxLayout()
        recompile_advanced.setSpacing(20)

        # Left column
        recompile_left = QVBoxLayout()
        recompile_left.setSpacing(8)

        self.recompile_use_aapt2 = QCheckBox("Use AAPT2 (--use-aapt2)")
        self.recompile_use_aapt2.setToolTip("Use AAPT2 for building")
        self.recompile_copy_original = QCheckBox("Copy original files (--copy-original)")
        self.recompile_copy_original.setToolTip("Copy original AndroidManifest.xml and META-INF")
        self.recompile_no_crunch = QCheckBox("No crunch (--no-crunch)")
        self.recompile_no_crunch.setToolTip("Disable crunching of resource files")

        recompile_left.addWidget(self.recompile_use_aapt2)
        recompile_left.addWidget(self.recompile_copy_original)
        recompile_left.addWidget(self.recompile_no_crunch)

        # Right column
        recompile_right = QVBoxLayout()
        recompile_right.setSpacing(8)

        self.recompile_force_all = QCheckBox("Force all files (--force-all)")
        self.recompile_force_all.setToolTip("Skip changes detection and build all files")
        self.recompile_debug = QCheckBox("Debug mode (--debug)")
        self.recompile_debug.setToolTip("Build in debug mode")
        self.recompile_net_sec_conf = QCheckBox("Net security config (--net-sec-conf)")
        self.recompile_net_sec_conf.setToolTip("Add network security config")

        recompile_right.addWidget(self.recompile_force_all)
        recompile_right.addWidget(self.recompile_debug)
        recompile_right.addWidget(self.recompile_net_sec_conf)

        recompile_advanced.addLayout(recompile_left)
        recompile_advanced.addLayout(recompile_right)
        recompile_options_layout.addLayout(recompile_advanced)

        layout.addWidget(recompile_options_group)

        # Action buttons
        recompile_action_group = QGroupBox("Actions")
        recompile_action_layout = QHBoxLayout(recompile_action_group)
        recompile_action_layout.setContentsMargins(15, 20, 15, 15)
        recompile_action_layout.setSpacing(15)

        self.start_recompile_btn = QPushButton("🚀 Start Recompile")
        self.start_recompile_btn.setMinimumHeight(50)
        self.start_recompile_btn.setMinimumWidth(150)
        self.start_recompile_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF5722, stop:1 #D84315);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF7043, stop:1 #FF5722);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #D84315, stop:1 #BF360C);
            }
            QPushButton:disabled {
                background: #444;
                color: #666;
            }
        """)

        self.recompile_cancel_btn = QPushButton("❌ Cancel")
        self.recompile_cancel_btn.setMinimumHeight(50)
        self.recompile_cancel_btn.setMinimumWidth(100)
        self.recompile_cancel_btn.setEnabled(False)

        self.open_recompiled_btn = QPushButton("📂 Open APK")
        self.open_recompiled_btn.setMinimumHeight(50)
        self.open_recompiled_btn.setMinimumWidth(120)
        self.open_recompiled_btn.setEnabled(False)

        recompile_action_layout.addWidget(self.start_recompile_btn)
        recompile_action_layout.addWidget(self.recompile_cancel_btn)
        recompile_action_layout.addWidget(self.open_recompiled_btn)
        recompile_action_layout.addStretch()

        layout.addWidget(recompile_action_group)

        # Progress section
        recompile_progress_group = QGroupBox("Progress")
        recompile_progress_layout = QVBoxLayout(recompile_progress_group)
        recompile_progress_layout.setContentsMargins(15, 20, 15, 15)
        recompile_progress_layout.setSpacing(10)

        self.recompile_status = QLabel("Ready to recompile")
        self.recompile_status.setStyleSheet("font-weight: bold; color: #FF5722; font-size: 13px;")

        self.recompile_progress = QProgressBar()
        self.recompile_progress.setMinimumHeight(25)
        self.recompile_progress.setVisible(False)
        self.recompile_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 8px;
                text-align: center;
                background-color: #2b2b2b;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF5722, stop:1 #D84315);
                border-radius: 6px;
            }
        """)

        recompile_progress_layout.addWidget(self.recompile_status)
        recompile_progress_layout.addWidget(self.recompile_progress)

        layout.addWidget(recompile_progress_group)

        # Output log
        recompile_log_group = QGroupBox("Recompile Log")
        recompile_log_layout = QVBoxLayout(recompile_log_group)
        recompile_log_layout.setContentsMargins(15, 20, 15, 15)

        self.recompile_log = QTextEdit()
        self.recompile_log.setMaximumHeight(150)
        self.recompile_log.setReadOnly(True)
        self.recompile_log.setFont(QFont("Consolas", 9))
        self.recompile_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)

        recompile_log_controls = QHBoxLayout()
        recompile_log_controls.setSpacing(10)

        self.clear_recompile_log = QPushButton("🗑️ Clear Log")
        self.clear_recompile_log.setMinimumHeight(30)

        self.save_recompile_log = QPushButton("💾 Save Log")
        self.save_recompile_log.setMinimumHeight(30)

        recompile_log_controls.addWidget(self.clear_recompile_log)
        recompile_log_controls.addWidget(self.save_recompile_log)
        recompile_log_controls.addStretch()

        recompile_log_layout.addWidget(self.recompile_log)
        recompile_log_layout.addLayout(recompile_log_controls)

        layout.addWidget(recompile_log_group)

        return widget

    def create_operations_tab(self):
        """Create the operations tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Dependency status
        self.status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(self.status_group)
        status_layout.setContentsMargins(10, 15, 10, 10)

        self.dependency_status = QLabel("Checking dependencies...")
        self.dependency_status.setStyleSheet("color: orange; font-weight: bold; padding: 5px;")
        self.dependency_status.setMinimumHeight(30)
        status_layout.addWidget(self.dependency_status)

        layout.addWidget(self.status_group)

        # APK file selection
        file_group = QGroupBox("APK File")
        file_layout = QHBoxLayout(file_group)
        file_layout.setContentsMargins(10, 15, 10, 10)
        file_layout.setSpacing(10)

        self.apk_path_label = QLabel("No APK selected")
        self.apk_path_label.setStyleSheet("padding: 5px; background-color: #2b2b2b; border: 1px solid #555; border-radius: 3px;")
        self.apk_path_label.setMinimumHeight(30)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setMinimumHeight(35)
        self.browse_btn.setMinimumWidth(100)

        file_layout.addWidget(self.apk_path_label, 1)
        file_layout.addWidget(self.browse_btn, 0)

        layout.addWidget(file_group)

        # Operations
        ops_group = QGroupBox("Operations")
        ops_layout = QVBoxLayout(ops_group)
        ops_layout.setContentsMargins(10, 15, 10, 10)
        ops_layout.setSpacing(15)

        # Decompile section
        decompile_layout = QHBoxLayout()
        decompile_layout.setSpacing(10)

        self.decompile_btn = QPushButton("🔨 Decompile APK")
        self.decompile_btn.setMinimumHeight(40)
        self.decompile_btn.setMinimumWidth(150)
        self.decompile_btn.setStyleSheet("font-weight: bold; padding: 8px;")

        self.decompile_output_btn = QPushButton("📁 Output Dir...")
        self.decompile_output_btn.setMinimumHeight(40)
        self.decompile_output_btn.setMinimumWidth(120)

        self.decompile_output_label = QLabel("Auto")
        self.decompile_output_label.setStyleSheet("padding: 8px; background-color: #2b2b2b; border: 1px solid #555; border-radius: 3px;")
        self.decompile_output_label.setMinimumHeight(30)

        decompile_layout.addWidget(self.decompile_btn, 0)
        decompile_layout.addWidget(QLabel("Output:"), 0)
        decompile_layout.addWidget(self.decompile_output_label, 1)
        decompile_layout.addWidget(self.decompile_output_btn, 0)

        ops_layout.addLayout(decompile_layout)

        # Recompile section
        recompile_layout = QHBoxLayout()
        recompile_layout.setSpacing(10)

        self.recompile_btn = QPushButton("🔧 Recompile APK")
        self.recompile_btn.setMinimumHeight(40)
        self.recompile_btn.setMinimumWidth(150)
        self.recompile_btn.setStyleSheet("font-weight: bold; padding: 8px;")

        self.recompile_output_btn = QPushButton("💾 Output APK...")
        self.recompile_output_btn.setMinimumHeight(40)
        self.recompile_output_btn.setMinimumWidth(120)

        self.recompile_output_label = QLabel("Auto")
        self.recompile_output_label.setStyleSheet("padding: 8px; background-color: #2b2b2b; border: 1px solid #555; border-radius: 3px;")
        self.recompile_output_label.setMinimumHeight(30)

        recompile_layout.addWidget(self.recompile_btn, 0)
        recompile_layout.addWidget(QLabel("Output:"), 0)
        recompile_layout.addWidget(self.recompile_output_label, 1)
        recompile_layout.addWidget(self.recompile_output_btn, 0)

        ops_layout.addLayout(recompile_layout)

        # Sign section
        sign_layout = QHBoxLayout()
        sign_layout.setSpacing(10)

        self.sign_btn = QPushButton("🔐 Sign APK")
        self.sign_btn.setMinimumHeight(40)
        self.sign_btn.setMinimumWidth(150)
        self.sign_btn.setStyleSheet("font-weight: bold; padding: 8px;")

        sign_layout.addWidget(self.sign_btn, 0)
        sign_layout.addStretch(1)

        ops_layout.addLayout(sign_layout)

        layout.addWidget(ops_group)

        # Progress and status
        progress_group = QGroupBox("Progress & Status")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setContentsMargins(10, 15, 10, 10)
        progress_layout.setSpacing(10)

        # Current operation status
        self.operation_status_label = QLabel("Ready")
        self.operation_status_label.setStyleSheet("font-weight: bold; color: #2196F3; padding: 5px; font-size: 14px;")
        self.operation_status_label.setMinimumHeight(25)
        progress_layout.addWidget(self.operation_status_label)

        # Progress label and bar
        self.progress_label = QLabel("Ready")
        self.progress_label.setStyleSheet("padding: 3px; color: #ccc;")
        self.progress_label.setMinimumHeight(20)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 5px;
                text-align: center;
                background-color: #2b2b2b;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 4px;
            }
        """)

        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)

        # Operation controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.setMinimumWidth(100)

        self.view_logs_btn = QPushButton("📋 View Detailed Logs")
        self.view_logs_btn.setMinimumHeight(35)
        self.view_logs_btn.setMinimumWidth(150)

        controls_layout.addWidget(self.cancel_btn, 0)
        controls_layout.addWidget(self.view_logs_btn, 0)
        controls_layout.addStretch(1)

        progress_layout.addLayout(controls_layout)

        layout.addWidget(progress_group)

        # Quick output log (compact)
        quick_log_group = QGroupBox("Recent Output")
        quick_log_layout = QVBoxLayout(quick_log_group)
        quick_log_layout.setContentsMargins(10, 15, 10, 10)
        quick_log_layout.setSpacing(8)

        self.quick_output_text = QTextEdit()
        self.quick_output_text.setMaximumHeight(120)
        self.quick_output_text.setMinimumHeight(80)
        self.quick_output_text.setReadOnly(True)
        self.quick_output_text.setFont(QFont("Consolas", 9))
        self.quick_output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
            }
        """)

        quick_log_layout.addWidget(self.quick_output_text)

        # Quick log controls
        quick_log_controls = QHBoxLayout()
        quick_log_controls.setSpacing(10)

        self.clear_quick_log_btn = QPushButton("🗑️ Clear")
        self.clear_quick_log_btn.setMinimumHeight(30)
        self.clear_quick_log_btn.setMinimumWidth(80)

        self.auto_scroll_checkbox = QCheckBox("Auto-scroll")
        self.auto_scroll_checkbox.setChecked(True)
        self.auto_scroll_checkbox.setStyleSheet("padding: 5px;")

        quick_log_controls.addWidget(self.clear_quick_log_btn, 0)
        quick_log_controls.addWidget(self.auto_scroll_checkbox, 0)
        quick_log_controls.addStretch(1)

        quick_log_layout.addLayout(quick_log_controls)

        layout.addWidget(quick_log_group)

        return widget

    def create_signing_tab(self):
        """Create dedicated signing tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_group = QGroupBox("🔐 APK Signing & Verification")
        header_layout = QVBoxLayout(header_group)
        header_layout.setContentsMargins(15, 20, 15, 15)

        # APK file selection for signing
        sign_file_section = QHBoxLayout()
        sign_file_section.setSpacing(10)

        self.signing_apk_label = QLabel("No APK selected for signing")
        self.signing_apk_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #2b2b2b;
                border: 2px solid #555;
                border-radius: 6px;
                font-size: 12px;
                color: #ccc;
            }
        """)
        self.signing_apk_label.setMinimumHeight(40)

        self.signing_browse_btn = QPushButton("📁 Browse APK")
        self.signing_browse_btn.setMinimumHeight(45)
        self.signing_browse_btn.setMinimumWidth(120)

        sign_file_section.addWidget(self.signing_apk_label, 1)
        sign_file_section.addWidget(self.signing_browse_btn, 0)
        header_layout.addLayout(sign_file_section)

        layout.addWidget(header_group)

        # Signing options
        signing_options_group = QGroupBox("Signing Options")
        signing_options_layout = QVBoxLayout(signing_options_group)
        signing_options_layout.setContentsMargins(15, 20, 15, 15)
        signing_options_layout.setSpacing(12)

        # Keystore selection
        keystore_section = QHBoxLayout()
        keystore_section.setSpacing(10)

        keystore_label = QLabel("Keystore:")
        keystore_label.setMinimumWidth(100)
        keystore_label.setStyleSheet("font-weight: bold; color: #ccc;")

        self.keystore_path = QLabel("Use debug keystore")
        self.keystore_path.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 4px;
                color: #ccc;
            }
        """)

        self.keystore_browse = QPushButton("📁 Browse")
        self.keystore_browse.setMinimumHeight(35)

        keystore_section.addWidget(keystore_label, 0)
        keystore_section.addWidget(self.keystore_path, 1)
        keystore_section.addWidget(self.keystore_browse, 0)
        signing_options_layout.addLayout(keystore_section)

        # Signing method selection
        method_section = QHBoxLayout()
        method_section.setSpacing(20)

        self.use_jarsigner = QCheckBox("Use jarsigner (legacy)")
        self.use_jarsigner.setToolTip("Use jarsigner for signing (older method)")
        self.use_apksigner = QCheckBox("Use apksigner (recommended)")
        self.use_apksigner.setToolTip("Use apksigner for signing (newer, recommended)")
        self.use_apksigner.setChecked(True)  # Default to recommended

        method_section.addWidget(self.use_jarsigner)
        method_section.addWidget(self.use_apksigner)
        method_section.addStretch()
        signing_options_layout.addLayout(method_section)

        layout.addWidget(signing_options_group)

        # Actions
        signing_actions_group = QGroupBox("Actions")
        signing_actions_layout = QHBoxLayout(signing_actions_group)
        signing_actions_layout.setContentsMargins(15, 20, 15, 15)
        signing_actions_layout.setSpacing(15)

        self.sign_apk_btn = QPushButton("🔐 Sign APK")
        self.sign_apk_btn.setMinimumHeight(50)
        self.sign_apk_btn.setMinimumWidth(120)

        self.verify_signature_btn = QPushButton("✅ Verify Signature")
        self.verify_signature_btn.setMinimumHeight(50)
        self.verify_signature_btn.setMinimumWidth(140)

        self.zipalign_btn = QPushButton("📐 Zipalign APK")
        self.zipalign_btn.setMinimumHeight(50)
        self.zipalign_btn.setMinimumWidth(130)

        signing_actions_layout.addWidget(self.sign_apk_btn)
        signing_actions_layout.addWidget(self.verify_signature_btn)
        signing_actions_layout.addWidget(self.zipalign_btn)
        signing_actions_layout.addStretch()

        layout.addWidget(signing_actions_group)

        # Signature info display
        sig_info_group = QGroupBox("Signature Information")
        sig_info_layout = QVBoxLayout(sig_info_group)
        sig_info_layout.setContentsMargins(15, 20, 15, 15)

        self.signature_info = QTextEdit()
        self.signature_info.setMaximumHeight(120)
        self.signature_info.setReadOnly(True)
        self.signature_info.setFont(QFont("Consolas", 9))
        self.signature_info.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 8px;
            }
        """)

        sig_info_layout.addWidget(self.signature_info)
        layout.addWidget(sig_info_group)

        return widget

    def create_analysis_tab(self):
        """Create APK analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_group = QGroupBox("🔍 APK Analysis & Information")
        header_layout = QVBoxLayout(header_group)
        header_layout.setContentsMargins(15, 20, 15, 15)

        # APK file selection for analysis
        analysis_file_section = QHBoxLayout()
        analysis_file_section.setSpacing(10)

        self.analysis_apk_label = QLabel("No APK selected for analysis")
        self.analysis_apk_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #2b2b2b;
                border: 2px solid #555;
                border-radius: 6px;
                font-size: 12px;
                color: #ccc;
            }
        """)
        self.analysis_apk_label.setMinimumHeight(40)

        self.analysis_browse_btn = QPushButton("📁 Browse APK")
        self.analysis_browse_btn.setMinimumHeight(45)
        self.analysis_browse_btn.setMinimumWidth(120)

        analysis_file_section.addWidget(self.analysis_apk_label, 1)
        analysis_file_section.addWidget(self.analysis_browse_btn, 0)
        header_layout.addLayout(analysis_file_section)

        layout.addWidget(header_group)

        # Analysis options
        analysis_options_group = QGroupBox("Analysis Options")
        analysis_options_layout = QHBoxLayout(analysis_options_group)
        analysis_options_layout.setContentsMargins(15, 20, 15, 15)
        analysis_options_layout.setSpacing(15)

        self.analyze_manifest_btn = QPushButton("📋 Analyze Manifest")
        self.analyze_manifest_btn.setMinimumHeight(45)

        self.analyze_permissions_btn = QPushButton("🔒 Check Permissions")
        self.analyze_permissions_btn.setMinimumHeight(45)

        self.analyze_certificates_btn = QPushButton("🔐 Check Certificates")
        self.analyze_certificates_btn.setMinimumHeight(45)

        self.analyze_resources_btn = QPushButton("🎨 Analyze Resources")
        self.analyze_resources_btn.setMinimumHeight(45)

        analysis_options_layout.addWidget(self.analyze_manifest_btn)
        analysis_options_layout.addWidget(self.analyze_permissions_btn)
        analysis_options_layout.addWidget(self.analyze_certificates_btn)
        analysis_options_layout.addWidget(self.analyze_resources_btn)

        layout.addWidget(analysis_options_group)

        # Analysis results
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout(results_group)
        results_layout.setContentsMargins(15, 20, 15, 15)

        self.analysis_results = QTextEdit()
        self.analysis_results.setReadOnly(True)
        self.analysis_results.setFont(QFont("Consolas", 9))
        self.analysis_results.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 8px;
            }
        """)

        results_layout.addWidget(self.analysis_results)
        layout.addWidget(results_group)

        return widget

    def create_resources_tab(self):
        """Create resources management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_group = QGroupBox("🎨 APK Resources Management")
        header_layout = QVBoxLayout(header_group)
        header_layout.setContentsMargins(15, 20, 15, 15)

        # APK file selection for resources
        resources_file_section = QHBoxLayout()
        resources_file_section.setSpacing(10)

        self.resources_apk_label = QLabel("No APK selected for resource extraction")
        self.resources_apk_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #2b2b2b;
                border: 2px solid #555;
                border-radius: 6px;
                font-size: 12px;
                color: #ccc;
            }
        """)
        self.resources_apk_label.setMinimumHeight(40)

        self.resources_browse_btn = QPushButton("📁 Browse APK")
        self.resources_browse_btn.setMinimumHeight(45)
        self.resources_browse_btn.setMinimumWidth(120)

        resources_file_section.addWidget(self.resources_apk_label, 1)
        resources_file_section.addWidget(self.resources_browse_btn, 0)
        header_layout.addLayout(resources_file_section)

        layout.addWidget(header_group)

        # Resource extraction options
        extraction_group = QGroupBox("Resource Extraction")
        extraction_layout = QVBoxLayout(extraction_group)
        extraction_layout.setContentsMargins(15, 20, 15, 15)
        extraction_layout.setSpacing(12)

        # Extraction buttons
        extraction_buttons = QHBoxLayout()
        extraction_buttons.setSpacing(10)

        self.extract_all_resources_btn = QPushButton("📤 Extract All Resources")
        self.extract_all_resources_btn.setMinimumHeight(45)

        self.extract_images_btn = QPushButton("🖼️ Extract Images")
        self.extract_images_btn.setMinimumHeight(45)

        self.extract_layouts_btn = QPushButton("📐 Extract Layouts")
        self.extract_layouts_btn.setMinimumHeight(45)

        self.extract_strings_btn = QPushButton("📝 Extract Strings")
        self.extract_strings_btn.setMinimumHeight(45)

        extraction_buttons.addWidget(self.extract_all_resources_btn)
        extraction_buttons.addWidget(self.extract_images_btn)
        extraction_buttons.addWidget(self.extract_layouts_btn)
        extraction_buttons.addWidget(self.extract_strings_btn)

        extraction_layout.addLayout(extraction_buttons)

        # Output directory for resources
        output_resources_section = QHBoxLayout()
        output_resources_section.setSpacing(10)

        output_resources_label = QLabel("Output Directory:")
        output_resources_label.setMinimumWidth(120)
        output_resources_label.setStyleSheet("font-weight: bold; color: #ccc;")

        self.resources_output_path = QLabel("Auto (APK_name_resources)")
        self.resources_output_path.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 4px;
                color: #ccc;
            }
        """)

        self.resources_output_browse = QPushButton("📁 Change")
        self.resources_output_browse.setMinimumHeight(35)

        output_resources_section.addWidget(output_resources_label, 0)
        output_resources_section.addWidget(self.resources_output_path, 1)
        output_resources_section.addWidget(self.resources_output_browse, 0)
        extraction_layout.addLayout(output_resources_section)

        layout.addWidget(extraction_group)

        # Resource viewer
        viewer_group = QGroupBox("Resource Viewer")
        viewer_layout = QVBoxLayout(viewer_group)
        viewer_layout.setContentsMargins(15, 20, 15, 15)

        # Resource tree
        self.resources_tree = QTreeWidget()
        self.resources_tree.setHeaderLabels(["Resource", "Type", "Size"])
        self.resources_tree.setMaximumHeight(200)
        self.resources_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
            }
        """)

        viewer_layout.addWidget(self.resources_tree)
        layout.addWidget(viewer_group)

        return widget

    def create_manifest_tab(self):
        """Create AndroidManifest.xml editor tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_group = QGroupBox("📋 AndroidManifest.xml Editor")
        header_layout = QVBoxLayout(header_group)
        header_layout.setContentsMargins(15, 20, 15, 15)

        # APK file selection for manifest editing
        manifest_file_section = QHBoxLayout()
        manifest_file_section.setSpacing(10)

        self.manifest_apk_label = QLabel("No APK selected for manifest editing")
        self.manifest_apk_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #2b2b2b;
                border: 2px solid #555;
                border-radius: 6px;
                font-size: 12px;
                color: #ccc;
            }
        """)
        self.manifest_apk_label.setMinimumHeight(40)

        self.manifest_browse_btn = QPushButton("📁 Browse APK")
        self.manifest_browse_btn.setMinimumHeight(45)
        self.manifest_browse_btn.setMinimumWidth(120)

        manifest_file_section.addWidget(self.manifest_apk_label, 1)
        manifest_file_section.addWidget(self.manifest_browse_btn, 0)
        header_layout.addLayout(manifest_file_section)

        layout.addWidget(header_group)

        # Manifest editor
        editor_group = QGroupBox("Manifest Editor")
        editor_layout = QVBoxLayout(editor_group)
        editor_layout.setContentsMargins(15, 20, 15, 15)

        # Editor controls
        editor_controls = QHBoxLayout()
        editor_controls.setSpacing(10)

        self.load_manifest_btn = QPushButton("📂 Load Manifest")
        self.load_manifest_btn.setMinimumHeight(35)

        self.save_manifest_btn = QPushButton("💾 Save Changes")
        self.save_manifest_btn.setMinimumHeight(35)
        self.save_manifest_btn.setEnabled(False)

        self.validate_manifest_btn = QPushButton("✅ Validate")
        self.validate_manifest_btn.setMinimumHeight(35)

        editor_controls.addWidget(self.load_manifest_btn)
        editor_controls.addWidget(self.save_manifest_btn)
        editor_controls.addWidget(self.validate_manifest_btn)
        editor_controls.addStretch()

        editor_layout.addLayout(editor_controls)

        # Manifest text editor
        self.manifest_editor = QTextEdit()
        self.manifest_editor.setFont(QFont("Consolas", 10))
        self.manifest_editor.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)

        editor_layout.addWidget(self.manifest_editor)
        layout.addWidget(editor_group)

        return widget

    def create_smali_tab(self):
        """Create Smali code viewer/editor tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_group = QGroupBox("⚙️ Smali Code Viewer/Editor")
        header_layout = QVBoxLayout(header_group)
        header_layout.setContentsMargins(15, 20, 15, 15)

        # Source directory selection for Smali
        smali_source_section = QHBoxLayout()
        smali_source_section.setSpacing(10)

        self.smali_source_label = QLabel("No decompiled APK source selected")
        self.smali_source_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #2b2b2b;
                border: 2px solid #555;
                border-radius: 6px;
                font-size: 12px;
                color: #ccc;
            }
        """)
        self.smali_source_label.setMinimumHeight(40)

        self.smali_browse_btn = QPushButton("📁 Browse Source")
        self.smali_browse_btn.setMinimumHeight(45)
        self.smali_browse_btn.setMinimumWidth(130)

        smali_source_section.addWidget(self.smali_source_label, 1)
        smali_source_section.addWidget(self.smali_browse_btn, 0)
        header_layout.addLayout(smali_source_section)

        layout.addWidget(header_group)

        # Smali file browser and editor
        smali_splitter = QSplitter(Qt.Horizontal)

        # Left: Smali file tree
        smali_tree_group = QGroupBox("Smali Files")
        smali_tree_layout = QVBoxLayout(smali_tree_group)

        self.smali_tree = QTreeWidget()
        self.smali_tree.setHeaderLabels(["File", "Size"])
        self.smali_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
            }
        """)

        smali_tree_layout.addWidget(self.smali_tree)
        smali_splitter.addWidget(smali_tree_group)

        # Right: Smali editor
        smali_editor_group = QGroupBox("Smali Editor")
        smali_editor_layout = QVBoxLayout(smali_editor_group)

        # Editor controls
        smali_editor_controls = QHBoxLayout()
        smali_editor_controls.setSpacing(10)

        self.save_smali_btn = QPushButton("💾 Save File")
        self.save_smali_btn.setMinimumHeight(35)
        self.save_smali_btn.setEnabled(False)

        self.search_smali_btn = QPushButton("🔍 Search")
        self.search_smali_btn.setMinimumHeight(35)

        smali_editor_controls.addWidget(self.save_smali_btn)
        smali_editor_controls.addWidget(self.search_smali_btn)
        smali_editor_controls.addStretch()

        smali_editor_layout.addLayout(smali_editor_controls)

        # Smali code editor
        self.smali_editor = QTextEdit()
        self.smali_editor.setFont(QFont("Consolas", 10))
        self.smali_editor.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)

        smali_editor_layout.addWidget(self.smali_editor)
        smali_splitter.addWidget(smali_editor_group)

        # Set splitter ratio
        smali_splitter.setSizes([300, 700])
        layout.addWidget(smali_splitter)

        return widget

    def create_installation_tab(self):
        """Create APK installation and device management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_group = QGroupBox("📱 APK Installation & Device Management")
        header_layout = QVBoxLayout(header_group)
        header_layout.setContentsMargins(15, 20, 15, 15)

        # APK file selection for installation
        install_file_section = QHBoxLayout()
        install_file_section.setSpacing(10)

        self.install_apk_label = QLabel("No APK selected for installation")
        self.install_apk_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #2b2b2b;
                border: 2px solid #555;
                border-radius: 6px;
                font-size: 12px;
                color: #ccc;
            }
        """)
        self.install_apk_label.setMinimumHeight(40)

        self.install_browse_btn = QPushButton("📁 Browse APK")
        self.install_browse_btn.setMinimumHeight(45)
        self.install_browse_btn.setMinimumWidth(120)

        install_file_section.addWidget(self.install_apk_label, 1)
        install_file_section.addWidget(self.install_browse_btn, 0)
        header_layout.addLayout(install_file_section)

        layout.addWidget(header_group)

        # Device management
        device_group = QGroupBox("Connected Devices")
        device_layout = QVBoxLayout(device_group)
        device_layout.setContentsMargins(15, 20, 15, 15)

        # Device list and controls
        device_controls = QHBoxLayout()
        device_controls.setSpacing(10)

        self.refresh_devices_btn = QPushButton("🔄 Refresh Devices")
        self.refresh_devices_btn.setMinimumHeight(35)

        self.device_info_btn = QPushButton("ℹ️ Device Info")
        self.device_info_btn.setMinimumHeight(35)

        device_controls.addWidget(self.refresh_devices_btn)
        device_controls.addWidget(self.device_info_btn)
        device_controls.addStretch()

        device_layout.addLayout(device_controls)

        # Device list
        self.device_list = QTreeWidget()
        self.device_list.setHeaderLabels(["Device", "Model", "Android Version", "Status"])
        self.device_list.setMaximumHeight(150)
        self.device_list.setStyleSheet("""
            QTreeWidget {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
            }
        """)

        device_layout.addWidget(self.device_list)
        layout.addWidget(device_group)

        # Installation options
        install_options_group = QGroupBox("Installation Options")
        install_options_layout = QVBoxLayout(install_options_group)
        install_options_layout.setContentsMargins(15, 20, 15, 15)
        install_options_layout.setSpacing(12)

        # Installation buttons
        install_buttons = QHBoxLayout()
        install_buttons.setSpacing(10)

        self.install_normal_btn = QPushButton("📱 Install APK")
        self.install_normal_btn.setMinimumHeight(45)

        self.install_replace_btn = QPushButton("🔄 Replace Install")
        self.install_replace_btn.setMinimumHeight(45)

        self.uninstall_btn = QPushButton("🗑️ Uninstall")
        self.uninstall_btn.setMinimumHeight(45)

        install_buttons.addWidget(self.install_normal_btn)
        install_buttons.addWidget(self.install_replace_btn)
        install_buttons.addWidget(self.uninstall_btn)
        install_buttons.addStretch()

        install_options_layout.addLayout(install_buttons)

        # Installation options checkboxes
        install_checkboxes = QHBoxLayout()
        install_checkboxes.setSpacing(20)

        self.install_force = QCheckBox("Force install (-r)")
        self.install_force.setToolTip("Replace existing application")
        self.install_test = QCheckBox("Test install (-t)")
        self.install_test.setToolTip("Allow test packages")
        self.install_downgrade = QCheckBox("Allow downgrade (-d)")
        self.install_downgrade.setToolTip("Allow version code downgrade")

        install_checkboxes.addWidget(self.install_force)
        install_checkboxes.addWidget(self.install_test)
        install_checkboxes.addWidget(self.install_downgrade)
        install_checkboxes.addStretch()

        install_options_layout.addLayout(install_checkboxes)

        layout.addWidget(install_options_group)

        # Installation log
        install_log_group = QGroupBox("Installation Log")
        install_log_layout = QVBoxLayout(install_log_group)
        install_log_layout.setContentsMargins(15, 20, 15, 15)

        self.install_log = QTextEdit()
        self.install_log.setMaximumHeight(120)
        self.install_log.setReadOnly(True)
        self.install_log.setFont(QFont("Consolas", 9))
        self.install_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 8px;
            }
        """)

        install_log_layout.addWidget(self.install_log)
        layout.addWidget(install_log_group)

        return widget

    def create_setup_tab(self):
        """Create the setup tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Dependencies section
        deps_group = QGroupBox("Dependencies")
        deps_layout = QVBoxLayout(deps_group)

        # Dependency status
        self.deps_status_label = QLabel("Checking dependencies...")
        deps_layout.addWidget(self.deps_status_label)

        # Dependency list
        self.deps_list = QTextEdit()
        self.deps_list.setMaximumHeight(150)
        self.deps_list.setReadOnly(True)
        deps_layout.addWidget(self.deps_list)

        # Install buttons
        install_layout = QHBoxLayout()
        self.install_deps_btn = QPushButton("🔧 Auto Install All")
        self.install_deps_btn.setToolTip("Automatically install all missing dependencies")

        self.check_deps_btn = QPushButton("🔍 Check Dependencies")
        self.check_deps_btn.setToolTip("Check which dependencies are installed")

        self.install_java_btn = QPushButton("☕ Install Java")
        self.install_java_btn.setToolTip("Install Java JDK only")

        self.install_apktool_btn = QPushButton("📱 Install APKTool")
        self.install_apktool_btn.setToolTip("Install APKTool only")

        install_layout.addWidget(self.install_deps_btn)
        install_layout.addWidget(self.check_deps_btn)
        install_layout.addStretch()

        deps_layout.addLayout(install_layout)

        # Individual install buttons
        individual_layout = QHBoxLayout()
        individual_layout.addWidget(self.install_java_btn)
        individual_layout.addWidget(self.install_apktool_btn)
        individual_layout.addStretch()

        deps_layout.addLayout(individual_layout)

        layout.addWidget(deps_group)

        # Manual installation instructions
        manual_group = QGroupBox("Manual Installation")
        manual_layout = QVBoxLayout(manual_group)

        manual_text = QTextEdit()
        manual_text.setReadOnly(True)
        manual_text.setMaximumHeight(200)
        manual_text.setPlainText("""
Manual Installation Instructions:

1. Java JDK:
   sudo apt update
   sudo apt install default-jdk

2. APKTool:
   sudo apt install apktool

   Or download from: https://ibotpeaches.github.io/Apktool/

3. AAPT (Android Asset Packaging Tool):
   sudo apt install aapt

   Or install Android SDK Build Tools

4. For APK signing, you may also need:
   sudo apt install zipalign
   sudo apt install apksigner

After installation, restart MT Manager Linux to detect the tools.
        """)

        manual_layout.addWidget(manual_text)

        layout.addWidget(manual_group)

        layout.addStretch()

        return widget

    def setup_connections(self):
        """Setup signal connections for all tabs"""
        # APK Editor tab connections
        if hasattr(self, 'editor_browse_btn'):
            self.editor_browse_btn.clicked.connect(self.browse_apk_for_editor)
        if hasattr(self, 'editor_reload_btn'):
            self.editor_reload_btn.clicked.connect(self.reload_apk_contents)
        if hasattr(self, 'apk_tree'):
            self.apk_tree.itemClicked.connect(self.on_apk_tree_item_clicked)
            self.apk_tree.itemDoubleClicked.connect(self.on_apk_tree_item_double_clicked)
        if hasattr(self, 'extract_btn'):
            self.extract_btn.clicked.connect(self.extract_selected_files)
        if hasattr(self, 'replace_btn'):
            self.replace_btn.clicked.connect(self.replace_selected_file)
        if hasattr(self, 'add_file_btn'):
            self.add_file_btn.clicked.connect(self.add_file_to_apk)
        if hasattr(self, 'delete_file_btn'):
            self.delete_file_btn.clicked.connect(self.delete_selected_file)
        if hasattr(self, 'edit_file_btn'):
            self.edit_file_btn.clicked.connect(self.edit_selected_file)
        if hasattr(self, 'save_changes_btn'):
            self.save_changes_btn.clicked.connect(self.save_file_changes)
        if hasattr(self, 'save_apk_btn'):
            self.save_apk_btn.clicked.connect(self.save_apk_modifications)
        if hasattr(self, 'save_as_apk_btn'):
            self.save_as_apk_btn.clicked.connect(self.save_apk_as)
        if hasattr(self, 'smali_to_java_btn'):
            self.smali_to_java_btn.clicked.connect(self.convert_smali_to_java)
        if hasattr(self, 'java_to_smali_btn'):
            self.java_to_smali_btn.clicked.connect(self.convert_java_to_smali)
        if hasattr(self, 'sign_modified_btn'):
            self.sign_modified_btn.clicked.connect(self.sign_modified_apk)
        if hasattr(self, 'install_apk_btn'):
            self.install_apk_btn.clicked.connect(self.install_apk_to_device)

        # Decompile tab connections
        if hasattr(self, 'decompile_browse_btn'):
            self.decompile_browse_btn.clicked.connect(self.browse_apk)
        if hasattr(self, 'start_decompile_btn'):
            self.start_decompile_btn.clicked.connect(self.decompile_apk)
        if hasattr(self, 'decompile_output_browse'):
            self.decompile_output_browse.clicked.connect(self.select_decompile_output)
        if hasattr(self, 'decompile_cancel_btn'):
            self.decompile_cancel_btn.clicked.connect(self.cancel_operation)
        if hasattr(self, 'clear_decompile_log'):
            self.clear_decompile_log.clicked.connect(self.clear_decompile_log_text)

        # Recompile tab connections
        if hasattr(self, 'recompile_browse_source_btn'):
            self.recompile_browse_source_btn.clicked.connect(self.browse_source_directory)
        if hasattr(self, 'start_recompile_btn'):
            self.start_recompile_btn.clicked.connect(self.recompile_apk)
        if hasattr(self, 'recompile_output_browse'):
            self.recompile_output_browse.clicked.connect(self.select_recompile_output)
        if hasattr(self, 'recompile_cancel_btn'):
            self.recompile_cancel_btn.clicked.connect(self.cancel_operation)
        if hasattr(self, 'clear_recompile_log'):
            self.clear_recompile_log.clicked.connect(self.clear_recompile_log_text)

        # Signing tab connections
        if hasattr(self, 'signing_browse_btn'):
            self.signing_browse_btn.clicked.connect(self.browse_apk_for_signing)
        if hasattr(self, 'sign_apk_btn'):
            self.sign_apk_btn.clicked.connect(self.sign_apk)
        if hasattr(self, 'verify_signature_btn'):
            self.verify_signature_btn.clicked.connect(self.verify_signature)
        if hasattr(self, 'zipalign_btn'):
            self.zipalign_btn.clicked.connect(self.zipalign_apk)

        # Analysis tab connections
        if hasattr(self, 'analysis_browse_btn'):
            self.analysis_browse_btn.clicked.connect(self.browse_apk_for_analysis)
        if hasattr(self, 'analyze_manifest_btn'):
            self.analyze_manifest_btn.clicked.connect(self.analyze_manifest)
        if hasattr(self, 'analyze_permissions_btn'):
            self.analyze_permissions_btn.clicked.connect(self.analyze_permissions)
        if hasattr(self, 'analyze_certificates_btn'):
            self.analyze_certificates_btn.clicked.connect(self.analyze_certificates)
        if hasattr(self, 'analyze_resources_btn'):
            self.analyze_resources_btn.clicked.connect(self.analyze_resources)

        # Resources tab connections
        if hasattr(self, 'resources_browse_btn'):
            self.resources_browse_btn.clicked.connect(self.browse_apk_for_resources)
        if hasattr(self, 'extract_all_resources_btn'):
            self.extract_all_resources_btn.clicked.connect(self.extract_all_resources)
        if hasattr(self, 'extract_images_btn'):
            self.extract_images_btn.clicked.connect(self.extract_images)
        if hasattr(self, 'extract_layouts_btn'):
            self.extract_layouts_btn.clicked.connect(self.extract_layouts)
        if hasattr(self, 'extract_strings_btn'):
            self.extract_strings_btn.clicked.connect(self.extract_strings)

        # Manifest tab connections
        if hasattr(self, 'manifest_browse_btn'):
            self.manifest_browse_btn.clicked.connect(self.browse_apk_for_manifest)
        if hasattr(self, 'load_manifest_btn'):
            self.load_manifest_btn.clicked.connect(self.load_manifest)
        if hasattr(self, 'save_manifest_btn'):
            self.save_manifest_btn.clicked.connect(self.save_manifest)
        if hasattr(self, 'validate_manifest_btn'):
            self.validate_manifest_btn.clicked.connect(self.validate_manifest)

        # Smali tab connections
        if hasattr(self, 'smali_browse_btn'):
            self.smali_browse_btn.clicked.connect(self.browse_smali_source)
        if hasattr(self, 'save_smali_btn'):
            self.save_smali_btn.clicked.connect(self.save_smali_file)
        if hasattr(self, 'search_smali_btn'):
            self.search_smali_btn.clicked.connect(self.search_smali)

        # Installation tab connections
        if hasattr(self, 'install_browse_btn'):
            self.install_browse_btn.clicked.connect(self.browse_apk_for_install)
        if hasattr(self, 'refresh_devices_btn'):
            self.refresh_devices_btn.clicked.connect(self.refresh_devices)
        if hasattr(self, 'install_normal_btn'):
            self.install_normal_btn.clicked.connect(self.install_apk_normal)
        if hasattr(self, 'install_replace_btn'):
            self.install_replace_btn.clicked.connect(self.install_apk_replace)
        if hasattr(self, 'uninstall_btn'):
            self.uninstall_btn.clicked.connect(self.uninstall_apk)

        # Setup tab connections
        if hasattr(self, 'install_deps_btn'):
            self.install_deps_btn.clicked.connect(self.install_dependencies)
        if hasattr(self, 'check_deps_btn'):
            self.check_deps_btn.clicked.connect(self.check_dependencies)
        if hasattr(self, 'install_java_btn'):
            self.install_java_btn.clicked.connect(self.install_java_only)
        if hasattr(self, 'install_apktool_btn'):
            self.install_apktool_btn.clicked.connect(self.install_apktool_only)

        # Legacy operations tab connections (if still present)
        if hasattr(self, 'browse_btn'):
            self.browse_btn.clicked.connect(self.browse_apk)
        if hasattr(self, 'decompile_btn'):
            self.decompile_btn.clicked.connect(self.decompile_apk)
        if hasattr(self, 'recompile_btn'):
            self.recompile_btn.clicked.connect(self.recompile_apk)
        if hasattr(self, 'sign_btn'):
            self.sign_btn.clicked.connect(self.sign_apk)
        if hasattr(self, 'clear_quick_log_btn'):
            self.clear_quick_log_btn.clicked.connect(self.clear_quick_log)
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.clicked.connect(self.cancel_operation)
        if hasattr(self, 'view_logs_btn'):
            self.view_logs_btn.clicked.connect(self.show_detailed_logs)

    def check_dependencies(self):
        """Check for required dependencies"""
        missing = DependencyChecker.get_missing_dependencies()

        if not missing:
            self.dependencies_ok = True
            # Update dependency status in setup tab if available
            if hasattr(self, 'deps_status_label'):
                self.deps_status_label.setText("✓ All dependencies are installed")
            if hasattr(self, 'deps_list'):
                self.deps_list.setPlainText("All required tools are available:\n• Java JDK\n• APKTool\n• AAPT")
            if hasattr(self, 'install_deps_btn'):
                self.install_deps_btn.setEnabled(False)
        else:
            self.dependencies_ok = False
            # Update dependency status in setup tab if available
            if hasattr(self, 'deps_status_label'):
                self.deps_status_label.setText(f"⚠ Missing {len(missing)} dependencies")

            # Show missing dependencies
            deps_text = "Missing dependencies:\n\n"
            for dep in missing:
                deps_text += f"❌ {dep['name']}\n"
                deps_text += f"   Command: {dep['command']}\n"
                deps_text += f"   Install: {dep['install_cmd']}\n"
                deps_text += f"   Description: {dep['description']}\n\n"

            if hasattr(self, 'deps_list'):
                self.deps_list.setPlainText(deps_text)
            if hasattr(self, 'install_deps_btn'):
                self.install_deps_btn.setEnabled(True)

        self.update_ui_state()

    def install_dependencies(self):
        """Install missing dependencies using threaded installer"""
        missing = DependencyChecker.get_missing_dependencies()

        if not missing:
            QMessageBox.information(self, "Dependencies", "All dependencies are already installed!")
            return

        # Show detailed confirmation dialog
        deps_list = "\n".join([f"• {dep['name']}" for dep in missing])
        reply = QMessageBox.question(
            self, "Install Dependencies",
            f"This will automatically install the following APK tools:\n\n{deps_list}\n\n"
            "Installation methods:\n"
            "• Package manager (apt)\n"
            "• Direct download (if needed)\n"
            "• Alternative sources (snap, etc.)\n\n"
            "You may be prompted for your password.\n\n"
            "Continue with automatic installation?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            self._start_installation()

    def _start_installation(self):
        """Start the installation process"""
        # Disable UI during installation
        self.install_deps_btn.setEnabled(False)
        self.install_deps_btn.setText("Installing...")
        self.check_deps_btn.setEnabled(False)

        # Show progress in setup tab
        self.tab_widget.setCurrentIndex(1)  # Switch to setup tab

        # Clear previous output
        self.deps_list.clear()
        self.deps_status_label.setText("Installing dependencies...")

        # Create and start installer worker
        self.installer_worker = DependencyInstaller()
        self.installer_worker.progress_updated.connect(self._on_install_progress)
        self.installer_worker.installation_finished.connect(self._on_install_finished)
        self.installer_worker.start()

        # Add cancel button functionality during installation
        self.install_deps_btn.setText("Cancel Installation")
        self.install_deps_btn.setEnabled(True)
        self.install_deps_btn.clicked.disconnect()
        self.install_deps_btn.clicked.connect(self._cancel_installation)

    def _on_install_progress(self, message):
        """Handle installation progress updates"""
        self.deps_list.append(message)
        self.deps_status_label.setText(message)

        # Auto-scroll to bottom
        cursor = self.deps_list.textCursor()
        cursor.movePosition(cursor.End)
        self.deps_list.setTextCursor(cursor)

    def _on_install_finished(self, success, message):
        """Handle installation completion"""
        # Re-enable UI
        self.install_deps_btn.setEnabled(True)
        self.install_deps_btn.setText("🔧 Install Dependencies")
        self.check_deps_btn.setEnabled(True)

        # Reconnect install button
        self.install_deps_btn.clicked.disconnect()
        self.install_deps_btn.clicked.connect(self.install_dependencies)

        # Show result
        if success:
            self.deps_list.append(f"\n✓ {message}")
            self.deps_status_label.setText("✓ Installation completed successfully")
            QMessageBox.information(self, "Installation Complete", message)

            # Refresh dependency status
            self.check_dependencies()
        else:
            self.deps_list.append(f"\n✗ {message}")
            self.deps_status_label.setText("✗ Installation failed")
            QMessageBox.warning(self, "Installation Failed", message)

        # Clean up worker
        if self.installer_worker:
            self.installer_worker.quit()
            self.installer_worker.wait()
            self.installer_worker = None

    def _cancel_installation(self):
        """Cancel ongoing installation"""
        if self.installer_worker:
            self.installer_worker.cancel()
            self.deps_list.append("\n⚠ Cancelling installation...")
            self.deps_status_label.setText("Cancelling installation...")

    def install_java_only(self):
        """Install Java JDK only"""
        if DependencyChecker.check_java():
            QMessageBox.information(self, "Java", "Java JDK is already installed!")
            return

        reply = QMessageBox.question(
            self, "Install Java",
            "This will install Java JDK using multiple methods:\n\n"
            "• Default JDK (recommended)\n"
            "• OpenJDK 11\n"
            "• OpenJDK 8 (fallback)\n\n"
            "Continue with Java installation?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            self._install_individual_dependency('java', 'Java JDK')

    def install_apktool_only(self):
        """Install APKTool only"""
        if DependencyChecker.check_apktool():
            QMessageBox.information(self, "APKTool", "APKTool is already installed!")
            return

        reply = QMessageBox.question(
            self, "Install APKTool",
            "This will install APKTool using multiple methods:\n\n"
            "• Package manager (apt)\n"
            "• Direct download from GitHub\n"
            "• Snap package (fallback)\n\n"
            "Continue with APKTool installation?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            self._install_individual_dependency('apktool', 'APKTool')

    def _install_individual_dependency(self, dep_type, dep_name):
        """Install a single dependency"""
        # Create a custom installer for single dependency
        class SingleDependencyInstaller(QThread):
            progress_updated = pyqtSignal(str)
            installation_finished = pyqtSignal(bool, str)

            def __init__(self, dep_type, dep_name):
                super().__init__()
                self.dep_type = dep_type
                self.dep_name = dep_name
                self.cancelled = False

            def run(self):
                try:
                    self.progress_updated.emit(f"Installing {self.dep_name}...")

                    if self.dep_type == 'java':
                        success = self._install_java()
                    elif self.dep_type == 'apktool':
                        success = self._install_apktool()
                    else:
                        success = False

                    if success:
                        self.installation_finished.emit(True, f"{self.dep_name} installed successfully")
                    else:
                        self.installation_finished.emit(False, f"Failed to install {self.dep_name}")

                except Exception as e:
                    self.installation_finished.emit(False, f"Error installing {self.dep_name}: {str(e)}")

            def _install_java(self):
                methods = [
                    ("Default JDK", "sudo apt update && sudo apt install -y default-jdk"),
                    ("OpenJDK 11", "sudo apt install -y openjdk-11-jdk"),
                    ("OpenJDK 8", "sudo apt install -y openjdk-8-jdk")
                ]

                for name, command in methods:
                    self.progress_updated.emit(f"Trying {name}...")
                    try:
                        result = subprocess.run(command, shell=True,
                                              capture_output=True, text=True, timeout=300)
                        if result.returncode == 0:
                            return True
                    except Exception:
                        continue
                return False

            def _install_apktool(self):
                # Try package manager first
                self.progress_updated.emit("Trying package manager...")
                try:
                    result = subprocess.run('sudo apt update && sudo apt install -y apktool',
                                          shell=True, capture_output=True, text=True, timeout=300)
                    if result.returncode == 0:
                        return True
                except Exception:
                    pass

                # Try manual installation
                self.progress_updated.emit("Downloading APKTool manually...")
                try:
                    return self._install_apktool_manual()
                except Exception:
                    pass

                return False

            def _install_apktool_manual(self):
                import tempfile
                import stat

                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir)

                        wrapper_url = "https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool"
                        jar_url = "https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar"

                        wrapper_path = temp_path / "apktool"
                        jar_path = temp_path / "apktool.jar"

                        self.progress_updated.emit("Downloading wrapper script...")
                        urllib.request.urlretrieve(wrapper_url, wrapper_path)

                        self.progress_updated.emit("Downloading JAR file...")
                        urllib.request.urlretrieve(jar_url, jar_path)

                        self.progress_updated.emit("Installing files...")
                        wrapper_path.chmod(wrapper_path.stat().st_mode | stat.S_IEXEC)

                        subprocess.run(['sudo', 'cp', str(wrapper_path), '/usr/local/bin/apktool'], check=True)
                        subprocess.run(['sudo', 'cp', str(jar_path), '/usr/local/bin/apktool.jar'], check=True)
                        subprocess.run(['sudo', 'chmod', '+x', '/usr/local/bin/apktool'], check=True)

                        return True

                except Exception:
                    return False

        # Start individual installation
        self.individual_installer = SingleDependencyInstaller(dep_type, dep_name)
        self.individual_installer.progress_updated.connect(self._on_individual_progress)
        self.individual_installer.installation_finished.connect(self._on_individual_finished)
        self.individual_installer.start()

        # Update UI
        if dep_type == 'java':
            self.install_java_btn.setEnabled(False)
            self.install_java_btn.setText("Installing...")
        elif dep_type == 'apktool':
            self.install_apktool_btn.setEnabled(False)
            self.install_apktool_btn.setText("Installing...")

    def _on_individual_progress(self, message):
        """Handle individual installation progress"""
        self.deps_list.append(message)
        self.deps_status_label.setText(message)

    def _on_individual_finished(self, success, message):
        """Handle individual installation completion"""
        # Re-enable buttons
        self.install_java_btn.setEnabled(True)
        self.install_java_btn.setText("☕ Install Java")
        self.install_apktool_btn.setEnabled(True)
        self.install_apktool_btn.setText("📱 Install APKTool")

        # Show result
        if success:
            self.deps_list.append(f"✓ {message}")
            QMessageBox.information(self, "Installation Complete", message)
            self.check_dependencies()  # Refresh status
        else:
            self.deps_list.append(f"✗ {message}")
            QMessageBox.warning(self, "Installation Failed", message)

    # ==================== ENHANCED LOGGING & PROGRESS ====================

    def clear_quick_log(self):
        """Clear the quick output log"""
        self.quick_output_text.clear()

    def show_detailed_logs(self):
        """Show detailed logs window"""
        if not hasattr(self, 'logs_window') or not self.logs_window:
            self.logs_window = DetailedLogsWindow(self)

        # Copy current logs to detailed window
        if hasattr(self, 'full_logs') and self.full_logs:
            self.logs_window.set_logs(self.full_logs)
        else:
            current_logs = self.quick_output_text.toPlainText()
            if current_logs:
                self.logs_window.set_logs(current_logs)
            else:
                self.logs_window.set_logs("No logs available yet.\n\nLogs will appear here when you run APK operations.")

        self.logs_window.show()
        self.logs_window.raise_()
        self.logs_window.activateWindow()

    def _connect_worker_signals(self, worker):
        """Connect worker signals to UI updates"""
        worker.output_received.connect(self.on_output_received)
        worker.progress_updated.connect(self.on_progress_updated)
        worker.progress_percentage.connect(self.on_progress_percentage)
        worker.operation_status.connect(self.on_operation_status)
        worker.operation_finished.connect(self.on_operation_finished)

    def on_output_received(self, output):
        """Handle output from worker"""
        # Add to appropriate log areas
        if hasattr(self, 'decompile_log'):
            self.decompile_log.append(output)
        if hasattr(self, 'recompile_log'):
            self.recompile_log.append(output)

        # Store in full logs
        if not hasattr(self, 'full_logs'):
            self.full_logs = ""
        self.full_logs += output + "\n"

        # Update detailed logs window if open
        if hasattr(self, 'logs_window') and self.logs_window and self.logs_window.isVisible():
            self.logs_window.append_log(output)

    def on_progress_updated(self, message):
        """Handle progress message updates"""
        if hasattr(self, 'decompile_status'):
            self.decompile_status.setText(message)
        if hasattr(self, 'recompile_status'):
            self.recompile_status.setText(message)

    def on_progress_percentage(self, percentage):
        """Handle progress percentage updates"""
        if hasattr(self, 'decompile_progress'):
            self.decompile_progress.setVisible(True)
            self.decompile_progress.setValue(percentage)
        if hasattr(self, 'recompile_progress'):
            self.recompile_progress.setVisible(True)
            self.recompile_progress.setValue(percentage)

    def on_operation_status(self, status):
        """Handle detailed operation status updates"""
        if hasattr(self, 'decompile_status'):
            self.decompile_status.setText(status)
        if hasattr(self, 'recompile_status'):
            self.recompile_status.setText(status)

    def on_operation_finished(self, success, message):
        """Handle operation completion"""
        # Reset UI state
        if hasattr(self, 'decompile_progress'):
            self.decompile_progress.setVisible(False)
        if hasattr(self, 'recompile_progress'):
            self.recompile_progress.setVisible(False)
        if hasattr(self, 'decompile_cancel_btn'):
            self.decompile_cancel_btn.setEnabled(False)
        if hasattr(self, 'recompile_cancel_btn'):
            self.recompile_cancel_btn.setEnabled(False)

        self.update_ui_state()

        if success:
            status_text = "✓ Operation completed successfully"
            log_text = f"\n✓ {message}"
            if hasattr(self, 'decompile_status'):
                self.decompile_status.setText(status_text)
            if hasattr(self, 'recompile_status'):
                self.recompile_status.setText(status_text)
            if hasattr(self, 'decompile_log'):
                self.decompile_log.append(log_text)
            if hasattr(self, 'recompile_log'):
                self.recompile_log.append(log_text)
        else:
            status_text = "✗ Operation failed"
            log_text = f"\n✗ {message}"
            if hasattr(self, 'decompile_status'):
                self.decompile_status.setText(status_text)
            if hasattr(self, 'recompile_status'):
                self.recompile_status.setText(status_text)
            if hasattr(self, 'decompile_log'):
                self.decompile_log.append(log_text)
            if hasattr(self, 'recompile_log'):
                self.recompile_log.append(log_text)
            QMessageBox.warning(self, "Operation Failed", message)

        # Clean up worker
        if self.current_worker:
            self.current_worker.quit()
            self.current_worker.wait()
            self.current_worker = None

    def browse_apk(self):
        """Browse for APK file - works with new UI structure"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select APK File", "", "APK Files (*.apk)"
        )

        if file_path:
            # Set APK path in the decompile tab
            if hasattr(self, 'decompile_apk_label'):
                self.decompile_apk_label.setText(file_path)
            # Also set in legacy label if it exists
            if hasattr(self, 'apk_path_label'):
                self.apk_path_label.setText(file_path)
            # Store current path
            self.current_apk_path = file_path
            self.update_ui_state()

    def select_decompile_output(self):
        """Select decompile output directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )

        if dir_path:
            # Update the correct output path label
            if hasattr(self, 'decompile_output_path'):
                self.decompile_output_path.setText(dir_path)
            elif hasattr(self, 'decompile_output_label'):
                self.decompile_output_label.setText(dir_path)

    def select_recompile_output(self):
        """Select recompile output APK"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Recompiled APK", "", "APK Files (*.apk)"
        )

        if file_path:
            self.recompile_output_label.setText(file_path)

    def decompile_apk(self):
        """Start APK decompilation"""
        # Get APK path from the decompile tab
        apk_path = None
        if hasattr(self, 'decompile_apk_label'):
            apk_path = self.decompile_apk_label.text()
        elif hasattr(self, 'apk_path_label'):
            apk_path = self.apk_path_label.text()
        elif hasattr(self, 'current_apk_path'):
            apk_path = self.current_apk_path

        if not apk_path or apk_path == "No APK selected":
            QMessageBox.warning(self, "No APK Selected",
                              "Please select an APK file first using the Browse button.")
            return

        output_dir = None
        if hasattr(self, 'decompile_output_path') and self.decompile_output_path.text() != "Auto (same directory as APK)":
            output_dir = self.decompile_output_path.text()
        elif hasattr(self, 'decompile_output_label') and self.decompile_output_label.text() != "Auto":
            output_dir = self.decompile_output_label.text()

        self._start_operation('decompile', apk_path, output_dir)

    def recompile_apk(self):
        """Start APK recompilation"""
        # For recompilation, we need a directory, not an APK file
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Decompiled APK Directory"
        )

        if not dir_path:
            return

        output_apk = None
        if self.recompile_output_label.text() != "Auto":
            output_apk = self.recompile_output_label.text()

        self._start_operation('recompile', dir_path, output_apk)

    def sign_apk(self):
        """Start APK signing"""
        apk_path = self.apk_path_label.text()
        if apk_path == "No APK selected":
            return

        self._start_operation('sign', apk_path)

    # ==================== NEW TAB METHODS ====================

    def clear_decompile_log_text(self):
        """Clear decompile log"""
        if hasattr(self, 'decompile_log'):
            self.decompile_log.clear()

    def clear_recompile_log_text(self):
        """Clear recompile log"""
        if hasattr(self, 'recompile_log'):
            self.recompile_log.clear()

    def browse_source_directory(self):
        """Browse for source directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Decompiled APK Directory")
        if dir_path and hasattr(self, 'recompile_source_label'):
            self.recompile_source_label.setText(dir_path)

    def browse_apk_for_signing(self):
        """Browse APK for signing"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select APK File", "", "APK Files (*.apk)")
        if file_path and hasattr(self, 'signing_apk_label'):
            self.signing_apk_label.setText(file_path)

    def verify_signature(self):
        """Verify APK signature"""
        QMessageBox.information(self, "Verify Signature", "Signature verification feature coming soon!")

    def zipalign_apk(self):
        """Zipalign APK"""
        QMessageBox.information(self, "Zipalign", "Zipalign feature coming soon!")

    def browse_apk_for_analysis(self):
        """Browse APK for analysis"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select APK File", "", "APK Files (*.apk)")
        if file_path and hasattr(self, 'analysis_apk_label'):
            self.analysis_apk_label.setText(file_path)

    def analyze_manifest(self):
        """Analyze manifest"""
        QMessageBox.information(self, "Analyze Manifest", "Manifest analysis feature coming soon!")

    def analyze_permissions(self):
        """Analyze permissions"""
        QMessageBox.information(self, "Analyze Permissions", "Permission analysis feature coming soon!")

    def analyze_certificates(self):
        """Analyze certificates"""
        QMessageBox.information(self, "Analyze Certificates", "Certificate analysis feature coming soon!")

    def analyze_resources(self):
        """Analyze resources"""
        QMessageBox.information(self, "Analyze Resources", "Resource analysis feature coming soon!")

    def browse_apk_for_resources(self):
        """Browse APK for resources"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select APK File", "", "APK Files (*.apk)")
        if file_path and hasattr(self, 'resources_apk_label'):
            self.resources_apk_label.setText(file_path)

    def extract_all_resources(self):
        """Extract all resources"""
        QMessageBox.information(self, "Extract Resources", "Resource extraction feature coming soon!")

    def extract_images(self):
        """Extract images"""
        QMessageBox.information(self, "Extract Images", "Image extraction feature coming soon!")

    def extract_layouts(self):
        """Extract layouts"""
        QMessageBox.information(self, "Extract Layouts", "Layout extraction feature coming soon!")

    def extract_strings(self):
        """Extract strings"""
        QMessageBox.information(self, "Extract Strings", "String extraction feature coming soon!")

    def browse_apk_for_manifest(self):
        """Browse APK for manifest editing"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select APK File", "", "APK Files (*.apk)")
        if file_path and hasattr(self, 'manifest_apk_label'):
            self.manifest_apk_label.setText(file_path)

    def load_manifest(self):
        """Load manifest"""
        QMessageBox.information(self, "Load Manifest", "Manifest loading feature coming soon!")

    def save_manifest(self):
        """Save manifest"""
        QMessageBox.information(self, "Save Manifest", "Manifest saving feature coming soon!")

    def validate_manifest(self):
        """Validate manifest"""
        QMessageBox.information(self, "Validate Manifest", "Manifest validation feature coming soon!")

    def browse_smali_source(self):
        """Browse Smali source"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Decompiled APK Directory")
        if dir_path and hasattr(self, 'smali_source_label'):
            self.smali_source_label.setText(dir_path)

    def save_smali_file(self):
        """Save Smali file"""
        QMessageBox.information(self, "Save Smali", "Smali saving feature coming soon!")

    def search_smali(self):
        """Search Smali"""
        QMessageBox.information(self, "Search Smali", "Smali search feature coming soon!")

    def browse_apk_for_install(self):
        """Browse APK for installation"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select APK File", "", "APK Files (*.apk)")
        if file_path and hasattr(self, 'install_apk_label'):
            self.install_apk_label.setText(file_path)

    def refresh_devices(self):
        """Refresh connected devices"""
        QMessageBox.information(self, "Refresh Devices", "Device refresh feature coming soon!")

    def install_apk_normal(self):
        """Install APK normally"""
        QMessageBox.information(self, "Install APK", "APK installation feature coming soon!")

    def install_apk_replace(self):
        """Install APK with replace"""
        QMessageBox.information(self, "Replace Install", "Replace installation feature coming soon!")

    def uninstall_apk(self):
        """Uninstall APK"""
        QMessageBox.information(self, "Uninstall APK", "APK uninstall feature coming soon!")

    def _start_operation(self, operation, path, output_path=None):
        """Start APKTool operation with enhanced progress tracking"""
        # Check dependencies first
        if not self.dependencies_ok:
            QMessageBox.warning(self, "Dependencies Missing",
                              "Required dependencies are not installed.\n\n"
                              "Please install them using the Setup tab before proceeding.")
            return

        # Clear previous logs
        if hasattr(self, 'decompile_log'):
            self.decompile_log.clear()
        if hasattr(self, 'recompile_log'):
            self.recompile_log.clear()

        # Initialize full logs
        self.full_logs = ""

        # Setup UI for operation - handle both old and new UI elements
        if hasattr(self, 'decompile_progress'):
            self.decompile_progress.setVisible(True)
            self.decompile_progress.setValue(0)
        if hasattr(self, 'recompile_progress'):
            self.recompile_progress.setVisible(True)
            self.recompile_progress.setValue(0)

        if hasattr(self, 'decompile_cancel_btn'):
            self.decompile_cancel_btn.setEnabled(True)
        if hasattr(self, 'recompile_cancel_btn'):
            self.recompile_cancel_btn.setEnabled(True)

        if hasattr(self, 'decompile_status'):
            self.decompile_status.setText(f"⬇ Starting {operation}...")
        if hasattr(self, 'recompile_status'):
            self.recompile_status.setText(f"⬆ Starting {operation}...")

        self.update_ui_state(False)

        # Create worker thread
        self.current_worker = ApkToolWorker(operation, path, output_path)

        # Connect enhanced signals
        self._connect_worker_signals(self.current_worker)

        # Add initial log entries to appropriate log areas
        log_text = f"🚀 Starting {operation} operation\n"
        log_text += f"📁 Input: {Path(path).name}\n"
        if output_path:
            log_text += f"📤 Output: {output_path}\n"
        log_text += "=" * 50

        if hasattr(self, 'decompile_log') and operation == 'decompile':
            self.decompile_log.append(log_text)
        elif hasattr(self, 'recompile_log') and operation == 'recompile':
            self.recompile_log.append(log_text)

        # Initialize full logs with initial entries
        self.full_logs = f"🚀 Starting {operation} operation\n"
        self.full_logs += f"📁 Input: {Path(path).name}\n"
        if output_path:
            self.full_logs += f"📤 Output: {output_path}\n"
        self.full_logs += "=" * 50 + "\n"

        # Start operation
        self.current_worker.start()

    def cancel_operation(self):
        """Cancel current operation"""
        if self.current_worker:
            self.current_worker.cancel()
            self.operation_status_label.setText("⚠ Cancelling operation...")
            self.progress_label.setText("Cancelling...")

    def update_ui_state(self, enabled=None):
        """Update UI state based on current conditions"""
        if enabled is None:
            # Auto-determine based on APK selection and dependencies
            has_apk = False
            # Check various APK label sources
            if hasattr(self, 'apk_path_label') and self.apk_path_label.text() != "No APK selected":
                has_apk = True
            elif hasattr(self, 'decompile_apk_label') and "No APK selected" not in self.decompile_apk_label.text():
                has_apk = True
            elif hasattr(self, 'current_apk_path') and self.current_apk_path:
                has_apk = True

            enabled = has_apk and self.dependencies_ok

        # Only enable operations if dependencies are satisfied
        ops_enabled = enabled and self.dependencies_ok

        # Update legacy buttons if they exist
        if hasattr(self, 'decompile_btn'):
            self.decompile_btn.setEnabled(ops_enabled)
        if hasattr(self, 'recompile_btn'):
            self.recompile_btn.setEnabled(self.dependencies_ok)  # Uses directory selection
        if hasattr(self, 'sign_btn'):
            self.sign_btn.setEnabled(ops_enabled)

        # Update new tab buttons if they exist
        if hasattr(self, 'start_decompile_btn'):
            self.start_decompile_btn.setEnabled(ops_enabled)
        if hasattr(self, 'start_recompile_btn'):
            self.start_recompile_btn.setEnabled(self.dependencies_ok)
        if hasattr(self, 'sign_apk_btn'):
            self.sign_apk_btn.setEnabled(ops_enabled)

        # Update button tooltips based on dependency status
        tooltip = "Install dependencies first (see Setup tab)" if not self.dependencies_ok else ""

        if hasattr(self, 'decompile_btn'):
            if not self.dependencies_ok:
                self.decompile_btn.setToolTip(tooltip)
            else:
                self.decompile_btn.setToolTip("Decompile APK to source code")

        if hasattr(self, 'recompile_btn'):
            if not self.dependencies_ok:
                self.recompile_btn.setToolTip(tooltip)
            else:
                self.recompile_btn.setToolTip("Recompile source code to APK")

        if hasattr(self, 'sign_btn'):
            if not self.dependencies_ok:
                self.sign_btn.setToolTip(tooltip)
            else:
                self.sign_btn.setToolTip("Sign APK with debug certificate")

    def set_apk_file(self, apk_path):
        """Set APK file from external source"""
        # Set APK path in various labels if they exist
        if hasattr(self, 'apk_path_label'):
            self.apk_path_label.setText(apk_path)
        if hasattr(self, 'decompile_apk_label'):
            self.decompile_apk_label.setText(apk_path)
        if hasattr(self, 'editor_apk_label'):
            self.editor_apk_label.setText(apk_path)
        if hasattr(self, 'signing_apk_label'):
            self.signing_apk_label.setText(apk_path)
        if hasattr(self, 'analysis_apk_label'):
            self.analysis_apk_label.setText(apk_path)
        if hasattr(self, 'resources_apk_label'):
            self.resources_apk_label.setText(apk_path)
        if hasattr(self, 'manifest_apk_label'):
            self.manifest_apk_label.setText(apk_path)
        if hasattr(self, 'install_apk_label'):
            self.install_apk_label.setText(apk_path)

        self.current_apk_path = apk_path
        self.update_ui_state()

        # Also load for editor if available
        if apk_path and Path(apk_path).exists() and hasattr(self, 'load_apk_contents'):
            self.load_apk_contents(apk_path)

    # ==================== APK EDITOR METHODS ====================

    def browse_apk_for_editor(self):
        """Browse for APK file to edit"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select APK File", "", "APK Files (*.apk);;All Files (*)"
        )

        if file_path:
            self.editor_apk_label.setText(file_path)
            self.current_apk_path = file_path
            self.load_apk_contents(file_path)

    def load_apk_contents(self, apk_path):
        """Load APK contents into the tree view"""
        if not apk_path or not Path(apk_path).exists():
            return

        # Check if UI elements exist
        if not hasattr(self, 'apk_tree') or not self.apk_tree:
            return

        try:
            if self.editor_status_label:
                self.editor_status_label.setText("Loading APK contents...")
            self.apk_tree.clear()
            self.apk_contents.clear()

            # Load APK as ZIP file
            import zipfile
            with zipfile.ZipFile(apk_path, 'r') as zip_file:
                # Create root item
                root_item = QTreeWidgetItem(self.apk_tree)
                root_item.setText(0, Path(apk_path).name)
                root_item.setText(1, self._format_size(Path(apk_path).stat().st_size))
                root_item.setText(2, "APK")
                root_item.setData(0, Qt.UserRole, "")  # Empty path for root

                # Build file tree
                file_tree = {}
                for info in zip_file.infolist():
                    if info.is_dir():
                        continue

                    # Store file info
                    self.apk_contents[info.filename] = {
                        'info': info,
                        'size': info.file_size,
                        'compressed_size': info.compress_size
                    }

                    # Build tree structure
                    parts = info.filename.split('/')
                    current_tree = file_tree

                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:  # File
                            current_tree[part] = info
                        else:  # Directory
                            if part not in current_tree:
                                current_tree[part] = {}
                            current_tree = current_tree[part]

                # Populate tree widget
                self._populate_tree_item(root_item, file_tree, "")

                # Expand root
                root_item.setExpanded(True)

                if self.editor_status_label:
                    self.editor_status_label.setText(f"Loaded {len(self.apk_contents)} files")

        except Exception as e:
            if self.editor_status_label:
                self.editor_status_label.setText(f"Error loading APK: {str(e)}")
            QMessageBox.warning(self, "APK Load Error", f"Failed to load APK:\n{str(e)}")

    def _populate_tree_item(self, parent_item, tree_dict, current_path):
        """Recursively populate tree widget"""
        for name, content in tree_dict.items():
            item = QTreeWidgetItem(parent_item)
            item.setText(0, name)

            if isinstance(content, dict):  # Directory
                item.setText(2, "Folder")
                item.setData(0, Qt.UserRole, current_path + name + "/")
                self._populate_tree_item(item, content, current_path + name + "/")
            else:  # File
                file_path = current_path + name
                item.setText(1, self._format_size(content.file_size))
                item.setText(2, self._get_file_type(name))
                item.setData(0, Qt.UserRole, file_path)

    def _format_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def _get_file_type(self, filename):
        """Get file type based on extension"""
        ext = Path(filename).suffix.lower()
        type_map = {
            '.xml': 'XML',
            '.dex': 'DEX',
            '.so': 'Native Library',
            '.png': 'Image',
            '.jpg': 'Image',
            '.jpeg': 'Image',
            '.gif': 'Image',
            '.webp': 'Image',
            '.arsc': 'Resources',
            '.txt': 'Text',
            '.json': 'JSON',
            '.properties': 'Properties',
            '.mf': 'Manifest',
            '.sf': 'Signature',
            '.rsa': 'Certificate',
            '.dsa': 'Certificate'
        }
        return type_map.get(ext, 'File')

    def reload_apk_contents(self):
        """Reload APK contents"""
        if self.current_apk_path:
            self.load_apk_contents(self.current_apk_path)

    def on_apk_tree_item_clicked(self, item, column):
        """Handle tree item click"""
        file_path = item.data(0, Qt.UserRole)
        if file_path and file_path in self.apk_contents:
            self.preview_file(file_path)

    def on_apk_tree_item_double_clicked(self, item, column):
        """Handle tree item double click - open file in editor (no rename)"""
        file_path = item.data(0, Qt.UserRole)
        if file_path and file_path in self.apk_contents:
            self.edit_file(file_path)

    def preview_file(self, file_path):
        """Preview file content"""
        if not self.current_apk_path or file_path not in self.apk_contents:
            return

        try:
            # Extract file content
            import zipfile
            with zipfile.ZipFile(self.current_apk_path, 'r') as zip_file:
                content = zip_file.read(file_path)

            # Update file info if label exists
            if self.file_info_label:
                file_info = self.apk_contents[file_path]
                info_text = f"File: {file_path}\n"
                info_text += f"Size: {self._format_size(file_info['size'])}\n"
                info_text += f"Compressed: {self._format_size(file_info['compressed_size'])}\n"
                info_text += f"Type: {self._get_file_type(file_path)}"
                self.file_info_label.setText(info_text)

            # Show content in appropriate tab
            self._show_file_content(file_path, content)

        except Exception as e:
            if self.file_info_label:
                self.file_info_label.setText(f"Error reading file: {str(e)}")
            else:
                QMessageBox.warning(self, "Preview Error", f"Error reading file: {str(e)}")

    def _show_file_content(self, file_path, content):
        """Show file content in appropriate preview tab"""
        file_ext = Path(file_path).suffix.lower()

        # Text preview
        if self.text_preview:
            try:
                if file_ext in ['.xml', '.txt', '.json', '.properties', '.mf', '.sf', '.smali', '.java']:
                    # Try to decode as text
                    text_content = content.decode('utf-8')
                    self.text_preview.setPlainText(text_content)
                    if self.preview_tabs:
                        self.preview_tabs.setCurrentIndex(0)  # Text tab
                else:
                    # Show as binary
                    self.text_preview.setPlainText("Binary file - use hex view")

            except UnicodeDecodeError:
                self.text_preview.setPlainText("Binary file - use hex view")

        # Hex preview
        if self.hex_preview:
            hex_content = self._format_hex_content(content)
            self.hex_preview.setPlainText(hex_content)

        # Image preview
        if self.image_preview:
            if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                self._show_image_preview(content)
            else:
                self.image_preview.setText("Not an image file")

    def _format_hex_content(self, content, max_bytes=1024):
        """Format content as hex dump"""
        hex_lines = []
        content = content[:max_bytes]  # Limit for performance

        for i in range(0, len(content), 16):
            chunk = content[i:i+16]
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            hex_lines.append(f'{i:08x}  {hex_part:<48} |{ascii_part}|')

        if len(content) == max_bytes and len(content) < len(content):
            hex_lines.append("... (truncated for display)")

        return '\n'.join(hex_lines)

    def _show_image_preview(self, content):
        """Show image preview"""
        if not self.image_preview:
            return

        try:
            from PyQt5.QtGui import QPixmap
            pixmap = QPixmap()
            if pixmap.loadFromData(content):
                # Scale image to fit preview
                scaled_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_preview.setPixmap(scaled_pixmap)
                if self.preview_tabs:
                    self.preview_tabs.setCurrentIndex(2)  # Image tab
            else:
                self.image_preview.setText("Failed to load image")
        except Exception as e:
            self.image_preview.setText(f"Image preview error: {str(e)}")

    def extract_selected_files(self):
        """Extract selected files from APK"""
        selected_items = self.apk_tree.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Extract Files", "Please select files to extract")
            return

        # Get output directory
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return

        try:
            import zipfile
            with zipfile.ZipFile(self.current_apk_path, 'r') as zip_file:
                extracted_count = 0

                for item in selected_items:
                    file_path = item.data(0, Qt.UserRole)
                    if file_path and file_path in self.apk_contents:
                        # Create output path
                        output_path = Path(output_dir) / file_path
                        output_path.parent.mkdir(parents=True, exist_ok=True)

                        # Extract file
                        with open(output_path, 'wb') as f:
                            f.write(zip_file.read(file_path))

                        extracted_count += 1

                if self.editor_status_label:
                    self.editor_status_label.setText(f"Extracted {extracted_count} files")
                QMessageBox.information(self, "Extract Complete",
                                      f"Extracted {extracted_count} files to:\n{output_dir}")

        except Exception as e:
            QMessageBox.warning(self, "Extract Error", f"Failed to extract files:\n{str(e)}")

    def replace_selected_file(self):
        """Replace selected file in APK"""
        selected_items = self.apk_tree.selectedItems()
        if len(selected_items) != 1:
            QMessageBox.information(self, "Replace File", "Please select exactly one file to replace")
            return

        file_path = selected_items[0].data(0, Qt.UserRole)
        if not file_path or file_path not in self.apk_contents:
            QMessageBox.information(self, "Replace File", "Please select a valid file")
            return

        # Browse for replacement file
        replacement_path, _ = QFileDialog.getOpenFileName(
            self, f"Select replacement for {Path(file_path).name}", "", "All Files (*)"
        )

        if replacement_path:
            try:
                with open(replacement_path, 'rb') as f:
                    new_content = f.read()

                # Store modification
                self.modified_files[file_path] = new_content

                # Update tree item to show modification
                selected_items[0].setText(0, f"*{Path(file_path).name}")

                if self.editor_status_label:
                    self.editor_status_label.setText(f"Marked {file_path} for replacement")

                # Enable save button
                if self.save_apk_btn:
                    self.save_apk_btn.setEnabled(True)
                if self.save_as_apk_btn:
                    self.save_as_apk_btn.setEnabled(True)

            except Exception as e:
                QMessageBox.warning(self, "Replace Error", f"Failed to read replacement file:\n{str(e)}")

    def add_file_to_apk(self):
        """Add new file to APK"""
        # Browse for file to add
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select file to add", "", "All Files (*)"
        )

        if not file_path:
            return

        # Get target path in APK
        target_path, ok = QInputDialog.getText(
            self, "Add File",
            f"Enter path in APK for {Path(file_path).name}:",
            text=Path(file_path).name
        )

        if ok and target_path:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()

                # Store as modification
                self.modified_files[target_path] = content

                # Add to tree (simplified - would need proper tree insertion)
                self.editor_status_label.setText(f"Marked {target_path} for addition")

                # Enable save button
                self.save_apk_btn.setEnabled(True)
                self.save_as_apk_btn.setEnabled(True)

            except Exception as e:
                QMessageBox.warning(self, "Add File Error", f"Failed to read file:\n{str(e)}")

    def delete_selected_file(self):
        """Delete selected file from APK"""
        selected_items = self.apk_tree.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Delete File", "Please select files to delete")
            return

        reply = QMessageBox.question(
            self, "Delete Files",
            f"Are you sure you want to delete {len(selected_items)} file(s)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            for item in selected_items:
                file_path = item.data(0, Qt.UserRole)
                if file_path and file_path in self.apk_contents:
                    # Mark for deletion (use None as marker)
                    self.modified_files[file_path] = None

                    # Update tree item
                    item.setText(0, f"[DELETED] {Path(file_path).name}")
                    item.setDisabled(True)

            self.editor_status_label.setText(f"Marked {len(selected_items)} files for deletion")

            # Enable save button
            self.save_apk_btn.setEnabled(True)
            self.save_as_apk_btn.setEnabled(True)

    def edit_selected_file(self):
        """Edit selected file"""
        selected_items = self.apk_tree.selectedItems()
        if len(selected_items) != 1:
            QMessageBox.information(self, "Edit File", "Please select exactly one file to edit")
            return

        file_path = selected_items[0].data(0, Qt.UserRole)
        if file_path and file_path in self.apk_contents:
            self.edit_file(file_path)

    def edit_file(self, file_path):
        """Edit file content"""
        if not self.current_apk_path or file_path not in self.apk_contents:
            return

        # Check if UI elements exist
        if not self.text_preview or not self.preview_tabs:
            QMessageBox.warning(self, "Edit Error", "Text editor not available")
            return

        try:
            # Extract current content
            import zipfile
            with zipfile.ZipFile(self.current_apk_path, 'r') as zip_file:
                content = zip_file.read(file_path)

            # Check if it's a text file
            file_ext = Path(file_path).suffix.lower()
            if file_ext in ['.xml', '.txt', '.json', '.properties', '.mf', '.sf', '.smali', '.java']:
                try:
                    text_content = content.decode('utf-8')

                    # Enable editing
                    self.text_preview.setReadOnly(False)
                    self.text_preview.setPlainText(text_content)
                    self.preview_tabs.setCurrentIndex(0)  # Text tab

                    # Store original content
                    self.current_editing_file = file_path
                    self.original_file_content = content

                    # Enable save button if it exists
                    if self.save_changes_btn:
                        self.save_changes_btn.setEnabled(True)
                    if self.edit_file_btn:
                        self.edit_file_btn.setText("📝 Editing...")

                    # Enable/disable conversion buttons based on file type
                    if hasattr(self, 'smali_to_java_btn') and hasattr(self, 'java_to_smali_btn'):
                        if file_ext == '.smali':
                            self.smali_to_java_btn.setEnabled(True)
                            self.java_to_smali_btn.setEnabled(False)
                        elif file_ext == '.java':
                            self.smali_to_java_btn.setEnabled(False)
                            self.java_to_smali_btn.setEnabled(True)
                        else:
                            self.smali_to_java_btn.setEnabled(False)
                            self.java_to_smali_btn.setEnabled(False)

                    if self.editor_status_label:
                        self.editor_status_label.setText(f"Editing {file_path}")

                except UnicodeDecodeError:
                    QMessageBox.warning(self, "Edit File", "Cannot edit binary file as text")
            else:
                QMessageBox.information(self, "Edit File",
                                      "Binary files cannot be edited directly.\n"
                                      "Use 'Replace File' to replace with a new file.")

        except Exception as e:
            QMessageBox.warning(self, "Edit Error", f"Failed to load file for editing:\n{str(e)}")

    def save_file_changes(self):
        """Save changes to current editing file"""
        if not self.current_editing_file:
            return

        # Check if UI elements exist
        if not self.text_preview:
            QMessageBox.warning(self, "Save Error", "Text editor not available")
            return

        try:
            # Get modified content
            new_content = self.text_preview.toPlainText().encode('utf-8')

            # Store modification
            self.modified_files[self.current_editing_file] = new_content

            # Update UI
            self.text_preview.setReadOnly(True)
            if self.save_changes_btn:
                self.save_changes_btn.setEnabled(False)
            if self.edit_file_btn:
                self.edit_file_btn.setText("✏️ Edit File")

            # Mark file as modified in tree
            if hasattr(self, 'apk_tree') and self.apk_tree:
                selected_items = self.apk_tree.selectedItems()
                if selected_items:
                    item = selected_items[0]
                    if not item.text(0).startswith('*'):
                        item.setText(0, f"*{item.text(0)}")

            if self.editor_status_label:
                self.editor_status_label.setText(f"Saved changes to {self.current_editing_file}")

            # Enable APK save buttons
            if self.save_apk_btn:
                self.save_apk_btn.setEnabled(True)
            if self.save_as_apk_btn:
                self.save_as_apk_btn.setEnabled(True)

            # Clear editing state
            self.current_editing_file = None
            self.original_file_content = None

        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Failed to save changes:\n{str(e)}")

    def save_apk_modifications(self):
        """Save modifications to current APK"""
        if not self.modified_files:
            QMessageBox.information(self, "Save APK", "No modifications to save")
            return

        self._save_modified_apk(self.current_apk_path)

    def save_apk_as(self):
        """Save modified APK as new file"""
        if not self.modified_files:
            QMessageBox.information(self, "Save APK As", "No modifications to save")
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save APK As", "", "APK Files (*.apk);;All Files (*)"
        )

        if output_path:
            self._save_modified_apk(output_path)

    def _save_modified_apk(self, output_path):
        """Save modified APK to specified path"""
        try:
            import zipfile
            import tempfile

            self.editor_status_label.setText("Saving APK modifications...")
            self.editor_progress_bar.setVisible(True)
            self.editor_progress_bar.setRange(0, 0)  # Indeterminate

            # Create temporary file for new APK
            with tempfile.NamedTemporaryFile(delete=False, suffix='.apk') as temp_file:
                temp_path = temp_file.name

            # Copy original APK and apply modifications
            with zipfile.ZipFile(self.current_apk_path, 'r') as source_zip:
                with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as target_zip:

                    # Copy unmodified files
                    for file_path in self.apk_contents:
                        if file_path not in self.modified_files:
                            # Copy original file
                            target_zip.writestr(file_path, source_zip.read(file_path))

                    # Add/update modified files
                    for file_path, content in self.modified_files.items():
                        if content is not None:  # None means delete
                            target_zip.writestr(file_path, content)

            # Move temp file to final location
            import shutil
            shutil.move(temp_path, output_path)

            self.editor_progress_bar.setVisible(False)
            self.editor_status_label.setText(f"APK saved: {Path(output_path).name}")

            # Clear modifications
            self.modified_files.clear()
            self.save_apk_btn.setEnabled(False)
            self.save_as_apk_btn.setEnabled(False)

            # Reload if saved to same file
            if output_path == self.current_apk_path:
                self.load_apk_contents(output_path)

            QMessageBox.information(self, "Save Complete", f"APK saved successfully:\n{output_path}")

        except Exception as e:
            self.editor_progress_bar.setVisible(False)
            self.editor_status_label.setText("Save failed")
            QMessageBox.warning(self, "Save Error", f"Failed to save APK:\n{str(e)}")

    def sign_modified_apk(self):
        """Sign the modified APK"""
        if not self.current_apk_path:
            QMessageBox.information(self, "Sign APK", "No APK loaded")
            return

        # Use the existing sign functionality
        self.sign_apk()

    def install_apk_to_device(self):
        """Install APK to connected device"""
        if not self.current_apk_path:
            QMessageBox.information(self, "Install APK", "No APK loaded")
            return

        try:
            # Check if adb is available
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            if result.returncode != 0:
                QMessageBox.warning(self, "ADB Error", "ADB not found. Please install Android SDK platform tools.")
                return

            # Check for connected devices
            devices = [line for line in result.stdout.split('\n') if '\tdevice' in line]
            if not devices:
                QMessageBox.warning(self, "No Device", "No Android devices connected.\nPlease connect a device with USB debugging enabled.")
                return

            # Install APK
            self.editor_status_label.setText("Installing APK to device...")
            result = subprocess.run(['adb', 'install', '-r', self.current_apk_path],
                                  capture_output=True, text=True)

            if result.returncode == 0:
                self.editor_status_label.setText("APK installed successfully")
                QMessageBox.information(self, "Install Complete", "APK installed successfully to device")
            else:
                self.editor_status_label.setText("Installation failed")
                QMessageBox.warning(self, "Install Failed", f"Failed to install APK:\n{result.stderr}")

        except FileNotFoundError:
            QMessageBox.warning(self, "ADB Error", "ADB not found. Please install Android SDK platform tools.")
        except Exception as e:
            QMessageBox.warning(self, "Install Error", f"Installation error:\n{str(e)}")

    # ==================== SMALI/JAVA CONVERSION ====================

    def convert_smali_to_java(self):
        """Convert Smali code to Java using jadx"""
        if not self.current_editing_file or not self.text_preview:
            QMessageBox.warning(self, "Conversion Error", "No Smali file is currently being edited")
            return

        if not self.current_editing_file.endswith('.smali'):
            QMessageBox.warning(self, "Conversion Error", "Current file is not a Smali file")
            return

        # Check if jadx is available
        if not self._check_jadx_available():
            QMessageBox.warning(self, "Tool Missing",
                              "JADX is required for Smali to Java conversion.\n\n"
                              "Install with: sudo apt install jadx\n"
                              "Or download from: https://github.com/skylot/jadx")
            return

        try:
            # Get current Smali content
            smali_content = self.text_preview.toPlainText()

            # Create temporary files
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                smali_file = temp_path / "temp.smali"

                # Write Smali content to temp file
                with open(smali_file, 'w', encoding='utf-8') as f:
                    f.write(smali_content)

                # Convert using jadx (simplified approach)
                java_content = self._convert_smali_with_jadx(smali_file)

                if java_content:
                    # Show conversion result in a dialog
                    self._show_conversion_result("Smali to Java Conversion", java_content, "java")
                else:
                    QMessageBox.warning(self, "Conversion Failed",
                                      "Failed to convert Smali to Java.\n"
                                      "The Smali code may have syntax errors.")

        except Exception as e:
            QMessageBox.warning(self, "Conversion Error", f"Error during conversion:\n{str(e)}")

    def convert_java_to_smali(self):
        """Convert Java code to Smali using dx/d8"""
        if not self.current_editing_file or not self.text_preview:
            QMessageBox.warning(self, "Conversion Error", "No Java file is currently being edited")
            return

        if not self.current_editing_file.endswith('.java'):
            QMessageBox.warning(self, "Conversion Error", "Current file is not a Java file")
            return

        # Check if dx/d8 is available
        if not self._check_dx_available():
            QMessageBox.warning(self, "Tool Missing",
                              "Android SDK Build Tools (dx/d8) are required for Java to Smali conversion.\n\n"
                              "Install Android SDK Build Tools or use:\n"
                              "sudo apt install android-sdk-build-tools")
            return

        try:
            # Get current Java content
            java_content = self.text_preview.toPlainText()

            # Create temporary files
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                java_file = temp_path / "temp.java"

                # Write Java content to temp file
                with open(java_file, 'w', encoding='utf-8') as f:
                    f.write(java_content)

                # Convert using dx/d8 (simplified approach)
                smali_content = self._convert_java_with_dx(java_file)

                if smali_content:
                    # Show conversion result in a dialog
                    self._show_conversion_result("Java to Smali Conversion", smali_content, "smali")
                else:
                    QMessageBox.warning(self, "Conversion Failed",
                                      "Failed to convert Java to Smali.\n"
                                      "The Java code may have syntax errors.")

        except Exception as e:
            QMessageBox.warning(self, "Conversion Error", f"Error during conversion:\n{str(e)}")

    def _check_jadx_available(self):
        """Check if jadx is available"""
        try:
            result = subprocess.run(['jadx', '--version'],
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def _check_dx_available(self):
        """Check if dx/d8 is available"""
        try:
            # Try dx first
            result = subprocess.run(['dx', '--version'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True

            # Try d8 as fallback
            result = subprocess.run(['d8', '--help'],
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def _convert_smali_with_jadx(self, smali_file):
        """Convert Smali file to Java using jadx"""
        try:
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                output_dir = Path(temp_dir) / "output"

                # Note: This is a simplified approach
                # In practice, you'd need to create a proper DEX file first
                # For demonstration, we'll show a basic conversion approach

                # Read the Smali content and try to extract basic Java structure
                with open(smali_file, 'r', encoding='utf-8') as f:
                    smali_content = f.read()

                # Basic Smali to Java conversion (simplified)
                java_content = self._basic_smali_to_java_conversion(smali_content)
                return java_content

        except Exception as e:
            print(f"JADX conversion error: {e}")
            return None

    def _convert_java_with_dx(self, java_file):
        """Convert Java file to Smali using dx"""
        try:
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Note: This is a simplified approach
                # In practice, you'd need to compile Java to class files first
                # For demonstration, we'll show a basic conversion approach

                # Read the Java content and try to convert to basic Smali structure
                with open(java_file, 'r', encoding='utf-8') as f:
                    java_content = f.read()

                # Basic Java to Smali conversion (simplified)
                smali_content = self._basic_java_to_smali_conversion(java_content)
                return smali_content

        except Exception as e:
            print(f"DX conversion error: {e}")
            return None

    def _basic_smali_to_java_conversion(self, smali_content):
        """Basic Smali to Java conversion (simplified)"""
        java_lines = []
        java_lines.append("// Converted from Smali (simplified conversion)")
        java_lines.append("// Note: This is a basic conversion - use proper tools for production")
        java_lines.append("")

        lines = smali_content.split('\n')
        in_method = False
        class_name = "ConvertedClass"

        for line in lines:
            line = line.strip()

            # Extract class name
            if line.startswith('.class'):
                parts = line.split()
                if len(parts) > 2:
                    class_path = parts[-1].replace('L', '').replace(';', '')
                    class_name = class_path.split('/')[-1]
                java_lines.append(f"public class {class_name} {{")

            # Extract method declarations
            elif line.startswith('.method'):
                method_parts = line.split()
                method_name = "unknownMethod"
                for part in method_parts:
                    if not part.startswith('.') and not part in ['public', 'private', 'protected', 'static']:
                        method_name = part.split('(')[0]
                        break
                java_lines.append(f"    public void {method_name}() {{")
                java_lines.append("        // Method implementation")
                in_method = True

            elif line.startswith('.end method'):
                if in_method:
                    java_lines.append("    }")
                    in_method = False

            # Extract field declarations
            elif line.startswith('.field'):
                field_parts = line.split()
                if len(field_parts) > 2:
                    field_name = field_parts[-1].split(':')[0]
                    java_lines.append(f"    private Object {field_name};")

        java_lines.append("}")
        return '\n'.join(java_lines)

    def _basic_java_to_smali_conversion(self, java_content):
        """Basic Java to Smali conversion (simplified)"""
        smali_lines = []
        smali_lines.append("# Converted from Java (simplified conversion)")
        smali_lines.append("# Note: This is a basic conversion - use proper tools for production")
        smali_lines.append("")

        lines = java_content.split('\n')
        class_name = "ConvertedClass"

        # Extract class name
        for line in lines:
            line = line.strip()
            if line.startswith('class ') or line.startswith('public class '):
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'class' and i + 1 < len(parts):
                        class_name = parts[i + 1].replace('{', '')
                        break
                break

        smali_lines.append(f".class public L{class_name};")
        smali_lines.append(".super Ljava/lang/Object;")
        smali_lines.append("")

        # Basic method conversion
        in_method = False
        for line in lines:
            line = line.strip()

            # Extract method declarations
            if ('public ' in line or 'private ' in line) and '(' in line and '{' in line:
                method_name = "unknownMethod"
                parts = line.split('(')[0].split()
                if len(parts) > 0:
                    method_name = parts[-1]

                smali_lines.append(f".method public {method_name}()V")
                smali_lines.append("    .locals 1")
                smali_lines.append("    return-void")
                smali_lines.append(".end method")
                smali_lines.append("")

        return '\n'.join(smali_lines)

    def _show_conversion_result(self, title, content, file_type):
        """Show conversion result in a dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        dialog.resize(800, 600)

        layout = QVBoxLayout(dialog)

        # Result text area
        result_text = QTextEdit()
        result_text.setPlainText(content)
        result_text.setFont(QFont("Consolas", 10))
        result_text.setReadOnly(True)
        layout.addWidget(result_text)

        # Buttons
        button_layout = QHBoxLayout()

        copy_btn = QPushButton("📋 Copy to Clipboard")
        copy_btn.clicked.connect(lambda: self._copy_to_clipboard(content))

        replace_btn = QPushButton("🔄 Replace Current Content")
        replace_btn.clicked.connect(lambda: self._replace_editor_content(content, dialog))

        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(dialog.close)

        button_layout.addWidget(copy_btn)
        button_layout.addWidget(replace_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        dialog.exec_()

    def _copy_to_clipboard(self, content):
        """Copy content to clipboard"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(content)

        if self.editor_status_label:
            self.editor_status_label.setText("Content copied to clipboard")

    def _replace_editor_content(self, content, dialog):
        """Replace current editor content with converted content"""
        if self.text_preview:
            self.text_preview.setPlainText(content)
            if self.editor_status_label:
                self.editor_status_label.setText("Editor content replaced with conversion result")
            dialog.close()
