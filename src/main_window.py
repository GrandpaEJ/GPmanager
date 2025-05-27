"""
Main window for GP Manager
"""
import sys
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QSplitter, QTabWidget, QMenuBar, QMenu, QAction,
                            QToolBar, QPushButton, QStatusBar, QMessageBox,
                            QFileDialog, QInputDialog, QApplication)
from PyQt5.QtGui import QKeySequence, QIcon
from src.file_manager.single_pane import SinglePaneManager
from src.editors.text_editor import TextEditorWidget
from src.tools.apktool import ApkToolWidget
from src.tools.archive_manager import ArchiveViewer
from src.viewers.image_viewer import ImageViewer
from src.ui.dialogs import PreferencesDialog, AboutDialog, FilePropertiesDialog
from src.ui.themes import ThemeManager
from src.ui.detachable_window import initialize_window_manager
from src.ui.tool_dock import FlexibleToolManager, ToolTabWidget
from src.utils.config import config
from src.utils.file_utils import FileUtils


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GP Manager")
        self.unsaved_changes = False
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_toolbar()
        self.setup_status_bar()
        self.setup_connections()
        self.setup_window_controls()
        self.load_settings()

        # Apply theme
        ThemeManager.apply_dark_theme(QApplication.instance())

    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main splitter (horizontal)
        self.main_splitter = QSplitter(Qt.Horizontal)

        # Left side: File manager
        self.file_manager = SinglePaneManager()
        self.main_splitter.addWidget(self.file_manager)

        # Right side: Flexible tool system
        self.tool_manager = FlexibleToolManager(self)

        # Initialize window manager for detachable tools
        self.window_manager = initialize_window_manager(self)

        # Create tool widgets
        self.text_editor = TextEditorWidget()
        self.apk_tools = ApkToolWidget()
        self.archive_viewer = ArchiveViewer()
        self.image_viewer = ImageViewer()

        # Hex editor is optional - only create when needed
        self.hex_editor = None

        # DEX editor is optional - only create when needed
        self.dex_editor = None

        # Register tools with window manager
        self.window_manager.register_tool("Text Editor", self.text_editor)
        self.window_manager.register_tool("APK Tools", self.apk_tools)
        self.window_manager.register_tool("Archive Viewer", self.archive_viewer)
        self.window_manager.register_tool("Image Viewer", self.image_viewer)

        # Add tools to tool manager
        self.tool_manager.add_tool("Text Editor", self.text_editor)
        self.tool_manager.add_tool("APK Tools", self.apk_tools)
        self.tool_manager.add_tool("Archive Viewer", self.archive_viewer)
        self.tool_manager.add_tool("Image Viewer", self.image_viewer)

        self.main_splitter.addWidget(self.tool_manager)

        # Set initial splitter ratio (70% file manager, 30% tools)
        self.main_splitter.setSizes([700, 300])

        layout.addWidget(self.main_splitter)

    def setup_menu_bar(self):
        """Setup menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_folder_action = QAction("New Folder", self)
        new_folder_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_folder_action.triggered.connect(self.new_folder)
        file_menu.addAction(new_folder_action)

        file_menu.addSeparator()

        open_file_action = QAction("Open File", self)
        open_file_action.setShortcut(QKeySequence.Open)
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        file_menu.addSeparator()

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_current_file)
        file_menu.addAction(save_action)

        save_all_action = QAction("Save All", self)
        save_all_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_all_action.triggered.connect(self.save_all_files)
        file_menu.addAction(save_all_action)

        file_menu.addSeparator()

        preferences_action = QAction("Preferences", self)
        preferences_action.setShortcut(QKeySequence("Ctrl+,"))
        preferences_action.triggered.connect(self.show_preferences)
        file_menu.addAction(preferences_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy_files)
        edit_menu.addAction(copy_action)

        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.cut_files)
        edit_menu.addAction(cut_action)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste_files)
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()

        delete_action = QAction("Delete", self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.delete_files)
        edit_menu.addAction(delete_action)

        rename_action = QAction("Rename", self)
        rename_action.setShortcut(QKeySequence("F2"))
        rename_action.triggered.connect(self.rename_file)
        edit_menu.addAction(rename_action)

        edit_menu.addSeparator()

        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)

        # View menu
        view_menu = menubar.addMenu("View")

        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self.refresh_views)
        view_menu.addAction(refresh_action)

        view_menu.addSeparator()

        # Navigation actions
        back_action = QAction("Back", self)
        back_action.setShortcut(QKeySequence("Alt+Left"))
        back_action.triggered.connect(self.go_back)
        view_menu.addAction(back_action)

        forward_action = QAction("Forward", self)
        forward_action.setShortcut(QKeySequence("Alt+Right"))
        forward_action.triggered.connect(self.go_forward)
        view_menu.addAction(forward_action)

        home_action = QAction("Home", self)
        home_action.setShortcut(QKeySequence("Alt+Home"))
        home_action.triggered.connect(self.go_home)
        view_menu.addAction(home_action)

        view_menu.addSeparator()

        # Window controls
        minimize_action = QAction("Minimize", self)
        minimize_action.setShortcut(QKeySequence("Ctrl+M"))
        minimize_action.triggered.connect(self.showMinimized)
        view_menu.addAction(minimize_action)

        maximize_action = QAction("Maximize/Restore", self)
        maximize_action.setShortcut(QKeySequence("F11"))
        maximize_action.triggered.connect(self.toggle_maximize)
        view_menu.addAction(maximize_action)

        fullscreen_action = QAction("Full Screen", self)
        fullscreen_action.setShortcut(QKeySequence("F11"))
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        apk_decompile_action = QAction("Decompile APK", self)
        apk_decompile_action.triggered.connect(self.decompile_apk)
        tools_menu.addAction(apk_decompile_action)

        tools_menu.addSeparator()

        # Optional tools
        enable_hex_action = QAction("🔧 Enable Hex Editor", self)
        enable_hex_action.triggered.connect(self.enable_hex_editor)
        tools_menu.addAction(enable_hex_action)

        tools_menu.addSeparator()

        # Tool window management
        detach_menu = tools_menu.addMenu("Detach Tools")

        detach_editor_action = QAction("Text Editor", self)
        detach_editor_action.triggered.connect(lambda: self.detach_tool("Text Editor"))
        detach_menu.addAction(detach_editor_action)

        detach_apk_action = QAction("APK Tools", self)
        detach_apk_action.triggered.connect(lambda: self.detach_tool("APK Tools"))
        detach_menu.addAction(detach_apk_action)

        detach_archive_action = QAction("Archive Viewer", self)
        detach_archive_action.triggered.connect(lambda: self.detach_tool("Archive Viewer"))
        detach_menu.addAction(detach_archive_action)

        detach_image_action = QAction("Image Viewer", self)
        detach_image_action.triggered.connect(lambda: self.detach_tool("Image Viewer"))
        detach_menu.addAction(detach_image_action)

        # Hex editor detach option (only shown when hex editor is enabled)
        self.detach_hex_action = QAction("Hex Editor", self)
        self.detach_hex_action.triggered.connect(lambda: self.detach_tool("Hex Editor"))
        self.detach_hex_action.setVisible(False)  # Initially hidden
        detach_menu.addAction(self.detach_hex_action)

        tools_menu.addSeparator()

        external_editors_action = QAction("Configure External Editors", self)
        external_editors_action.triggered.connect(self.configure_external_editors)
        tools_menu.addAction(external_editors_action)

        setup_wizard_action = QAction("Setup Wizard", self)
        setup_wizard_action.triggered.connect(self.show_setup_wizard)
        tools_menu.addAction(setup_wizard_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_toolbar(self):
        """Setup enhanced toolbar with organized button groups"""
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a, stop:1 #2d2d2d);
                border: 1px solid #555;
                spacing: 3px;
                padding: 4px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a4a, stop:1 #3a3a3a);
                border: 1px solid #666;
                border-radius: 4px;
                padding: 4px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a5a5a, stop:1 #4a4a4a);
                border: 1px solid #777;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #3a3a3a);
            }
            QPushButton:disabled {
                background: #2a2a2a;
                color: #666;
                border: 1px solid #444;
            }
        """)

        # Group 1: Navigation History
        self.back_btn = QPushButton("⬅")
        self.back_btn.setToolTip("Go Back (Alt+Left)")
        self.back_btn.setFixedSize(36, 36)
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        toolbar.addWidget(self.back_btn)

        self.forward_btn = QPushButton("➡")
        self.forward_btn.setToolTip("Go Forward (Alt+Right)")
        self.forward_btn.setFixedSize(36, 36)
        self.forward_btn.clicked.connect(self.go_forward)
        self.forward_btn.setEnabled(False)
        toolbar.addWidget(self.forward_btn)

        self.up_btn = QPushButton("⬆")
        self.up_btn.setToolTip("Go Up (Alt+Up)")
        self.up_btn.setFixedSize(36, 36)
        self.up_btn.clicked.connect(self.navigate_up)
        toolbar.addWidget(self.up_btn)

        self.home_btn = QPushButton("🏠")
        self.home_btn.setToolTip("Go Home (Alt+Home)")
        self.home_btn.setFixedSize(36, 36)
        self.home_btn.clicked.connect(self.go_home)
        toolbar.addWidget(self.home_btn)

        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setToolTip("Refresh (F5)")
        self.refresh_btn.setFixedSize(36, 36)
        self.refresh_btn.clicked.connect(self.refresh_views)
        toolbar.addWidget(self.refresh_btn)

        toolbar.addSeparator()

        # Group 2: File Operations
        self.copy_btn = QPushButton("📋")
        self.copy_btn.setToolTip("Copy selected files (Ctrl+C)")
        self.copy_btn.setFixedSize(36, 36)
        self.copy_btn.clicked.connect(self.copy_files)
        toolbar.addWidget(self.copy_btn)

        self.cut_btn = QPushButton("✂")
        self.cut_btn.setToolTip("Cut selected files (Ctrl+X)")
        self.cut_btn.setFixedSize(36, 36)
        self.cut_btn.clicked.connect(self.cut_files)
        toolbar.addWidget(self.cut_btn)

        self.paste_btn = QPushButton("📄")
        self.paste_btn.setToolTip("Paste files (Ctrl+V)")
        self.paste_btn.setFixedSize(36, 36)
        self.paste_btn.clicked.connect(self.paste_files)
        toolbar.addWidget(self.paste_btn)

        self.delete_btn = QPushButton("🗑")
        self.delete_btn.setToolTip("Delete selected files (Delete)")
        self.delete_btn.setFixedSize(36, 36)
        self.delete_btn.clicked.connect(self.delete_files)
        toolbar.addWidget(self.delete_btn)

        toolbar.addSeparator()

        # Group 3: Quick Actions
        self.new_folder_btn = QPushButton("📁")
        self.new_folder_btn.setToolTip("Create New Folder (Ctrl+Shift+N)")
        self.new_folder_btn.setFixedSize(36, 36)
        self.new_folder_btn.clicked.connect(self.new_folder)
        toolbar.addWidget(self.new_folder_btn)

        self.quick_decompile_btn = QPushButton("🔨")
        self.quick_decompile_btn.setToolTip("Quick Decompile Selected APK")
        self.quick_decompile_btn.setFixedSize(36, 36)
        self.quick_decompile_btn.clicked.connect(self.quick_decompile_apk)
        toolbar.addWidget(self.quick_decompile_btn)

        toolbar.addSeparator()

        # Group 4: Tools
        self.editor_btn = QPushButton("📝")
        self.editor_btn.setToolTip("Text Editor")
        self.editor_btn.setFixedSize(36, 36)
        self.editor_btn.clicked.connect(lambda: self.focus_tool("Text Editor"))
        toolbar.addWidget(self.editor_btn)

        self.apk_btn = QPushButton("📱")
        self.apk_btn.setToolTip("APK Tools")
        self.apk_btn.setFixedSize(36, 36)
        self.apk_btn.clicked.connect(lambda: self.focus_tool("APK Tools"))
        toolbar.addWidget(self.apk_btn)

        self.archive_btn = QPushButton("📦")
        self.archive_btn.setToolTip("Archive Viewer")
        self.archive_btn.setFixedSize(36, 36)
        self.archive_btn.clicked.connect(lambda: self.focus_tool("Archive Viewer"))
        toolbar.addWidget(self.archive_btn)

        self.image_btn = QPushButton("🖼️")
        self.image_btn.setToolTip("Image Viewer")
        self.image_btn.setFixedSize(36, 36)
        self.image_btn.clicked.connect(lambda: self.focus_tool("Image Viewer"))
        toolbar.addWidget(self.image_btn)

        toolbar.addSeparator()

        # Group 5: Tool Management
        self.detach_btn = QPushButton("⧉")
        self.detach_btn.setToolTip("Detach current tool")
        self.detach_btn.setFixedSize(36, 36)
        self.detach_btn.clicked.connect(self.detach_current_tool)
        toolbar.addWidget(self.detach_btn)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setToolTip("Settings & Preferences")
        self.settings_btn.setFixedSize(36, 36)
        self.settings_btn.clicked.connect(self.show_preferences)
        toolbar.addWidget(self.settings_btn)

    def setup_status_bar(self):
        """Setup enhanced status bar with multiple sections"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Style the status bar
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a, stop:1 #2d2d2d);
                border-top: 1px solid #555;
                color: white;
                padding: 2px;
            }
            QStatusBar::item {
                border: none;
                padding: 2px 8px;
            }
        """)

        # Main status message
        self.status_bar.showMessage("Ready - GP Manager")

        # Add permanent widgets for additional info
        from PyQt5.QtWidgets import QLabel

        # File count label
        self.file_count_label = QLabel("0 items")
        self.file_count_label.setStyleSheet("color: #ccc; padding: 2px 8px;")
        self.status_bar.addPermanentWidget(self.file_count_label)

        # Selection info label
        self.selection_label = QLabel("")
        self.selection_label.setStyleSheet("color: #ccc; padding: 2px 8px;")
        self.status_bar.addPermanentWidget(self.selection_label)

        # Tool status label
        self.tool_status_label = QLabel("Tools: Ready")
        self.tool_status_label.setStyleSheet("color: #4CAF50; padding: 2px 8px;")
        self.status_bar.addPermanentWidget(self.tool_status_label)

    def setup_connections(self):
        """Setup signal connections"""
        # File manager connections
        self.file_manager.file_selected.connect(self.on_file_selected)
        self.file_manager.file_double_clicked.connect(self.on_file_double_clicked)

        # Connect to file manager for directory changes
        if hasattr(self.file_manager, 'directory_changed'):
            self.file_manager.directory_changed.connect(self.on_directory_changed)

        # Archive viewer connections
        self.archive_viewer.file_double_clicked.connect(self.on_archive_file_double_clicked)

        # Text editor connections
        self.text_editor.file_modified.connect(self.on_file_modified)

        # APK tools connections
        if hasattr(self.apk_tools, 'operation_started'):
            self.apk_tools.operation_started.connect(self.on_apk_operation_started)
        if hasattr(self.apk_tools, 'operation_finished'):
            self.apk_tools.operation_finished.connect(self.on_apk_operation_finished)

        # Update navigation buttons when path changes
        self.update_navigation_buttons()

        # Initial file count update
        self.update_file_count()

    def setup_window_controls(self):
        """Setup window controls and properties"""
        # Set window properties
        self.setMinimumSize(800, 600)

        # Enable drag and drop
        self.setAcceptDrops(True)

        # Enable window controls
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowCloseButtonHint
        )

        # Set window icon (you can add an actual icon file later)
        # self.setWindowIcon(QIcon('resources/icons/gpmanager.png'))

        # Enable window scaling
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Set initial window state
        if config.get('window_maximized', False):
            self.showMaximized()

    def on_file_modified(self, file_path, is_modified):
        """Handle file modification status change"""
        # Suppress unused parameter warning
        _ = file_path

        self.unsaved_changes = is_modified
        self.update_window_title()

    def update_window_title(self):
        """Update window title based on current state"""
        title = "GP Manager"

        # Add current file info if available
        current_editor = self.text_editor.get_current_editor()
        if current_editor and current_editor.file_path:
            file_name = Path(current_editor.file_path).name
            if current_editor.is_modified:
                file_name += " *"
            title += f" - {file_name}"

        # Add unsaved changes indicator
        if self.unsaved_changes:
            title += " [Modified]"

        self.setWindowTitle(title)

    def on_directory_changed(self, directory_path):
        """Handle directory change in file manager"""
        self.update_file_count()
        self.status_bar.showMessage(f"Directory: {directory_path}")
        # Clear selection info
        self.selection_label.setText("")
        # Reset tool status
        self.tool_status_label.setText("Tools: Ready")
        self.tool_status_label.setStyleSheet("color: #4CAF50; padding: 2px 8px;")
        # Disable quick decompile if no APK selected
        self.quick_decompile_btn.setEnabled(False)

    def update_file_count(self):
        """Update file count in status bar"""
        try:
            # Get current directory from file manager
            current_path = getattr(self.file_manager, 'current_path', None)
            if current_path and Path(current_path).exists():
                items = list(Path(current_path).iterdir())
                file_count = len([item for item in items if item.is_file()])
                dir_count = len([item for item in items if item.is_dir()])

                if dir_count > 0:
                    count_text = f"{file_count} files, {dir_count} folders"
                else:
                    count_text = f"{file_count} files"

                self.file_count_label.setText(count_text)
            else:
                self.file_count_label.setText("0 items")
        except Exception:
            self.file_count_label.setText("0 items")

    def on_apk_operation_started(self, operation_name):
        """Handle APK operation start"""
        self.tool_status_label.setText(f"APK: {operation_name}...")
        self.tool_status_label.setStyleSheet("color: #FF9800; padding: 2px 8px;")
        self.status_bar.showMessage(f"APK operation: {operation_name}")

    def on_apk_operation_finished(self, operation_name, success):
        """Handle APK operation completion"""
        if success:
            self.tool_status_label.setText(f"APK: {operation_name} completed")
            self.tool_status_label.setStyleSheet("color: #4CAF50; padding: 2px 8px;")
            self.status_bar.showMessage(f"APK {operation_name} completed successfully")
        else:
            self.tool_status_label.setText(f"APK: {operation_name} failed")
            self.tool_status_label.setStyleSheet("color: #F44336; padding: 2px 8px;")
            self.status_bar.showMessage(f"APK {operation_name} failed")

    def load_settings(self):
        """Load application settings"""
        # Window geometry
        geometry = config.get('window_geometry', {})
        if geometry:
            self.resize(geometry.get('width', 1200), geometry.get('height', 800))
            self.move(geometry.get('x', 100), geometry.get('y', 100))
        else:
            self.resize(1200, 800)

    def save_settings(self):
        """Save application settings"""
        # Window geometry
        geometry = self.geometry()
        config.set('window_geometry', {
            'width': geometry.width(),
            'height': geometry.height(),
            'x': geometry.x(),
            'y': geometry.y()
        })

        # Window state
        config.set('window_maximized', self.isMaximized())

        # File manager state
        self.file_manager.save_state()

        # Save detached window states
        if self.window_manager:
            self.window_manager.save_all_states()

        config.save_config()

    def closeEvent(self, event):
        """Handle window close event with save confirmation"""
        # Check for unsaved changes in text editor
        if self.has_unsaved_changes():
            reply = self.show_save_confirmation()

            if reply == QMessageBox.Save:
                # Save all modified files
                if self.save_all_files():
                    self.save_settings()
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.Discard:
                # Close without saving
                self.save_settings()
                event.accept()
            else:  # Cancel
                event.ignore()
        else:
            # No unsaved changes, close normally
            self.save_settings()
            event.accept()

    def has_unsaved_changes(self):
        """Check if there are any unsaved changes"""
        # Check text editor tabs
        for i in range(self.text_editor.tab_widget.count()):
            editor = self.text_editor.tab_widget.widget(i)
            if editor and editor.is_modified:
                return True

        return False

    def show_save_confirmation(self):
        """Show save confirmation dialog"""
        modified_files = []

        # Collect modified files
        for i in range(self.text_editor.tab_widget.count()):
            editor = self.text_editor.tab_widget.widget(i)
            if editor and editor.is_modified:
                file_name = editor.get_file_name()
                modified_files.append(file_name)

        if len(modified_files) == 1:
            message = f"Save changes to {modified_files[0]}?"
        else:
            message = f"Save changes to {len(modified_files)} files?"
            message += "\n\nModified files:\n" + "\n".join(f"• {name}" for name in modified_files[:5])
            if len(modified_files) > 5:
                message += f"\n... and {len(modified_files) - 5} more"

        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            message,
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )

        return reply

    def save_all_files(self):
        """Save all modified files"""
        success = True

        for i in range(self.text_editor.tab_widget.count()):
            editor = self.text_editor.tab_widget.widget(i)
            if editor and editor.is_modified:
                if editor.file_path and not editor.file_path.startswith("Untitled"):
                    # Save existing file
                    if not editor.save_file():
                        success = False
                        break
                else:
                    # Need to save as new file
                    file_path, _ = QFileDialog.getSaveFileName(
                        self, f"Save {editor.get_file_name()}", "", "All Files (*)"
                    )
                    if file_path:
                        if not editor.save_file(file_path):
                            success = False
                            break
                    else:
                        # User cancelled save dialog
                        success = False
                        break

        return success

    # File operations
    def new_folder(self):
        """Create new folder"""
        self.file_manager.create_new_folder()

    def open_file(self):
        """Open file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*)"
        )
        if file_path:
            self.open_file_in_editor(file_path)

    def save_current_file(self):
        """Save current file in text editor"""
        return self.text_editor.save_current_file()

    def copy_files(self):
        """Copy selected files"""
        file_pane = self.file_manager.get_active_pane()
        if file_pane:
            file_pane.copy_selected()

    def cut_files(self):
        """Cut selected files"""
        file_pane = self.file_manager.get_active_pane()
        if file_pane:
            file_pane.cut_selected()

    def paste_files(self):
        """Paste files"""
        file_pane = self.file_manager.get_active_pane()
        if file_pane:
            file_pane.paste_files()

    def delete_files(self):
        """Delete selected files"""
        self.file_manager.delete_selected()

    def rename_file(self):
        """Rename selected file"""
        self.file_manager.rename_selected()

    def select_all(self):
        """Select all files in file manager"""
        file_pane = self.file_manager.get_active_pane()
        if file_pane:
            file_pane.tree_view.selectAll()

    def refresh_views(self):
        """Refresh file views"""
        self.file_manager.refresh_views()

    def navigate_up(self):
        """Navigate up in file manager"""
        self.file_manager.navigate_up()
        self.update_navigation_buttons()

    def go_back(self):
        """Go back in navigation history"""
        self.file_manager.go_back()
        self.update_navigation_buttons()

    def go_forward(self):
        """Go forward in navigation history"""
        self.file_manager.go_forward()
        self.update_navigation_buttons()

    def go_home(self):
        """Navigate to home directory"""
        self.file_manager.go_home()
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Update navigation button states based on file manager history"""
        if hasattr(self.file_manager, 'history_index') and hasattr(self.file_manager, 'history'):
            # Enable/disable back button
            self.back_btn.setEnabled(self.file_manager.history_index > 0)
            # Enable/disable forward button
            self.forward_btn.setEnabled(self.file_manager.history_index < len(self.file_manager.history) - 1)
        else:
            # Fallback if file manager doesn't have history
            self.back_btn.setEnabled(False)
            self.forward_btn.setEnabled(False)

    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    # File handling
    def on_file_selected(self, file_path):
        """Handle file selection with enhanced status updates"""
        file_name = Path(file_path).name
        file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0

        # Format file size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        elif file_size < 1024 * 1024 * 1024:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{file_size / (1024 * 1024 * 1024):.1f} GB"

        # Update status bar
        self.status_bar.showMessage(f"Selected: {file_name} ({size_str})")

        # Update selection label
        self.selection_label.setText(f"1 selected ({size_str})")

        # Update tool status based on file type
        if FileUtils.is_apk_file(file_path):
            self.tool_status_label.setText("APK: Ready to decompile")
            self.tool_status_label.setStyleSheet("color: #4CAF50; padding: 2px 8px;")
            # Enable quick decompile button
            self.quick_decompile_btn.setEnabled(True)
        elif FileUtils.is_archive_file(file_path):
            self.tool_status_label.setText("Archive: Ready to view")
            self.tool_status_label.setStyleSheet("color: #2196F3; padding: 2px 8px;")
            self.quick_decompile_btn.setEnabled(False)
        elif FileUtils.is_text_file(file_path):
            self.tool_status_label.setText("Text: Ready to edit")
            self.tool_status_label.setStyleSheet("color: #9C27B0; padding: 2px 8px;")
            self.quick_decompile_btn.setEnabled(False)
        else:
            self.tool_status_label.setText("Tools: Ready")
            self.tool_status_label.setStyleSheet("color: #666; padding: 2px 8px;")
            self.quick_decompile_btn.setEnabled(False)

    def on_file_double_clicked(self, file_path):
        """Handle file double click based on user preferences"""
        from src.utils.config import config

        print(f"DEBUG: Double-click detected on: {file_path}")
        print(f"DEBUG: File exists: {Path(file_path).exists()}")
        print(f"DEBUG: Is file: {Path(file_path).is_file()}")

        # Get user preference for double-click action
        double_click_action = config.get('double_click_action', 'Open')
        print(f"DEBUG: Double-click action: {double_click_action}")

        if double_click_action == 'Rename':
            # Trigger rename action
            self.rename_file(file_path)
            return
        elif double_click_action == 'Properties':
            # Show file properties
            self.show_file_properties(file_path)
            return

        # Default 'Open' behavior - smart file opening based on type
        if Path(file_path).is_file():
            print(f"DEBUG: Processing file: {file_path}")
            # Check file type and open in appropriate viewer
            if FileUtils.is_image_file(file_path):
                print(f"DEBUG: Detected as image file")
                # Open images in image viewer
                self.open_image_in_viewer(file_path)
            elif FileUtils.is_apk_file(file_path):
                print(f"DEBUG: Detected as APK file")
                # Load APK in APK tools
                self.apk_tools.set_apk_file(file_path)
                self.focus_tool("APK Tools")  # Switch to APK tools
            elif FileUtils.is_archive_file(file_path):
                print(f"DEBUG: Detected as archive file")
                # Load archive in archive viewer
                self.archive_viewer.load_archive(file_path)
                self.focus_tool("Archive Viewer")  # Switch to archive viewer
            elif FileUtils.is_dex_file(file_path):
                print(f"DEBUG: Detected as DEX file")
                # Load DEX in DEX editor
                self.open_dex_file(file_path)
            else:
                print(f"DEBUG: Detected as other file type, opening in text editor")
                # For text files and others, open in text editor
                self.open_file_in_editor(file_path)
        else:
            print(f"DEBUG: Not a file, showing options dialog")
            # For other file types, show options dialog
            self.show_file_open_options(file_path)

    def on_archive_file_double_clicked(self, archive_path, file_path):
        """Handle double click on file in archive"""
        # Extract file content and open in editor if it's a text file
        if FileUtils.is_text_file(file_path):
            content = self.archive_viewer.extract_file_content(file_path)
            if content:
                try:
                    text_content = content.decode('utf-8', errors='ignore')
                    # Create a temporary editor tab
                    self.text_editor.open_archive_file(archive_path, file_path, text_content)
                    self.focus_tool("Text Editor")  # Switch to editor
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to open file: {str(e)}")

    def open_file_in_editor(self, file_path):
        """Open file in text editor"""
        self.text_editor.open_file(file_path)
        self.focus_tool("Text Editor")  # Switch to editor

    def open_dex_file(self, file_path):
        """Open DEX file in DEX editor"""
        # Enable DEX editor if not already enabled
        if self.dex_editor is None:
            self.enable_dex_editor()

        if self.dex_editor:
            self.dex_editor.load_dex_file(file_path)
            self.focus_tool("DEX Editor")  # Switch to DEX editor

    def open_in_hex_editor(self, file_path):
        """Open file in hex editor"""
        # Enable hex editor if not already enabled
        if self.hex_editor is None:
            self.enable_hex_editor()

        try:
            if self.hex_editor and self.hex_editor.load_file(file_path):
                self.focus_tool("Hex Editor")  # Switch to hex editor
                self.status_bar.showMessage(f"Opened in hex editor: {Path(file_path).name}")
            else:
                QMessageBox.warning(self, "Hex Editor", f"Failed to open file: {Path(file_path).name}")
        except Exception as e:
            QMessageBox.warning(self, "Hex Editor", f"Error opening file: {str(e)}")

    def enable_hex_editor(self):
        """Enable the hex editor tool"""
        if self.hex_editor is None:
            try:
                from src.editors.hex_editor import HexEditor
                self.hex_editor = HexEditor()

                # Register with window manager
                self.window_manager.register_tool("Hex Editor", self.hex_editor)

                # Add to tool manager
                self.tool_manager.add_tool("Hex Editor", self.hex_editor)

                # Show detach option in menu
                self.detach_hex_action.setVisible(True)

                # Add toolbar button
                self.add_hex_editor_toolbar_button()

                self.status_bar.showMessage("Hex Editor enabled")

            except Exception as e:
                QMessageBox.warning(self, "Hex Editor", f"Failed to enable hex editor: {str(e)}")

    def enable_dex_editor(self):
        """Enable the DEX editor tool"""
        if self.dex_editor is None:
            try:
                from src.editors.dex_editor import DexEditor
                self.dex_editor = DexEditor()

                # Register with window manager
                self.window_manager.register_tool("DEX Editor", self.dex_editor)

                # Add to tool manager
                self.tool_manager.add_tool("DEX Editor", self.dex_editor)

                # Connect signals
                self.dex_editor.file_opened.connect(self.on_dex_file_opened)

                self.status_bar.showMessage("DEX Editor enabled")

            except Exception as e:
                QMessageBox.warning(self, "DEX Editor", f"Failed to enable DEX editor: {str(e)}")

    def on_dex_file_opened(self, file_path):
        """Handle DEX file opened in DEX editor"""
        self.status_bar.showMessage(f"DEX file loaded: {Path(file_path).name}")

    def add_hex_editor_toolbar_button(self):
        """Add hex editor button to toolbar"""
        # Find the toolbar
        toolbar = self.findChild(QWidget, "Main")
        if toolbar:
            # Create hex editor button
            hex_btn = QPushButton("🔧")
            hex_btn.setToolTip("Hex Editor")
            hex_btn.setFixedSize(32, 32)
            hex_btn.clicked.connect(lambda: self.focus_tool("Hex Editor"))

            # Insert before the last separator (tool management section)
            actions = toolbar.actions()
            if len(actions) >= 2:
                # Insert before the last separator
                toolbar.insertWidget(actions[-2], hex_btn)
            else:
                # Fallback: just add to the end
                toolbar.addWidget(hex_btn)

    def open_with_external_editor(self, file_path, editor_name=None):
        """Open file with external editor"""
        try:
            from src.editors.external_editor import external_editor_manager

            success, message = external_editor_manager.open_file(file_path, editor_name)
            if success:
                self.status_bar.showMessage(message)
            else:
                QMessageBox.warning(self, "External Editor", message)
        except Exception as e:
            QMessageBox.warning(self, "External Editor", f"Error opening file: {str(e)}")

    # Tool operations
    def decompile_apk(self):
        """Decompile selected APK"""
        selected_files = self.file_manager.get_current_selection()
        apk_files = [f for f in selected_files if FileUtils.is_apk_file(f)]

        if apk_files:
            self.apk_tools.set_apk_file(apk_files[0])
            self.focus_tool("APK Tools")
            # Switch to operations tab if APK tools has tabs
            if hasattr(self.apk_tools, 'tab_widget'):
                self.apk_tools.tab_widget.setCurrentIndex(1)  # Operations tab (index 1)
        else:
            QMessageBox.information(self, "No APK", "Please select an APK file first.")

    def quick_decompile_apk(self):
        """Quick decompile APK with one click"""
        selected_files = self.file_manager.get_current_selection()
        apk_files = [f for f in selected_files if FileUtils.is_apk_file(f)]

        if not apk_files:
            # Show file dialog to select APK
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select APK File", "", "APK Files (*.apk);;All Files (*)"
            )
            if file_path:
                apk_files = [file_path]
            else:
                return

        apk_path = apk_files[0]

        # Update status
        self.status_bar.showMessage(f"Quick decompiling: {Path(apk_path).name}")
        self.tool_status_label.setText("APK: Decompiling...")
        self.tool_status_label.setStyleSheet("color: #FF9800; padding: 2px 8px;")

        try:
            # Set APK in tools and switch to operations tab
            self.apk_tools.set_apk_file(apk_path)
            self.focus_tool("APK Tools")

            # Switch to operations tab
            if hasattr(self.apk_tools, 'tab_widget'):
                self.apk_tools.tab_widget.setCurrentIndex(1)  # Operations tab

            # Auto-start decompile if dependencies are OK
            if hasattr(self.apk_tools, 'dependencies_ok') and self.apk_tools.dependencies_ok:
                # Trigger decompile automatically
                if hasattr(self.apk_tools, 'decompile_apk'):
                    self.apk_tools.decompile_apk()
                    self.status_bar.showMessage(f"Decompiling {Path(apk_path).name}...")
                else:
                    self.status_bar.showMessage(f"APK loaded: {Path(apk_path).name} - Click Decompile to start")
            else:
                # Show setup tab if dependencies missing
                if hasattr(self.apk_tools, 'tab_widget'):
                    self.apk_tools.tab_widget.setCurrentIndex(2)  # Setup tab
                self.status_bar.showMessage("APK Tools dependencies missing - Check Setup tab")
                self.tool_status_label.setText("APK: Setup Required")
                self.tool_status_label.setStyleSheet("color: #F44336; padding: 2px 8px;")

        except Exception as e:
            QMessageBox.warning(self, "Quick Decompile Error", f"Failed to start decompile:\n{str(e)}")
            self.status_bar.showMessage("Quick decompile failed")
            self.tool_status_label.setText("APK: Error")
            self.tool_status_label.setStyleSheet("color: #F44336; padding: 2px 8px;")

    # Dialog methods
    def show_preferences(self):
        """Show preferences dialog"""
        dialog = PreferencesDialog(self)
        dialog.exec_()

    def configure_external_editors(self):
        """Configure external editors"""
        from src.editors.external_editor import external_editor_manager, ExternalEditorDialog

        dialog = ExternalEditorDialog(external_editor_manager, self)
        dialog.exec_()

    def detach_tool(self, tool_name):
        """Detach a tool to separate window"""
        if self.window_manager:
            self.window_manager.detach_tool(tool_name)

    def attach_tool(self, tool_name, tool_widget):
        """Attach a tool back to main window"""
        if self.tool_manager:
            self.tool_manager.add_tool(tool_name, tool_widget)

    def focus_tool(self, tool_name):
        """Focus on a specific tool"""
        # Check if tool is detached
        if self.window_manager and self.window_manager.is_tool_detached(tool_name):
            # Show detached window
            self.window_manager.show_detached_tool(tool_name)
        else:
            # Focus tool in main window
            if hasattr(self.tool_manager, 'focus_tool'):
                self.tool_manager.focus_tool(tool_name)
            elif hasattr(self.tool_manager, 'tab_widget'):
                # Find the tab with the tool
                for i in range(self.tool_manager.tab_widget.count()):
                    if self.tool_manager.tab_widget.tabText(i) == tool_name:
                        self.tool_manager.tab_widget.setCurrentIndex(i)
                        break

    def detach_current_tool(self):
        """Detach currently active tool"""
        # Get current tool from tool manager
        # This would need to be implemented based on tool manager structure
        QMessageBox.information(self, "Detach Tool", "Select a tool from the Tools menu to detach it.")

    def show_about(self):
        """Show about dialog"""
        dialog = AboutDialog(self)
        dialog.exec_()

    def show_setup_wizard(self):
        """Show setup wizard dialog"""
        try:
            from src.ui.install_wizard import InstallWizard
            dialog = InstallWizard(self)
            dialog.exec_()
        except ImportError as e:
            QMessageBox.warning(
                self, "Setup Wizard Error",
                f"Cannot load setup wizard: {e}\n\n"
                "Please run: python3 setup.py --gui"
            )

    # Drag and Drop Support
    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle drop event"""
        if event.mimeData().hasUrls():
            files = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    files.append(file_path)

            if files:
                self.handle_dropped_files(files)
                event.acceptProposedAction()
        else:
            event.ignore()

    def handle_dropped_files(self, files):
        """Handle dropped files"""
        for file_path in files:
            file_path = Path(file_path)

            if file_path.is_file():
                # Determine how to handle the file based on its type
                if FileUtils.is_image_file(str(file_path)):
                    # Open image files in image viewer
                    self.open_image_in_viewer(str(file_path))
                elif FileUtils.is_text_file(str(file_path)):
                    # Open text files in the text editor
                    self.open_file_in_editor(str(file_path))
                elif FileUtils.is_apk_file(str(file_path)):
                    # Load APK files in APK tools
                    self.apk_tools.set_apk_file(str(file_path))
                    self.focus_tool("APK Tools")
                elif FileUtils.is_archive_file(str(file_path)):
                    # Load archive files in archive viewer
                    self.archive_viewer.load_archive(str(file_path))
                    self.focus_tool("Archive Viewer")
                elif FileUtils.is_dex_file(str(file_path)):
                    # Load DEX files in DEX editor
                    self.open_dex_file(str(file_path))
                else:
                    # For other files, ask user what to do
                    self.show_file_open_options(str(file_path))
            elif file_path.is_dir():
                # Navigate to dropped directory
                self.file_manager.navigate_to(str(file_path))

    def show_file_open_options(self, file_path):
        """Show options for opening unknown file types"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

        dialog = QDialog(self)
        dialog.setWindowTitle("Open File")
        dialog.setModal(True)
        dialog.resize(500, 200)

        layout = QVBoxLayout(dialog)

        # File info
        file_name = Path(file_path).name
        layout.addWidget(QLabel(f"How would you like to open '{file_name}'?"))

        # Buttons
        button_layout = QHBoxLayout()

        # Add Image Viewer option for image files
        if FileUtils.is_image_file(file_path):
            image_btn = QPushButton("🖼️ Image Viewer")
            image_btn.clicked.connect(lambda: self.open_file_with_option(file_path, "image"))
            image_btn.clicked.connect(dialog.accept)
            button_layout.addWidget(image_btn)

        text_btn = QPushButton("📝 Text Editor")
        text_btn.clicked.connect(lambda: self.open_file_with_option(file_path, "text"))
        text_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(text_btn)

        hex_btn = QPushButton("🔧 Hex Editor")
        hex_btn.clicked.connect(lambda: self.open_file_with_option(file_path, "hex"))
        hex_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(hex_btn)

        external_btn = QPushButton("⚙️ External Editor")
        external_btn.clicked.connect(lambda: self.open_file_with_option(file_path, "external"))
        external_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(external_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec_()

    def open_file_with_option(self, file_path, option):
        """Open file with specified option"""
        if option == "text":
            self.open_file_in_editor(file_path)
        elif option == "hex":
            self.open_in_hex_editor(file_path)
        elif option == "external":
            self.open_with_external_editor(file_path)
        elif option == "image":
            self.open_image_in_viewer(file_path)
        elif option == "dex":
            self.open_dex_file(file_path)

    def rename_file(self, file_path):
        """Rename a file"""
        from PyQt5.QtWidgets import QInputDialog
        old_path = Path(file_path)
        new_name, ok = QInputDialog.getText(
            self, "Rename", "New name:", text=old_path.name
        )
        if ok and new_name and new_name != old_path.name:
            try:
                new_path = old_path.parent / new_name
                old_path.rename(new_path)
                self.file_manager.refresh_views()
                self.status_bar.showMessage(f"Renamed to: {new_name}")
            except Exception as e:
                QMessageBox.warning(self, "Rename Error", f"Failed to rename file:\n{str(e)}")

    def show_file_properties(self, file_path):
        """Show file properties dialog"""
        from src.ui.dialogs import FilePropertiesDialog
        dialog = FilePropertiesDialog(file_path, self)
        dialog.exec_()

    def open_image_in_viewer(self, file_path):
        """Open image file in the image viewer"""
        try:
            print(f"DEBUG: Attempting to open image: {file_path}")
            print(f"DEBUG: File exists: {Path(file_path).exists()}")
            print(f"DEBUG: Is image file: {FileUtils.is_image_file(file_path)}")

            # Load the image in the image viewer
            if self.image_viewer.load_image(file_path):
                # Switch to image viewer tool
                self.focus_tool("Image Viewer")
                self.status_bar.showMessage(f"Opened image: {Path(file_path).name}")
                print(f"DEBUG: Successfully opened image in viewer")
                return True
            else:
                print(f"DEBUG: Image viewer load_image returned False")
                return False
        except Exception as e:
            print(f"DEBUG: Exception in open_image_in_viewer: {str(e)}")
            QMessageBox.warning(self, "Image Viewer", f"Failed to open image: {str(e)}")
            return False
