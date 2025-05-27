"""
Custom dialogs for MT Manager Linux
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QTextEdit, QTabWidget,
                            QGroupBox, QCheckBox, QSpinBox, QComboBox,
                            QFileDialog, QMessageBox, QDialogButtonBox, QWidget)
from pathlib import Path
from src.utils.config import config
from src.utils.file_utils import FileUtils


class PreferencesDialog(QDialog):
    """Application preferences dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)

        # Tab widget for different preference categories
        self.tab_widget = QTabWidget()

        # General tab
        general_tab = self.create_general_tab()
        self.tab_widget.addTab(general_tab, "General")

        # Editor tab
        editor_tab = self.create_editor_tab()
        self.tab_widget.addTab(editor_tab, "Editor")

        # Tools tab
        tools_tab = self.create_tools_tab()
        self.tab_widget.addTab(tools_tab, "Tools")

        # Languages tab
        languages_tab = self.create_languages_tab()
        self.tab_widget.addTab(languages_tab, "Languages")

        layout.addWidget(self.tab_widget)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)

        layout.addWidget(button_box)

    def create_general_tab(self):
        """Create general preferences tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        theme_layout.addWidget(QLabel("Theme:"))
        theme_layout.addWidget(self.theme_combo)

        layout.addWidget(theme_group)

        # File manager settings
        fm_group = QGroupBox("File Manager")
        fm_layout = QVBoxLayout(fm_group)

        self.show_hidden_cb = QCheckBox("Show hidden files")
        fm_layout.addWidget(self.show_hidden_cb)

        layout.addWidget(fm_group)

        # Window settings
        window_group = QGroupBox("Window")
        window_layout = QVBoxLayout(window_group)

        self.custom_titlebar_cb = QCheckBox("Use custom title bar (requires restart)")
        self.custom_titlebar_cb.setToolTip("Enable custom title bar with integrated window controls")
        window_layout.addWidget(self.custom_titlebar_cb)

        layout.addWidget(window_group)

        layout.addStretch()
        return widget

    def create_editor_tab(self):
        """Create editor preferences tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Font settings
        font_group = QGroupBox("Font")
        font_layout = QVBoxLayout(font_group)

        font_family_layout = QHBoxLayout()
        font_family_layout.addWidget(QLabel("Font Family:"))
        self.font_family_edit = QLineEdit()
        font_family_layout.addWidget(self.font_family_edit)
        font_layout.addLayout(font_family_layout)

        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("Font Size:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        font_size_layout.addWidget(self.font_size_spin)
        font_layout.addLayout(font_size_layout)

        layout.addWidget(font_group)

        layout.addStretch()
        return widget

    def create_tools_tab(self):
        """Create tools preferences tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # APKTool settings
        apktool_group = QGroupBox("APKTool")
        apktool_layout = QVBoxLayout(apktool_group)

        apktool_path_layout = QHBoxLayout()
        apktool_path_layout.addWidget(QLabel("APKTool Path:"))
        self.apktool_path_edit = QLineEdit()
        apktool_browse_btn = QPushButton("Browse...")
        apktool_browse_btn.clicked.connect(self.browse_apktool)
        apktool_path_layout.addWidget(self.apktool_path_edit)
        apktool_path_layout.addWidget(apktool_browse_btn)
        apktool_layout.addLayout(apktool_path_layout)

        java_path_layout = QHBoxLayout()
        java_path_layout.addWidget(QLabel("Java Path:"))
        self.java_path_edit = QLineEdit()
        java_browse_btn = QPushButton("Browse...")
        java_browse_btn.clicked.connect(self.browse_java)
        java_path_layout.addWidget(self.java_path_edit)
        java_path_layout.addWidget(java_browse_btn)
        apktool_layout.addLayout(java_path_layout)

        layout.addWidget(apktool_group)

        layout.addStretch()
        return widget

    def create_languages_tab(self):
        """Create languages preferences tab"""
        try:
            from src.ui.language_selector import LanguageInfoWidget
            return LanguageInfoWidget()
        except ImportError:
            # Fallback if language selector not available
            widget = QWidget()
            layout = QVBoxLayout(widget)

            info_label = QLabel(
                "Syntax highlighting is available for multiple programming languages.\n\n"
                "Supported languages include:\n"
                "• Python (.py)\n"
                "• Java (.java)\n"
                "• C++ (.cpp, .hpp)\n"
                "• C# (.cs)\n"
                "• JavaScript (.js)\n"
                "• HTML (.html)\n"
                "• XML (.xml)\n"
                "• CSS (.css)\n"
                "• JSON (.json)\n"
                "• SQL (.sql)\n"
                "• Smali (.smali)\n"
                "• PHP (.php)\n"
                "• Bash (.sh)\n"
                "• YAML (.yaml)\n"
                "• Markdown (.md)\n\n"
                "Syntax highlighting is automatically applied based on file extension."
            )
            info_label.setWordWrap(True)
            layout.addWidget(info_label)

            layout.addStretch()
            return widget

    def browse_apktool(self):
        """Browse for APKTool executable"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select APKTool", "", "Executable Files (*)"
        )
        if file_path:
            self.apktool_path_edit.setText(file_path)

    def browse_java(self):
        """Browse for Java executable"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Java", "", "Executable Files (*)"
        )
        if file_path:
            self.java_path_edit.setText(file_path)

    def load_settings(self):
        """Load current settings into dialog"""
        # General settings
        theme = config.get('theme', 'dark')
        self.theme_combo.setCurrentText(theme.capitalize())
        self.show_hidden_cb.setChecked(config.get('show_hidden_files', False))
        self.custom_titlebar_cb.setChecked(config.get('use_custom_titlebar', False))

        # Editor settings
        self.font_family_edit.setText(config.get('font_family', 'Consolas'))
        self.font_size_spin.setValue(config.get('font_size', 10))

        # Tools settings
        self.apktool_path_edit.setText(config.get('apktool_path', 'apktool'))
        self.java_path_edit.setText(config.get('java_path', 'java'))

    def apply_settings(self):
        """Apply settings without closing dialog"""
        # General settings
        config.set('theme', self.theme_combo.currentText().lower())
        config.set('show_hidden_files', self.show_hidden_cb.isChecked())
        config.set('use_custom_titlebar', self.custom_titlebar_cb.isChecked())

        # Editor settings
        config.set('font_family', self.font_family_edit.text())
        config.set('font_size', self.font_size_spin.value())

        # Tools settings
        config.set('apktool_path', self.apktool_path_edit.text())
        config.set('java_path', self.java_path_edit.text())

        # Save config
        config.save_config()

        QMessageBox.information(self, "Settings", "Settings applied successfully.")

    def accept(self):
        """Accept dialog and apply settings"""
        self.apply_settings()
        super().accept()


class AboutDialog(QDialog):
    """About dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About MT Manager Linux")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)

        # Application info
        app_label = QLabel("MT Manager Linux")
        app_label.setAlignment(Qt.AlignCenter)
        app_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(app_label)

        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        description = QTextEdit()
        description.setReadOnly(True)
        description.setMaximumHeight(150)
        description.setPlainText(
            "A dual-pane file manager for Linux with APK tools integration.\n\n"
            "Features:\n"
            "• Dual-pane file browser\n"
            "• APK decompile/recompile with APKTool\n"
            "• Text editor with syntax highlighting\n"
            "• Archive viewer and extractor\n"
            "• Dark theme support\n\n"
            "Built with PyQt5 and Python."
        )
        layout.addWidget(description)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class FilePropertiesDialog(QDialog):
    """File properties dialog"""

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowTitle(f"Properties - {Path(file_path).name}")
        self.setModal(True)
        self.resize(400, 300)
        self.setup_ui()
        self.load_file_info()

    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)

        # File info display
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        layout.addWidget(self.info_text)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def load_file_info(self):
        """Load and display file information"""
        try:
            import stat
            from datetime import datetime

            path = Path(self.file_path)
            stat_info = path.stat()

            info_text = f"File: {path.name}\n"
            info_text += f"Path: {path.parent}\n"
            info_text += f"Type: {'Directory' if path.is_dir() else 'File'}\n"

            if path.is_file():
                size = stat_info.st_size
                info_text += f"Size: {FileUtils.get_file_size_str(size)} ({size:,} bytes)\n"

            # Timestamps
            created = datetime.fromtimestamp(stat_info.st_ctime)
            modified = datetime.fromtimestamp(stat_info.st_mtime)
            accessed = datetime.fromtimestamp(stat_info.st_atime)

            info_text += f"Created: {created.strftime('%Y-%m-%d %H:%M:%S')}\n"
            info_text += f"Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}\n"
            info_text += f"Accessed: {accessed.strftime('%Y-%m-%d %H:%M:%S')}\n"

            # Permissions
            permissions = stat.filemode(stat_info.st_mode)
            info_text += f"Permissions: {permissions}\n"
            info_text += f"Owner: {stat_info.st_uid}\n"
            info_text += f"Group: {stat_info.st_gid}\n"

            self.info_text.setPlainText(info_text)

        except Exception as e:
            self.info_text.setPlainText(f"Error loading file information: {str(e)}")


class GoToLineDialog(QDialog):
    """Go to line dialog for text editor"""

    def __init__(self, max_line=1, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Go to Line")
        self.setModal(True)
        self.setFixedSize(300, 120)
        self.max_line = max_line
        self.line_number = 1
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)

        # Line number input
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Line number:"))

        self.line_edit = QLineEdit()
        self.line_edit.setText("1")
        self.line_edit.selectAll()
        input_layout.addWidget(self.line_edit)

        layout.addLayout(input_layout)

        # Info label
        self.info_label = QLabel(f"(1 - {self.max_line})")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Set focus to line edit
        self.line_edit.setFocus()

    def accept(self):
        """Validate and accept dialog"""
        try:
            line_num = int(self.line_edit.text())
            if 1 <= line_num <= self.max_line:
                self.line_number = line_num
                super().accept()
            else:
                QMessageBox.warning(
                    self, "Invalid Line Number",
                    f"Line number must be between 1 and {self.max_line}"
                )
        except ValueError:
            QMessageBox.warning(
                self, "Invalid Input",
                "Please enter a valid line number"
            )
