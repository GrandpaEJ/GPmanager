"""
File pane widget for GP Manager
"""
import os
from pathlib import Path
from PyQt5.QtCore import Qt, QDir, QFileInfo, pyqtSignal, QModelIndex
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeView,
                            QLineEdit, QPushButton, QHeaderView, QMenu,
                            QInputDialog, QMessageBox, QApplication)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QFont
from src.utils.file_utils import FileUtils
from src.utils.config import config
from src.editors.external_editor import external_editor_manager


class FileModel(QStandardItemModel):
    """Custom file model for the tree view"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(['Name', 'Size', 'Type', 'Modified'])
        self.current_path = Path.home()
        self.show_hidden = config.get('show_hidden_files', False)

    def load_directory(self, path):
        """Load directory contents into the model"""
        self.clear()
        self.setHorizontalHeaderLabels(['Name', 'Size', 'Type', 'Modified'])

        try:
            path = Path(path)
            self.current_path = path

            # Add parent directory entry if not at root
            if path.parent != path:
                parent_item = QStandardItem('..')
                parent_item.setData(str(path.parent), Qt.UserRole)
                parent_item.setIcon(QIcon())  # Folder icon
                size_item = QStandardItem('')
                type_item = QStandardItem('Folder')
                modified_item = QStandardItem('')
                self.appendRow([parent_item, size_item, type_item, modified_item])

            # Get directory contents
            try:
                entries = list(path.iterdir())
            except PermissionError:
                return

            # Sort entries: directories first, then files
            entries.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

            for entry in entries:
                if not self.show_hidden and FileUtils.is_hidden_file(str(entry)):
                    continue

                # Name column
                name_item = QStandardItem(entry.name)
                name_item.setData(str(entry), Qt.UserRole)

                # Set icon based on file type
                icon_type = FileUtils.get_file_icon_type(str(entry))
                name_item.setIcon(QIcon())  # You can add actual icons here

                # Size column
                if entry.is_file():
                    try:
                        size = entry.stat().st_size
                        size_str = FileUtils.get_file_size_str(size)
                    except OSError:
                        size_str = 'Unknown'
                else:
                    size_str = ''
                size_item = QStandardItem(size_str)

                # Type column
                if entry.is_dir():
                    type_str = 'Folder'
                else:
                    type_str = entry.suffix.upper()[1:] if entry.suffix else 'File'
                type_item = QStandardItem(type_str)

                # Modified column
                modified_str = FileUtils.get_file_modified_time(str(entry))
                modified_item = QStandardItem(modified_str)

                self.appendRow([name_item, size_item, type_item, modified_item])

        except Exception as e:
            print(f"Error loading directory: {e}")


class FilePane(QWidget):
    """File browser pane widget"""

    path_changed = pyqtSignal(str)
    file_selected = pyqtSignal(str)
    file_double_clicked = pyqtSignal(str)

    def __init__(self, initial_path=None, parent=None):
        super().__init__(parent)
        self.current_path = Path(initial_path or Path.home())
        self.setup_ui()
        self.setup_connections()
        self.load_directory(str(self.current_path))

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Address bar
        address_layout = QHBoxLayout()
        self.address_edit = QLineEdit()
        self.address_edit.setText(str(self.current_path))
        self.up_button = QPushButton('↑')
        self.up_button.setMaximumWidth(30)
        self.refresh_button = QPushButton('⟳')
        self.refresh_button.setMaximumWidth(30)

        address_layout.addWidget(self.address_edit)
        address_layout.addWidget(self.up_button)
        address_layout.addWidget(self.refresh_button)

        layout.addLayout(address_layout)

        # File tree view
        self.tree_view = QTreeView()
        self.file_model = FileModel()
        self.tree_view.setModel(self.file_model)

        # Configure tree view
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSelectionMode(QTreeView.ExtendedSelection)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.setSortingEnabled(True)

        # Set column widths
        header = self.tree_view.header()
        header.resizeSection(0, 200)  # Name
        header.resizeSection(1, 80)   # Size
        header.resizeSection(2, 60)   # Type
        header.resizeSection(3, 120)  # Modified

        layout.addWidget(self.tree_view)

        # Status label
        self.status_label = QLineEdit()
        self.status_label.setReadOnly(True)
        self.status_label.setMaximumHeight(25)
        layout.addWidget(self.status_label)

    def setup_connections(self):
        """Setup signal connections"""
        self.address_edit.returnPressed.connect(self.navigate_to_address)
        self.up_button.clicked.connect(self.navigate_up)
        self.refresh_button.clicked.connect(self.refresh)

        self.tree_view.doubleClicked.connect(self.on_double_click)
        self.tree_view.clicked.connect(self.on_single_click)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)

    def load_directory(self, path):
        """Load directory into the file view"""
        try:
            path = Path(path)
            if path.exists() and path.is_dir():
                self.current_path = path
                self.file_model.load_directory(str(path))
                self.address_edit.setText(str(path))
                self.update_status()
                self.path_changed.emit(str(path))
                config.add_recent_path(str(path))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot access directory: {e}")

    def navigate_to_address(self):
        """Navigate to the path in address bar"""
        path = self.address_edit.text().strip()
        if path:
            self.load_directory(path)

    def navigate_up(self):
        """Navigate to parent directory"""
        parent = self.current_path.parent
        if parent != self.current_path:
            self.load_directory(str(parent))

    def refresh(self):
        """Refresh current directory"""
        self.load_directory(str(self.current_path))

    def on_double_click(self, index):
        """Handle double click on item"""
        if not index.isValid():
            return

        item = self.file_model.itemFromIndex(index)
        if item is None:
            return

        file_path = item.data(Qt.UserRole)
        if file_path:
            path = Path(file_path)
            if path.is_dir():
                self.load_directory(str(path))
            else:
                self.file_double_clicked.emit(str(path))

    def on_single_click(self, index):
        """Handle single click on item"""
        if not index.isValid():
            return

        item = self.file_model.itemFromIndex(index)
        if item is None:
            return

        file_path = item.data(Qt.UserRole)
        if file_path:
            self.file_selected.emit(file_path)

    def get_selected_files(self):
        """Get list of selected file paths"""
        selected_files = []
        selection = self.tree_view.selectionModel()
        if selection:
            for index in selection.selectedRows():
                item = self.file_model.itemFromIndex(index)
                if item:
                    file_path = item.data(Qt.UserRole)
                    if file_path and file_path != '..':
                        selected_files.append(file_path)
        return selected_files

    def show_context_menu(self, position):
        """Show context menu"""
        index = self.tree_view.indexAt(position)
        menu = QMenu(self)

        # Common actions
        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(self.refresh)

        new_folder_action = menu.addAction("New Folder")
        new_folder_action.triggered.connect(self.create_new_folder)

        menu.addSeparator()

        if index.isValid():
            item = self.file_model.itemFromIndex(index)
            if item:
                file_path = item.data(Qt.UserRole)
                if file_path and file_path != '..':
                    # File/folder specific actions
                    copy_action = menu.addAction("Copy")
                    copy_action.triggered.connect(self.copy_selected)

                    cut_action = menu.addAction("Cut")
                    cut_action.triggered.connect(self.cut_selected)

                    rename_action = menu.addAction("Rename")
                    rename_action.triggered.connect(self.rename_selected)

                    delete_action = menu.addAction("Delete")
                    delete_action.triggered.connect(self.delete_selected)

                    menu.addSeparator()

                    # Open with external editors
                    if Path(file_path).is_file():
                        self.add_external_editor_menu(menu, file_path)

                    menu.addSeparator()

                    # APK specific actions
                    if FileUtils.is_apk_file(file_path):
                        decompile_action = menu.addAction("Decompile APK")
                        decompile_action.triggered.connect(
                            lambda: self.decompile_apk(file_path)
                        )

        # Show paste option if clipboard has files
        if hasattr(self, 'clipboard_files') and self.clipboard_files:
            paste_action = menu.addAction("Paste")
            paste_action.triggered.connect(self.paste_files)

        menu.exec_(self.tree_view.mapToGlobal(position))

    def update_status(self):
        """Update status bar with directory info"""
        try:
            items = list(self.current_path.iterdir())
            folders = sum(1 for item in items if item.is_dir())
            files = len(items) - folders
            self.status_label.setText(f"{folders} folders, {files} files")
        except:
            self.status_label.setText("Access denied")

    # Placeholder methods for context menu actions
    def create_new_folder(self):
        """Create new folder"""
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and name:
            if hasattr(self.parent(), 'file_operations'):
                self.parent().file_operations.create_folder(str(self.current_path), name)

    def copy_selected(self):
        """Copy selected files to clipboard"""
        selected = self.get_selected_files()
        if selected:
            self.clipboard_files = ('copy', selected)

    def cut_selected(self):
        """Cut selected files to clipboard"""
        selected = self.get_selected_files()
        if selected:
            self.clipboard_files = ('cut', selected)

    def paste_files(self):
        """Paste files from clipboard"""
        if hasattr(self, 'clipboard_files') and self.clipboard_files:
            operation, files = self.clipboard_files
            if hasattr(self.parent(), 'file_operations'):
                if operation == 'copy':
                    self.parent().file_operations.copy_files(files, str(self.current_path))
                elif operation == 'cut':
                    self.parent().file_operations.move_files(files, str(self.current_path))
                    self.clipboard_files = None

    def rename_selected(self):
        """Rename selected file"""
        selected = self.get_selected_files()
        if len(selected) == 1:
            old_path = Path(selected[0])
            new_name, ok = QInputDialog.getText(
                self, "Rename", "New name:", text=old_path.name
            )
            if ok and new_name:
                if hasattr(self.parent(), 'file_operations'):
                    self.parent().file_operations.rename_file(selected[0], new_name)

    def delete_selected(self):
        """Delete selected files"""
        selected = self.get_selected_files()
        if selected and hasattr(self.parent(), 'file_operations'):
            self.parent().file_operations.delete_files(selected)

    def decompile_apk(self, apk_path):
        """Decompile APK file"""
        if hasattr(self.parent(), 'apk_tools'):
            self.parent().apk_tools.decompile_apk(apk_path)

    def get_current_path(self):
        """Get current directory path"""
        return str(self.current_path)

    def set_focus(self):
        """Set focus to this pane"""
        self.tree_view.setFocus()

    def add_external_editor_menu(self, menu, file_path):
        """Add external editor submenu"""
        from src.editors.external_editor import external_editor_manager

        # Get suitable editors for this file
        suitable_editors = external_editor_manager.get_editors_for_file(file_path)

        if suitable_editors:
            # Create "Open with" submenu
            open_with_menu = menu.addMenu("Open with")

            # Add built-in hex editor for all files
            hex_editor_action = open_with_menu.addAction("🔧 Built-in Hex Editor")
            hex_editor_action.triggered.connect(
                lambda: self.open_in_hex_editor(file_path)
            )

            if suitable_editors:
                open_with_menu.addSeparator()

            # Add external editors
            for editor in suitable_editors[:10]:  # Limit to 10 editors
                icon = "📝" if "text" in editor.name.lower() else "⚙️"
                action_text = f"{icon} {editor.name}"
                action = open_with_menu.addAction(action_text)
                action.triggered.connect(
                    lambda checked, e=editor.name: self.open_with_external_editor(file_path, e)
                )

            # Add "Choose application" option
            if len(suitable_editors) > 10:
                open_with_menu.addSeparator()
                choose_action = open_with_menu.addAction("📋 Choose application...")
                choose_action.triggered.connect(
                    lambda: self.choose_external_editor(file_path)
                )

            # Add "Configure editors" option
            open_with_menu.addSeparator()
            config_action = open_with_menu.addAction("⚙️ Configure editors...")
            config_action.triggered.connect(self.configure_external_editors)
        else:
            # No suitable editors, just add hex editor and configure option
            hex_editor_action = menu.addAction("🔧 Open in Hex Editor")
            hex_editor_action.triggered.connect(
                lambda: self.open_in_hex_editor(file_path)
            )

            config_action = menu.addAction("⚙️ Configure external editors...")
            config_action.triggered.connect(self.configure_external_editors)

    def open_with_external_editor(self, file_path, editor_name):
        """Open file with specific external editor"""
        # Try to find main window and use its method
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'open_with_external_editor'):
            main_window.open_with_external_editor(file_path, editor_name)
        else:
            # Fallback to direct call
            from src.editors.external_editor import external_editor_manager
            success, message = external_editor_manager.open_file(file_path, editor_name)
            if not success:
                QMessageBox.warning(self, "External Editor", message)

    def choose_external_editor(self, file_path):
        """Show dialog to choose external editor"""
        from src.editors.external_editor import external_editor_manager
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Choose External Editor")
        dialog.setModal(True)
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)

        editor_list = QListWidget()
        suitable_editors = external_editor_manager.get_editors_for_file(file_path)

        for editor in suitable_editors:
            item_text = f"{editor.name} - {editor.description}"
            editor_list.addItem(item_text)

        layout.addWidget(editor_list)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            current_row = editor_list.currentRow()
            if current_row >= 0:
                editor = suitable_editors[current_row]
                self.open_with_external_editor(file_path, editor.name)

    def configure_external_editors(self):
        """Open external editors configuration dialog"""
        from src.editors.external_editor import external_editor_manager, ExternalEditorDialog

        dialog = ExternalEditorDialog(external_editor_manager, self)
        dialog.exec_()

    def get_main_window(self):
        """Find and return the main window"""
        widget = self
        while widget.parent():
            widget = widget.parent()
            if hasattr(widget, 'open_with_external_editor') and hasattr(widget, 'open_in_hex_editor'):
                return widget
        return None

    def open_in_hex_editor(self, file_path):
        """Open file in built-in hex editor"""
        # Try to find main window and use its method
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'open_in_hex_editor'):
            main_window.open_in_hex_editor(file_path)
        else:
            QMessageBox.information(self, "Hex Editor", "Hex editor not available")
