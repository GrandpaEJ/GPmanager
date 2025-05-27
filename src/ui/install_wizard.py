"""
Installation wizard for MT Manager Linux dependencies
"""
import sys
from pathlib import Path
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTextEdit, QProgressBar, QCheckBox,
                            QGroupBox, QScrollArea, QWidget, QMessageBox,
                            QTabWidget, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QFont, QIcon
from src.utils.system_installer import SystemInstaller


class InstallWorker(QThread):
    """Worker thread for dependency installation"""
    
    progress_updated = pyqtSignal(str)
    dependency_installed = pyqtSignal(str, bool, str)
    installation_finished = pyqtSignal(dict)
    
    def __init__(self, installer, dependencies, skip_optional=False):
        super().__init__()
        self.installer = installer
        self.dependencies = dependencies
        self.skip_optional = skip_optional
    
    def run(self):
        """Run installation process"""
        results = {}
        
        for dep_name in self.dependencies:
            self.progress_updated.emit(f"Installing {dep_name}...")
            
            success, message = self.installer.install_dependency(
                dep_name, interactive=False
            )
            
            results[dep_name] = (success, message)
            self.dependency_installed.emit(dep_name, success, message)
        
        self.installation_finished.emit(results)


class InstallWizard(QDialog):
    """Installation wizard dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.installer = SystemInstaller()
        self.dependency_status = {}
        self.setWindowTitle("MT Manager Linux - Setup Wizard")
        self.setModal(True)
        self.resize(600, 500)
        self.setup_ui()
        self.check_dependencies()
    
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("MT Manager Linux Setup Wizard")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Dependencies tab
        deps_tab = self.create_dependencies_tab()
        self.tab_widget.addTab(deps_tab, "Dependencies")
        
        # Installation tab
        install_tab = self.create_installation_tab()
        self.tab_widget.addTab(install_tab, "Installation")
        
        # Manual tab
        manual_tab = self.create_manual_tab()
        self.tab_widget.addTab(manual_tab, "Manual Installation")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.check_btn = QPushButton("Recheck Dependencies")
        self.check_btn.clicked.connect(self.check_dependencies)
        button_layout.addWidget(self.check_btn)
        
        button_layout.addStretch()
        
        self.install_btn = QPushButton("Install Missing")
        self.install_btn.clicked.connect(self.start_installation)
        button_layout.addWidget(self.install_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def create_dependencies_tab(self):
        """Create dependencies status tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Info label
        info_label = QLabel(
            "Check the status of required and optional dependencies below. "
            "Required dependencies are needed for basic functionality, while "
            "optional dependencies enable additional features like APK operations."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Dependencies list
        self.deps_list = QListWidget()
        layout.addWidget(self.deps_list)
        
        # Options
        options_group = QGroupBox("Installation Options")
        options_layout = QVBoxLayout(options_group)
        
        self.skip_optional_cb = QCheckBox("Skip optional dependencies")
        self.skip_optional_cb.setToolTip("Skip APKTool, Java, and Git installation")
        options_layout.addWidget(self.skip_optional_cb)
        
        self.use_pip_cb = QCheckBox("Prefer pip over system packages")
        self.use_pip_cb.setToolTip("Use pip instead of system package manager when possible")
        options_layout.addWidget(self.use_pip_cb)
        
        layout.addWidget(options_group)
        
        return widget
    
    def create_installation_tab(self):
        """Create installation progress tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Progress info
        self.progress_label = QLabel("Ready to install")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Installation log
        log_group = QGroupBox("Installation Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Results
        results_group = QGroupBox("Installation Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_list = QListWidget()
        results_layout.addWidget(self.results_list)
        
        layout.addWidget(results_group)
        
        return widget
    
    def create_manual_tab(self):
        """Create manual installation tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Info
        info_label = QLabel(
            "If automatic installation fails, you can use the commands below "
            "to manually install dependencies:"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Script text
        self.script_text = QTextEdit()
        self.script_text.setReadOnly(True)
        self.script_text.setFont(QFont("monospace"))
        layout.addWidget(self.script_text)
        
        # Copy button
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_script)
        layout.addWidget(copy_btn)
        
        return widget
    
    def check_dependencies(self):
        """Check dependency status"""
        self.dependency_status = self.installer.check_all_dependencies()
        self.update_dependencies_list()
        self.update_manual_script()
        
        # Update install button state
        missing_deps = [name for name, status in self.dependency_status.items() 
                       if not status['installed']]
        self.install_btn.setEnabled(len(missing_deps) > 0)
        
        if len(missing_deps) == 0:
            self.progress_label.setText("All dependencies are installed!")
        else:
            self.progress_label.setText(f"{len(missing_deps)} dependencies need installation")
    
    def update_dependencies_list(self):
        """Update dependencies list widget"""
        self.deps_list.clear()
        
        required_deps = ['python3-pyqt5', 'python3-pyqt5.qsci', 'python3-pygments', 'python3-magic']
        optional_deps = ['apktool', 'java', 'git']
        
        # Add required dependencies
        for dep_name in required_deps:
            if dep_name in self.dependency_status:
                status = self.dependency_status[dep_name]
                item = QListWidgetItem()
                
                if status['installed']:
                    item.setText(f"✓ {dep_name} - {status['description']}")
                    item.setBackground(Qt.green)
                else:
                    item.setText(f"✗ {dep_name} - {status['description']} (REQUIRED)")
                    item.setBackground(Qt.red)
                
                self.deps_list.addItem(item)
        
        # Add optional dependencies
        for dep_name in optional_deps:
            if dep_name in self.dependency_status:
                status = self.dependency_status[dep_name]
                item = QListWidgetItem()
                
                if status['installed']:
                    item.setText(f"✓ {dep_name} - {status['description']}")
                    item.setBackground(Qt.green)
                else:
                    item.setText(f"○ {dep_name} - {status['description']} (optional)")
                    item.setBackground(Qt.yellow)
                
                self.deps_list.addItem(item)
    
    def update_manual_script(self):
        """Update manual installation script"""
        script = self.installer.get_installation_script()
        self.script_text.setPlainText(script)
    
    def start_installation(self):
        """Start automatic installation"""
        missing_deps = [name for name, status in self.dependency_status.items() 
                       if not status['installed']]
        
        if not missing_deps:
            QMessageBox.information(self, "No Installation Needed", 
                                  "All dependencies are already installed!")
            return
        
        # Switch to installation tab
        self.tab_widget.setCurrentIndex(1)
        
        # Clear previous results
        self.log_text.clear()
        self.results_list.clear()
        
        # Setup progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(missing_deps))
        self.progress_bar.setValue(0)
        
        # Disable buttons during installation
        self.install_btn.setEnabled(False)
        self.check_btn.setEnabled(False)
        
        # Start installation worker
        self.install_worker = InstallWorker(
            self.installer, 
            missing_deps, 
            self.skip_optional_cb.isChecked()
        )
        
        self.install_worker.progress_updated.connect(self.on_progress_updated)
        self.install_worker.dependency_installed.connect(self.on_dependency_installed)
        self.install_worker.installation_finished.connect(self.on_installation_finished)
        
        self.install_worker.start()
    
    def on_progress_updated(self, message):
        """Handle progress update"""
        self.progress_label.setText(message)
        self.log_text.append(message)
    
    def on_dependency_installed(self, dep_name, success, message):
        """Handle individual dependency installation result"""
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        
        # Add to results list
        item = QListWidgetItem()
        if success:
            item.setText(f"✓ {dep_name}: {message}")
            item.setBackground(Qt.green)
        else:
            item.setText(f"✗ {dep_name}: {message}")
            item.setBackground(Qt.red)
        
        self.results_list.addItem(item)
        
        # Add to log
        status_symbol = "✓" if success else "✗"
        self.log_text.append(f"{status_symbol} {dep_name}: {message}")
    
    def on_installation_finished(self, results):
        """Handle installation completion"""
        self.progress_bar.setVisible(False)
        
        # Re-enable buttons
        self.install_btn.setEnabled(True)
        self.check_btn.setEnabled(True)
        
        # Show completion message
        successful = sum(1 for success, _ in results.values() if success)
        total = len(results)
        
        self.progress_label.setText(
            f"Installation completed: {successful}/{total} successful"
        )
        
        self.log_text.append(f"\nInstallation completed: {successful}/{total} successful")
        
        # Recheck dependencies
        self.check_dependencies()
        
        # Show completion dialog
        if successful == total:
            QMessageBox.information(
                self, "Installation Complete",
                "All dependencies were installed successfully!\n"
                "You can now use MT Manager Linux with full functionality."
            )
        else:
            failed = total - successful
            QMessageBox.warning(
                self, "Installation Partially Failed",
                f"{failed} dependencies failed to install.\n"
                "Check the installation log for details.\n"
                "You may need to install them manually."
            )
    
    def copy_script(self):
        """Copy installation script to clipboard"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.script_text.toPlainText())
        
        QMessageBox.information(
            self, "Copied",
            "Installation script copied to clipboard.\n"
            "You can paste and run it in a terminal."
        )
