"""
Single pane file manager for GP Manager
"""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
from src.file_manager.file_pane import FilePane
from src.file_manager.file_operations import FileOperations
from src.utils.config import config


class SinglePaneManager(QWidget):
    """Single pane file manager widget"""

    file_selected = pyqtSignal(str)
    file_double_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

        # Initialize file operations
        self.file_operations = FileOperations(self)

        # Load initial paths
        self.load_initial_state()

    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Address bar only (navigation buttons are in main toolbar)
        nav_layout = QHBoxLayout()

        # Current path label
        path_label = QLabel("Path:")
        path_label.setMinimumWidth(40)
        nav_layout.addWidget(path_label)

        # Address bar
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Enter path or press Enter to navigate...")
        self.address_edit.returnPressed.connect(self.navigate_to_address)
        nav_layout.addWidget(self.address_edit)

        layout.addLayout(nav_layout)

        # File pane
        self.file_pane = FilePane()
        layout.addWidget(self.file_pane)

        # Status bar
        status_layout = QHBoxLayout()

        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        self.selection_label = QLabel("")
        status_layout.addWidget(self.selection_label)

        layout.addLayout(status_layout)

        # Navigation history
        self.history = []
        self.history_index = -1

    def setup_connections(self):
        """Setup signal connections"""
        self.file_pane.file_selected.connect(self.on_file_selected)
        self.file_pane.file_double_clicked.connect(self.on_file_double_clicked)
        self.file_pane.path_changed.connect(self.on_path_changed)

    def load_initial_state(self):
        """Load initial file manager state"""
        # Load last path or default to home
        last_path = config.get('last_path', str(self.file_pane.current_path))
        self.navigate_to(last_path)

    def save_state(self):
        """Save current state"""
        config.set('last_path', str(self.file_pane.current_path))
        config.save_config()

    def navigate_to(self, path):
        """Navigate to specific path"""
        if self.file_pane.load_directory(path):
            self.add_to_history(path)
            self.update_navigation_buttons()
            self.address_edit.setText(path)

    def navigate_to_address(self):
        """Navigate to path in address bar"""
        path = self.address_edit.text().strip()
        if path:
            self.navigate_to(path)

    def navigate_up(self):
        """Navigate to parent directory"""
        current_path = self.file_pane.current_path
        parent = current_path.parent
        if parent != current_path:
            self.navigate_to(str(parent))

    def go_back(self):
        """Go back in history"""
        if self.history_index > 0:
            self.history_index -= 1
            path = self.history[self.history_index]
            self.file_pane.load_directory(path)
            self.address_edit.setText(path)
            self.update_navigation_buttons()

    def go_forward(self):
        """Go forward in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            path = self.history[self.history_index]
            self.file_pane.load_directory(path)
            self.address_edit.setText(path)
            self.update_navigation_buttons()

    def go_home(self):
        """Navigate to home directory"""
        from pathlib import Path
        self.navigate_to(str(Path.home()))

    def refresh(self):
        """Refresh current directory"""
        self.file_pane.refresh()

    def add_to_history(self, path):
        """Add path to navigation history"""
        # Remove any forward history if we're not at the end
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]

        # Add new path if it's different from current
        if not self.history or self.history[-1] != path:
            self.history.append(path)
            self.history_index = len(self.history) - 1

        # Limit history size
        if len(self.history) > 50:
            self.history = self.history[-50:]
            self.history_index = len(self.history) - 1

    def update_navigation_buttons(self):
        """Update navigation button states (handled by main toolbar now)"""
        # Navigation buttons are now in the main toolbar
        # This method is kept for compatibility but does nothing
        pass

    def on_file_selected(self, file_path):
        """Handle file selection"""
        self.file_selected.emit(file_path)

        # Update selection status
        selected_files = self.file_pane.get_selected_files()
        if len(selected_files) == 0:
            self.selection_label.setText("")
        elif len(selected_files) == 1:
            self.selection_label.setText(f"1 item selected")
        else:
            self.selection_label.setText(f"{len(selected_files)} items selected")

    def on_file_double_clicked(self, file_path):
        """Handle file double click"""
        self.file_double_clicked.emit(file_path)

    def on_path_changed(self, path):
        """Handle path change"""
        self.status_label.setText(f"Path: {path}")
        self.address_edit.setText(path)

    # File operations interface (for compatibility with existing code)
    def get_active_pane(self):
        """Get the active (only) pane"""
        return self.file_pane

    def get_current_selection(self):
        """Get currently selected files"""
        return self.file_pane.get_selected_files()

    def create_new_folder(self):
        """Create new folder"""
        self.file_pane.create_new_folder()

    def delete_selected(self):
        """Delete selected files"""
        selected = self.file_pane.get_selected_files()
        if selected:
            self.file_operations.delete_files(selected)

    def rename_selected(self):
        """Rename selected file"""
        self.file_pane.rename_selected()

    def refresh_views(self):
        """Refresh file view"""
        self.refresh()

    def copy_to_other_pane(self):
        """Copy files (single pane - show message)"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Single Pane Mode",
                              "Copy to other pane is not available in single pane mode.\n"
                              "Use Ctrl+C to copy and Ctrl+V to paste instead.")

    def move_to_other_pane(self):
        """Move files (single pane - show message)"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Single Pane Mode",
                              "Move to other pane is not available in single pane mode.\n"
                              "Use Ctrl+X to cut and Ctrl+V to paste instead.")

    def swap_panes(self):
        """Swap panes (single pane - not applicable)"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Single Pane Mode",
                              "Swap panes is not available in single pane mode.")

    def sync_panes(self):
        """Sync panes (single pane - not applicable)"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Single Pane Mode",
                              "Sync panes is not available in single pane mode.")

    def open_in_hex_editor(self, file_path):
        """Open file in hex editor"""
        # Forward to parent if available
        if hasattr(self.parent(), 'open_in_hex_editor'):
            self.parent().open_in_hex_editor(file_path)

    def get_current_path(self):
        """Get current directory path"""
        return str(self.file_pane.current_path)
