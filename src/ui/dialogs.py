"""
Custom dialogs for GP Manager
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QTextEdit, QTabWidget,
                            QGroupBox, QCheckBox, QSpinBox, QComboBox,
                            QFileDialog, QMessageBox, QDialogButtonBox, QWidget,
                            QSlider, QFontComboBox, QColorDialog, QFrame,
                            QScrollArea, QGridLayout, QButtonGroup, QRadioButton)
from pathlib import Path
from src.utils.config import config
from src.utils.file_utils import FileUtils


class PreferencesDialog(QDialog):
    """Application preferences dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.resize(600, 500)
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

        # Appearance tab
        appearance_tab = self.create_appearance_tab()
        self.tab_widget.addTab(appearance_tab, "Appearance")

        # Advanced tab
        advanced_tab = self.create_advanced_tab()
        self.tab_widget.addTab(advanced_tab, "Advanced")

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
        self.theme_combo.addItems(["Dark", "Light", "Auto"])
        theme_layout.addWidget(QLabel("Theme:"))
        theme_layout.addWidget(self.theme_combo)

        layout.addWidget(theme_group)

        # File manager settings
        fm_group = QGroupBox("File Manager")
        fm_layout = QVBoxLayout(fm_group)

        self.show_hidden_cb = QCheckBox("Show hidden files")
        fm_layout.addWidget(self.show_hidden_cb)

        self.show_file_extensions_cb = QCheckBox("Always show file extensions")
        fm_layout.addWidget(self.show_file_extensions_cb)

        self.confirm_delete_cb = QCheckBox("Confirm file deletions")
        fm_layout.addWidget(self.confirm_delete_cb)

        self.double_click_action_combo = QComboBox()
        self.double_click_action_combo.addItems(["Open", "Rename", "Properties"])
        fm_layout.addWidget(QLabel("Double-click action:"))
        fm_layout.addWidget(self.double_click_action_combo)

        layout.addWidget(fm_group)

        # Window settings
        window_group = QGroupBox("Window")
        window_layout = QVBoxLayout(window_group)

        self.custom_titlebar_cb = QCheckBox("Use custom title bar (requires restart)")
        self.custom_titlebar_cb.setToolTip("Enable custom title bar with integrated window controls")
        window_layout.addWidget(self.custom_titlebar_cb)

        self.remember_window_state_cb = QCheckBox("Remember window size and position")
        window_layout.addWidget(self.remember_window_state_cb)

        self.start_maximized_cb = QCheckBox("Start maximized")
        window_layout.addWidget(self.start_maximized_cb)

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

        # Font family with combo box
        font_family_layout = QHBoxLayout()
        font_family_layout.addWidget(QLabel("Font Family:"))
        self.font_family_combo = QFontComboBox()
        font_family_layout.addWidget(self.font_family_combo)
        font_layout.addLayout(font_family_layout)

        # Font size with slider and spinbox
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("Font Size:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 72)
        self.font_size_spin.setSuffix(" pt")
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(6, 72)
        self.font_size_slider.valueChanged.connect(self.font_size_spin.setValue)
        self.font_size_spin.valueChanged.connect(self.font_size_slider.setValue)
        font_size_layout.addWidget(self.font_size_spin)
        font_size_layout.addWidget(self.font_size_slider)
        font_layout.addLayout(font_size_layout)

        layout.addWidget(font_group)

        # Editor behavior
        behavior_group = QGroupBox("Editor Behavior")
        behavior_layout = QVBoxLayout(behavior_group)

        self.word_wrap_cb = QCheckBox("Enable word wrap")
        behavior_layout.addWidget(self.word_wrap_cb)

        self.line_numbers_cb = QCheckBox("Show line numbers")
        behavior_layout.addWidget(self.line_numbers_cb)

        self.highlight_current_line_cb = QCheckBox("Highlight current line")
        behavior_layout.addWidget(self.highlight_current_line_cb)

        self.auto_indent_cb = QCheckBox("Auto indent")
        behavior_layout.addWidget(self.auto_indent_cb)

        # Tab settings
        tab_layout = QHBoxLayout()
        tab_layout.addWidget(QLabel("Tab width:"))
        self.tab_width_spin = QSpinBox()
        self.tab_width_spin.setRange(1, 16)
        self.tab_width_spin.setSuffix(" spaces")
        tab_layout.addWidget(self.tab_width_spin)
        behavior_layout.addLayout(tab_layout)

        self.use_spaces_cb = QCheckBox("Use spaces instead of tabs")
        behavior_layout.addWidget(self.use_spaces_cb)

        layout.addWidget(behavior_group)

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

    def create_appearance_tab(self):
        """Create appearance preferences tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Color scheme
        color_group = QGroupBox("Color Scheme")
        color_layout = QVBoxLayout(color_group)

        # Theme variants
        self.theme_variant_combo = QComboBox()
        self.theme_variant_combo.addItems(["Default", "High Contrast", "Blue", "Green"])
        color_layout.addWidget(QLabel("Theme Variant:"))
        color_layout.addWidget(self.theme_variant_combo)

        # Custom colors
        custom_colors_layout = QGridLayout()

        # Background color
        custom_colors_layout.addWidget(QLabel("Background:"), 0, 0)
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(50, 30)
        self.bg_color_btn.clicked.connect(lambda: self.choose_color('background'))
        custom_colors_layout.addWidget(self.bg_color_btn, 0, 1)

        # Text color
        custom_colors_layout.addWidget(QLabel("Text:"), 0, 2)
        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedSize(50, 30)
        self.text_color_btn.clicked.connect(lambda: self.choose_color('text'))
        custom_colors_layout.addWidget(self.text_color_btn, 0, 3)

        # Accent color
        custom_colors_layout.addWidget(QLabel("Accent:"), 1, 0)
        self.accent_color_btn = QPushButton()
        self.accent_color_btn.setFixedSize(50, 30)
        self.accent_color_btn.clicked.connect(lambda: self.choose_color('accent'))
        custom_colors_layout.addWidget(self.accent_color_btn, 1, 1)

        color_layout.addLayout(custom_colors_layout)
        layout.addWidget(color_group)

        # UI Scale
        scale_group = QGroupBox("Interface Scale")
        scale_layout = QVBoxLayout(scale_group)

        scale_slider_layout = QHBoxLayout()
        scale_slider_layout.addWidget(QLabel("Scale:"))
        self.ui_scale_slider = QSlider(Qt.Horizontal)
        self.ui_scale_slider.setRange(50, 200)
        self.ui_scale_slider.setValue(100)
        self.ui_scale_label = QLabel("100%")
        self.ui_scale_slider.valueChanged.connect(
            lambda v: self.ui_scale_label.setText(f"{v}%")
        )
        scale_slider_layout.addWidget(self.ui_scale_slider)
        scale_slider_layout.addWidget(self.ui_scale_label)
        scale_layout.addLayout(scale_slider_layout)

        layout.addWidget(scale_group)

        # Icon settings
        icon_group = QGroupBox("Icons")
        icon_layout = QVBoxLayout(icon_group)

        self.show_file_icons_cb = QCheckBox("Show file type icons")
        icon_layout.addWidget(self.show_file_icons_cb)

        icon_size_layout = QHBoxLayout()
        icon_size_layout.addWidget(QLabel("Icon size:"))
        self.icon_size_combo = QComboBox()
        self.icon_size_combo.addItems(["Small (16px)", "Medium (24px)", "Large (32px)"])
        icon_size_layout.addWidget(self.icon_size_combo)
        icon_layout.addLayout(icon_size_layout)

        layout.addWidget(icon_group)

        layout.addStretch()
        return widget

    def create_advanced_tab(self):
        """Create advanced preferences tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Performance
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout(perf_group)

        self.enable_animations_cb = QCheckBox("Enable animations")
        perf_layout.addWidget(self.enable_animations_cb)

        self.hardware_acceleration_cb = QCheckBox("Hardware acceleration")
        perf_layout.addWidget(self.hardware_acceleration_cb)

        # Cache settings
        cache_layout = QHBoxLayout()
        cache_layout.addWidget(QLabel("Cache size (MB):"))
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setSuffix(" MB")
        cache_layout.addWidget(self.cache_size_spin)
        perf_layout.addLayout(cache_layout)

        layout.addWidget(perf_group)

        # Backup and restore
        backup_group = QGroupBox("Backup & Restore")
        backup_layout = QVBoxLayout(backup_group)

        self.auto_backup_cb = QCheckBox("Auto-backup settings")
        backup_layout.addWidget(self.auto_backup_cb)

        backup_buttons_layout = QHBoxLayout()
        backup_btn = QPushButton("Backup Settings")
        restore_btn = QPushButton("Restore Settings")
        reset_btn = QPushButton("Reset to Defaults")
        backup_buttons_layout.addWidget(backup_btn)
        backup_buttons_layout.addWidget(restore_btn)
        backup_buttons_layout.addWidget(reset_btn)
        backup_layout.addLayout(backup_buttons_layout)

        layout.addWidget(backup_group)

        # Debug options
        debug_group = QGroupBox("Debug")
        debug_layout = QVBoxLayout(debug_group)

        self.debug_mode_cb = QCheckBox("Enable debug mode")
        debug_layout.addWidget(self.debug_mode_cb)

        self.verbose_logging_cb = QCheckBox("Verbose logging")
        debug_layout.addWidget(self.verbose_logging_cb)

        layout.addWidget(debug_group)

        layout.addStretch()
        return widget

    def choose_color(self, color_type):
        """Open color chooser dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            button = getattr(self, f"{color_type}_color_btn")
            button.setStyleSheet(f"background-color: {color.name()}")
            # Store color in config
            config.set(f"{color_type}_color", color.name())

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
        self.show_file_extensions_cb.setChecked(config.get('show_file_extensions', True))
        self.confirm_delete_cb.setChecked(config.get('confirm_delete', True))
        self.double_click_action_combo.setCurrentText(config.get('double_click_action', 'Open'))
        self.custom_titlebar_cb.setChecked(config.get('use_custom_titlebar', False))
        self.remember_window_state_cb.setChecked(config.get('remember_window_state', True))
        self.start_maximized_cb.setChecked(config.get('start_maximized', False))

        # Editor settings
        font_family = config.get('font_family', 'Consolas')
        self.font_family_combo.setCurrentFont(self.font_family_combo.font())
        self.font_family_combo.setCurrentText(font_family)

        font_size = config.get('font_size', 10)
        self.font_size_spin.setValue(font_size)
        self.font_size_slider.setValue(font_size)

        self.word_wrap_cb.setChecked(config.get('word_wrap', False))
        self.line_numbers_cb.setChecked(config.get('line_numbers', True))
        self.highlight_current_line_cb.setChecked(config.get('highlight_current_line', True))
        self.auto_indent_cb.setChecked(config.get('auto_indent', True))
        self.tab_width_spin.setValue(config.get('tab_width', 4))
        self.use_spaces_cb.setChecked(config.get('use_spaces', True))

        # Tools settings
        self.apktool_path_edit.setText(config.get('apktool_path', 'apktool'))
        self.java_path_edit.setText(config.get('java_path', 'java'))

        # Appearance settings
        self.theme_variant_combo.setCurrentText(config.get('theme_variant', 'Default'))
        self.ui_scale_slider.setValue(config.get('ui_scale', 100))
        self.ui_scale_label.setText(f"{config.get('ui_scale', 100)}%")
        self.show_file_icons_cb.setChecked(config.get('show_file_icons', True))
        self.icon_size_combo.setCurrentText(config.get('icon_size', 'Medium (24px)'))

        # Set color button backgrounds
        bg_color = config.get('background_color', '#2b2b2b')
        self.bg_color_btn.setStyleSheet(f"background-color: {bg_color}")
        text_color = config.get('text_color', '#ffffff')
        self.text_color_btn.setStyleSheet(f"background-color: {text_color}")
        accent_color = config.get('accent_color', '#0078d4')
        self.accent_color_btn.setStyleSheet(f"background-color: {accent_color}")

        # Advanced settings
        self.enable_animations_cb.setChecked(config.get('enable_animations', True))
        self.hardware_acceleration_cb.setChecked(config.get('hardware_acceleration', True))
        self.cache_size_spin.setValue(config.get('cache_size', 100))
        self.auto_backup_cb.setChecked(config.get('auto_backup', False))
        self.debug_mode_cb.setChecked(config.get('debug_mode', False))
        self.verbose_logging_cb.setChecked(config.get('verbose_logging', False))

    def apply_settings(self):
        """Apply settings without closing dialog"""
        # General settings
        config.set('theme', self.theme_combo.currentText().lower())
        config.set('show_hidden_files', self.show_hidden_cb.isChecked())
        config.set('show_file_extensions', self.show_file_extensions_cb.isChecked())
        config.set('confirm_delete', self.confirm_delete_cb.isChecked())
        config.set('double_click_action', self.double_click_action_combo.currentText())
        config.set('use_custom_titlebar', self.custom_titlebar_cb.isChecked())
        config.set('remember_window_state', self.remember_window_state_cb.isChecked())
        config.set('start_maximized', self.start_maximized_cb.isChecked())

        # Editor settings
        config.set('font_family', self.font_family_combo.currentText())
        config.set('font_size', self.font_size_spin.value())
        config.set('word_wrap', self.word_wrap_cb.isChecked())
        config.set('line_numbers', self.line_numbers_cb.isChecked())
        config.set('highlight_current_line', self.highlight_current_line_cb.isChecked())
        config.set('auto_indent', self.auto_indent_cb.isChecked())
        config.set('tab_width', self.tab_width_spin.value())
        config.set('use_spaces', self.use_spaces_cb.isChecked())

        # Tools settings
        config.set('apktool_path', self.apktool_path_edit.text())
        config.set('java_path', self.java_path_edit.text())

        # Appearance settings
        config.set('theme_variant', self.theme_variant_combo.currentText())
        config.set('ui_scale', self.ui_scale_slider.value())
        config.set('show_file_icons', self.show_file_icons_cb.isChecked())
        config.set('icon_size', self.icon_size_combo.currentText())

        # Advanced settings
        config.set('enable_animations', self.enable_animations_cb.isChecked())
        config.set('hardware_acceleration', self.hardware_acceleration_cb.isChecked())
        config.set('cache_size', self.cache_size_spin.value())
        config.set('auto_backup', self.auto_backup_cb.isChecked())
        config.set('debug_mode', self.debug_mode_cb.isChecked())
        config.set('verbose_logging', self.verbose_logging_cb.isChecked())

        # Save config
        config.save_config()

        # Apply theme and settings immediately
        if hasattr(self.parent(), 'apply_theme'):
            self.parent().apply_theme()
        if hasattr(self.parent(), 'apply_font_settings'):
            self.parent().apply_font_settings()

        QMessageBox.information(self, "Settings", "Settings applied successfully.")

    def accept(self):
        """Accept dialog and apply settings"""
        self.apply_settings()
        super().accept()


class AboutDialog(QDialog):
    """About dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About GP Manager")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)

        # Application info
        app_label = QLabel("GP Manager")
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
