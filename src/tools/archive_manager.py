"""
Archive manager for GP Manager
"""
import os
import zipfile
import tarfile
from pathlib import Path
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeView,
                            QPushButton, QLabel, QMessageBox, QFileDialog,
                            QProgressDialog, QInputDialog, QSplitter,
                            QTextEdit, QGroupBox)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from src.utils.file_utils import FileUtils


class ArchiveExtractWorker(QThread):
    """Worker thread for archive extraction"""

    progress_updated = pyqtSignal(int)
    operation_finished = pyqtSignal(bool, str)
    file_extracted = pyqtSignal(str)

    def __init__(self, archive_path, extract_path, selected_files=None, parent=None):
        super().__init__(parent)
        self.archive_path = archive_path
        self.extract_path = extract_path
        self.selected_files = selected_files or []
        self.cancelled = False

    def run(self):
        """Extract archive"""
        try:
            if self.archive_path.endswith('.zip') or self.archive_path.endswith('.apk'):
                self._extract_zip()
            elif self.archive_path.endswith(('.tar', '.tar.gz', '.tar.bz2')):
                self._extract_tar()
            else:
                raise Exception("Unsupported archive format")

            if not self.cancelled:
                self.operation_finished.emit(True, "Extraction completed successfully")
        except Exception as e:
            self.operation_finished.emit(False, str(e))

    def cancel(self):
        """Cancel extraction"""
        self.cancelled = True

    def _extract_zip(self):
        """Extract ZIP/APK archive"""
        with zipfile.ZipFile(self.archive_path, 'r') as zip_file:
            files_to_extract = self.selected_files if self.selected_files else zip_file.namelist()
            total_files = len(files_to_extract)

            for i, file_name in enumerate(files_to_extract):
                if self.cancelled:
                    break

                try:
                    zip_file.extract(file_name, self.extract_path)
                    self.file_extracted.emit(file_name)
                except Exception as e:
                    print(f"Failed to extract {file_name}: {e}")

                progress = int((i + 1) * 100 / total_files)
                self.progress_updated.emit(progress)

    def _extract_tar(self):
        """Extract TAR archive"""
        with tarfile.open(self.archive_path, 'r') as tar_file:
            files_to_extract = self.selected_files if self.selected_files else tar_file.getnames()
            total_files = len(files_to_extract)

            for i, file_name in enumerate(files_to_extract):
                if self.cancelled:
                    break

                try:
                    tar_file.extract(file_name, self.extract_path)
                    self.file_extracted.emit(file_name)
                except Exception as e:
                    print(f"Failed to extract {file_name}: {e}")

                progress = int((i + 1) * 100 / total_files)
                self.progress_updated.emit(progress)


