"""
Dual pane file manager for GP Manager
"""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSplitter, QVBoxLayout, QLabel
from src.file_manager.file_pane import FilePane
from src.file_manager.file_operations import FileOperations
from src.utils.config import config


class DualPaneManager(QWidget):
    """Dual pane file manager widget"""

    file_selected = pyqtSignal(str)
    file_double_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_pane = None
        self.setup_ui()
        self.setup_connections()

        # Initialize file operations
        self.file_operations = FileOperations(self)

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create splitter for dual panes
        self.splitter = QSplitter(Qt.Horizontal)

        # Create left and right panes
        self.left_pane = FilePane(parent=self)
        self.right_pane = FilePane(parent=self)

        # Add panes to splitter
        self.splitter.addWidget(self.left_pane)
        self.splitter.addWidget(self.right_pane)

        # Set initial splitter ratio
        ratio = config.get('pane_splitter_ratio', 0.5)
        self.splitter.setSizes([int(1000 * ratio), int(1000 * (1 - ratio))])

        layout.addWidget(self.splitter)

        # Set left pane as initially active
        self.set_active_pane(self.left_pane)

    def setup_connections(self):
        """Setup signal connections"""
        # Left pane connections
        self.left_pane.file_selected.connect(self.on_file_selected)
        self.left_pane.file_double_clicked.connect(self.on_file_double_clicked)
        self.left_pane.tree_view.clicked.connect(
            lambda: self.set_active_pane(self.left_pane)
        )

        # Right pane connections
        self.right_pane.file_selected.connect(self.on_file_selected)
        self.right_pane.file_double_clicked.connect(self.on_file_double_clicked)
        self.right_pane.tree_view.clicked.connect(
            lambda: self.set_active_pane(self.right_pane)
        )

    def set_active_pane(self, pane):
        """Set the active pane"""
        if self.active_pane:
            # Remove focus styling from previous active pane
            self.active_pane.setStyleSheet("")

        self.active_pane = pane

        # Add focus styling to active pane
        pane.setStyleSheet("""
            QWidget {
                border: 2px solid #0078d4;
            }
        """)

        pane.set_focus()

    def get_active_pane(self):
        """Get the currently active pane"""
        return self.active_pane

    def get_inactive_pane(self):
        """Get the inactive pane"""
        if self.active_pane == self.left_pane:
            return self.right_pane
        else:
            return self.left_pane

    def on_file_selected(self, file_path):
        """Handle file selection"""
        self.file_selected.emit(file_path)

    def on_file_double_clicked(self, file_path):
        """Handle file double click"""
        self.file_double_clicked.emit(file_path)

    def refresh_views(self):
        """Refresh both panes"""
        self.left_pane.refresh()
        self.right_pane.refresh()

    def copy_to_other_pane(self):
        """Copy selected files from active pane to inactive pane"""
        if not self.active_pane:
            return

        selected_files = self.active_pane.get_selected_files()
        if not selected_files:
            return

        inactive_pane = self.get_inactive_pane()
        destination = inactive_pane.get_current_path()

        self.file_operations.copy_files(selected_files, destination)

    def move_to_other_pane(self):
        """Move selected files from active pane to inactive pane"""
        if not self.active_pane:
            return

        selected_files = self.active_pane.get_selected_files()
        if not selected_files:
            return

        inactive_pane = self.get_inactive_pane()
        destination = inactive_pane.get_current_path()

        self.file_operations.move_files(selected_files, destination)

    def delete_selected(self):
        """Delete selected files from active pane"""
        if not self.active_pane:
            return

        selected_files = self.active_pane.get_selected_files()
        if selected_files:
            self.file_operations.delete_files(selected_files)

    def rename_selected(self):
        """Rename selected file in active pane"""
        if self.active_pane:
            self.active_pane.rename_selected()

    def create_new_folder(self):
        """Create new folder in active pane"""
        if self.active_pane:
            self.active_pane.create_new_folder()

    def navigate_up(self):
        """Navigate up in active pane"""
        if self.active_pane:
            self.active_pane.navigate_up()

    def refresh_active_pane(self):
        """Refresh active pane"""
        if self.active_pane:
            self.active_pane.refresh()

    def swap_panes(self):
        """Swap the contents of left and right panes"""
        left_path = self.left_pane.get_current_path()
        right_path = self.right_pane.get_current_path()

        self.left_pane.load_directory(right_path)
        self.right_pane.load_directory(left_path)

    def sync_panes(self):
        """Sync inactive pane to active pane's directory"""
        if self.active_pane:
            active_path = self.active_pane.get_current_path()
            inactive_pane = self.get_inactive_pane()
            inactive_pane.load_directory(active_path)

    def get_splitter_ratio(self):
        """Get current splitter ratio"""
        sizes = self.splitter.sizes()
        if sum(sizes) > 0:
            return sizes[0] / sum(sizes)
        return 0.5

    def set_splitter_ratio(self, ratio):
        """Set splitter ratio"""
        total_size = 1000
        left_size = int(total_size * ratio)
        right_size = total_size - left_size
        self.splitter.setSizes([left_size, right_size])

    def save_state(self):
        """Save pane state to config"""
        config.set('pane_splitter_ratio', self.get_splitter_ratio())
        config.save_config()

    def get_current_selection(self):
        """Get currently selected files from active pane"""
        if self.active_pane:
            return self.active_pane.get_selected_files()
        return []
