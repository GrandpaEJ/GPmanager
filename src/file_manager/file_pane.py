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
        """Show comprehensive context menu"""
        index = self.tree_view.indexAt(position)
        menu = QMenu(self)

        if index.isValid():
            item = self.file_model.itemFromIndex(index)
            if item:
                file_path = item.data(Qt.UserRole)
                if file_path and file_path != '..':
                    path = Path(file_path)

                    # === OPEN WITH SECTION ===
                    open_menu = menu.addMenu("📂 Open with")

                    # Text Editor
                    text_action = open_menu.addAction("📝 Text Editor")
                    text_action.triggered.connect(lambda: self.open_with_text_editor(file_path))

                    # Hex Editor
                    hex_action = open_menu.addAction("🔧 Hex Editor")
                    hex_action.triggered.connect(lambda: self.open_in_hex_editor(file_path))

                    # DEX Editor (for .dex files)
                    if self.is_dex_file(file_path):
                        dex_action = open_menu.addAction("⚙️ DEX Editor")
                        dex_action.triggered.connect(lambda: self.open_in_dex_editor(file_path))

                    open_menu.addSeparator()

                    # External Editors submenu
                    if path.is_file():
                        self.add_external_editor_menu(open_menu, file_path)

                    # Media viewers for specific file types
                    if self.is_image_file(file_path):
                        image_action = open_menu.addAction("🖼️ Image Viewer")
                        image_action.triggered.connect(lambda: self.open_as_image(file_path))

                    if self.is_video_file(file_path):
                        video_action = open_menu.addAction("🎬 Video Player")
                        video_action.triggered.connect(lambda: self.open_as_video(file_path))

                    if self.is_audio_file(file_path):
                        audio_action = open_menu.addAction("🎵 Audio Player")
                        audio_action.triggered.connect(lambda: self.open_as_audio(file_path))

                    # System default
                    open_menu.addSeparator()
                    system_action = open_menu.addAction("⚙️ System Default")
                    system_action.triggered.connect(lambda: self.open_with_system_default(file_path))

                    menu.addSeparator()

                    # === APK TOOLS SECTION ===
                    if FileUtils.is_apk_file(file_path):
                        apk_menu = menu.addMenu("📱 APK Tools")

                        decompile_action = apk_menu.addAction("🔓 Decompile")
                        decompile_action.triggered.connect(lambda: self.decompile_apk(file_path))

                        recompile_action = apk_menu.addAction("🔒 Recompile")
                        recompile_action.triggered.connect(lambda: self.recompile_apk(file_path))

                        apk_menu.addSeparator()

                        info_action = apk_menu.addAction("ℹ️ APK Info")
                        info_action.triggered.connect(lambda: self.show_apk_info(file_path))

                        extract_action = apk_menu.addAction("📦 Extract APK")
                        extract_action.triggered.connect(lambda: self.extract_apk(file_path))

                        menu.addSeparator()

                    # === ARCHIVE TOOLS SECTION ===
                    if FileUtils.is_archive_file(file_path) and not FileUtils.is_apk_file(file_path):
                        archive_menu = menu.addMenu("📦 Archive Tools")

                        extract_action = archive_menu.addAction("📤 Extract Here")
                        extract_action.triggered.connect(lambda: self.extract_archive(file_path))

                        extract_to_action = archive_menu.addAction("📁 Extract To...")
                        extract_to_action.triggered.connect(lambda: self.extract_archive_to(file_path))

                        view_action = archive_menu.addAction("👁️ View Contents")
                        view_action.triggered.connect(lambda: self.view_archive_contents(file_path))

                        menu.addSeparator()

                    # === FILE OPERATIONS SECTION ===
                    file_ops_menu = menu.addMenu("📋 File Operations")

                    copy_action = file_ops_menu.addAction("📄 Copy")
                    copy_action.triggered.connect(self.copy_selected)

                    cut_action = file_ops_menu.addAction("✂️ Cut")
                    cut_action.triggered.connect(self.cut_selected)

                    rename_action = file_ops_menu.addAction("✏️ Rename")
                    rename_action.triggered.connect(self.rename_selected)

                    file_ops_menu.addSeparator()

                    delete_action = file_ops_menu.addAction("🗑️ Delete")
                    delete_action.triggered.connect(self.delete_selected)

                    menu.addSeparator()

                    # === TOOLS SECTION ===
                    tools_menu = menu.addMenu("🔧 Tools")

                    # Compression tools
                    if path.is_file():
                        compress_action = tools_menu.addAction("🗜️ Compress")
                        compress_action.triggered.connect(lambda: self.compress_file(file_path))

                    # Hash calculation
                    hash_action = tools_menu.addAction("🔐 Calculate Hash")
                    hash_action.triggered.connect(lambda: self.calculate_hash(file_path))

                    # File comparison
                    compare_action = tools_menu.addAction("⚖️ Compare Files")
                    compare_action.triggered.connect(lambda: self.compare_files(file_path))

                    menu.addSeparator()

                    # === PROPERTIES ===
                    properties_action = menu.addAction("ℹ️ Properties")
                    properties_action.triggered.connect(lambda: self.show_properties(file_path))

        # === GENERAL ACTIONS ===
        menu.addSeparator()

        # Paste option if clipboard has files
        if hasattr(self, 'clipboard_files') and self.clipboard_files:
            paste_action = menu.addAction("📋 Paste")
            paste_action.triggered.connect(self.paste_files)

        # General folder actions
        new_folder_action = menu.addAction("📁 New Folder")
        new_folder_action.triggered.connect(self.create_new_folder)

        new_file_action = menu.addAction("📄 New File")
        new_file_action.triggered.connect(self.create_new_file)

        menu.addSeparator()

        refresh_action = menu.addAction("🔄 Refresh")
        refresh_action.triggered.connect(self.refresh)

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

    def open_in_dex_editor(self, file_path):
        """Open file in DEX editor"""
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'open_dex_file'):
            main_window.open_dex_file(file_path)
        else:
            QMessageBox.information(self, "DEX Editor", "DEX editor not available")

    # === FILE TYPE DETECTION METHODS ===
    def is_image_file(self, file_path):
        """Check if file is an image"""
        ext = Path(file_path).suffix.lower()
        return ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff', '.ico']

    def is_video_file(self, file_path):
        """Check if file is a video"""
        ext = Path(file_path).suffix.lower()
        return ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp']

    def is_audio_file(self, file_path):
        """Check if file is audio"""
        ext = Path(file_path).suffix.lower()
        return ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus']

    def is_dex_file(self, file_path):
        """Check if file is a DEX file"""
        return FileUtils.is_dex_file(file_path)

    # === OPEN WITH METHODS ===
    def open_with_text_editor(self, file_path):
        """Open file with text editor"""
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'open_file_in_editor'):
            main_window.open_file_in_editor(file_path)
        else:
            QMessageBox.information(self, "Text Editor", "Text editor not available")

    def open_as_image(self, file_path):
        """Open file as image"""
        # Try to use built-in image viewer first
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'open_image_in_viewer'):
            if main_window.open_image_in_viewer(file_path):
                return

        # Fallback to system default
        try:
            import subprocess
            subprocess.run(['xdg-open', file_path])
        except Exception as e:
            QMessageBox.warning(self, "Image Viewer", f"Failed to open image: {str(e)}")

    def open_as_video(self, file_path):
        """Open file as video"""
        try:
            import subprocess
            # Try common video players
            players = ['vlc', 'mpv', 'totem', 'xdg-open']
            for player in players:
                try:
                    subprocess.run([player, file_path], check=True)
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            QMessageBox.warning(self, "Video Player", "No video player found")
        except Exception as e:
            QMessageBox.warning(self, "Video Player", f"Failed to open video: {str(e)}")

    def open_as_audio(self, file_path):
        """Open file as audio"""
        try:
            import subprocess
            # Try common audio players
            players = ['vlc', 'audacious', 'rhythmbox', 'xdg-open']
            for player in players:
                try:
                    subprocess.run([player, file_path], check=True)
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            QMessageBox.warning(self, "Audio Player", "No audio player found")
        except Exception as e:
            QMessageBox.warning(self, "Audio Player", f"Failed to open audio: {str(e)}")

    def open_with_system_default(self, file_path):
        """Open file with system default application"""
        try:
            import subprocess
            subprocess.run(['xdg-open', file_path])
        except Exception as e:
            QMessageBox.warning(self, "System Default", f"Failed to open file: {str(e)}")

    # === APK TOOLS METHODS ===
    def recompile_apk(self, file_path):
        """Recompile APK file"""
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'apk_tools'):
            main_window.apk_tools.set_apk_file(file_path)
            main_window.focus_tool("APK Tools")
            # Switch to operations tab and trigger recompile
            if hasattr(main_window.apk_tools, 'tab_widget'):
                main_window.apk_tools.tab_widget.setCurrentIndex(1)  # Operations tab
        else:
            QMessageBox.information(self, "APK Tools", "APK tools not available")

    def show_apk_info(self, file_path):
        """Show APK information"""
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'apk_tools'):
            main_window.apk_tools.set_apk_file(file_path)
            main_window.focus_tool("APK Tools")
            # Switch to info tab
            if hasattr(main_window.apk_tools, 'tab_widget'):
                main_window.apk_tools.tab_widget.setCurrentIndex(0)  # Info tab
        else:
            QMessageBox.information(self, "APK Tools", "APK tools not available")

    def extract_apk(self, file_path):
        """Extract APK contents"""
        try:
            import zipfile
            extract_dir = Path(file_path).parent / f"{Path(file_path).stem}_extracted"
            extract_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            QMessageBox.information(self, "Extract APK", f"APK extracted to: {extract_dir}")
            self.refresh()
        except Exception as e:
            QMessageBox.warning(self, "Extract APK", f"Failed to extract APK: {str(e)}")

    # === ARCHIVE TOOLS METHODS ===
    def extract_archive(self, file_path):
        """Extract archive to current directory"""
        try:
            import shutil
            extract_dir = Path(file_path).parent / Path(file_path).stem
            extract_dir.mkdir(exist_ok=True)

            shutil.unpack_archive(file_path, extract_dir)
            QMessageBox.information(self, "Extract Archive", f"Archive extracted to: {extract_dir}")
            self.refresh()
        except Exception as e:
            QMessageBox.warning(self, "Extract Archive", f"Failed to extract archive: {str(e)}")

    def extract_archive_to(self, file_path):
        """Extract archive to chosen directory"""
        from PyQt5.QtWidgets import QFileDialog
        extract_dir = QFileDialog.getExistingDirectory(self, "Extract To", str(self.current_path))
        if extract_dir:
            try:
                import shutil
                shutil.unpack_archive(file_path, extract_dir)
                QMessageBox.information(self, "Extract Archive", f"Archive extracted to: {extract_dir}")
            except Exception as e:
                QMessageBox.warning(self, "Extract Archive", f"Failed to extract archive: {str(e)}")

    def view_archive_contents(self, file_path):
        """View archive contents"""
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'archive_viewer'):
            main_window.archive_viewer.load_archive(file_path)
            main_window.focus_tool("Archive Viewer")
        else:
            QMessageBox.information(self, "Archive Viewer", "Archive viewer not available")

    # === TOOLS METHODS ===
    def compress_file(self, file_path):
        """Compress file or directory"""
        from PyQt5.QtWidgets import QFileDialog

        # Ask for output file
        default_name = f"{Path(file_path).stem}.zip"
        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save Compressed File",
            str(Path(file_path).parent / default_name),
            "ZIP Files (*.zip);;TAR Files (*.tar.gz);;All Files (*)"
        )

        if output_file:
            try:
                import shutil
                if output_file.endswith('.zip'):
                    shutil.make_archive(output_file[:-4], 'zip', Path(file_path).parent, Path(file_path).name)
                elif output_file.endswith('.tar.gz'):
                    shutil.make_archive(output_file[:-7], 'gztar', Path(file_path).parent, Path(file_path).name)
                else:
                    shutil.make_archive(output_file, 'zip', Path(file_path).parent, Path(file_path).name)

                QMessageBox.information(self, "Compress", f"File compressed to: {output_file}")
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Compress", f"Failed to compress file: {str(e)}")

    def calculate_hash(self, file_path):
        """Calculate file hash"""
        try:
            import hashlib

            # Calculate multiple hashes
            hash_md5 = hashlib.md5()
            hash_sha1 = hashlib.sha1()
            hash_sha256 = hashlib.sha256()

            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
                    hash_sha1.update(chunk)
                    hash_sha256.update(chunk)

            # Show results in a dialog
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton

            dialog = QDialog(self)
            dialog.setWindowTitle(f"File Hashes - {Path(file_path).name}")
            dialog.resize(500, 300)

            layout = QVBoxLayout(dialog)

            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(
                f"File: {Path(file_path).name}\n"
                f"Size: {Path(file_path).stat().st_size:,} bytes\n\n"
                f"MD5:    {hash_md5.hexdigest()}\n"
                f"SHA1:   {hash_sha1.hexdigest()}\n"
                f"SHA256: {hash_sha256.hexdigest()}"
            )
            layout.addWidget(text_edit)

            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)

            dialog.exec_()

        except Exception as e:
            QMessageBox.warning(self, "Calculate Hash", f"Failed to calculate hash: {str(e)}")

    def compare_files(self, file_path):
        """Compare files"""
        from PyQt5.QtWidgets import QFileDialog

        # Ask for second file to compare
        other_file, _ = QFileDialog.getOpenFileName(
            self, "Select File to Compare", str(self.current_path), "All Files (*)"
        )

        if other_file:
            try:
                import filecmp

                # Basic comparison
                are_same = filecmp.cmp(file_path, other_file, shallow=False)

                # Size comparison
                size1 = Path(file_path).stat().st_size
                size2 = Path(other_file).stat().st_size

                # Show results
                result_text = f"File 1: {Path(file_path).name} ({size1:,} bytes)\n"
                result_text += f"File 2: {Path(other_file).name} ({size2:,} bytes)\n\n"
                result_text += f"Files are {'identical' if are_same else 'different'}"

                QMessageBox.information(self, "File Comparison", result_text)

            except Exception as e:
                QMessageBox.warning(self, "Compare Files", f"Failed to compare files: {str(e)}")

    def show_properties(self, file_path):
        """Show file properties"""
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'show_file_properties'):
            main_window.show_file_properties(file_path)
        else:
            # Fallback to basic properties dialog
            from src.ui.dialogs import FilePropertiesDialog
            dialog = FilePropertiesDialog(file_path, self)
            dialog.exec_()

    def create_new_file(self):
        """Create new file"""
        name, ok = QInputDialog.getText(self, "New File", "File name:")
        if ok and name:
            try:
                new_file = self.current_path / name
                new_file.touch()
                self.refresh()
                QMessageBox.information(self, "New File", f"Created: {name}")
            except Exception as e:
                QMessageBox.warning(self, "New File", f"Failed to create file: {str(e)}")