class ArchiveModel(QStandardItemModel):
    """Model for archive contents"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(['Name', 'Size', 'Compressed', 'Modified'])
        self.archive_path = None

    def load_archive(self, archive_path):
        """Load archive contents"""
        self.clear()
        self.setHorizontalHeaderLabels(['Name', 'Size', 'Compressed', 'Modified'])
        self.archive_path = archive_path

        try:
            if archive_path.endswith('.zip') or archive_path.endswith('.apk'):
                self._load_zip(archive_path)
            elif archive_path.endswith(('.tar', '.tar.gz', '.tar.bz2')):
                self._load_tar(archive_path)
        except Exception as e:
            print(f"Error loading archive: {e}")

    def _load_zip(self, archive_path):
        """Load ZIP/APK archive contents"""
        with zipfile.ZipFile(archive_path, 'r') as zip_file:
            for info in zip_file.infolist():
                if info.is_dir():
                    continue

                # Name
                name_item = QStandardItem(info.filename)
                name_item.setData(info.filename, Qt.UserRole)

                # Size
                size_str = FileUtils.get_file_size_str(info.file_size)
                size_item = QStandardItem(size_str)

                # Compressed size
                compressed_str = FileUtils.get_file_size_str(info.compress_size)
                compressed_item = QStandardItem(compressed_str)

                # Modified time
                import datetime
                modified_time = datetime.datetime(*info.date_time)
                modified_str = modified_time.strftime('%Y-%m-%d %H:%M:%S')
                modified_item = QStandardItem(modified_str)

                self.appendRow([name_item, size_item, compressed_item, modified_item])

    def _load_tar(self, archive_path):
        """Load TAR archive contents"""
        with tarfile.open(archive_path, 'r') as tar_file:
            for info in tar_file.getmembers():
                if info.isdir():
                    continue

                # Name
                name_item = QStandardItem(info.name)
                name_item.setData(info.name, Qt.UserRole)

                # Size
                size_str = FileUtils.get_file_size_str(info.size)
                size_item = QStandardItem(size_str)

                # Compressed (not available for TAR)
                compressed_item = QStandardItem('-')

                # Modified time
                import datetime
                modified_time = datetime.datetime.fromtimestamp(info.mtime)
                modified_str = modified_time.strftime('%Y-%m-%d %H:%M:%S')
                modified_item = QStandardItem(modified_str)

                self.appendRow([name_item, size_item, compressed_item, modified_item])


class ArchiveViewer(QWidget):
    """Archive viewer widget"""

    file_double_clicked = pyqtSignal(str, str)  # archive_path, file_path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_archive = None
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)

        # Archive info
        info_group = QGroupBox("Archive Information")
        info_layout = QVBoxLayout(info_group)

        self.archive_label = QLabel("No archive loaded")
        self.info_label = QLabel("")

        info_layout.addWidget(self.archive_label)
        info_layout.addWidget(self.info_label)

        layout.addWidget(info_group)

        # Archive contents
        contents_group = QGroupBox("Contents")
        contents_layout = QVBoxLayout(contents_group)

        # Tree view for archive contents
        self.tree_view = QTreeView()
        self.archive_model = ArchiveModel()
        self.tree_view.setModel(self.archive_model)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSelectionMode(QTreeView.ExtendedSelection)
        self.tree_view.setSortingEnabled(True)

        # Set column widths
        header = self.tree_view.header()
        header.resizeSection(0, 300)  # Name
        header.resizeSection(1, 80)   # Size
        header.resizeSection(2, 80)   # Compressed
        header.resizeSection(3, 120)  # Modified

        contents_layout.addWidget(self.tree_view)

        # Action buttons
        button_layout = QHBoxLayout()

        self.extract_all_btn = QPushButton("Extract All")
        self.extract_selected_btn = QPushButton("Extract Selected")
        self.view_file_btn = QPushButton("View File")

        button_layout.addWidget(self.extract_all_btn)
        button_layout.addWidget(self.extract_selected_btn)
        button_layout.addWidget(self.view_file_btn)
        button_layout.addStretch()

        contents_layout.addLayout(button_layout)

        layout.addWidget(contents_group)

        # Initially disable buttons
        self.update_ui_state()

    def setup_connections(self):
        """Setup signal connections"""
        self.extract_all_btn.clicked.connect(self.extract_all)
        self.extract_selected_btn.clicked.connect(self.extract_selected)
        self.view_file_btn.clicked.connect(self.view_selected_file)
        self.tree_view.doubleClicked.connect(self.on_file_double_clicked)

    def load_archive(self, archive_path):
        """Load archive for viewing"""
        try:
            self.current_archive = archive_path
            self.archive_model.load_archive(archive_path)

            # Update labels
            archive_name = Path(archive_path).name
            self.archive_label.setText(f"Archive: {archive_name}")

            # Get archive info
            file_size = Path(archive_path).stat().st_size
            size_str = FileUtils.get_file_size_str(file_size)
            file_count = self.archive_model.rowCount()

            self.info_label.setText(f"Size: {size_str} | Files: {file_count}")

            self.update_ui_state()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load archive: {str(e)}")

    def get_selected_files(self):
        """Get selected file paths from archive"""
        selected_files = []
        selection = self.tree_view.selectionModel()
        if selection:
            for index in selection.selectedRows():
                item = self.archive_model.itemFromIndex(index)
                if item:
                    file_path = item.data(Qt.UserRole)
                    if file_path:
                        selected_files.append(file_path)
        return selected_files

    def extract_all(self):
        """Extract all files from archive"""
        if not self.current_archive:
            return

        extract_dir = QFileDialog.getExistingDirectory(
            self, "Select Extract Directory"
        )

        if extract_dir:
            self._extract_files(extract_dir)

    def extract_selected(self):
        """Extract selected files from archive"""
        if not self.current_archive:
            return

        selected_files = self.get_selected_files()
        if not selected_files:
            QMessageBox.information(self, "No Selection", "Please select files to extract.")
            return

        extract_dir = QFileDialog.getExistingDirectory(
            self, "Select Extract Directory"
        )

        if extract_dir:
            self._extract_files(extract_dir, selected_files)

    def _extract_files(self, extract_dir, selected_files=None):
        """Extract files with progress dialog"""
        progress_dialog = QProgressDialog(
            "Extracting files...", "Cancel", 0, 100, self
        )
        progress_dialog.setWindowTitle("Extract Archive")
        progress_dialog.setModal(True)
        progress_dialog.show()

        # Create worker thread
        worker = ArchiveExtractWorker(
            self.current_archive, extract_dir, selected_files
        )

        # Connect signals
        worker.progress_updated.connect(progress_dialog.setValue)
        worker.operation_finished.connect(
            lambda success, message: self._on_extract_finished(
                success, message, progress_dialog, worker
            )
        )
        progress_dialog.canceled.connect(worker.cancel)

        # Start extraction
        worker.start()

    def _on_extract_finished(self, success, message, progress_dialog, worker):
        """Handle extraction completion"""
        progress_dialog.close()
        worker.quit()
        worker.wait()

        if success:
            QMessageBox.information(self, "Success", "Files extracted successfully.")
        else:
            QMessageBox.critical(self, "Error", f"Extraction failed: {message}")

    def view_selected_file(self):
        """View selected file content"""
        selected_files = self.get_selected_files()
        if len(selected_files) == 1:
            self.file_double_clicked.emit(self.current_archive, selected_files[0])

    def on_file_double_clicked(self, index):
        """Handle file double click"""
        if not index.isValid():
            return

        item = self.archive_model.itemFromIndex(index)
        if item:
            file_path = item.data(Qt.UserRole)
            if file_path:
                self.file_double_clicked.emit(self.current_archive, file_path)

    def update_ui_state(self):
        """Update UI state"""
        has_archive = self.current_archive is not None

        self.extract_all_btn.setEnabled(has_archive)
        self.extract_selected_btn.setEnabled(has_archive)
        self.view_file_btn.setEnabled(has_archive)

    def extract_file_content(self, file_path):
        """Extract single file content for viewing"""
        if not self.current_archive:
            return None

        try:
            if self.current_archive.endswith('.zip') or self.current_archive.endswith('.apk'):
                with zipfile.ZipFile(self.current_archive, 'r') as zip_file:
                    return zip_file.read(file_path)
            elif self.current_archive.endswith(('.tar', '.tar.gz', '.tar.bz2')):
                with tarfile.open(self.current_archive, 'r') as tar_file:
                    member = tar_file.getmember(file_path)
                    return tar_file.extractfile(member).read()
        except Exception as e:
            print(f"Error extracting file content: {e}")
            return None
